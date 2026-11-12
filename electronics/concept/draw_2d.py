"""2D drawings for the HAEBOT Hand Controller v2 concept.

  ../renders/layout_top.png              to-scale top view, every part with ref + name
  ../renders/wiring_back_colorcoded.png  BOTTOM view (mirrored), colour-coded nets, every part ref + name + purpose
  ../renders/power_tree_v2.png           power tree with amps / watts per branch (numbers from power_budget.csv)

Run with the repo venv:  /workspace/venv/bin/python draw_2d.py
"""
import os, sys, csv, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Patch
from matplotlib.lines import Line2D
sys.path.insert(0, os.path.dirname(__file__))
from layout import *

HERE = os.path.dirname(os.path.abspath(__file__))
ELEC = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ELEC, "renders")
plt.rcParams["font.family"] = "DejaVu Sans"
PCB = "#0f1a14"

# ------------------------------------------------------------------ label list (clusters merged)
MERGE = {"C3": ("C3-C6", "22 µF 25 V x4", "U3 input MLCCs (TI min. 88 µF)"),
         "C8": ("C8-C13", "47 µF 10 V x6", "U3 output MLCCs (TI min. 134 µF eff.)"),
         "C17": ("C17,C18", "22 µF 25 V x2", "U4 input MLCCs"),
         "C20": ("C20-C23", "22 µF 25 V x4", "U4 output MLCCs")}
def label_items():
    out, groups = [], {}
    for p in P:
        r = p["ref"]
        if not p["label"]:
            key = next(k for k in MERGE if (r[0] == "C" and (
                (k == "C3" and 3 <= int(r[1:]) <= 6) or (k == "C8" and 8 <= int(r[1:]) <= 13) or
                (k == "C17" and 17 <= int(r[1:]) <= 18) or (k == "C20" and 20 <= int(r[1:]) <= 23))))
            groups.setdefault(key, []).append(p); continue
        out.append(dict(ref=r, name=p["name"], purpose=p["purpose"], x=p["x"] + p["w"] / 2, y=p["y"] + p["h"] / 2, net=p["net"]))
    for k, ps in groups.items():
        x = np.mean([q["x"] + q["w"] / 2 for q in ps]); y = np.mean([q["y"] + q["h"] / 2 for q in ps])
        ref, nm, pu = MERGE[k]
        out.append(dict(ref=ref, name=nm, purpose=pu, x=x, y=y, net=ps[0]["net"]))
    for hn, (hx, hy) in HOLES:
        pass
    out.append(dict(ref="H1-H6", name="M2.5 holes", purpose="H1-H4 Pi 5 pattern (18 mm standoffs), H5/H6 open-zone support",
                    x=PI_HOLES[0][0], y=PI_HOLES[0][1], net="OTHER"))
    return out

def short_tag(it):
    r = it["ref"]
    if len(r) <= 7 and "," not in r:
        return r
    return r.replace(",", " ").split()[0].split("-")[0] + "…"

def draw_parts(ax, X, ghost=False):
    for p in P:
        x0 = X(p["x"] + p["w"]) if X(0) > X(1) else X(p["x"])
        style = dict(fc="none", ec="#e9ecef", lw=1.0, ls=(0, (3, 2)), zorder=6) if ghost else \
                dict(fc=p["color"], ec=NET[p["net"]], lw=1.4, ls="-", zorder=3)
        if p["kind"] == "cyl":
            ax.add_patch(Circle((X(p["x"] + p["w"] / 2), p["y"] + p["h"] / 2), p["w"] / 2, **style))
        else:
            ax.add_patch(Rectangle((x0, p["y"]), p["w"], p["h"], **style))
    for hn, (hx, hy) in HOLES:
        ax.add_patch(Circle((X(hx), hy), 2.6, fc="#c9a227", ec="none", zorder=5))
        ax.add_patch(Circle((X(hx), hy), 1.35, fc="white", ec="none", zorder=5.1))

