# -*- coding: utf-8 -*-
"""
Core patch logic for the theHunter:COTW Thai mod installer.
In-place patch of game72 (Thai strings) + game78 (Thai font + logo).
Small backup (~1MB) enables clean uninstall (no need to keep 900MB arcs).
"""
import struct, json, os
from pathlib import Path

SP = 448
POOLREL = 14_111_712
ALIGN = 0x1000
STR_ENTRY = 157        # game72 entry: the StringLookup ADF
FONT_ENTRY = 2529      # game78 entry: font_en.gfx (CFX)
LOGO_ENTRY = 2562      # game78 entry: UI atlas holding the main-menu logo
# Thai non-spacing marks that vanish if they are the LAST char (Scaleform bug)
TRAILMARK = set([0x0E31]) | set(range(0x0E34, 0x0E3B)) | set(range(0x0E47, 0x0E4F))


def _rd(pool, off, n=2000):   # MUST match the n used to build thai_full.json keys
    if off < 0 or off >= len(pool):
        return None
    e = pool.find(b'\x00', off, off + n)
    e = e if e != -1 else min(off + n, len(pool))
    try:
        return pool[off:e].decode('utf-8', 'strict')
    except Exception:
        return None


def _tab_entry(tab, idx):
    o = 0xC + idx * 12
    return struct.unpack_from("<III", tab, o)  # (hash, offset, size)


def _tab_set(tab, idx, offset, size):
    o = 0xC + idx * 12
    struct.pack_into("<I", tab, o + 4, offset)
    struct.pack_into("<I", tab, o + 8, size)


def build_string_entry(entry, trans, keyov, hk):
    """Grow the StringLookup pool with Thai. Returns (new_entry_bytes, blen)."""
    entry = bytearray(entry)
    assert struct.unpack_from("<I", entry, 0)[0] == 0x41444620, "not an ADF entry"
    assert struct.unpack_from("<I", entry, 96 + 0x10)[0] == POOLREL, "unexpected pool layout (game version mismatch?)"
    pool_base = 96 + POOLREL
    pool = bytes(entry[pool_base:])
    pool_used = struct.unpack_from("<I", entry, 96 + 0x18)[0]
    inst_off = struct.unpack_from("<I", entry, 0x0C)[0]
    total = struct.unpack_from("<I", entry, 0x28)[0]
    assert total == len(entry), "entry size mismatch"
    insert_pos = pool_base + pool_used
    assert insert_pos <= inst_off, "insert past metadata"

    blob = bytearray(); newoffs = {}
    for i in range(22049):
        h = struct.unpack_from("<I", entry, SP + i * 8)[0]
        t = struct.unpack_from("<I", entry, SP + i * 8 + 4)[0]
        en = _rd(pool, t) if 0 < t < len(pool) else None
        kn = hk.get("%08X" % h)
        th = None
        if kn and kn in keyov:
            th = keyov[kn]
        elif en:
            th = trans.get(en)
        if th and ord(th[-1]) in TRAILMARK:
            th = th + " "
        if th:
            newoffs[i] = pool_used + len(blob)
            blob.extend(th.encode('utf-8') + b'\x00')
    blen = len(blob)

    new = bytearray(entry[:insert_pos]) + blob + bytearray(entry[insert_pos:])

    def add(off, delta):
        v = struct.unpack_from("<I", new, off)[0]
        struct.pack_into("<I", new, off, v + delta)
    add(96 + 0x18, blen)  # pool_used
    add(0x0C, blen)       # instance_offset
    add(0x14, blen)       # typedef_offset
    add(0x1C, blen)       # stringhash_offset
    add(0x24, blen)       # nametable_offset
    add(0x28, blen)       # total_size
    new_inst_off = struct.unpack_from("<I", new, 0x0C)[0]
    add(new_inst_off + 12, blen)  # instance[0].size
    for i, no in newoffs.items():
        struct.pack_into("<I", new, SP + i * 8 + 4, no)
    return bytes(new), blen


def arcs(game_root):
    a = Path(game_root) / "archives_win64"
    return a / "game72.arc", a / "game72.tab", a / "game78.arc", a / "game78.tab"


