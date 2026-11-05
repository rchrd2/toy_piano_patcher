# Toy piano patcher

Patcher version [v3](#release-notes)

Turn the **Toy** setting into a piano on a certain compact 37-key electric piano. 

A small tool with a simple window. It brings its own Python, so there's nothing to install on a Mac or Windows PC.

This is independent work, not affiliated with or endorsed by the manufacturer. No firmware is included: you supply the manufacturer's own updater.

## What it does

The hidden piano normally needs a fiddly trick: powering on with the TYPE knob balanced between two positions. This tool patches the v1.30 firmware so the Toy position selects bank 0/0, program 0 instead of the Toy sound. It can send the patched firmware straight to your keyboard, or make a patched copy of the updater for you to run. That voice is the hidden piano, so you can reach it at any time just by turning the knob. It also raises the Toy position's volume to full, so the piano isn't quieter than it should be.

Your other five sounds aren't touched, but the Toy sound is replaced until you go back to the original firmware.

## ⚠️ Before you start: use at your own risk

**This is unofficial, experimental software. Flashing modified firmware can permanently damage your instrument or leave it unusable. You alone are responsible for the outcome.** If you can't accept the risk of losing the use of your keyboard, don't use this.

- **It replaces your keyboard's main firmware.** Recovery has worked in one case, but that's evidence, not a guarantee. See [If something goes wrong](#if-something-goes-wrong).
- **There is no warranty.** This software is provided "as is", without warranty of any kind, express or implied, including merchantability, fitness for a particular purpose and non-infringement.
- **The authors accept no liability.** To the fullest extent permitted by law, the authors are not liable for any claim, damage or loss arising from using this software or any firmware it produces, including a damaged instrument, lost settings, or repair costs.
- **Check the manufacturer's licence.** Firmware licences commonly restrict altering or reverse-engineering firmware, and this one may do so. Using modified firmware may also affect your warranty or eligibility for service. Whether to go ahead is your decision and your responsibility.
- **Patched firmware is for your own personal use.** Use it on a keyboard you own, with an updater you obtained yourself. Patched updaters contain the manufacturer's firmware, so don't share them.

## What you need

- The keyboard, with its AC adaptor and a USB cable.
- The manufacturer's original **v1.30** updater, for Mac or Windows. The tool checks the firmware's SHA-256, which must start with `115cd5bbc80ec1d5`. It refuses anything else, including updaters for other keyboards in the same family.
- Nothing to install on a Mac or a Windows PC: Python is included in the `vendor` folder (see [Why there's a `vendor` folder](#why-theres-a-vendor-folder)). On Linux, the launchers aren't included; run the tool with your own Python 3.8 or newer, with Tkinter.
- To patch a Mac updater, a Mac, so the copy can be re-signed with `codesign`. It comes with macOS.

## Use the patcher

1. **Open the patcher.** Double-click the launcher for your system. The first time, your system asks you to allow it, because it was downloaded from the internet and isn't signed by a registered developer:
    - **Mac:** `mac_open_patcher.command`. If macOS says it can't be opened, open **System Settings → Privacy & Security**, scroll down, click **Open Anyway** next to the launcher's name, and confirm. On macOS 14 and earlier you can instead Control-click the launcher and choose **Open**. You only need to do this once.
    - **Windows:** `win_open_patcher.bat`. If SmartScreen warns you, choose **More info**, then **Run anyway**.
2. **Choose the original.** Under **Original updater**, click **Choose...** and select the updater app (Mac), the updater's `.exe` (Windows), or the `.zip` you downloaded it in. You can also paste the path to the updater's folder or its `.dat` into the box. It is only read, never changed.
3. **Accept the risk.** Tick the box.
4. **Choose how to update** under **How to update**. Both options apply the same patch and run the same checks first.
    - **Update the keyboard directly from this app:** the patcher sends the patched firmware to the keyboard over USB MIDI itself. Nothing to re-sign or run, and no Rosetta needed on Apple Silicon Macs. See [Option 1](#option-1-update-the-keyboard-directly).
    - **Create a patched updater to run yourself:** the patcher makes a patched, re-signed copy of the manufacturer's updater, and you flash with that. See [Option 2](#option-2-create-a-patched-updater).

Before either option, do a test run: flash the **original** updater once, following the manufacturer's guide. If that fails, stop here.

### Option 1: Update the keyboard directly

1. **Prepare.** Connect the keyboard with USB, use its AC adaptor, and stop your computer from sleeping. Close other programs that use MIDI.
2. **Enter update mode.** Switch the keyboard off, hold **F#3, A3 and C#4** together, and switch it on. The **Rd I** lamp lights.
3. **Choose the port.** Under **MIDI port**, choose the keyboard. It's selected for you when its name contains "reface". Click **Refresh** if you connected it after opening the patcher.
4. **Send.** Click **Send to keyboard** and confirm. Sending takes about 2.5 minutes, and the progress bar shows how far it has got. Don't unplug anything or close the patcher.
5. **Wait until ALL 6 TYPE lamps are lit, however long it takes.** The patcher can look finished while the keyboard is still writing. Then switch the keyboard off and on.

If sending stops part-way, switch the keyboard off, enter update mode again, and send again, or flash the original updater.

### Option 2: Create a patched updater

1. **Choose where to save it.** Under **Save location**, choose a folder, or create one in the picker. The tool creates a new folder inside it.
2. **Create it.** Click **Create patched copy**. Progress appears in the log, and it takes a few seconds.
3. **Find it.** Click **Show patched file** to see the result in Finder or File Explorer. On a Mac, the patched app is already re-signed, so it opens normally.
4. **Flash it** as described in [Flash the patched updater](#flash-the-patched-updater).

#### What you get

| Your original | Folder created | Contains |
|---|---|---|
| Mac updater, or its `.zip` | `toy_piano_updater_v130-3_v3_mac` | `toy piano updater v130-3_v3.app`, renamed and signed locally |
| Windows updater, or its `.zip` | `toy_piano_updater_v130-3_v3_win` | A copy of the updater folder with the patched `.dat` |
| A `.dat` path pasted into the box | `toy_piano_updater_v130-3_v3_dat` | Only the patched `.dat` |

`v130-3` is the manufacturer's updater version, and `v3` is the patcher's own version, which goes up with each release (see [Release notes](#release-notes)). That way you can tell which patcher made a copy.

The tool only reads your original. It won't overwrite an existing output, and it won't save inside the original updater.

If a write fails partway, the tool leaves a folder ending in `.tmp` and tells you where it is. Don't use it. Delete it yourself before trying again.

### Opening the patcher from the command line

If the launcher won't run, or you want to see any error messages, start the patcher from a terminal with the bundled Python. It opens the same window and takes no options.

1. Open **Terminal** on a Mac, or **Command Prompt** on Windows.
2. Go to the patcher's folder, for example:

    ```bash
    cd ~/Downloads/toy_piano_patcher
    ```

3. Start it:
    - **Apple Silicon Mac:** `vendor/python-mac-arm64/bin/python3.13 toy_piano_patcher.py`
    - **Intel Mac:** `vendor/python-mac-x86_64/bin/python3.13 toy_piano_patcher.py`
    - **Windows:** `vendor\python-win\python.exe toy_piano_patcher.py`
    - **Linux, or your own Python:** `python3 toy_piano_patcher.py`

Then carry on from step 2 above. Any errors appear in the terminal, and closing the window returns you to the prompt.

## Flash the patched updater

For [Option 2](#option-2-create-a-patched-updater). Follow the manufacturer's updater guide alongside these steps, and keep the original updater.

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
- **The patcher crashes with `macOS 13 (1307) or later required, have instead 13 (1306)` (or similar) and `abort`:** you started it with the Python from Apple's developer tools, whose window library was built for a newer macOS than yours. Use the launcher, or the bundled Python as in [Opening the patcher from the command line](#opening-the-patcher-from-the-command-line).
- **The keyboard isn't listed under MIDI port, or it can't be opened:** check the USB cable, make sure the keyboard is on, and click **Refresh**. On Windows, close other programs that use MIDI first, because only one program can use a port at a time. macOS's IAC buses can't be used.
- **The launcher says the bundled Python is missing:** the download is incomplete. Download the patcher again.
- **The patched Mac app "is damaged and can't be opened":** its signature doesn't match its contents, which happens if it was changed after the patcher made it. Delete it and make a new one with the patcher, which signs it for you.

## Known limitations

- **Security prompts on Mac and Windows:** the launchers and the bundled Python aren't signed by a registered developer, so macOS and Windows may block them or warn that they can't be verified. Allowing them once usually works: see step 1 of [Use the patcher](#use-the-patcher). If the patcher still doesn't open, run it from the terminal as in [Opening it from the command line](#opening-the-patcher-from-the-command-line), or try [facelift](https://github.com/dgoeke/facelift), a web-based alternative by dgoeke that flashes the keyboard from Chrome or Edge.

## How it works

The patch changes four bytes of the 4,456,448-byte firmware image:

| Image offset | Purpose | Before | After |
|---|---|---|---|
| `0x1F672B` | Toy bank LSB | `01` | `00` |
| `0x1F672D` | Toy program | `09` | `00` |
| `0x1F672F` | Toy level: 74, set for the Toy sound, raised to the maximum, 127 | `4a` | `7f` |
| `0x29FFFE` | Code section checksum balance | `dc` | `b1` |

The first three are in the Toy position's sound record. Each of the six sounds has its own level there: Rd I 75, Rd II 110, Wr 120, Clv 95, Toy 74 and CP 100. Keeping Toy's 74 left the piano about 9.4 dB quieter.

Two update-block checksums in the `.dat` are recalculated too. Because the patcher only accepts one exact original, the change to the `.dat` is always the same six bytes:

| `.dat` offset | Purpose | Before | After |
|---|---|---|---|
| 2355258 | Toy bank LSB | `01` | `00` |
| 2355261 | Toy program | `09` | `00` |
| 2355263 | Toy level | `4a` | `7f` |
| 2360219 | Update-block checksum | `19` | `6e` |
| 3150031 | Checksum balance byte, in the `.dat`'s 7-bit packed form | `5c` | `31` |
| 3163329 | Update-block checksum | `3e` | `69` |

The patcher (`toy_piano_patcher.py`) decodes its own output again before saving and confirms that:

- only the four firmware bytes differ
- every update-block checksum is valid
- both firmware sections pass the model of the ROM check
- the result matches the expected SHA-256, which starts with `d11b28e6fe510add`
These checks show the file was built as intended. They can't show that it will work on your keyboard.

## Why there's a `vendor` folder

The `vendor` folder holds three self-contained copies of Python 3.13: for Apple Silicon Macs, Intel Macs and 64-bit Windows. The launchers use them so the patcher works without installing anything. They take about 150 MB unpacked, which is most of this download.

They're included for three reasons:

- **Many computers have no suitable Python.** Windows never includes Python, and recent Macs only have it if Apple's developer tools are installed.
- **Apple's own Python can crash.** The Python from Apple's developer tools uses an old window library (Tk 8.5) that aborts on some macOS versions with `macOS 13 (1307) or later required, have instead 13 (1306)`. The bundled copies have their own Tk 9.0 (Mac) or 8.6 (Windows).
- **The patcher signs the Mac app for you.** A patched Mac app must be re-signed, or macOS calls it damaged. Running on your computer, the patcher does this with `codesign`, which comes with macOS, so you don't need any Terminal steps.

The copies come unmodified from [python-build-standalone](https://github.com/astral-sh/python-build-standalone) (release `20261026`, Python 3.13.18), with unused parts such as pip, IDLE and the C headers left out. [vendor/README.md](vendor/README.md) lists the archives and their SHA-256 hashes, what was left out, and how to update them. Each copy has a `licenses` folder with the licences of Python and the libraries built into it, such as Tcl/Tk and OpenSSL. Those licences cover the bundled Python only; this tool's own MIT licence is in [LICENSE](LICENSE).

The first time you open the Mac launcher, macOS asks you to allow it. The launcher then clears the same download flag from the `vendor` folder, so macOS doesn't ask again about the bundled Python.

## Release notes

- **v3:** You can now update the keyboard directly from the patcher: choose its MIDI port and click **Send to keyboard**. There's nothing to re-sign or run, and no Rosetta needed on Apple Silicon Macs. Creating a patched updater is still available as the other option.
- **v2:** The piano now plays at full volume. The patch kept the Toy position's own level, 74, which suits the Toy sound but left the piano about 9.4 dB quieter. It's now 127, the maximum. This fix comes from [facelift](https://github.com/dgoeke/facelift) by dgoeke, a web-based updater built on this patcher. The version number is now raised by hand at each release, instead of on every commit.
- **v1:** Python is included for Mac and Windows, so there's nothing to install. **Choose...** selects the updater app, its `.exe`, the `.zip` it was downloaded in, or the `.dat`. The patched Mac app's download quarantine flag is cleared, so it opens without an extra warning. Patched copies are named with the patcher version.
- **First release (no number):** Toy plays the hidden piano.

## Licence

The code and documentation in this folder are under the MIT licence: see [LICENSE](LICENSE). That covers this tool only, not the manufacturer's firmware or any patched updater made from it.