def draw_tags(ax, items, X):
    """ref tags on the board; pushed apart so they never overlap, with a leader when moved."""
    pts = np.array([[X(it["x"]), it["y"]] for it in items], float)
    tags = [short_tag(it) for it in items]
    wh = np.array([[0.62 * len(t) + 0.9, 1.75] for t in tags])
    pos = pts.copy()
    for _ in range(600):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                d = pos[j] - pos[i]
                ox = (wh[i, 0] + wh[j, 0]) / 2 + 0.15 - abs(d[0]); oy = (wh[i, 1] + wh[j, 1]) / 2 + 0.15 - abs(d[1])
                if ox > 0 and oy > 0:
                    moved = True
                    if oy < ox:
                        s = 1 if d[1] >= 0 else -1; pos[i, 1] -= s * oy / 2; pos[j, 1] += s * oy / 2
                    else:
                        s = 1 if d[0] >= 0 else -1; pos[i, 0] -= s * ox / 2; pos[j, 0] += s * ox / 2
        pos[:, 0] = np.clip(pos[:, 0], 1.0, BOARD_L - 1.0); pos[:, 1] = np.clip(pos[:, 1], 1.0, BOARD_W - 1.0)
        if not moved: break
    for it, t, (x, y), (px, py) in zip(items, tags, pos, pts):
        if abs(x - px) + abs(y - py) > 0.6:
            ax.plot([px, x], [py, y], color="white", lw=0.7, zorder=11)
            ax.plot([px], [py], "o", ms=2.2, color="white", zorder=11)
        ax.text(x, y, t, ha="center", va="center", fontsize=7.6, weight="bold", color="black", zorder=12,
                bbox=dict(boxstyle="round,pad=0.18", fc=NET[it["net"]], ec="white", lw=0.7))

def board(ax, X, title_zone=True):
    ax.add_patch(FancyBboxPatch((0, 0), BOARD_L, BOARD_W, boxstyle="round,pad=0,rounding_size=2.5", fc=PCB, ec="#000", lw=1.5, zorder=1))
    ax.plot([X(PI_X0), X(PI_X0)], [0, BOARD_W], color="#7ee0a1", lw=1.0, ls=(0, (2, 2)), zorder=1.8)
    if title_zone:
        ax.text((X(0) + X(PI_X0)) / 2, BOARD_W + 1.2, "OPEN ZONE", ha="center", va="bottom", fontsize=10, color="#1a7f37", weight="bold")
        ax.text((X(PI_X0) + X(BOARD_L)) / 2, BOARD_W + 1.2, "UNDER THE Pi 5  (parts ≤ 12 mm tall)", ha="center", va="bottom", fontsize=10, color="#1a7f37", weight="bold")

def part_table(ax, items, title):
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.text(0.0, 1.0, title, ha="left", va="top", fontsize=12, weight="bold", color="#1f2328")
    n = len(items); step = 0.965 / max(n, 1)
    for k, it in enumerate(items):
        y = 0.955 - k * step
        ax.text(0.0, y, short_tag(it), ha="left", va="top", fontsize=9, weight="bold", color="black",
                bbox=dict(boxstyle="round,pad=0.2", fc=NET[it["net"]], ec="#495057", lw=0.6))
        ax.text(0.115, y, f"{it['ref']}  —  {it['name']}", ha="left", va="top", fontsize=9.6, weight="bold", color="#1f2328")
        ax.text(0.115, y - step * 0.45, it["purpose"], ha="left", va="top", fontsize=9.0, color="#495057")

