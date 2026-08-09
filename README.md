# theHunter: Call of the Wild — Thai Language Mod (Installer Source)

Source code for the Thai localization mod installer by **Wild Horizon Gaming**
([Nexus Mods #1027](https://www.nexusmods.com/thehuntercallofthewild/mods/1027)).

## What it does
This is a small **offline game-file patcher**. When run, it:

1. Reads the game's own local archive files (`game72`, `game78`) inside the
   theHunter: Call of the Wild installation folder.
2. Injects the **Thai translation strings**, a **Thai font**, and a **translated
   logo** directly into those files (in-place binary patch).
3. Saves a small (~1 MB) backup so the mod can be **cleanly uninstalled**.

## What it does NOT do
- ❌ No network connections of any kind
- ❌ No registry changes
- ❌ No writes outside the game's own folder
- ❌ No background processes, no persistence

## Why the .exe gets flagged (false positive)
The distributable `.exe` is built with **PyInstaller**, which bundles a Python
interpreter into a standalone executable. This is a very common trigger for
heuristic antivirus / site-security false positives. The complete source is in
this repository — nothing is hidden.

## Repository contents

**Source code (this is the code the .exe runs):**
- `patcher_core.py` — the patch logic: reads the game archives, injects the Thai
  strings/font/logo, writes them back, and creates the uninstall backup.
- `patcher_gui.py` — the installer's graphical interface (buttons, folder picker,
  progress). Calls into `patcher_core.py`.

**Mod data that gets injected (no code, just assets/text):**
- `moddata/thai_full.json` — the full Thai translation (key → Thai text)
- `moddata/overrides_th.json`, `moddata/overrides_by_key.json` — manual translation fixes
- `moddata/hash_keyname.json`, `moddata/refinfo.json` — key/offset lookup tables
- `moddata/font_en.gfx` — the Thai font (Scaleform) injected into the UI
- `moddata/logo_2562.bin`, `moddata/banner.png` — the translated main-menu logo/banner

**Docs & assets:**
- `README.md` (this file), `README_TH.txt` — user instructions
- `NEXUS_PAGE.txt` — the Nexus mod page text
- `SHA256.txt` — checksum of the released .exe
- `icon/` — the app icon (.ico/.svg/.png)

> Not included here: the built `.exe`, the PyInstaller build folder, and the
> release `.zip` — those are just the compiled output of the code above and are
> already available on the Nexus mod page.

## Build
```
pip install pyinstaller
pyinstaller patcher_gui.py
```

— Wild Horizon Gaming 🇹🇭