def find_game():
    """Best-effort auto-detect of the COTW install (Epic/Steam). Returns path or ''."""
    import re
    cands = []
    pf = [os.environ.get("ProgramFiles", r"C:\Program Files"),
          os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")]
    for p in pf:
        cands.append(Path(p) / "Epic Games" / "theHunterCallOfTheWild")
        cands.append(Path(p) / "Steam" / "steamapps" / "common" / "theHunterCotW")
        vdf = Path(p) / "Steam" / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            try:
                for m in re.findall(r'"path"\s*"([^"]+)"', vdf.read_text(errors='ignore')):
                    cands.append(Path(m.replace('\\\\', '\\')) / "steamapps" / "common" / "theHunterCotW")
            except Exception:
                pass
    for d in "CDEFGH":
        cands.append(Path(f"{d}:/Epic/theHunterCallOfTheWild"))
        cands.append(Path(f"{d}:/Program Files/Epic Games/theHunterCallOfTheWild"))
        cands.append(Path(f"{d}:/SteamLibrary/steamapps/common/theHunterCotW"))
        cands.append(Path(f"{d}:/Games/theHunterCallOfTheWild"))
    for c in cands:
        try:
            if (c / "archives_win64" / "game72.arc").exists():
                return str(c)
        except Exception:
            pass
    return ""


def validate(game_root, moddata):
    """Return dict: valid, message, version_ok, already_installed."""
    root = Path(game_root)
    g72a, g72t, g78a, g78t = arcs(root)
    exe = root / "theHunterCotW_F.exe"
    for f in (g72a, g72t, g78a, g78t):
        if not f.exists():
            return {"valid": False, "message": f"ไม่พบ {f.name} — โฟลเดอร์นี้ไม่ใช่เกม COTW"}
    if not exe.exists():
        return {"valid": False, "message": "ไม่พบ theHunterCotW_F.exe — เลือกโฟลเดอร์หลักของเกม"}
    ref = json.loads((Path(moddata) / "refinfo.json").read_text(encoding='utf-8'))
    bkdir = root / "archives_win64" / "_thaimod_backup"
    already = (bkdir / "manifest.json").exists()
    sz = g72a.stat().st_size
    version_ok = (sz == ref["game72_arc_size"]) or already
    msg = "พบเกม COTW ✓"
    if already:
        msg += "  (ติดตั้งมอดไว้แล้ว — กด INSTALL เพื่ออัปเดต)"
    elif not version_ok:
        msg += f"  ⚠️ เวอร์ชันอาจไม่ตรง (คาด {ref['game72_arc_size']:,} ไบต์, พบ {sz:,}) — ติดตั้งได้แต่เสี่ยง"
    return {"valid": True, "message": msg, "version_ok": version_ok, "already_installed": already}


def _load_mod(moddata):
    md = Path(moddata)
    trans = json.loads((md / "thai_full.json").read_text(encoding='utf-8'))
    if "translations" in trans:
        trans = trans["translations"]
    ov = json.loads((md / "overrides_th.json").read_text(encoding='utf-8')).get("overrides", {})
    trans = dict(trans); trans.update(ov)
    keyov = json.loads((md / "overrides_by_key.json").read_text(encoding='utf-8')).get("overrides", {})
    hk = json.loads((md / "hash_keyname.json").read_text(encoding='utf-8'))
    return trans, keyov, hk


def install(game_root, moddata, progress=lambda p, m: None):
    root = Path(game_root)
    g72a, g72t, g78a, g78t = arcs(root)
    bkdir = root / "archives_win64" / "_thaimod_backup"
    # 1) if already installed, restore first so we build from the clean base
    if (bkdir / "manifest.json").exists():
        progress(2, "คืนค่าเดิมก่อนติดตั้งใหม่...")
        uninstall(game_root, quiet=True)
    bkdir.mkdir(parents=True, exist_ok=True)

    progress(5, "สำรองไฟล์เดิม (backup)...")
    clean72 = g72a.stat().st_size
    clean78 = g78a.stat().st_size
    (bkdir / "game72.tab.bak").write_bytes(g72t.read_bytes())
    (bkdir / "game78.tab.bak").write_bytes(g78t.read_bytes())
    # original logo entry bytes (for restore)
    t78 = g78t.read_bytes()
    _, lo, ls = _tab_entry(t78, LOGO_ENTRY)
    with open(g78a, "rb") as f:
        f.seek(lo); (bkdir / "logo_orig.bin").write_bytes(f.read(ls))
    (bkdir / "manifest.json").write_text(json.dumps(
        {"clean72": clean72, "clean78": clean78, "logo_off": lo, "logo_size": ls}))

    # 2) patch game72 strings
    progress(15, "โหลดข้อมูลคำแปล...")
    trans, keyov, hk = _load_mod(moddata)
    tab72 = bytearray(g72t.read_bytes())
    _, ro, size = _tab_entry(tab72, STR_ENTRY)
    with open(g72a, "rb") as f:
        f.seek(ro); entry = f.read(size)
    progress(30, "สร้างข้อความไทย (2 หมื่นคำ)...")
    new_entry, blen = build_string_entry(entry, trans, keyov, hk)
    new_off = (clean72 + ALIGN - 1) // ALIGN * ALIGN
    progress(55, "เขียนไฟล์ game72 (ข้อความ)...")
    with open(g72a, "r+b") as f:
        f.truncate(clean72)                 # ensure clean base
        f.seek(clean72); f.write(b'\x00' * (new_off - clean72))
        f.write(new_entry)
    _tab_set(tab72, STR_ENTRY, new_off, len(new_entry))
    g72t.write_bytes(tab72)

    # 3) patch game78 font + logo
    progress(75, "ติดตั้งฟอนต์ไทย + โลโก้...")
    tab78 = bytearray(g78t.read_bytes())
    # logo: in-place overwrite (same size)
    logo = (Path(moddata) / "logo_2562.bin").read_bytes()
    _, lo2, ls2 = _tab_entry(tab78, LOGO_ENTRY)
    assert len(logo) == ls2, "logo size mismatch (game version?)"
    # font: append + retarget
    font = (Path(moddata) / "font_en.gfx").read_bytes()
    assert font[:3] == b'CFX', "font not CFX"
    font_off = (clean78 + ALIGN - 1) // ALIGN * ALIGN
    with open(g78a, "r+b") as f:
        f.truncate(clean78)
        f.seek(lo2); f.write(logo)                       # logo overwrite
        f.seek(clean78); f.write(b'\x00' * (font_off - clean78))
        f.write(font)                                    # font append
    _tab_set(tab78, FONT_ENTRY, font_off, len(font))
    g78t.write_bytes(tab78)
    progress(100, "ติดตั้งเสร็จสมบูรณ์! 🇹🇭")
    return True


def uninstall(game_root, quiet=False, progress=lambda p, m: None):
    root = Path(game_root)
    g72a, g72t, g78a, g78t = arcs(root)
    bkdir = root / "archives_win64" / "_thaimod_backup"
    man = bkdir / "manifest.json"
    if not man.exists():
        return False
    m = json.loads(man.read_text())
    if not quiet:
        progress(20, "คืนค่า game72...")
    # game72: truncate + restore tab
    with open(g72a, "r+b") as f:
        f.truncate(m["clean72"])
    g72t.write_bytes((bkdir / "game72.tab.bak").read_bytes())
    if not quiet:
        progress(60, "คืนค่า game78 (ฟอนต์/โลโก้)...")
    # game78: restore logo bytes + truncate font + restore tab
    logo_orig = (bkdir / "logo_orig.bin").read_bytes()
    with open(g78a, "r+b") as f:
        f.seek(m["logo_off"]); f.write(logo_orig)
        f.truncate(m["clean78"])
    g78t.write_bytes((bkdir / "game78.tab.bak").read_bytes())
    # remove backup
    for p in bkdir.glob("*"):
        p.unlink()
    bkdir.rmdir()
    if not quiet:
        progress(100, "ถอนการติดตั้งเรียบร้อย (คืนค่าเดิมแล้ว)")
    return True
