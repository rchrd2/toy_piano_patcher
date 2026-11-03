#!/usr/bin/env python3
"""Toy-to-piano patcher. Unofficial, personal use, no warranty: see README.md.

Makes a patched copy of the supported v1.30 updater (see README.md), so the Toy position selects
bank 0/0 program 0. The source is only ever read.

Open it with mac_open_patcher.command or win_open_patcher.bat, or: python3 toy_piano_patcher.py
"""
import hashlib
import os
import plistlib
import queue
import re
import shutil
import stat
import struct
import subprocess
import sys
import threading
import zipfile

PATCHER_VERSION = '1'  # a whole number, set by the pre-commit hook from VERSION
FIRMWARE_TAG = 'v130-3'  # the manufacturer's updater version this patches
TOOL_TAG = f'{FIRMWARE_TAG}_v{PATCHER_VERSION}'  # used in output names, e.g. v130-3_v1
DAT_NAME = 'reface updater.dat'
SOURCE_SHA256 = '115cd5bbc80ec1d5852bd1bdc3d36dd0ce5e2c82e7534710028ac35329b931e4'
PATCHED_SHA256 = '5f78926f05a1c4c78e05c6434c1b069829cc46da2d34e1ee1582f1c968596385'
IMAGE_SIZE = 0x440000
BLOCK_PAYLOAD = 16368

# Image offset, original value, new value.
EDITS = (
    (0x1F672B, 0x01, 0x00),  # Toy record: bank LSB
    (0x1F672D, 0x09, 0x00),  # Toy record: program
    (0x29FFFE, 0xDC, 0xE6),  # Code section trailer: balance byte, up by 10 to match
)
# Byte ranges in the image that each end in their own 8-byte checksum trailer.
SECTIONS = ((0, 0x2A0000), (0x2C0000, 0x440000))

RISK_TEXT = (
    'UNOFFICIAL. Not made, endorsed or supported by the manufacturer. For personal use on your own '
    'keyboard. Flashing modified firmware can leave it unusable and may affect warranty or '
    'support. There is NO WARRANTY and you use this entirely at your own risk.'
)
FLASH_TEXT = (
    'When flashing: use the AC adaptor, and do not power off until ALL 6 TYPE lamps are lit, '
    'even after the app looks finished. Keep the original updater so you can restore.'
)


class PatchError(Exception):
    """A problem to show the user, as opposed to a bug."""


def read_vlq(data, pos):
    value = 0
    while True:
        byte = data[pos]
        pos += 1
        value = value << 7 | byte & 0x7F
        if not byte & 0x80:
            return value, pos


def sysex_messages(data):
    """Return (start, length) of each SysEx body in the updater's MIDI file."""
    pos = 8 + int.from_bytes(data[4:8], 'big')
    end = pos + 8 + int.from_bytes(data[pos + 4:pos + 8], 'big')
    pos += 8
    messages = []
    while pos < end:
        _, pos = read_vlq(data, pos)
        if data[pos] == 0xF0:
            length, pos = read_vlq(data, pos + 1)
            messages.append((pos, length))
            pos += length
        elif data[pos] == 0xFF:
            length, pos = read_vlq(data, pos + 2)
            pos += length
        else:
            raise PatchError('Unexpected data in the firmware file.')
    return messages


def decode_image(data):
    """Unpack the firmware image, checking every message checksum on the way."""
    image = bytearray()
    for start, length in sysex_messages(data):
        message = data[start:start + length]
        if sum(message[6:-1]) & 0x7F:
            raise PatchError('A SysEx message checksum is wrong.')
        if length < 64:
            continue  # the header message carries no image data
        payload = message[14:-2]
        for i in range(0, len(payload) & ~7, 8):
            high = payload[i]
            image += bytes(b | ((high >> (6 - j)) & 1) << 7 for j, b in enumerate(payload[i + 1:i + 8]))
    return bytes(image[:IMAGE_SIZE])


def sample_offsets(size):
    """Offsets the firmware's quick ROM check reads: 0,4,8,16..0x40000 in each 0x80000 window."""
    step, window = 0, 0
    while window + step < size:
        yield window + step
        if step == 0:
            step = 4
        else:
            step <<= 1
            if step > 0x40000:
                step, window = 0, window + 0x80000


