# Changelog

## v1.2 — 2026-10-30

**Compatibility:** COTW game update of 30 Oct 2026 (Epic build `3366163` / archives `3364269`). The archive layout is unchanged from v0.14 (StringLookup game72 #495, font game78 #3697, logo game78 #3722), so v1.1 still installs; v1.2 adds translations.

### Added
- **13 Old West Weapon Pack texts** promised in v1.1 (shop info panel): the descriptions of the Hween .45-90 Buffalo, Maijo .44-40 Special, Humphrey 10GA coach gun, Flavus 6x/10x scopes, the 10GA birdshot / buckshot / slug loads, the .44-40 and .45-90 ammo, plus the pack's store description.
- **4 strings that showed English after recent patches** (reworded or reformatted by the developers): the Game Feeder tutorial page, the mineral lick station (with its full species list, using the in-game Thai animal names), the trophy plaque size message, and the "Animal Whisperer" mission briefing.
- **Dominguez–Escalante lore text** (Silver Ridge Peaks) that stayed English since v1.0. It is the first string in the game's text pool (offset 0), which the by-text matching skips, so it is now set by its key `lore_rockies_08_description`.

Total: 21,794 strings in Thai. Only an internal "???" name and one placeholder the game itself shows untranslated stay as they are.

### Fixed
- **String table size is read from the game file** (22,079 entries in game v0.14) instead of a hard-coded 22,082. The 3 extra "slots" were the start of another data array in the same file. v1.1 never wrote there, but a new translation could match one of them, and a pre-release v1.2 build (never published for download) did change one value there.
- **Safer handling of game updates**: the installer only restores its backup when the game files are exactly the ones it modded. After a game update or Verify Files it discards the old backup instead of restoring it, so it can no longer truncate updated archives, and the uninstall button stays off in that state.

### Upgrade guide
- From v1.1: run the v1.2 installer and click INSTALL.
- After a game update: Verify Files in your store, then run the installer again. If it shows a yellow version warning, wait for a mod update.

---

## v1.1 — 2026-09-15

**Compatibility:** COTW game version 0.14 (Old West Weapon Pack patch, build `3331010` / archives `3322479`)

### Fixed
- **Support for game v0.14** — game archive structure changed in this patch:
  - `StringLookup` moved from `game72` entry 157 → **495**
  - Font entry moved from `game78` entry 2529 → **3697**
  - Logo atlas moved from `game78` entry 2562 → **3722**
  - Updated `POOLREL` constant + string slot count (22049 → 22082) for the new pool layout
- **Stale-backup safety fix** — installer now detects when the game was updated after a prior mod install and skips the destructive uninstall step (which would truncate the new archives). Previously, running v1.0's installer over a game-updated install would damage `game72.arc` / `game78.arc`.

### Added
- **17 new translations** for Old West Weapon Pack items:
  - Weapon names: ปืนโค้ชกัน ฮัมฟรีย์ 10GA · ปืนไรเฟิลควาย ฮวีน .45-90 · ปืนพก ไมโจ .44-40 สเปเชียล
  - Scopes: กล้องเล็งไรเฟิล ฟลาวุส 6×17 / 10×17
  - Ammo: 10GA / .44-40 / .45-90 variants (Birdshot / Buckshot / Slug / FMJ / Soft Lead / Flat Nose / Cowboy Load)
  - Fabled fur names: Eclipse · Saffronglow · Cirrus · Stormcloak · Starthistle

### Known limitation
- 14 long Old West Weapon Pack item descriptions (in-shop info panel) are still English in v1.1. These will be added in v1.1.1 within a few days.

### Upgrade guide
- Users on v1.0: **before updating the game**, uninstall v1.0 first. If you already updated the game with v1.0 still installed, run Epic Games / Steam **Verify** to restore clean archives before installing v1.1.
- Users installing fresh: just run the installer as usual.

---

## v1.0 — 2026-08-04
- Initial release — 22,047 Thai strings covering menus, HUD, missions, dialogue, codex.
