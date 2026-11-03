# Toy piano patcher

Patcher version v1

Turn the **Toy** setting into a piano on a certain compact 37-key electric piano. A small tool with a simple window. It brings its own Python, so there's nothing to install on a Mac or Windows PC.

This is for the keyboard from a well-known Japanese instrument maker with a six-position **TYPE** knob and a rumoured hidden piano sound. If you own one, you'll recognise it.

This is independent work, not affiliated with or endorsed by the manufacturer. No firmware is included: you supply the manufacturer's own updater.

## What it does

The hidden piano normally needs a fiddly trick: powering on with the TYPE knob balanced between two positions. This tool makes a patched copy of the v1.30 updater in which the Toy position selects bank 0/0, program 0 instead of the Toy sound. That voice is the hidden piano, so you can reach it at any time just by turning the knob.

Your other five sounds aren't touched, but the Toy sound is replaced until you go back to the original firmware.

## ⚠️ Before you start: use at your own risk

**This is unofficial, experimental software. Flashing modified firmware can permanently damage your instrument or leave it unusable. You alone are responsible for the outcome.** If you can't accept the risk of losing the use of your keyboard, don't use this.

- **It replaces your keyboard's main firmware.** Recovery has worked in one case, but that's evidence, not a guarantee. See [If something goes wrong](#if-something-goes-wrong).
- **Testing has been limited.** It has been flashed and confirmed working on one keyboard, from a Mac. That doesn't guarantee it will work on yours. See [Known limitations](#known-limitations).
- **It has not been tested on Windows.** The patched Windows updater has never been run on a Windows PC, so Windows users would be the first to try it.
- **There is no warranty.** This software is provided "as is", without warranty of any kind, express or implied, including merchantability, fitness for a particular purpose and non-infringement.
- **The authors accept no liability.** To the fullest extent permitted by law, the authors are not liable for any claim, damage or loss arising from using this software or any firmware it produces, including a damaged instrument, lost settings, or repair costs.
- **Check the manufacturer's licence.** Firmware licences commonly restrict altering or reverse-engineering firmware, and this one may do so. Using modified firmware may also affect your warranty or eligibility for service. Whether to go ahead is your decision and your responsibility.
- **Patched firmware is for your own personal use.** Use it on a keyboard you own, with an updater you obtained yourself. Patched updaters contain the manufacturer's firmware, so don't share them.

## What you need

- The keyboard, with its AC adaptor and a USB cable.
- The manufacturer's original **v1.30** updater, for Mac or Windows. The tool checks the firmware's SHA-256, which must start with `115cd5bbc80ec1d5`. It refuses anything else, including updaters for other keyboards in the same family.
- Nothing to install on a Mac or a Windows PC: Python is included in the `vendor` folder (see [Why there's a `vendor` folder](#why-theres-a-vendor-folder)). On Linux, the launchers aren't included; run the tool with your own Python 3.8 or newer, with Tkinter.
- To patch a Mac updater, a Mac, so the copy can be re-signed with `codesign`. It comes with macOS.

## Make the patched updater

1. **Open the patcher.** Double-click the launcher for your system. The first time, your system asks you to allow it, because it was downloaded from the internet and isn't signed by a registered developer:
    - **Mac:** `mac_open_patcher.command`. If macOS says it can't be opened, open **System Settings → Privacy & Security**, scroll down, click **Open Anyway** next to the launcher's name, and confirm. On macOS 14 and earlier you can instead Control-click the launcher and choose **Open**. You only need to do this once.
    - **Windows (untested):** `win_open_patcher.bat`. If SmartScreen warns you, choose **More info**, then **Run anyway**.
2. **Choose the original.** Under **Original updater**, click **Choose...** and select the updater app (Mac), the updater's `.exe` (Windows), or the `.zip` you downloaded it in. You can also paste the path to the updater's folder or its `.dat` into the box. If you choose the zip, nothing is unpacked except into the new patched copy.
3. **Choose where to save it.** Under **Save location**, choose a folder, or create one in the picker. The tool creates a new folder inside it.
4. **Create it.** Tick the risk box and click **Create patched copy**. Progress appears in the log, and it takes a few seconds.
5. **Find it.** Click **Show patched file** to see the result in Finder or File Explorer. On a Mac, the patched app is already re-signed, so it opens normally.

### What you get

| Your original | Folder created | Contains |
|---|---|---|
| Mac updater, or its `.zip` | `toy_piano_updater_v130-3_v1_mac` | `toy piano updater v130-3_v1.app`, renamed and signed locally |
| Windows updater, or its `.zip` | `toy_piano_updater_v130-3_v1_win` | A copy of the updater folder with the patched `.dat` |
| A `.dat` path pasted into the box | `toy_piano_updater_v130-3_v1_dat` | Only the patched `.dat` |

`v130-3` is the manufacturer's updater version, and `v1` is the patcher's own version, which goes up with each update (see [Versioning](#versioning)). That way you can tell which patcher made a copy.

The tool only reads your original. It won't overwrite an existing output, and it won't save inside the original updater.

If a write fails partway, the tool leaves a folder ending in `.tmp` and tells you where it is. Don't use it. Delete it yourself before trying again.

### Opening it from the command line

If the launcher won't run, or you want to see any error messages, start the patcher from a terminal with the bundled Python. It opens the same window and takes no options.

1. Open **Terminal** on a Mac, or **Command Prompt** on Windows.
2. Go to the patcher's folder, for example:

    ```bash
    cd ~/Downloads/toy_piano_patcher
    ```

3. Start it:
    - **Apple Silicon Mac:** `vendor/python-mac-arm64/bin/python3.13 toy_piano_patcher.py`
    - **Intel Mac:** `vendor/python-mac-x86_64/bin/python3.13 toy_piano_patcher.py`
    - **Windows (untested):** `vendor\python-win\python.exe toy_piano_patcher.py`
    - **Linux, or your own Python:** `python3 toy_piano_patcher.py`

Then carry on from step 2 above. Any errors appear in the terminal, and closing the window returns you to the prompt.

## Flash it

Follow the manufacturer's updater guide alongside these steps, and keep the original updater.

1. **Test your setup.** Flash the **original** updater first, using the steps below. If that fails, stop here.
2. **Prepare.** Use the AC adaptor, and stop your computer from sleeping.
3. **Enter update mode.** Switch the keyboard off, hold **F#3, A3 and C#4** together, and switch it on. The **Rd I** lamp lights.
4. **Start the update.** Open the patched updater, set **MIDI Port** to the keyboard, and click **Start**.
5. **Wait until ALL 6 TYPE lamps are lit, however long it takes.** The whole update takes about five minutes. The app can look finished while the keyboard is still writing, and fewer than 6 lit lamps means it isn't done. Don't touch the keyboard or the cable.
6. **Restart.** Quit the app, then switch the keyboard off and on.

## Using it

Turn the TYPE knob to **Toy** and play the piano. Check the other five positions too.

## Going back to the original firmware

Enter update mode as above, and flash the **original** updater, again waiting for all 6 lamps. Updating resets your settings to factory defaults.

## If something goes wrong

- **The app looks finished but not all lamps are lit:** wait. The keyboard is still writing.
- **All 6 lamps flash, or the keyboard behaves oddly or won't start:** switch it off, enter update mode, and flash the original updater. This worked after an update was interrupted by powering off early, but that's only one case.
- **Update mode won't start:** try the key combination again, pressing all three keys before switching on. If it still won't start, the keyboard may need service.
- **The patcher crashes with `macOS 13 (1307) or later required, have instead 13 (1306)` (or similar) and `abort`:** you started it with the Python from Apple's developer tools, whose window library was built for a newer macOS than yours. Use the launcher, or the bundled Python as in [Opening it from the command line](#opening-it-from-the-command-line).
- **The launcher says the bundled Python is missing:** the download is incomplete. Download the patcher again.
- **The patched Mac app "is damaged and can't be opened":** its signature doesn't match its contents, which happens if it was changed after the patcher made it. Delete it and make a new one with the patcher, which signs it for you.

## Known limitations

- **Tested on one keyboard, from a Mac.** On that keyboard, the patched firmware was accepted, and Toy plays the hidden piano and sounds the same.
- **Not yet tested on Windows:** the patcher and its launcher, the bundled Windows Python, and the patched Windows updater have not been run on a Windows PC.
- **Bundled Python tested on an Intel Mac only:** the Apple Silicon build hasn't been run yet.
- **Update code not reviewed:** the code that performs updates isn't in the updater, so the file checks below rely on a model of the firmware's own ROM check.

## How it works

The patch changes three bytes of the 4,456,448-byte firmware image:

| Image offset | Purpose | Before | After |
|---|---|---|---|
| `0x1F672B` | Toy bank LSB | `01` | `00` |
| `0x1F672D` | Toy program | `09` | `00` |
| `0x29FFFE` | Code section checksum balance | `dc` | `e6` |

Two update-block checksums in the `.dat` are recalculated too. Because the patcher only accepts one exact original, the change to the `.dat` is always the same five bytes:

| `.dat` offset | Purpose | Before | After |
|---|---|---|---|
| 2355258 | Toy bank LSB | `01` | `00` |
| 2355261 | Toy program | `09` | `00` |
| 2360219 | Update-block checksum | `19` | `23` |
| 3150031 | Checksum balance byte, in the `.dat`'s 7-bit packed form | `5c` | `66` |
| 3163329 | Update-block checksum | `3e` | `34` |

The patcher (`toy_piano_patcher.py`) decodes its own output again before saving and confirms that:

- only the three firmware bytes differ
- every update-block checksum is valid
- both firmware sections pass the model of the ROM check
- the result matches the expected SHA-256, which starts with `5f78926f05a1c4c7`
These checks show the file was built as intended. They can't show that it will work on your keyboard.

## Why there's a `vendor` folder

The `vendor` folder holds three self-contained copies of Python 3.13: for Apple Silicon Macs, Intel Macs and 64-bit Windows. The launchers use them so the patcher works without installing anything. They take about 150 MB unpacked, which is most of this download.

They're included for three reasons:

- **Many computers have no suitable Python.** Windows never includes Python, and recent Macs only have it if Apple's developer tools are installed.
- **Apple's own Python can crash.** The Python from Apple's developer tools uses an old window library (Tk 8.5) that aborts on some macOS versions with `macOS 13 (1307) or later required, have instead 13 (1306)`. The bundled copies have their own Tk 9.0 (Mac) or 8.6 (Windows).
- **The patcher signs the Mac app for you.** A patched Mac app must be re-signed, or macOS calls it damaged. Running on your computer, the patcher does this with `codesign`, which comes with macOS, so you don't need any Terminal steps.

The copies come unmodified from [python-build-standalone](https://github.com/astral-sh/python-build-standalone) (release `20261026`, Python 3.13.18), with unused parts such as pip, IDLE and the C headers left out. [vendor/README.md](vendor/README.md) lists the archives and their SHA-256 hashes, what was left out, and how to update them. Each copy has a `licenses` folder with the licences of Python and the libraries built into it, such as Tcl/Tk and OpenSSL. Those licences cover the bundled Python only; this tool's own MIT licence is in [LICENSE](LICENSE).

The first time you open the Mac launcher, macOS asks you to allow it. The launcher then clears the same download flag from the `vendor` folder, so macOS doesn't ask again about the bundled Python.

## Versioning

The patcher has its own version, a whole number written `v1`, `v2` and so on, like the manufacturer's `v130`. It's shown in the patcher window's title and at the top of this README. Patched copies are named with the manufacturer's updater version followed by the patcher's version, for example `toy_piano_updater_v130-3_v1_mac`.

- `VERSION` holds the current number, such as `1`.
- Each commit increases it by one, through the pre-commit hook in `.githooks/pre-commit`. The hook also writes the number into `toy_piano_patcher.py` and the top of this README, and adds them to the commit. The examples elsewhere in this README stay at `v1`.
- To set the number yourself, edit `VERSION` and include it in the commit. The hook then uses your number as it is.
- After cloning, turn the hook on once with:

    ```bash
    git config core.hooksPath .githooks
    ```

The hook stops the commit if one of those files has changes that aren't staged, so it never commits work you didn't mean to include.

## Licence

The code and documentation in this folder are under the MIT licence: see [LICENSE](LICENSE). That covers this tool only, not the manufacturer's firmware or any patched updater made from it.