def section_ok(section):
    """Model of the firmware's check. Trailer layout: L0 L1 L2 L3 S FF Z FF."""
    trailer = section[-8:]
    lanes = [0, 0, 0, 0]
    for offset in sample_offsets(len(section) - 8):
        for lane in range(4):
            lanes[lane] = (lanes[lane] + section[offset + lane]) & 0xFF
    return (bytes(lanes) == trailer[:4]
            and sum(trailer[:4]) & 0xFF == trailer[4]
            and -(sum(section[:-2])) & 0xFF == trailer[6])


def patch_dat(original):
    """Return patched file bytes. Every edit is checked against the expected old value."""
    data = bytearray(original)
    blocks = sysex_messages(data)[1:]
    touched = set()
    for image_offset, old, new in EDITS:
        group, position = divmod(image_offset, 7)
        encoded = group * 8 + 1 + position
        block, within = divmod(encoded, BLOCK_PAYLOAD)
        offset = blocks[block][0] + 14 + within
        # The top bit is stored in a separate byte, so these edits must leave it alone.
        if (old ^ new) & 0x80 or data[offset] != old & 0x7F:
            raise PatchError(f'Firmware byte at image offset {image_offset:#x} is not as expected.')
        data[offset] = new & 0x7F
        touched.add(block)
    for block in touched:
        start, length = blocks[block]
        checksum_at = start + length - 2
        data[checksum_at] = -sum(data[start + 6:checksum_at]) & 0x7F
    return bytes(data)


def verify_patch(original, patched):
    """Decode the output from scratch and confirm it differs only as intended."""
    before, after = decode_image(original), decode_image(patched)
    if len(after) != IMAGE_SIZE:
        raise PatchError('Patched image has the wrong size.')
    changed = {i: (before[i], after[i]) for i in range(IMAGE_SIZE) if before[i] != after[i]}
    if changed != {offset: (old, new) for offset, old, new in EDITS}:
        raise PatchError('Patched image differs in unexpected places.')
    for start, end in SECTIONS:
        if not section_ok(after[start:end]):
            raise PatchError(f'Section {start:#x}-{end:#x} fails its checksum.')
    if hashlib.sha256(patched).hexdigest() != PATCHED_SHA256:
        raise PatchError('Patched file does not match the expected hash.')


def is_within(path, parent):
    path, parent = os.path.realpath(path), os.path.realpath(parent)
    return path == parent or path.startswith(parent + os.sep)


def find_source(source):
    """Work out what the user selected. Returns (kind, root, path to the .dat file)."""
    source = os.path.abspath(os.path.expanduser(source))
    if not os.path.exists(source):
        raise PatchError(f'Not found: {source}')
    if os.path.isfile(source):
        if os.path.basename(source).lower().endswith('.dat'):
            return 'dat', source, source
        if os.path.basename(source).lower().endswith('.zip'):
            return 'zip', source, None
        if os.path.basename(source).lower().endswith('.exe'):
            source = os.path.dirname(source)
        else:
            raise PatchError('Select the updater app, its .exe, the .zip it came in, its folder, or its .dat file.')
    if source.endswith('.app'):
        return 'mac', source, os.path.join(source, 'Contents', 'Resources', DAT_NAME)
    if os.path.isfile(os.path.join(source, DAT_NAME)):
        return 'windows', source, os.path.join(source, DAT_NAME)
    apps = [n for n in sorted(os.listdir(source)) if n.endswith('.app')]
    if len(apps) == 1:
        return find_source(os.path.join(source, apps[0]))
    raise PatchError(f'No "{DAT_NAME}" found in {source}')


def zip_contents(path):
    """Find the firmware inside a downloaded zip, without unpacking anything.
    Returns (kind, member name of the .dat, prefix of the updater's files inside the zip)."""
    try:
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist() if not n.startswith('__MACOSX/')]
    except (zipfile.BadZipFile, OSError) as error:
        raise PatchError(f'Could not read the zip file: {error}')
    members = [n for n in names if n.rsplit('/', 1)[-1] == DAT_NAME]
    if not members:
        raise PatchError(f'No "{DAT_NAME}" found in {path}')
    if len(members) > 1:
        raise PatchError(f'More than one "{DAT_NAME}" in {path}. Unzip it and choose the updater itself.')
    member = members[0]
    app = re.match(r'(.*\.app/)Contents/Resources/[^/]+$', member)
    if app:
        return 'mac', member, app.group(1)
    if '/' in member:
        return 'windows', member, member.rsplit('/', 1)[0] + '/'
    return 'dat', member, ''