def sheet(path, mirror, title, subtitle, footer, nets=False):
    X = (lambda x: BOARD_L - x) if mirror else (lambda x: x)
    fig = plt.figure(figsize=(34, 19), dpi=100)
    fig.text(0.5, 0.982, title, ha="center", va="top", fontsize=24, weight="bold", color="#1f2328")
    fig.text(0.5, 0.950, subtitle, ha="center", va="top", fontsize=12, color="#57606a")
    fig.text(0.995, 0.004, footer, ha="right", va="bottom", fontsize=9, color="#6e7781")
    ax = fig.add_axes([0.255, 0.255, 0.49, 0.665]); ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-4, BOARD_L + 4); ax.set_ylim(-12, BOARD_W + 14)
    board(ax, X)
    if nets:
        ax.add_patch(FancyBboxPatch((0.8, 0.8), BOARD_L - 1.6, BOARD_W - 1.6, boxstyle="round,pad=0,rounding_size=2",
                                    fc="#16331f", ec="#2f9e44", hatch="////", lw=0.0, zorder=1.5))
        draw_nets(ax, X)
        draw_parts(ax, X, ghost=True)
    else:
        for gx in np.arange(0, BOARD_L + 1, 10):
            ax.text(X(gx), -1.6, f"{gx:.0f}", ha="center", va="top", fontsize=8, color="#57606a")
            ax.plot([X(gx), X(gx)], [-0.8, 0], color="#57606a", lw=0.8)
        for gy in np.arange(0, BOARD_W + 1, 10):
            ax.text(-1.6, gy, f"{gy:.0f}", ha="right", va="center", fontsize=8, color="#57606a")
            ax.plot([-0.8, 0], [gy, gy], color="#57606a", lw=0.8)
        draw_parts(ax, X)
        ax.add_patch(FancyBboxPatch((PI_X0, 0), PI_L, PI_W, boxstyle="round,pad=0,rounding_size=3",
                                    fc="none", ec="#da77f2", lw=1.8, ls="--", zorder=8))
        ax.text(PI_X0 + PI_L / 2, -4.5, "dashed purple = Raspberry Pi 5 outline (85 × 56 mm), 18 mm above the board", ha="center", fontsize=9.5, color="#9c36b5")
        ax.text(BOARD_L / 2, -8.5, "x [mm] →   origin = bottom-left corner (top view)", ha="center", fontsize=9, color="#57606a")
    j = part("J2")
    for i, nm in enumerate(SERVO_CH):
        xx = X(j["x"]) - 0.6 if not mirror else X(j["x"]) + 0.6
        ax.text(xx, j["y"] + 1.27 + i * 2.54, f"CH{i} {nm}", ha="right" if not mirror else "left", va="center", fontsize=6.5, color="white", zorder=7)
    items = label_items()
    draw_tags(ax, items, X)
    mid = X(BOARD_L / 2)
    left = sorted([it for it in items if X(it["x"]) < mid], key=lambda t: (-round(t["y"] / 4), X(t["x"])))
    right = sorted([it for it in items if X(it["x"]) >= mid], key=lambda t: (-round(t["y"] / 4), X(t["x"])))
    part_table(fig.add_axes([0.008, 0.03, 0.24, 0.9]), left, "LEFT half of this view (tag · ref · name / purpose)")
    part_table(fig.add_axes([0.755, 0.03, 0.24, 0.9]), right, "RIGHT half of this view (tag · ref · name / purpose)")
    return fig, ax, X

# ------------------------------------------------------------------ top layout
def layout_png(path):
    fig, ax, X = sheet(path, False, "HAEBOT Hand Controller v2 — to-scale TOP view (concept placement, real package sizes)",
        "115 × 56 mm, 4-layer (preliminary) · outline colour = main net · small 0603 passives serving one IC are one box (tag ends with …) · every tag is explained in the side tables",
        "Jinie EduTech · HAEBOT Hand i2 V1 · not a routed PCB — validate fit in KiCad before JLCPCB")
    lax = fig.add_axes([0.255, 0.03, 0.49, 0.19]); lax.axis("off")
    hs = [Patch(fc="white", ec=NET[n], lw=2.5, label=t) for n, t in [("12V", "12 V input / bus"), ("6V", "6 V servo rail"), ("5V1", "5.1 V Pi rail / 5 V MCU"),
          ("3V3", "3.3 V logic"), ("I2C", "I²C"), ("UART", "UART"), ("STEP", "stepper"), ("USB", "USB"), ("OTHER", "other / passives")]]
    lax.legend(handles=hs, loc="upper center", ncol=5, fontsize=11, title="Outline / tag colour = the net the part mainly belongs to", title_fontsize=12)
    lax.text(0.5, 0.22, "Heights: J1 XT60 8.3 mm · F1 blade ~16.5 mm · J2 servo pins 8.5 mm (+ plugs) — all in the OPEN ZONE.\nUnder the Pi: C1/C2/C14/C15 470 µF 10.5 mm · "
             "C7/C47 hybrid 10.2 mm · J5 Micro-Fit 9.9 mm · J7 8.5 mm · U3 module ~5 mm · L1 4.7 mm (all ≤ 12 mm).",
             ha="center", va="center", fontsize=11, color="#495057")
    fig.savefig(path, dpi=100, facecolor="white"); plt.close(fig)
    print("wrote", path)

