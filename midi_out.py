"""Send MIDI System Exclusive messages with the operating system's own MIDI library.

Standard library only (ctypes): CoreMIDI on macOS, winmm on Windows. The sending mirrors the manufacturer's
updater, as read from its code (see analysis/NOTES.md in the research folder):

- macOS: each complete message goes into one MIDIPacketList, split into packets of at most 256 bytes, all
  stamped "now", and is passed to MIDISend once.
- Windows: each complete message is prepared and sent with midiOutLongMsg, then we wait until the driver marks
  it done before returning.

Nothing is read back: the manufacturer's updater doesn't listen to the keyboard either.
"""
import ctypes
import sys
import time


class MidiError(Exception):
    """A MIDI problem to show the user."""


def supported():
    return sys.platform in ('darwin', 'win32')


def list_outputs():
    """Names of the MIDI outputs, in the order open_output() takes."""
    if sys.platform == 'darwin':
        return _CoreMidi.instance().destination_names()
    if sys.platform == 'win32':
        return _WinMM.instance().device_names()
    raise MidiError('Sending directly is only available on macOS and Windows.')


def open_output(index):
    """Open the output at this position in list_outputs(). Returns an object with send_sysex() and close()."""
    if sys.platform == 'darwin':
        return _CoreMidi.instance().open(index)
    if sys.platform == 'win32':
        return _WinMM.instance().open(index)
    raise MidiError('Sending directly is only available on macOS and Windows.')


# ---- macOS: CoreMIDI ----------------------------------------------------------------------------------------

class _CoreMidi:
    _instance = None
    UTF8 = 0x08000100  # kCFStringEncodingUTF8

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        cf = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
        cm = ctypes.CDLL('/System/Library/Frameworks/CoreMIDI.framework/CoreMIDI')
        self.cf, self.cm = cf, cm
        u32, vp = ctypes.c_uint32, ctypes.c_void_p

        cf.CFStringCreateWithCString.argtypes = [vp, ctypes.c_char_p, u32]
        cf.CFStringCreateWithCString.restype = vp
        cf.CFStringGetCString.argtypes = [vp, ctypes.c_char_p, ctypes.c_long, u32]
        cf.CFStringGetCString.restype = ctypes.c_bool
        cf.CFRelease.argtypes = [vp]

        cm.MIDIClientCreate.argtypes = [vp, vp, vp, ctypes.POINTER(u32)]
        cm.MIDIClientCreate.restype = ctypes.c_int32
        cm.MIDIOutputPortCreate.argtypes = [u32, vp, ctypes.POINTER(u32)]
        cm.MIDIOutputPortCreate.restype = ctypes.c_int32
        cm.MIDIPortDispose.argtypes = [u32]
        cm.MIDIPortDispose.restype = ctypes.c_int32
        cm.MIDIGetNumberOfDestinations.argtypes = []
        cm.MIDIGetNumberOfDestinations.restype = ctypes.c_ulong
        cm.MIDIGetDestination.argtypes = [ctypes.c_ulong]
        cm.MIDIGetDestination.restype = u32
        cm.MIDIObjectGetStringProperty.argtypes = [u32, vp, ctypes.POINTER(vp)]
        cm.MIDIObjectGetStringProperty.restype = ctypes.c_int32
        cm.MIDIPacketListInit.argtypes = [vp]
        cm.MIDIPacketListInit.restype = vp
        cm.MIDIPacketListAdd.argtypes = [vp, ctypes.c_ulong, vp, ctypes.c_uint64, ctypes.c_ulong, vp]
        cm.MIDIPacketListAdd.restype = vp
        cm.MIDISend.argtypes = [u32, u32, vp]
        cm.MIDISend.restype = ctypes.c_int32
        self.display_name = vp.in_dll(cm, 'kMIDIPropertyDisplayName')

        self.client = u32()
        status = cm.MIDIClientCreate(self._cfstr('Toy piano patcher'), None, None, ctypes.byref(self.client))
        if status:
            raise MidiError(f'Could not start CoreMIDI (error {status}).')

    def _cfstr(self, text):
        return self.cf.CFStringCreateWithCString(None, text.encode('utf-8'), self.UTF8)

    def destination_names(self):
        names = []
        for i in range(self.cm.MIDIGetNumberOfDestinations()):
            endpoint = self.cm.MIDIGetDestination(i)
            string = ctypes.c_void_p()
            name = f'MIDI output {i + 1}'
            if not self.cm.MIDIObjectGetStringProperty(endpoint, self.display_name, ctypes.byref(string)) and string:
                buffer = ctypes.create_string_buffer(512)
                if self.cf.CFStringGetCString(string, buffer, len(buffer), self.UTF8):
                    name = buffer.value.decode('utf-8', 'replace')
                self.cf.CFRelease(string)
            names.append(name)
        return names

    def open(self, index):
        if not 0 <= index < self.cm.MIDIGetNumberOfDestinations():
            raise MidiError('That MIDI output is no longer there. Click Refresh.')
        port = ctypes.c_uint32()
        status = self.cm.MIDIOutputPortCreate(self.client, self._cfstr('Toy piano patcher out'), ctypes.byref(port))
        if status:
            raise MidiError(f'Could not open a MIDI output port (error {status}).')
        return _CoreMidiOutput(self.cm, port.value, self.cm.MIDIGetDestination(index))