def extract_updater(zip_path, prefix, target):
    """Unpack only the zip entries under prefix into target, keeping permissions and symlinks,
    so an unpacked Mac app can still run."""
    os.mkdir(target)
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            name = info.filename
            if not name.startswith(prefix) or name == prefix:
                continue
            parts = name[len(prefix):].rstrip('/').split('/')
            if any(part in ('', '.', '..') for part in parts):
                raise PatchError(f'Unsafe path in the zip, so nothing was made: {name}')
            out = os.path.join(target, *parts)
            if name.endswith('/'):
                os.makedirs(out, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                os.symlink(archive.read(info).decode('utf-8'), out)
                continue
            with archive.open(info) as src, open(out, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            if mode & 0o777:
                os.chmod(out, mode & 0o777)


def read_original(source_kind, root, dat_path):
    """The original firmware bytes, from a file or from inside a zip."""
    if source_kind == 'zip':
        with zipfile.ZipFile(root) as archive:
            return archive.read(dat_path)
    with open(dat_path, 'rb') as handle:
        return handle.read()


def sign_mac_app(app, log):
    if sys.platform != 'darwin':
        log('WARNING: not on macOS, so the app was not re-signed. Run on a Mac: '
            f'codesign --force --deep -s - "{app}"')
        return
    try:
        subprocess.run(['codesign', '--force', '--deep', '-s', '-', app],
                       check=True, capture_output=True, text=True)
        subprocess.run(['codesign', '--verify', '--deep', '--strict', app],
                       check=True, capture_output=True, text=True)
    except FileNotFoundError:
        raise PatchError('codesign was not found. Install the Xcode command line tools.')
    except subprocess.CalledProcessError as error:
        raise PatchError(f'Signing failed: {error.stderr.strip()}')
    # The copy inherits the download's quarantine flag from the original. Clear it on the new app only,
    # so macOS doesn't stop the patched copy with a separate warning. The original is never touched.
    subprocess.run(['xattr', '-dr', 'com.apple.quarantine', app], capture_output=True)
    log('Signed the new app locally.')


def build(source, dest_parent, log):
    """Create the patched copy inside dest_parent and return its path."""
    kind, root, dat_path = find_source(source)
    source_kind, prefix = kind, None
    if source_kind == 'zip':
        # Read the firmware straight from the zip; only the updater itself is unpacked, into the output.
        kind, dat_path, prefix = zip_contents(root)
        log(f'Source: {root} ({kind} updater, inside a zip)')
    else:
        if not os.path.isfile(dat_path):
            raise PatchError(f'No "{DAT_NAME}" found inside {root}')
        log(f'Source: {root} ({kind})')
    original = read_original(source_kind, root, dat_path)
    digest = hashlib.sha256(original).hexdigest()
    if digest != SOURCE_SHA256:
        raise PatchError('This is not the v1.30 firmware this tool supports, so nothing '
                         f'was changed.\nFound SHA-256: {digest}')
    log('Source firmware recognised.')

    dest_parent = os.path.abspath(os.path.expanduser(dest_parent))
    if not os.path.isdir(dest_parent):
        raise PatchError(f'Destination folder does not exist: {dest_parent}')
    if source_kind not in ('dat', 'zip') and is_within(dest_parent, root):
        raise PatchError('The destination cannot be inside the original updater.')
    suffix = {'mac': 'mac', 'windows': 'win', 'dat': 'dat'}[kind]
    output = os.path.join(dest_parent, f'toy_piano_updater_{TOOL_TAG}_{suffix}')
    if os.path.lexists(output):
        raise PatchError(f'Already exists, and will not be overwritten: {output}')

    log('Patching and checking...')
    patched = patch_dat(original)
    verify_patch(original, patched)
    log('Check passed: only the 3 intended firmware bytes differ, and checksums are valid.')

    # Build under a .tmp name and only rename when complete, so a failure can't look finished.
    work = output + '.tmp'
    if os.path.lexists(work):
        raise PatchError(f'Already exists, please remove it first: {work}')

    def copy_updater(target):
        if source_kind == 'zip':
            extract_updater(root, prefix, target)
        else:
            shutil.copytree(root, target, symlinks=True)

    try:
        if kind == 'dat':
            os.mkdir(work)
            with open(os.path.join(work, DAT_NAME), 'wb') as handle:
                handle.write(patched)
        elif kind == 'windows':
            copy_updater(work)
            with open(os.path.join(work, DAT_NAME), 'wb') as handle:
                handle.write(patched)
        else:
            os.mkdir(work)
            app = os.path.join(work, f'toy piano updater {TOOL_TAG}.app')
            copy_updater(app)
            with open(os.path.join(app, 'Contents', 'Resources', DAT_NAME), 'wb') as handle:
                handle.write(patched)
            plist_path = os.path.join(app, 'Contents', 'Info.plist')
            with open(plist_path, 'rb') as handle:
                info = plistlib.load(handle)
            info['CFBundleName'] = f'toy piano updater {TOOL_TAG}'
            # Bundle identifiers allow only letters, digits, hyphens and dots, so no underscore here.
            info['CFBundleIdentifier'] = f'local.toy-piano-updater.{FIRMWARE_TAG}-v{PATCHER_VERSION}'
            info['CFBundleGetInfoString'] = (f'{TOOL_TAG}: UNOFFICIAL patched build, not from the manufacturer. '
                                             'Toy selects bank 0/0 program 0.')
            with open(plist_path, 'wb') as handle:
                plistlib.dump(info, handle)
            sign_mac_app(app, log)
        os.rename(work, output)
    except OSError as error:
        raise PatchError(f'Could not write the new copy: {error}\n'
                         f'Do not use the incomplete folder, and delete it yourself: {work}') from error

    if hashlib.sha256(read_original(source_kind, root, dat_path)).hexdigest() != SOURCE_SHA256:
        raise PatchError('The original firmware changed during this run. Do not use either copy.')
    log('Original left unchanged.')
    log(f'Created: {output}')
    log(FLASH_TEXT)
    return output


def patched_item(output):
    """The thing to show the user inside an output folder: the .app, otherwise the .dat."""
    for name in sorted(os.listdir(output)):
        if name.endswith('.app'):
            return os.path.join(output, name)
    return os.path.join(output, DAT_NAME)


def reveal_in_file_manager(path):
    """Show the item selected in Finder or Explorer; elsewhere, open its folder."""
    if sys.platform == 'darwin':
        subprocess.Popen(['open', '-R', path])
    elif sys.platform == 'win32':
        subprocess.Popen(f'explorer /select,"{os.path.normpath(path)}"')
    else:
        subprocess.Popen(['xdg-open', os.path.dirname(path)])


def run_gui():
    try:
        import tkinter as tk
        from tkinter import filedialog, ttk
    except ImportError:
        print('This Python has no Tkinter, which the patcher window needs.\n'
              'Install Python from https://www.python.org/downloads/ and try again.', file=sys.stderr)
        return 1

    try:
        root = tk.Tk()
    except tk.TclError:
        print('Could not open the patcher window. Run it from a normal desktop session.\n'
              'If that fails too, install Python from https://www.python.org/downloads/ and try again.',
              file=sys.stderr)
        return 1
    root.title(f'Toy piano patcher v{PATCHER_VERSION}')
    source, dest, accepted = tk.StringVar(), tk.StringVar(), tk.BooleanVar()
    frame = ttk.Frame(root, padding=12)
    frame.grid(sticky='nsew')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(9, weight=1)

    ttk.Label(frame, text=RISK_TEXT, wraplength=560, justify='left').grid(row=0, column=0, columnspan=2, sticky='w')

    def choose_source():
        # A file picker, so a Mac .app (which macOS treats as a file), a Windows .exe, the downloaded
        # .zip or the .dat can all be selected. A folder path can still be pasted into the box.
        path = filedialog.askopenfilename(title='Select the original updater: the .app, .exe, .zip or .dat')
        if path:
            source.set(path)

    def choose_dest():
        # mustexist=False is what makes the Mac picker offer New Folder.
        path = filedialog.askdirectory(title='Select where to save the patched copy', mustexist=False)
        if path:
            try:
                os.makedirs(path, exist_ok=True)
            except OSError as error:
                write_log(f'STOPPED: could not create {path}: {error}')
                return
            dest.set(path)

    ttk.Label(frame, text='Original updater', font='TkDefaultFont 13 bold').grid(row=1, column=0, columnspan=2, sticky='w', pady=(12, 0))
    ttk.Label(frame, text='Select the original updater: the app on a Mac, the .exe on Windows, or the .zip you downloaded it in. '
                          'You can also paste the path to its folder or .dat. It is only read, never changed.',
              wraplength=560, justify='left').grid(row=2, column=0, columnspan=2, sticky='w')
    ttk.Entry(frame, textvariable=source).grid(row=3, column=0, sticky='ew', pady=2)
    ttk.Button(frame, text='Choose...', command=choose_source).grid(row=3, column=1, padx=(6, 0), pady=2)

    ttk.Label(frame, text='Save location', font='TkDefaultFont 13 bold').grid(row=4, column=0, columnspan=2, sticky='w', pady=(12, 0))
    ttk.Label(frame, text=f'Select a folder, or create one. A new folder named toy_piano_updater_{TOOL_TAG}_mac (or _win) '
                          'containing the patched updater is created inside it. Nothing is overwritten.',
              wraplength=560, justify='left').grid(row=5, column=0, columnspan=2, sticky='w')
    ttk.Entry(frame, textvariable=dest).grid(row=6, column=0, sticky='ew', pady=2)
    ttk.Button(frame, text='Choose...', command=choose_dest).grid(row=6, column=1, padx=(6, 0), pady=2)

    ttk.Checkbutton(frame, variable=accepted, text='I accept the risk, and this is for my own personal use.',
                    command=lambda: refresh()).grid(row=7, column=0, columnspan=2, sticky='w', pady=(12, 2))
    actions = ttk.Frame(frame)
    actions.grid(row=8, column=0, columnspan=2, sticky='w', pady=4)
    patch_button = ttk.Button(actions, text='Create patched copy', state='disabled')
    patch_button.grid(row=0, column=0)
    show_button = ttk.Button(actions, text='Show patched file', state='disabled')
    show_button.grid(row=0, column=1, padx=(6, 0))

    log_box = tk.Text(frame, height=10, width=78, state='disabled', wrap='word',
                      foreground='black', background='white')
    log_box.grid(row=9, column=0, columnspan=2, sticky='nsew', pady=(4, 0))
    write_flash = ttk.Label(frame, text=FLASH_TEXT, wraplength=560, justify='left')
    write_flash.grid(row=10, column=0, columnspan=2, sticky='w', pady=(6, 0))

    def write_log(text):
        log_box.configure(state='normal')
        log_box.insert('end', text + '\n')
        log_box.see('end')
        log_box.configure(state='disabled')

    busy = [False]
    patched = [None]

    def refresh():
        ready = accepted.get() and source.get().strip() and dest.get().strip() and not busy[0]
        patch_button.configure(state='normal' if ready else 'disabled')

    source.trace_add('write', lambda *_: refresh())
    dest.trace_add('write', lambda *_: refresh())

    # The worker thread never touches the window. It queues messages, and the main thread shows them.
    events = queue.Queue()

    def worker(src, dst):
        try:
            events.put(('done', build(src, dst, lambda text: events.put(('log', text)))))
        except PatchError as error:
            events.put(('log', f'STOPPED: {error}'))
            events.put(('done', None))
        except Exception as error:  # keep the window usable and show what went wrong
            events.put(('log', f'STOPPED, unexpected error: {error!r}'))
            events.put(('done', None))

    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == 'log':
                    write_log(value)
                else:
                    busy[0] = False
                    if value:
                        patched[0] = patched_item(value)
                        show_button.configure(state='normal')
                        write_log('Done. Click "Show patched file" to find it.')
                    refresh()
        except queue.Empty:
            pass
        root.after(100, poll)

    def start():
        busy[0] = True
        patched[0] = None
        show_button.configure(state='disabled')
        refresh()
        write_log('Starting. This takes a few seconds...')
        threading.Thread(target=worker, args=(source.get().strip(), dest.get().strip()), daemon=True).start()

    def show_patched():
        try:
            reveal_in_file_manager(patched[0])
        except OSError as error:
            write_log(f'Could not open the file manager: {error}. The file is at: {patched[0]}')

    show_button.configure(command=show_patched)
    poll()
    patch_button.configure(command=start)
    root.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(run_gui())