# ------------------------------------------------------------------ nets (top-view coordinates, flattened over all layers)
# (net, width_pt, points, text, dashed)
J2V = 21.0 + 1.27 + 2.54; J2S = 21.0 + 1.27; J2G = 21.0 + 1.27 + 5.08
J5P = [64.0 + 3.0 + 3.0 * k for k in range(7)]  # pin x positions 1..7
NETS = [
    ("12V", 9, [(5.3, 10.9), (15.45, 10.9), (15.45, 1.8), (64.5, 1.8)], "12 V in · 11.2 A worst / 3.7 A typ", False),
    ("12V", 5, [(24.5, 1.8), (24.5, 26.7)], "bulk C1 C2 + TVS D1", False),
    ("12V", 3, [(35.75, 1.8), (35.75, 12.15)], "", False),
    ("12V", 7, [(42.45, 1.8), (42.45, 21.0), (45.0, 21.0)], "U3 in 7.8 A", False),
    ("12V", 3.5, [(64.5, 1.8), (64.5, 14.0), (71.5, 14.5)], "U4 in 2.3 A", False),
    ("12V", 2.2, [(64.5, 14.0), (64.5, 44.0), (57.6, 44.0), (57.6, 41.8)], "", False),
    ("12V", 2.2, [(57.6, 41.8), (49.0, 41.8)], "", False),
    ("12V", 1.5, [(64.5, 35.65), (65.15, 35.65)], "", False),
    ("12V", 0.8, [(64.5, 22.0), (72.0, 22.5)], "", True),
    ("6V", 10, [(50.5, 23.0), (50.5, 23.6), (36.0, 23.6), (36.0, 33.5), (J2V, 35.0), (J2V, 52.8)], "6 V servo bus · 15 A worst / 4.2 A typ", False),
    ("6V", 5, [(56.0, 15.0), (61.0, 15.0)], "", False),
    ("6V", 0.8, [(56.0, 22.5), (73.5, 22.5)], "", True),
    ("5V1", 6, [(73.0, 14.5), (75.0, 14.1), (85.5, 14.1), (92.5, 14.1)], "5.1 V · 5.2 A worst", False),
    ("5V1", 6, [(92.5, 14.1), (92.5, 44.0), (J5P[0], 44.0), (J5P[0], 45.8)], "to Pi 5.2 A", False),
    ("5V1", 6, [(J5P[1], 44.0), (J5P[1], 45.8)], "", False),
    ("5V1", 1.2, [(92.5, 12.0), (95.0, 12.0)], "", False),
    ("5V1", 1.0, [(92.5, 31.4), (96.0, 31.4)], "", False),
    ("5V_MCU", 1.4, [(97.7, 11.0), (99.5, 11.0), (99.5, 15.0), (92.0, 15.6), (91.0, 28.0), (81.0, 30.5)], "5 V MCU (diode-OR)", True),
    ("5V_MCU", 1.0, [(99.5, 15.0), (99.5, 17.0)], "", True),
    ("5V_MCU", 1.0, [(91.0, 28.0), (91.0, 43.0), (79.5, 43.0), (79.5, 42.8)], "", True),
    ("5V_MCU", 1.0, [(91.0, 43.0), (101.2, 46.2)], "", True),
    ("5V_MCU", 0.9, [(79.5, 43.0), (54.0, 45.0), (52.5, 42.0)], "", True),
    ("3V3", 1.3, [(97.45, 32.8), (97.45, 34.0), (60.0, 34.0), (55.0, 31.4)], "3.3 V · 42 mA", False),
    ("3V3", 1.0, [(73.5, 34.0), (73.5, 40.0)], "", False),
    ("3V3", 1.0, [(60.0, 34.0), (55.0, 36.0)], "", False),
    ("I2C", 1.3, [(72.0, 29.0), (68.0, 29.0), (58.5, 28.0), (52.7, 28.0)], "I²C 5 V pull-ups", False),
    ("I2C", 1.3, [(81.0, 33.0), (94.0, 42.0), (101.2, 46.2)], "", False),
    ("UART", 1.3, [(J5P[5], 45.8), (J5P[5], 43.6), (77.45, 42.8)], "", False),
    ("UART", 1.3, [(J5P[6], 45.8), (J5P[6], 44.6), (73.45, 44.6), (73.45, 42.8)], "Pi UART", False),
    ("UART", 1.3, [(74.9, 41.4), (88.0, 41.6), (104.0, 27.0), (106.4, 25.8)], "", False),
    ("UART", 1.3, [(100.0, 22.0), (106.4, 25.0)], "", False),
    ("UART", 1.3, [(106.4, 26.6), (81.0, 32.5)], "", False),
    ("USB", 1.6, [(107.65, 9.5), (100.0, 9.5), (97.7, 10.0)], "USB VBUS", False),
    ("USB", 1.3, [(107.65, 8.0), (104.75, 8.0), (100.0, 19.0)], "USB D+/D−", False),
    ("STEP", 1.3, [(72.0, 27.0), (62.0, 42.8), (49.0, 39.5)], "STEP/DIR/EN", False),
    ("STEP", 3.0, [(46.5, 42.0), (46.5, 44.0), (44.2, 46.2)], "coils 1.0 A RMS", False),
    ("OTHER", 1.0, [(47.85, 31.4), (47.85, 32.5)], "", False),
    ("OTHER", 1.3, [(43.0, 33.5), (42.0, 44.5), (J2S, 44.5)], "PWM x8", False),
    ("OTHER", 1.0, [(J2S, 35.0), (J2S, 52.8)], "", False),
    ("OTHER", 1.0, [(3.6, 23.0), (19.4, 23.0), (19.4, 6.5), (28.9, 6.5)], "SW1 -> Q1 gate", False),
    ("OTHER", 0.8, [(51.0, 6.2), (51.0, 6.6), (66.0, 6.6), (72.0, 21.5)], "PGOOD", True),
    ("OTHER", 0.8, [(56.95, 46.2), (68.0, 36.0), (72.0, 33.0)], "LIMIT", True),
    ("OTHER", 0.8, [(3.6, 38.0), (6.5, 38.0), (6.5, 49.3), (3.6, 49.3)], "", True),
]

