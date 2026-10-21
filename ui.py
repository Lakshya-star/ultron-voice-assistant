"""Ultron interface — sci-fi FUI/HUD style (Tkinter, no extra deps).

A dark tactical dashboard: segmented rotating scan rings with tick marks
around a 3D point-cloud core, corner brackets, radial gauges, segmented
level bars, monospaced all-caps readouts and a comms log. When Ultron
wakes, the accents shift from cyan to green like an active scan.
Geometry helpers come from viz.py.
"""
import math
import random
import time
import tkinter as tk
from tkinter import scrolledtext

import viz

BG = "#02060f"         # near-black navy
PANEL = "#04101f"      # module background
EDGE = "#123a63"       # thin module borders
CYAN = "#27d5ff"       # primary accent
CYAN_DIM = "#0e6f9e"
BRIGHT = "#aef4ff"     # hot highlight
GREEN = "#00ff9d"      # active-scan accent
TEXT = "#c8e6f5"
DIM = "#4a7095"

FONT = "Menlo"         # mac default mono (Tk substitutes if missing)


# ------------------------------------------------------------------ point cloud
def _fibonacci_sphere(n):
    """n points evenly spread on a unit sphere."""
    pts, golden = [], math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - 2 * i / (n - 1)
        r = math.sqrt(max(0.0, 1 - y * y))
        a = golden * i
        pts.append((math.cos(a) * r, y, math.sin(a) * r))
    return pts