class _CoreMidiOutput:
    def __init__(self, cm, port, destination):
        self.cm, self.port, self.destination = cm, port, destination

    def send_sysex(self, message):
        # The same packet list the manufacturer's updater builds: packets of at most 256 bytes, all stamped
        # now (timestamp 0), sent with one MIDISend. Buffer size as in its code: length * 0x10C / 256 + 0x110.
        size = len(message) * 0x10C // 256 + 0x110
        packet_list = ctypes.create_string_buffer(size)
        data = ctypes.create_string_buffer(bytes(message), len(message))
        packet = self.cm.MIDIPacketListInit(packet_list)
        for offset in range(0, len(message), 256):
            chunk = min(256, len(message) - offset)
            packet = self.cm.MIDIPacketListAdd(packet_list, size, packet, 0, chunk,
                                               ctypes.addressof(data) + offset)
            if not packet:
                raise MidiError('Could not build the MIDI packet list.')
        status = self.cm.MIDISend(self.port, self.destination, packet_list)
        if status:
            raise MidiError(f'MIDI send failed (error {status}).')

    def close(self):
        if self.port:
            self.cm.MIDIPortDispose(self.port)
            self.port = 0


# ---- Windows: winmm -----------------------------------------------------------------------------------------

class _MIDIOUTCAPSW(ctypes.Structure):
    _fields_ = [('wMid', ctypes.c_ushort), ('wPid', ctypes.c_ushort), ('vDriverVersion', ctypes.c_uint),
                ('szPname', ctypes.c_wchar * 32), ('wTechnology', ctypes.c_ushort), ('wVoices', ctypes.c_ushort),
                ('wNotes', ctypes.c_ushort), ('wChannelMask', ctypes.c_ushort), ('dwSupport', ctypes.c_ulong)]


class _MIDIHDR(ctypes.Structure):
    pass


_MIDIHDR._fields_ = [('lpData', ctypes.c_void_p), ('dwBufferLength', ctypes.c_ulong),
                     ('dwBytesRecorded', ctypes.c_ulong), ('dwUser', ctypes.c_size_t), ('dwFlags', ctypes.c_ulong),
                     ('lpNext', ctypes.POINTER(_MIDIHDR)), ('reserved', ctypes.c_size_t),
                     ('dwOffset', ctypes.c_ulong), ('dwReserved', ctypes.c_size_t * 8)]

MHDR_DONE = 0x00000001
CALLBACK_NULL = 0


class _WinMM:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        mm = ctypes.WinDLL('winmm')
        self.mm = mm
        handle = ctypes.c_void_p
        mm.midiOutGetNumDevs.restype = ctypes.c_uint
        mm.midiOutGetDevCapsW.argtypes = [ctypes.c_size_t, ctypes.POINTER(_MIDIOUTCAPSW), ctypes.c_uint]
        mm.midiOutGetDevCapsW.restype = ctypes.c_uint
        mm.midiOutOpen.argtypes = [ctypes.POINTER(handle), ctypes.c_uint, ctypes.c_size_t, ctypes.c_size_t,
                                   ctypes.c_ulong]
        mm.midiOutOpen.restype = ctypes.c_uint
        for name in ('midiOutPrepareHeader', 'midiOutUnprepareHeader', 'midiOutLongMsg'):
            fn = getattr(mm, name)
            fn.argtypes = [handle, ctypes.POINTER(_MIDIHDR), ctypes.c_uint]
            fn.restype = ctypes.c_uint
        mm.midiOutClose.argtypes = [handle]
        mm.midiOutClose.restype = ctypes.c_uint
        mm.midiOutGetErrorTextW.argtypes = [ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_uint]
        mm.midiOutGetErrorTextW.restype = ctypes.c_uint

    def error_text(self, code):
        buffer = ctypes.create_unicode_buffer(256)
        if self.mm.midiOutGetErrorTextW(code, buffer, len(buffer)) == 0:
            return f'{buffer.value} (error {code})'
        return f'error {code}'

    def device_names(self):
        names = []
        for i in range(self.mm.midiOutGetNumDevs()):
            caps = _MIDIOUTCAPSW()
            if self.mm.midiOutGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
                names.append(caps.szPname)
            else:
                names.append(f'MIDI output {i + 1}')
        return names

    def open(self, index):
        if not 0 <= index < self.mm.midiOutGetNumDevs():
            raise MidiError('That MIDI output is no longer there. Click Refresh.')
        handle = ctypes.c_void_p()
        status = self.mm.midiOutOpen(ctypes.byref(handle), index, 0, 0, CALLBACK_NULL)
        if status:
            raise MidiError(f'Could not open the MIDI output: {self.error_text(status)}. '
                            'Close other programs that use MIDI and try again.')
        return _WinMMOutput(self, handle)


class _WinMMOutput:
    def __init__(self, winmm, handle):
        self.winmm, self.handle = winmm, handle

    def send_sysex(self, message):
        # As the manufacturer's updater does: prepare, send the whole message with midiOutLongMsg, wait until
        # the driver has finished with it, then unprepare.
        mm = self.winmm.mm
        data = ctypes.create_string_buffer(bytes(message), len(message))
        header = _MIDIHDR()
        header.lpData = ctypes.cast(data, ctypes.c_void_p)
        header.dwBufferLength = header.dwBytesRecorded = len(message)
        size = ctypes.sizeof(header)
        status = mm.midiOutPrepareHeader(self.handle, ctypes.byref(header), size)
        if status:
            raise MidiError(f'MIDI send failed: {self.winmm.error_text(status)}.')
        try:
            status = mm.midiOutLongMsg(self.handle, ctypes.byref(header), size)
            if status:
                raise MidiError(f'MIDI send failed: {self.winmm.error_text(status)}.')
            deadline = time.monotonic() + 30
            while not header.dwFlags & MHDR_DONE:
                if time.monotonic() > deadline:
                    raise MidiError('The MIDI driver did not finish sending a message within 30 seconds.')
                time.sleep(0.001)
        finally:
            mm.midiOutUnprepareHeader(self.handle, ctypes.byref(header), size)

    def close(self):
        if self.handle:
            self.winmm.mm.midiOutClose(self.handle)
            self.handle = None