def draw_nets(ax, X):
    for net, w, pts, txt, dashed in NETS:
        xs = [X(px) for px, _ in pts]; ys = [py for _, py in pts]
        ax.plot(xs, ys, color=NET[net], lw=w * 1.25, solid_capstyle="round", solid_joinstyle="round",
                ls=(0, (2.5, 1.5)) if dashed else "-", zorder=4 + (0.5 if w > 4 else 0.8), alpha=0.95)
    caps = [("12V", (8.0, 20.2), "12 V IN 11.2 A max"), ("12V", (40.0, -1.4), "12 V bus → U3 7.8 A · U4 2.3 A · TMC 1 A"),
            ("6V", (34.0, 26.0), "6 V SERVO BUS 15 A worst"), ("5V1", (84.0, 17.0), "5.1 V 5.2 A"),
            ("5V1", (95.5, 38.0), "→ Pi via J5"), ("3V3", (87.0, 33.0), "3.3 V 42 mA"), ("I2C", (62.0, 26.6), "I²C"),
            ("UART", (98.0, 36.5), "UART"), ("STEP", (56.0, 37.0), "STEP/DIR/EN"), ("USB", (104.0, 13.0), "USB"),
            ("OTHER", (34.0, 45.6), "PWM ×8 → J2 S")]
    for net, (x, y), t in caps:
        ax.text(X(x), y, t, ha="center", va="center", fontsize=8.5, weight="bold", color="black", zorder=9,
                bbox=dict(boxstyle="round,pad=0.2", fc=NET[net], ec="white", lw=0.6, alpha=0.95))