def _neighbor_pairs(pts, max_dist):
    """Indices of sphere points close enough to link with a line."""
    pairs = []
    for i in range(len(pts)):
        x1, y1, z1 = pts[i]
        for j in range(i + 1, len(pts)):
            x2, y2, z2 = pts[j]
            if (x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2 < max_dist ** 2:
                pairs.append((i, j))
    return pairs


def _project(p, angle, tilt):
    """Rotate a unit-sphere point, then perspective-project it -> (x, y, z)."""
    x, y, z = viz.rot_y(p, angle)
    x, y, z = viz.rot_x((x, y, z), tilt)
    f = 2.6 / (2.6 - z)
    return x * f, y * f, z


class UltronUI:
    def __init__(self, cfg, on_text_submit, on_mic_press):
        self.cfg = cfg
        self.on_text_submit = on_text_submit
        self.on_mic_press = on_mic_press
        self.pending_confirm = None  # kept for API compatibility with main.py

        # --- all state must exist before _build() draws anything ---
        self._phase = 0.0
        self._awake = False
        self._pulses = []
        self._last_pulse = -1
        self._t0 = time.time()
        self._sphere = _fibonacci_sphere(80)
        self._links = _neighbor_pairs(self._sphere, 0.55)
        self._gauge_vals = {"core": 0.72, "net": 0.55}
        self._bars = {"pwr": 0.86, "sig": 0.42, "aud": 0.10}

        self.root = tk.Tk()
        self.root.title(cfg.get("assistant_name", "Ultron"))
        self.root.configure(bg=BG)
        self.root.geometry("950x700")
        self.root.minsize(900, 640)
        try:
            self.root.attributes("-topmost", True)
            self.root.after(2000, lambda: self.root.attributes("-topmost", False))
        except Exception:
            pass

        self._build()
        self._animate()
        self._tick()

    # ------------------------------------------------------------------ widgets
    def _panel(self, parent, title):
        """A bordered FUI module: thin edge frame, header, inner body."""
        outer = tk.Frame(parent, bg=EDGE, bd=0)
        inner = tk.Frame(outer, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(inner, text=f"■ {title}", bg=PANEL, fg=CYAN,
                 font=(FONT, 9, "bold"), anchor="w").pack(fill="x", padx=10, pady=(8, 2))
        return outer, inner

    def _row(self, parent, label, value=""):
        """A label/value readout line; returns the value Label for updates."""
        f = tk.Frame(parent, bg=PANEL)
        f.pack(fill="x", padx=10, pady=1)
        tk.Label(f, text=label, bg=PANEL, fg=DIM, font=(FONT, 9), width=7,
                 anchor="w").pack(side="left")
        lab = tk.Label(f, text=value, bg=PANEL, fg=CYAN, font=(FONT, 10, "bold"),
                        anchor="w")
        lab.pack(side="left")
        return lab

    def _build(self):
        # ---------- top bar ----------
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(top, text="U L T R O N", fg=CYAN, bg=BG,
                 font=(FONT, 24, "bold")).pack(side="left")
        self._clock = tk.Label(top, text="--:--:--", fg=TEXT, bg=BG, font=(FONT, 12))
        self._clock.pack(side="right")
        self._uptime = tk.Label(top, text="T+00:00", fg=DIM, bg=BG, font=(FONT, 10))
        self._uptime.pack(side="right", padx=(0, 14))
        self._topstat = tk.Label(top, text="SYS.STATUS [ ONLINE ]", fg=GREEN, bg=BG,
                                 font=(FONT, 10, "bold"))
        self._topstat.pack(side="right", padx=(0, 14))
        tk.Frame(self.root, bg=EDGE, height=1).pack(fill="x", padx=14)

        # ---------- main 3-column grid ----------
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=8)
        body.grid_columnconfigure(1, weight=1)

        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        center = tk.Frame(body, bg=BG)
        center.grid(row=0, column=1)
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=2, sticky="ns", padx=(8, 0))

        # ----- left column: CORE / DIAG / LEVELS modules
        p, inner = self._panel(left, "CORE")
        p.pack(fill="x")
        wake = self.cfg.get("wake_words", ["hey ultron"])[0].upper()
        self._row(inner, "MODEL", self.cfg.get("ollama_model", "llama3.2"))
        self._row(inner, "MODE", "VOICE / TEXT")
        self._row(inner, "WAKE", wake)
        self._state_lab = self._row(inner, "STATE", "BOOT")
        self._row(inner, "BRN", "LOCAL")
        tk.Frame(inner, bg=PANEL).pack(pady=(0, 8))

        p, inner = self._panel(left, "DIAG")
        p.pack(fill="x", pady=(8, 0))
        self.gauges = tk.Canvas(inner, width=206, height=118, bg=PANEL,
                               highlightthickness=0)
        self.gauges.pack(padx=8, pady=(2, 8))

        p, inner = self._panel(left, "LEVELS")
        p.pack(fill="x", pady=(8, 0))
        self.bars = tk.Canvas(inner, width=206, height=128, bg=PANEL,
                              highlightthickness=0)
        self.bars.pack(padx=8, pady=(2, 8))

        # ----- center: the big scan
        self.canvas = tk.Canvas(center, width=440, height=440, bg=BG,
                                highlightthickness=0)
        self.canvas.pack()

        # ----- right column: comms log
        p, inner = self._panel(right, "COMMS LOG")
        p.pack(fill="both", expand=True)
        self.chat = scrolledtext.ScrolledText(
            inner, bg=PANEL, fg=TEXT, font=(FONT, 10), insertbackground=CYAN,
            relief="flat", wrap="word", state="disabled", bd=0,
            padx=12, pady=10, height=16, width=30, highlightthickness=0)
        self.chat.pack(fill="both", expand=True, padx=8, pady=(2, 8))
        self.chat.tag_config("you", foreground=CYAN, font=(FONT, 10, "bold"))
        self.chat.tag_config("ultron", foreground="#9fd1ff")
        self.chat.tag_config("sys", foreground=DIM, font=(FONT, 9, "italic"))

        # ---------- bottom: command input ----------
        tk.Frame(self.root, bg=EDGE, height=1).pack(fill="x", padx=14)
        bot = tk.Frame(self.root, bg=BG)
        bot.pack(fill="x", padx=14, pady=(8, 2))
        tk.Label(bot, text="CMD >", fg=CYAN, bg=BG,
                 font=(FONT, 10, "bold")).pack(side="left")

        entry_frame = tk.Frame(bot, bg=EDGE)
        entry_frame.pack(side="left", fill="x", expand=True, padx=(8, 10))
        self.entry = tk.Entry(entry_frame, bg=PANEL, fg=TEXT, insertbackground=CYAN,
                              font=(FONT, 11), relief="flat", bd=0,
                              highlightthickness=0)
        self.entry.pack(fill="x", ipady=8, padx=2, pady=2)
        self.entry.insert(0, "TYPE COMMAND + ENTER")
        self.entry.bind("<FocusIn>", lambda e: self._clear_placeholder())
        self.entry.bind("<Return>", lambda e: self._submit())

        self.mic_btn = tk.Button(bot, text="◉ MIC", command=self._mic_clicked,
                                 bg="#06304a", fg=CYAN, font=(FONT, 11, "bold"),
                                 relief="flat", padx=18, pady=9,
                                 activebackground="#0a4a6a", activeforeground=BRIGHT)
        self.mic_btn.pack(side="right", padx=(10, 0))
        self.mic_btn.bind("<Enter>", lambda e: self.mic_btn.config(fg=BRIGHT))
        self.mic_btn.bind("<Leave>", lambda e: self.mic_btn.config(fg=CYAN))

        hint = tk.Label(self.root,
                        text=f"SAY '{self.cfg.get('wake_words', ['hey ultron'])[0]}' — OR TYPE A COMMAND",
                        fg=DIM, bg=BG, font=(FONT, 9))
        hint.pack(pady=(2, 10))

    # ------------------------------------------------------------------ center scene
    def _draw_scene(self):
        c = self.canvas
        c.delete("all")
        cx = cy = 220
        awake = self._awake
        ring = GREEN if awake else CYAN
        dim = "#0d5c3f" if awake else "#0a2748"

        # scanlines + crosshair
        for y in range(0, 440, 5):
            c.create_line(0, y, 440, y, fill="#04101f")
        c.create_line(cx, 6, cx, 434, fill="#07203d")
        c.create_line(6, cy, 434, cy, fill="#07203d")

        # corner brackets
        for (bx, by, dx, dy) in ((10, 10, 1, 1), (430, 10, -1, 1),
                                (10, 430, 1, -1), (430, 430, -1, -1)):
            c.create_line(bx, by, bx + 26 * dx, by, fill=CYAN_DIM, width=2)
            c.create_line(bx, by, bx, by + 26 * dy, fill=CYAN_DIM, width=2)

        # outer tick ring
        for deg in range(0, 360, 5):
            rad = math.radians(deg)
            big = deg % 30 == 0
            r1 = 196
            r2 = 196 + (13 if big else 7)
            col = CYAN_DIM if big else "#0a2c4f"
            c.create_line(cx + r1 * math.sin(rad), cy - r1 * math.cos(rad),
                          cx + r2 * math.sin(rad), cy - r2 * math.cos(rad),
                          fill=col, width=1)

        # segmented rotating arcs (glow pass + bright pass)
        for k in range(4):
            st = math.degrees(self._phase * 18) + k * 90
            c.create_arc(cx - 184, cy - 184, cx + 184, cy + 184, start=st,
                         extent=55, style="arc", outline=dim, width=6)
            c.create_arc(cx - 184, cy - 184, cx + 184, cy + 184, start=st,
                         extent=55, style="arc", outline=ring, width=2)

        # dashed ring, counter-rotating
        c.create_arc(cx - 168, cy - 168, cx + 168, cy + 168,
                     start=math.degrees(-self._phase * 8), extent=359.5,
                     style="arc", outline=CYAN_DIM, width=1, dash=(3, 12))

        # fixed thin ring + block segment ring
        c.create_oval(cx - 152, cy - 152, cx + 152, cy + 152, outline="#0a2748")
        step = int(self._phase * 6)
        for i in range(32):
            rad = math.radians(i * 11.25)
            lit = (i + step) % 8 == 0
            r1, r2 = 124, 132
            c.create_line(cx + r1 * math.sin(rad), cy - r1 * math.cos(rad),
                          cx + r2 * math.sin(rad), cy - r2 * math.cos(rad),
                          fill=ring if lit else "#0a2c4f", width=6)

        # rotating 3D point-cloud core
        tilt = math.radians(18) + math.sin(self._phase * 0.3) * 0.2
        proj = [_project(p, self._phase * 0.5, tilt) for p in self._sphere]
        for i, j in self._links:
            x1, y1, z1 = proj[i]
            x2, y2, z2 = proj[j]
            t = ((z1 + z2) / 2 + 1) / 2
            col = viz.lerp_color("#08304f", ring, t * t)
            c.create_line(cx + x1 * 82, cy + y1 * 82, cx + x2 * 82, cy + y2 * 82,
                          fill=col, width=1)
        for x, y, z in proj:
            t = (z + 1) / 2
            s = 1 + 1.8 * t
            c.create_oval(cx + x * 82 - s, cy + y * 82 - s,
                          cx + x * 82 + s, cy + y * 82 + s,
                          fill=viz.lerp_color("#0d3b5e", BRIGHT, t * t), outline="")

        # expanding scan pulses while awake
        if awake:
            tick = int(self._phase * 2)
            if tick != self._last_pulse:
                self._last_pulse = tick
                self._pulses.append((36, 1.0))
        alive = []
        for radius, alpha in self._pulses:
            radius += 3.5
            alpha -= 0.02
            if alpha > 0:
                alive.append((radius, alpha))
                c.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                              outline=viz.lerp_color("#031126", ring, alpha),
                              width=max(1, int(3 * alpha)))
        self._pulses = alive

        # core disc + letter
        c.create_oval(cx - 30, cy - 30, cx + 30, cy + 30, fill="#06233d",
                      outline=ring, width=2)
        c.create_text(cx, cy + 1, text="U", fill=BRIGHT, font=(FONT, 22, "bold"))

        # readouts
        c.create_text(20, 18, anchor="nw",
                      text=f"SCAN [ {'ACTIVE' if awake else 'IDLE'} ]",
                      font=(FONT, 9), fill=ring)
        c.create_text(420, 18, anchor="ne", text="CORE NOMINAL",
                      font=(FONT, 9), fill=GREEN)
        az = (math.degrees(self._phase * 20)) % 360
        c.create_text(420, 422, anchor="se", text=f"AZ {az:06.1f}°",
                      font=(FONT, 9), fill=CYAN_DIM)
        c.create_text(20, 422, anchor="sw",
                      text=f"LINKS {len(self._links)}  NODES {len(self._sphere)}",
                      font=(FONT, 9), fill=CYAN_DIM)

    def _draw_gauges(self):
        g = self.gauges
        g.delete("all")
        for idx, (key, label) in enumerate((("core", "CORE"), ("net", "NET"))):
            cx, cy, r = 58 + idx * 106, 58, 34
            g.create_arc(cx - r, cy - r, cx + r, cy + r, start=150, extent=240,
                         style="arc", outline="#0a2748", width=5)
            v = self._gauge_vals[key]
            g.create_arc(cx - r, cy - r, cx + r, cy + r, start=150,
                         extent=240 * v, style="arc", outline=CYAN, width=5)
            rad = math.radians(150 + 240 * v)
            g.create_line(cx, cy, cx + (r - 9) * math.cos(rad),
                          cy - (r - 9) * math.sin(rad), fill=BRIGHT, width=2)
            g.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=CYAN, outline="")
            g.create_text(cx, cy + r + 13, text=label, font=(FONT, 8), fill=DIM)
            g.create_text(cx, cy + 13, text=f"{int(v * 100)}",
                          font=(FONT, 10, "bold"), fill=CYAN)

    def _draw_bars(self):
        b = self.bars
        b.delete("all")
        for row, (key, label) in enumerate((("pwr", "PWR"), ("sig", "SIG"),
                                            ("aud", "AUD"))):
            y = 24 + row * 36
            b.create_text(4, y - 8, anchor="w", text=label,
                          font=(FONT, 9), fill=DIM)
            n, lit = 18, int(self._bars[key] * 18)
            for i in range(n):
                x = 4 + i * 11
                if i < lit:
                    col = GREEN if (key == "aud" and self._awake) else CYAN
                else:
                    col = "#0a2748"
                b.create_rectangle(x, y, x + 7, y + 13, fill=col, outline="")

    def _animate(self):
        self._phase += 0.022
        try:
            self._draw_scene()
        except Exception:
            pass  # never let a drawing hiccup kill the animation loop
        self.root.after(33, self._animate)

    def _tick(self):
        for k in self._gauge_vals:
            self._gauge_vals[k] = min(0.97, max(0.30,
                self._gauge_vals[k] + random.uniform(-0.04, 0.04)))
        self._bars["pwr"] = 0.82 + 0.10 * math.sin(time.time() * 0.5)
        self._bars["sig"] = min(1.0, max(0.15,
            self._bars["sig"] + random.uniform(-0.07, 0.07)))
        self._bars["aud"] = random.uniform(0.55, 0.95) if self._awake \
            else random.uniform(0.03, 0.18)
        try:
            self._draw_gauges()
            self._draw_bars()
        except Exception:
            pass
        self._clock.config(text=time.strftime("%H:%M:%S"))
        up = int(time.time() - self._t0)
        self._uptime.config(text=f"T+{up // 60:02d}:{up % 60:02d}")
        self.root.after(150, self._tick)

    # ------------------------------------------------------------------ public API
    def set_awake(self, awake):
        self._awake = awake
        if awake:
            self.pop_to_front()
            self._pulses.append((36, 1.0))

    def pop_to_front(self):
        """Bring the Ultron window forward, like Siri popping up."""
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after(2500, lambda: self.root.attributes("-topmost", False))
        except Exception:
            pass

    def set_status(self, text):
        def _s():
            short = (text[:22] + "…") if len(text) > 23 else text
            try:
                self._state_lab.config(text=short.upper())
            except Exception:
                pass
        self._run_in_main(_s)

    def show(self, who, text):
        """who in {'you','ultron','sys'} — thread-safe transcript append."""
        labels = {"you": "YOU    >> ",
                  "ultron": f"{self.cfg.get('assistant_name', 'Ultron')[:5].upper()} >> ",
                  "sys": "SYS    >> "}
        def _a():
            self.chat.configure(state="normal")
            self.chat.insert("end", labels.get(who, "") + text + "\n\n", who)
            self.chat.see("end")
            self.chat.configure(state="disabled")
        self._run_in_main(_a)

    def _run_in_main(self, fn):
        try:
            self.root.after(0, fn)
        except RuntimeError:
            pass

    # ------------------------------------------------------------------ input handlers
    def _clear_placeholder(self):
        if self.entry.get() == "TYPE COMMAND + ENTER":
            self.entry.delete(0, "end")

    def _submit(self):
        text = self.entry.get().strip()
        if not text or text == "TYPE COMMAND + ENTER":
            return
        self.entry.delete(0, "end")
        self.on_text_submit(text)

    def _mic_clicked(self):
        self.on_mic_press()

    # ------------------------------------------------------------------ main loop
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.mainloop()
