# -*- coding: utf-8 -*-
"""Thai GUI installer for the theHunter:COTW Thai localization mod (Wild Horizon Gaming)."""
import sys, os, threading, traceback
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import patcher_core as pc

# colors / fonts
BG = "#171a1f"; CARD = "#20242b"; ORANGE = "#F5A020"; WHITE = "#f2f2f2"
GREY = "#8b93a0"; GREEN = "#5bd06a"; RED = "#e5564b"; YELLOW = "#e8c14a"
THAI_FONT = "Leelawadee UI"   # Windows Thai UI font (falls back to Tahoma)


def resource(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "moddata", name)


class App:
    def __init__(self, root):
        self.root = root
        self.path = tk.StringVar()
        self.valid = False
        self.moddata = os.path.dirname(resource("refinfo.json"))
        root.title("ตัวติดตั้งมอดภาษาไทย · theHunter: Call of the Wild")
        root.configure(bg=BG)
        root.geometry("560x620"); root.resizable(False, False)
        try:
            root.iconbitmap(default="")  # no icon file; ignore
        except Exception:
            pass

        # ---- banner ----
        self._banner_img = None
        banner = tk.Frame(root, bg=BG); banner.pack(fill="x", pady=(18, 4))
        try:
            from PIL import Image, ImageTk
            im = Image.open(resource("banner.png")).convert("RGBA")
            scale = min(500 / im.width, 150 / im.height)
            im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
            bg = Image.new("RGBA", im.size, (23, 26, 31, 255)); bg.alpha_composite(im)
            self._banner_img = ImageTk.PhotoImage(bg.convert("RGB"))
            tk.Label(banner, image=self._banner_img, bg=BG).pack()
        except Exception:
            tk.Label(banner, text="theHunter™\nเสียงเรียกแห่งพงไพร", fg=WHITE, bg=BG,
                     font=(THAI_FONT, 22, "bold")).pack()

        tk.Label(root, text="มอดแปลภาษาไทย (ฉบับสมบูรณ์)", fg=ORANGE, bg=BG,
                 font=(THAI_FONT, 15, "bold")).pack(pady=(6, 0))
        tk.Label(root, text="โดย Wild Horizon Gaming", fg=GREY, bg=BG,
                 font=(THAI_FONT, 10)).pack()

        # ---- path chooser card ----
        card = tk.Frame(root, bg=CARD, bd=0); card.pack(fill="x", padx=26, pady=(18, 8))
        tk.Label(card, text="1. เลือกโฟลเดอร์ที่ติดตั้งเกม", fg=WHITE, bg=CARD,
                 font=(THAI_FONT, 11, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        row = tk.Frame(card, bg=CARD); row.pack(fill="x", padx=14, pady=(0, 6))
        self.entry = tk.Entry(row, textvariable=self.path, font=(THAI_FONT, 9),
                              bg="#12151a", fg=WHITE, insertbackground=WHITE, bd=0, relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        tk.Button(row, text="เลือก...", command=self.browse, bg="#333a44", fg=WHITE,
                  font=(THAI_FONT, 9, "bold"), bd=0, relief="flat", padx=14, pady=4,
                  activebackground="#3d4550", cursor="hand2").pack(side="right")
        self.status = tk.Label(card, text="ยังไม่ได้เลือกโฟลเดอร์", fg=GREY, bg=CARD,
                               font=(THAI_FONT, 9), anchor="w", justify="left", wraplength=470)
        self.status.pack(anchor="w", padx=14, pady=(0, 12))

        # ---- install card ----
        card2 = tk.Frame(root, bg=CARD); card2.pack(fill="x", padx=26, pady=8)
        tk.Label(card2, text="2. ติดตั้ง", fg=WHITE, bg=CARD,
                 font=(THAI_FONT, 11, "bold")).pack(anchor="w", padx=14, pady=(12, 8))
        self.btn_install = tk.Button(card2, text="ติดตั้งมอด (INSTALL)", command=self.do_install,
                                     bg=ORANGE, fg="#1a1a1a", font=(THAI_FONT, 13, "bold"),
                                     bd=0, relief="flat", pady=10, state="disabled",
                                     activebackground="#ffb733", cursor="hand2")
        self.btn_install.pack(fill="x", padx=14)
        self.btn_uninstall = tk.Button(card2, text="ถอนการติดตั้ง (คืนค่าเดิม)", command=self.do_uninstall,
                                       bg="#333a44", fg=WHITE, font=(THAI_FONT, 10),
                                       bd=0, relief="flat", pady=7, state="disabled",
                                       activebackground="#3d4550", cursor="hand2")
        self.btn_uninstall.pack(fill="x", padx=14, pady=(8, 12))

        # ---- progress ----
        self.pbar_c = tk.Canvas(root, height=8, bg="#12151a", highlightthickness=0)
        self.pbar_c.pack(fill="x", padx=26, pady=(10, 2))
        self.pmsg = tk.Label(root, text="", fg=GREY, bg=BG, font=(THAI_FONT, 9))
        self.pmsg.pack()

        tk.Label(root, text="⚠️ ปิดเกมก่อนติดตั้ง · จะสำรองไฟล์เดิมให้อัตโนมัติ",
                 fg=YELLOW, bg=BG, font=(THAI_FONT, 8)).pack(side="bottom", pady=10)

        # auto-detect
        g = pc.find_game()
        if g:
            self.path.set(g); self.check()

    def _bar(self, pct):
        self.pbar_c.delete("all")
        w = self.pbar_c.winfo_width() or 508
        self.pbar_c.create_rectangle(0, 0, w * pct / 100, 8, fill=ORANGE, outline="")

    def browse(self):
        d = filedialog.askdirectory(title="เลือกโฟลเดอร์หลักของเกม (มี theHunterCotW_F.exe)")
        if d:
            self.path.set(d); self.check()

    def check(self):
        p = self.path.get().strip()
        if not p:
            return
        v = pc.validate(p, self.moddata)
        if v["valid"]:
            self.valid = True
            color = GREEN if v.get("version_ok", True) else YELLOW
            self.status.config(text="✓ " + v["message"], fg=color)
            self.btn_install.config(state="normal")
            self.btn_uninstall.config(state="normal" if v.get("already_installed") else "disabled")
        else:
            self.valid = False
            self.status.config(text="✗ " + v["message"], fg=RED)
            self.btn_install.config(state="disabled")
            self.btn_uninstall.config(state="disabled")

    def _busy(self, on):
        st = "disabled" if on else "normal"
        self.btn_install.config(state=st if not on else "disabled")
        self.btn_uninstall.config(state="disabled" if on else self.btn_uninstall["state"])

    def do_install(self):
        p = self.path.get().strip()
        self._busy(True)
        def prog(pct, msg):
            self.root.after(0, lambda: (self._bar(pct), self.pmsg.config(text=msg, fg=WHITE)))
        def work():
            try:
                pc.install(p, os.path.dirname(resource("refinfo.json")), progress=prog)
                self.root.after(0, self._done_ok)
            except Exception as e:
                tb = traceback.format_exc()
                self.root.after(0, lambda: self._done_err(str(e), tb))
        threading.Thread(target=work, daemon=True).start()

    def _done_ok(self):
        self.pmsg.config(text="ติดตั้งเสร็จสมบูรณ์! เปิดเกมเล่นภาษาไทยได้เลย 🇹🇭", fg=GREEN)
        messagebox.showinfo("สำเร็จ", "ติดตั้งมอดภาษาไทยเรียบร้อย!\n\nเปิดเกมได้เลย — เมนู/บทสนทนาจะเป็นภาษาไทย\n(ถ้าเกมอัปเดต ให้รันตัวติดตั้งนี้อีกครั้ง)")
        self.check()

    def _done_err(self, msg, tb):
        self._bar(0); self.pmsg.config(text="เกิดข้อผิดพลาด", fg=RED)
        messagebox.showerror("ผิดพลาด", f"ติดตั้งไม่สำเร็จ:\n{msg}\n\nไฟล์เดิมยังปลอดภัย (ลองปิดเกมแล้วลองใหม่)")
        self.check()

    def do_uninstall(self):
        if not messagebox.askyesno("ยืนยัน", "ต้องการถอนมอด และคืนค่าเกมเป็นภาษาอังกฤษเดิมใช่ไหม?"):
            return
        p = self.path.get().strip(); self._busy(True)
        def prog(pct, msg):
            self.root.after(0, lambda: (self._bar(pct), self.pmsg.config(text=msg, fg=WHITE)))
        def work():
            try:
                ok = pc.uninstall(p, progress=prog)
                self.root.after(0, lambda: self._uninst_done(ok))
            except Exception as e:
                self.root.after(0, lambda: self._done_err(str(e), ""))
        threading.Thread(target=work, daemon=True).start()

    def _uninst_done(self, ok):
        if ok:
            self.pmsg.config(text="คืนค่าเดิมเรียบร้อย (เกมเป็นภาษาอังกฤษแล้ว)", fg=GREEN)
            messagebox.showinfo("เสร็จ", "ถอนมอดเรียบร้อย คืนค่าเกมเป็นเวอร์ชันเดิมแล้ว")
        self.check()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