def wiring_png(path):
    fig, ax, X = sheet(path, True, "HAEBOT Hand Controller v2 — colour-coded wiring, BOTTOM VIEW (what goes where)",
        "All 4 copper layers flattened into one picture for understanding (L1 top · L2 solid GND · L3 power planes · L4 bottom). Routes are schematic, not final traces. "
        "Line width ∝ current; currents = worst case from power_budget.md.",
        "Jinie EduTech · HAEBOT Hand i2 V1 · controller v2 concept · not a routed PCB", nets=True)
    ax.text(X(BOARD_L / 2), BOARD_W + 8.0, "BOTTOM VIEW — board flipped left ↔ right (mirrored): XT60, fuse and servo headers are on the RIGHT here",
            ha="center", va="center", fontsize=14, weight="bold", color="#c92a2a",
            bbox=dict(boxstyle="round,pad=0.4", fc="#fff5f5", ec="#c92a2a", lw=1.8), zorder=10)
    ax.annotate("", xy=(X(0), -4.5), xytext=(X(BOARD_L), -4.5), arrowprops=dict(arrowstyle="<->", color="#495057", lw=1.0))
    ax.text(X(BOARD_L / 2), -6.3, "115 mm · seen from below: top-view x = 0 (XT60 end) is the RIGHT edge here", ha="center", va="top", fontsize=10, color="#495057")
    lax = fig.add_axes([0.255, 0.01, 0.49, 0.225]); lax.axis("off")
    hs = [Line2D([0], [0], color=NET["12V"], lw=7, label="12 V input / bus (red)"),
          Line2D([0], [0], color=NET["6V"], lw=7, label="6 V servo rail (orange)"),
          Line2D([0], [0], color=NET["5V1"], lw=6, label="5.1 V Pi rail (yellow)"),
          Line2D([0], [0], color=NET["5V_MCU"], lw=2, ls=(0, (2.5, 1.5)), label="5 V MCU after diode-OR (yellow dashed)"),
          Line2D([0], [0], color=NET["3V3"], lw=3, label="3.3 V logic (gold)"),
          Patch(fc="#16331f", ec="#2f9e44", hatch="////", label="GND: solid plane L2 + fills (green hatched)"),
          Line2D([0], [0], color=NET["I2C"], lw=2.5, label="I²C SDA/SCL (blue)"),
          Line2D([0], [0], color=NET["UART"], lw=2.5, label="UART Pi / USB / MCU (purple)"),
          Line2D([0], [0], color=NET["STEP"], lw=3, label="stepper STEP/DIR/EN + coils (cyan)"),
          Line2D([0], [0], color=NET["USB"], lw=2.5, label="USB D+/D− and VBUS (magenta)"),
          Line2D([0], [0], color=NET["OTHER"], lw=2.5, label="other: PWM, PGOOD, switch, sense (grey)"),
          Line2D([0], [0], color="#adb5bd", lw=1.2, ls=(0, (3, 2)), label="dashed outline = part on the TOP side, seen through")]
    lax.legend(handles=hs, loc="upper center", ncol=3, fontsize=11.5, title="NET COLOURS  ·  line width ∝ current", title_fontsize=13, frameon=True)
    fig.savefig(path, dpi=100, facecolor="white"); plt.close(fig)
    print("wrote", path)

# ------------------------------------------------------------------ power tree
def load_budget():
    rows = list(csv.DictReader(open(os.path.join(ELEC, "power_budget.csv"))))
    g = lambda ref: next(r for r in rows if r["ref"] == ref)
    return g

