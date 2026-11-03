# Bundled Python

These folders hold self-contained Python builds, so the double-click launchers work without installing anything. See [Why there's a `vendor` folder](../README.md#why-theres-a-vendor-folder) in the main README for the reasons.

| Folder | Used on | Started by |
|---|---|---|
| `python-mac-arm64` | Apple Silicon Macs | `mac_open_patcher.command` |
| `python-mac-x86_64` | Intel Macs | `mac_open_patcher.command` |
| `python-win` | Windows (64-bit) | `win_open_patcher.bat` |

## Source

[python-build-standalone](https://github.com/astral-sh/python-build-standalone), release `20261026`, CPython 3.13.18. The files are unmodified apart from the parts listed under [Removed](#removed).

| Folder | Archive | SHA-256 |
|---|---|---|
| `python-mac-arm64` | `cpython-3.13.18+20261026-aarch64-apple-darwin-install_only.tar.gz` | `e5af2fde6a937a0e0c795a0c595c4efb70578d57463a2657c819992b9b9acbac` |
| `python-mac-x86_64` | `cpython-3.13.18+20261026-x86_64-apple-darwin-install_only.tar.gz` | `708be9e7df297f68bdae589ea9e62a621db5abe7708f79e851c41410347452d1` |
| `python-win` | `cpython-3.13.18+20261026-x86_64-pc-windows-msvc-install_only_stripped.tar.gz` | `7369f7a35f261222a6ac8b3a87c1c88eeebee8af945d85346202591a64038dd3` |

These hashes match the release's own `SHA256SUMS` file.

## Licences

Each folder has a `licenses` folder with the licences of Python and the libraries built into it, including Tcl/Tk, OpenSSL, libffi, SQLite, zlib, bzip2, xz, mpdecimal and ncurses. These were taken from the matching "full" archive of the same release (`...-pgo+lto-full.tar.zst` on Mac, `...-pgo-full.tar.zst` on Windows), because the smaller archives above don't include them. Python's own licence is also at `lib/python3.13/LICENSE.txt` (Mac) and `LICENSE.txt` (Windows). These licences cover the bundled Python only; the patcher itself is under the MIT licence in `../LICENSE`.

## Removed

To save space, parts the patcher never uses were left out when copying from the archives:

- Every build: `include/`, `__pycache__/` folders, `idlelib/`, `ensurepip/`, `pydoc_data/`, `turtledemo/`, and pip in `site-packages/`.
- Mac: `share/`, `lib/pkgconfig/`, and the `idle`, `pip`, `pydoc` and `*-config` programs in `bin/`.
- Windows: `libs/`, `Scripts/`, the `_test*` modules in `DLLs/`, and the Tcl build files (`tcl/nmake/`, `tcl/*.lib`, `tcl/tix*`).

Unpacked, the three folders take about 54, 54 and 42 MB.

## Updating

1. Download the three archives above for a newer release, and check them against that release's `SHA256SUMS`.
2. Unpack each one, and copy its `python` folder here with the same parts left out, for example with `rsync -a --exclude=...`.
3. Copy `python/licenses/` from the matching full archive into each folder.
4. Update the release, version and hashes in this file and in the main README. If the Python version changes, update the `python3.13` path in `mac_open_patcher.command`.
5. Check that the window opens: `vendor/python-mac-x86_64/bin/python3.13 -c "import tkinter; tkinter.Tk().destroy()"` (or the `arm64` folder on Apple Silicon).
