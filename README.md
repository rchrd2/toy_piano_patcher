# Toy piano patcher

Turn the **Toy** setting into a piano on a certain compact 37-key electric piano. A small Python tool with a simple window.

This is for the keyboard from a well-known Japanese instrument maker with a six-position **TYPE** knob and a rumoured hidden piano sound. If you own one, you'll recognise it.

This is independent work, not affiliated with or endorsed by the manufacturer. No firmware is included: you supply the manufacturer's own updater.

## What it does

The hidden piano normally needs a fiddly trick: powering on with the TYPE knob balanced between two positions. This tool makes a patched copy of the v1.30 updater in which the Toy position selects bank 0/0, program 0 instead of the Toy sound. That voice is the hidden piano, so you can reach it at any time just by turning the knob.

Your other five sounds aren't touched, but the Toy sound is replaced until you go back to the original firmware.

## ⚠️ Before you start: use at your own risk

**This is unofficial, experimental software. Flashing modified firmware can permanently damage your instrument or leave it unusable. You alone are responsible for the outcome.** If you can't accept the risk of losing the use of your keyboard, don't use this.

- **It replaces your keyboard's main firmware.** Recovery has worked in one case, but that's evidence, not a guarantee. See [If something goes wrong](#if-something-goes-wrong).
- **Testing has been limited.** It has been flashed and confirmed working on one keyboard, from a Mac. That doesn't guarantee it will work on yours. See [Known limitations](#known-limitations).
- **It has not been tested on Windows.** The tool, its launcher and the patched Windows updater have never been run on a Windows PC, so Windows users would be the first to try them.
- **There is no warranty.** This software is provided "as is", without warranty of any kind, express or implied, including merchantability, fitness for a particular purpose and non-infringement.
- **The authors accept no liability.** To the fullest extent permitted by law, the authors are not liable for any claim, damage or loss arising from using this software or any firmware it produces, including a damaged instrument, lost settings, or repair costs.
- **Check the manufacturer's licence.** Firmware licences commonly restrict altering or reverse-engineering firmware, and this one may do so. Using modified firmware may also affect your warranty or eligibility for service. Whether to go ahead is your decision and your responsibility.
- **Patched firmware is for your own personal use.** Use it on a keyboard you own, with an updater you obtained yourself. Patched updaters contain the manufacturer's firmware, so don't share them.

## What you need

- The keyboard, with its AC adaptor and a USB cable.
- The manufacturer's original **v1.30** updater, for Mac or Windows. The tool checks the firmware's SHA-256, which must start with `115cd5bbc80ec1d5`. It refuses anything else, including updaters for other keyboards in the same family.
- Python 3.8 or newer, with nothing else to install. The window needs Tkinter, which some Python installs leave out. If yours does, install Python from [python.org](https://www.python.org/downloads/), which includes it.
- To patch a Mac updater, a Mac, so the copy can be re-signed. On another system, the tool warns you and shows the command to run later.

## Make the patched updater

1. **Open the patcher.** Double-click the launcher for your system:
    - **Mac:** `mac_open_patcher.command`. If macOS blocks it, Control-click it and choose **Open**, or allow it in **System Settings → Privacy & Security**.
    - **Windows (untested):** `win_open_patcher.bat`. If SmartScreen warns you, choose **More info**, then **Run anyway**.
2. **Choose the original.** Under **Original updater**, click **Choose...** and select the folder containing the updater. You can also paste the path to the `.app`, `.exe` or `.dat` into the box.
3. **Choose where to save it.** Under **Save location**, choose a folder, or create one in the picker. The tool creates a new folder inside it.
4. **Create it.** Tick the risk box and click **Create patched copy**. Progress appears in the log, and it takes a few seconds.
5. **Find it.** Click **Show patched file** to see the result in Finder or File Explorer.

### Opening it from the command line

If the launcher won't run, or you want to see any error messages, start the patcher from a terminal instead. It opens the same window and takes no options.

1. Open **Terminal** on a Mac, or **Command Prompt** on Windows.
2. Go to the folder containing `toy_piano_patcher.py`, for example:

    ```bash
    cd ~/Downloads/toy_piano_patcher
    ```

3. Start it:
    - **Mac or Linux:** `python3 toy_piano_patcher.py`
    - **Windows (untested):** `py -3 toy_piano_patcher.py`, or `python toy_piano_patcher.py` if `py` isn't found.

Then carry on from step 2 above. Any errors appear in the terminal, and closing the window returns you to the prompt.

### What you get

| Your original | Folder created | Contains |
|---|---|---|
| Mac updater | `toy_piano_updater_v130-3p_mac` | `toy piano updater v130-3p.app`, renamed and signed locally |
| Windows updater | `toy_piano_updater_v130-3p_win` | A copy of the updater folder with the patched `.dat` |
| A `.dat` path pasted into the box | `toy_piano_updater_v130-3p_dat` | Only the patched `.dat` |

The tool only reads your original. It won't overwrite an existing output, and it won't save inside the original updater.

If a write fails partway, the tool leaves a folder ending in `.tmp` and tells you where it is. Don't use it. Delete it yourself before trying again.

If macOS won't open the new app, clear the quarantine flag on that app only. In Terminal, go to the new `toy_piano_updater_v130-3p_mac` folder and run:

```bash
xattr -dr com.apple.quarantine "toy piano updater v130-3p.app"
```

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

## Known limitations

- **Tested on one keyboard, from a Mac.** On that keyboard, the patched firmware was accepted, and Toy plays the hidden piano and sounds the same.
- **Not yet tested on Windows:** the launcher, the tool, and the patched Windows updater have not been run on a Windows PC.
- **Update code not reviewed:** the code that performs updates isn't in the updater, so the file checks below rely on a model of the firmware's own ROM check.

## How it works

The patch changes three bytes of the 4,456,448-byte firmware image:

| Image offset | Purpose | Before | After |
|---|---|---|---|
| `0x1F672B` | Toy bank LSB | `01` | `00` |
| `0x1F672D` | Toy program | `09` | `00` |
| `0x29FFFE` | Code section checksum balance | `dc` | `e6` |

Two update-block checksums in the `.dat` are recalculated too. Before saving, the tool decodes its own output again and confirms that:

- only these three bytes differ
- every update-block checksum is valid
- both firmware sections pass the model of the ROM check
- the result matches the expected SHA-256

These checks show the file was built as intended. They can't show that it will work on your keyboard.

## Licence

The code and documentation in this folder are under the MIT licence: see [LICENSE](LICENSE). That covers this tool only, not the manufacturer's firmware or any patched updater made from it.
