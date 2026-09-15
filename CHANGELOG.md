# Changelog

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