def power_png(path):
    g = load_budget()
    u3, u4, tot, u9 = g("U3"), g("U4"), g("J1"), g("U9")
    fig, ax = plt.subplots(figsize=(22, 13.5), dpi=110)
    ax.set_xlim(0, 22); ax.set_ylim(0, 13.5); ax.axis("off")
    def box(x, y, w, h, title, lines, fc, ec, tc="#1f2328"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=fc, ec=ec, lw=2))
        ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top", fontsize=12, weight="bold", color=tc)
        for i, l in enumerate(lines):
            ax.text(x + 0.18, y + h - 0.78 - i * 0.36, l, ha="left", va="top", fontsize=9.6, color=tc)
    def arrow(p0, p1, col, lw=3, txt=None, off=(0.12, 0)):
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=18))
        if txt:
            ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], txt, fontsize=9.4, color=col, weight="bold", va="center")
    R, O, Y, Gd, Cy, Gr = NET["12V"], NET["6V"], "#c9a000", NET["3V3"], NET["STEP"], "#495057"
    box(0.3, 10.9, 4.0, 2.2, "AC 230 V", ["IEC inlet + switch", "fuse 4 A T (slow)", f"≈ 53 W typ / 158 W worst"], "#f1f3f5", Gr)
    box(5.0, 10.9, 5.0, 2.2, "Mean Well LRS-350-12", ["12 V 29 A 348 W, ~85 %", "load: 39 % worst (44 % clone peak)", "OLP 110-140 % hiccup, OVP 13.8-16.2 V"], "#ffe3e3", R)
    box(10.7, 10.9, 5.6, 2.2, "J1 XT60 → F1 20 A → Q1 → D1 TVS", ["reverse polarity + soft switch SW1", f"12 V: {float(tot['typ_A_total']):.2f} A / {float(tot['typ_W']):.1f} W typ",
        f"{float(tot['worst_A_total']):.2f} A / {float(tot['worst_W']):.1f} W worst"], "#ffe3e3", R)
    box(17.0, 10.9, 4.7, 2.2, "12 V BUS + 2×470 µF", ["16 AWG cable SMPS → J1", "clone-servo case 12.8 A / 154 W", "F1 at 56 % (64 % clone)"], "#ffe3e3", R)
    arrow((4.3, 12.0), (5.0, 12.0), Gr); arrow((10.0, 12.0), (10.7, 12.0), R); arrow((16.3, 12.0), (17.0, 12.0), R)
    # branches
    box(0.3, 5.9, 6.6, 3.7, "U3 TPSM41625  →  6 V (5.96 V)", [
        f"in: {float(u3['typ_A_total']):.2f} A / {float(u3['typ_W']):.1f} W typ · {float(u3['worst_A_total']):.2f} A / {float(u3['worst_W']):.1f} W worst",
        "out: 4.2 A / 25 W typ · 15.0 A / 89 W worst",
        "loss 2.0 W typ · 4.3 W worst (5.3 W clone 18 A)",
        "rating at 6 V ≈ 20 A (TI derating) → 75 %",
        "ILIM set −30 % ≈ 22 A · OTP 165 °C · PGOOD → A2",
        "Tj ≈ 80 °C typ · ≈126 °C if all stalled (ASSUMPTION)", "→ firmware stall timeout + airflow"], "#fff4e6", O)
    box(7.4, 5.9, 6.6, 3.7, "U4 TPS56837  →  5.10 V", [
        f"in: {float(u4['typ_A_total']):.2f} A / {float(u4['typ_W']):.1f} W typ · {float(u4['worst_A_total']):.2f} A / {float(u4['worst_W']):.1f} W worst",
        "out: 2.43 A / 12.4 W typ · 5.19 A / 26.5 W worst",
        "(4.19 A with default Pi USB limit 0.6 A)",
        "8 A part → 65 % · current limit 9.6 A",
        "loss 0.65 W typ · 1.7 W worst · Tj ≈ 91 °C", "500 kHz, L1 3.3 µH, 4×22 µF out"], "#fff9db", Y)
    box(14.5, 5.9, 7.2, 3.7, "F2 2 A → U5 TMC2209 (12 V VS)", [
        "NEMA 17 17HS4401S (1.7 A, 1.5 Ω)", "set 1.0 A RMS (VREF 1.41 V, 0.11 Ω)",
        "12 V: 0.39 A / 4.7 W typ · 1.0 A / 12 W allowance", "driver loss 0.68 W typ · 0.98 W at 1.2 A",
        "StealthChop, standalone, 1/16 → 1/256", "optional UART jumper JP1 → D8"], "#e3fafc", Cy)
    arrow((19.3, 10.9), (3.6, 9.6), R)
    arrow((19.3, 10.9), (10.7, 9.6), R)
    arrow((19.3, 10.9), (18.1, 9.6), R)
    for (x, y, t) in [(6.2, 9.95, f"{float(u3['worst_A_total']):.2f} A / {float(u3['worst_W']):.1f} W"),
                      (13.0, 10.05, f"{float(u4['worst_A_total']):.2f} A / {float(u4['worst_W']):.1f} W"),
                      (19.0, 10.1, "1.0 A / 12 W")]:
        ax.text(x, y, t + " (worst, at 12 V)", fontsize=9.6, color=R, weight="bold", ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    # loads
    box(0.3, 0.6, 6.6, 4.4, "6 V LOADS — J2 (PCA9685 CH0-CH5)", [
        "6 × MG996R: 5 fingers + wrist", "idle 0.06 A · moving 6 × 0.7 A = 4.2 A (typ)",
        "grip: 5 stalled + wrist = 13.2 A", "ALL stalled 6 × 2.5 A = 15.0 A (worst)",
        "clone peak 6 × 3 A = 18 A (ASSUMPTION)", "bulk: 2 × 470 µF at J2 + 6 × 47 µF",
        "CH6-CH7 spare: light duty only", "PWM 3.3 V from PCA9685 (validate)"], "#fff4e6", O)
    box(7.4, 0.6, 6.6, 4.4, "5.1 V LOADS", [
        "J5 PI-LINK → Raspberry Pi 5:", "   board 2.0 / 3.0 A · cam 0.3 A · fan 0.1 A",
        "   USB 0 / 1.6 A (0.6 A default)  → 2.4 / 5.0 A",
        "MCU 5 V (diode-OR): ATmega 14 mA, CH340C 20 mA,", "   TMC2209 IO 5 mA, LEDs, J6 I²C 0.1 A",
        f"U9 TLV75533P → 3.3 V: {float(u9['typ_A_total'])*1000:.0f} / {float(u9['worst_A_total'])*1000:.0f} mA",
        "   PCA9685, SN74LVC1T45 ×2, VREF, LED", "   loss ≤ 76 mW (500 mA part → 8 %)"], "#fff9db", Y)
    box(14.5, 0.6, 7.2, 4.4, "PROTECTION & NOTES", [
        "AC 4 A T · F1 20 A (board) · F2 2 A (motor)", "6 V / 5.1 V: regulator current limit + hiccup",
        "D1 SMBJ13A: TPSM41625 PVIN abs. max 17 V →", "   keep LRS at 12.0 V, no hot-plug (validate)",
        "USB VBUS only reaches the MCU (B5819W OR)", "board heat: 3.5 W typ · 7.8 W worst",
        "AC side: 53 W typ · 158 W worst (85 % eff.)", "all numbers: power_budget.md / .csv"], "#f1f3f5", Gr)
    arrow((3.6, 5.9), (3.6, 5.0), O, txt="15 A / 89 W", off=(0.15, 0))
    arrow((10.7, 5.9), (10.7, 5.0), Y, txt="5.2 A / 26.5 W", off=(0.15, 0))
    fig.suptitle("HAEBOT Hand Controller v2 — power tree (typical / worst case, amps and watts per branch)", fontsize=18, weight="bold", y=0.985)
    fig.text(0.5, 0.945, "Jinie EduTech · one 12 V input → TPSM41625 6 V servo rail · TPS56837 5.1 V Pi rail · TLV75533P 3.3 V · TMC2209 on 12 V · all grounds common (L2 plane)",
             ha="center", fontsize=10.5, color="#57606a")
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white"); plt.close(fig)
    print("wrote", path)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    layout_png(os.path.join(OUT, "layout_top.png"))
    wiring_png(os.path.join(OUT, "wiring_back_colorcoded.png"))
    power_png(os.path.join(OUT, "power_tree_v2.png"))
