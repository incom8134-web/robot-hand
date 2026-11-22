"""Top-view layout drawing of the P1 base: SMPS, controller board, mains corner with the user's inlet, USB, forearm socket.
Writes images/..._img_13_base_layout.png (reads the parameters from the base build script)."""
import os, sys, json
sys.dont_write_bytecode = True
import importlib.util as iu, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patches as pt
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(fn, n):
    s = iu.spec_from_file_location(n, fn); m = iu.module_from_spec(s); s.loader.exec_module(m); return m
paths = _load(os.path.join(HERE, "dona_univ_robot_hand_2026-11-17_Sanjev_A_paths.py"), "p"); F = paths.F
b = _load(F("base_build.py"), "b")
rep = json.load(open(F("base_report.json")))
fig, ax = plt.subplots(figsize=(11, 8.2))
def rect(x0, y0, x1, y1, fc, ec="k", lw=1.2, a=1.0, ls="-"):
    ax.add_patch(pt.Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw, alpha=a, ls=ls))
W, D, WL = b.W, b.Dp, b.WALL
rect(0, 0, W, D, "#d9dbe0", lw=2); rect(WL, WL, W - WL, D - WL, "white", ec="#999")
lo, hi = b.PSU_LO, b.PSU_HI
# mains zone: front-right corner + wire channel at the PSU terminal end
rect(b.PART_X + 2, WL, W - WL, lo[1] - 1, "#ffd9d9", ec="#c33", ls="--")
rect(hi[0], lo[1], W - WL, hi[1], "#ffd9d9", ec="#c33", ls="--")
rect(b.PART_X, WL, b.PART_X + 2, lo[1] - 1, "#c33", ec="#c33")
ax.text((b.PART_X + W) / 2 - 10, lo[1] - 10, "MAINS 230 V", ha="center", fontsize=8, color="#a00", weight="bold")
# SMPS
rect(lo[0], lo[1], hi[0], hi[1], "#c9ccd2", lw=1.5)
ax.text((lo[0] + hi[0]) / 2, hi[1] - 20, f"SMPS  Mean Well LRS-350-12\n{b.PSU[0]:.0f} x {b.PSU[1]:.0f} x {b.PSU[2]:.0f} mm, 12 V 29 A - on 5 mm rails, 2 straps",
        ha="center", va="center", fontsize=9)
for x in (lo[0] + 45, hi[0] - 45):
    rect(x - 7, lo[1] - b.PSU_CLR - 8, x + 7, hi[1] + b.PSU_CLR + 6, "#555", ec="#333", a=0.35)
ax.text(hi[0] - 3, (lo[1] + hi[1]) / 2, "terminals (AC in, 12 V out)", ha="right", va="center", fontsize=7, rotation=90)
# inlet in the right wall
cy, cz = b.IEC_C
rect(W - WL - b.IEC_BODY_DEPTH, cy - b.IEC_BODY[0] / 2, W - WL, cy + b.IEC_BODY[0] / 2, "#333", a=0.9)
rect(W, cy - b.IEC_FLANGE[0] / 2, W + 3, cy + b.IEC_FLANGE[0] / 2, "#111")
ax.text(W - WL - b.IEC_BODY_DEPTH / 2, cy, "INLET\nP087", ha="center", va="center", fontsize=8, color="white", weight="bold")
ax.annotate("your inlet: C14 + fuse + switch\nscrewed into the RIGHT side wall\n(2 x M3, sizes to measure)", (W + 3, cy), (W + 10, cy - 8), ha="left", va="center",
            fontsize=8, arrowprops=dict(arrowstyle="->"))
# board
x0, y0 = b.PCB_X0, b.PCB_Y0
rect(x0, y0, x0 + b.PCB[0], y0 + b.PCB[1], "#2ea043", a=0.9, lw=1.5)
ax.text(x0 + b.PCB[0] / 2, y0 + b.PCB[1] / 2, f"CONTROLLER BOARD\n{b.PCB[0]:.0f} x {b.PCB[1]:.0f} mm\n4 x M3 standoffs, {b.PCB_STANDOFF:.0f} mm",
        ha="center", va="center", fontsize=9, color="white", weight="bold")
for (x, y) in b.pcb_holes(): ax.add_patch(pt.Circle((x, y), 3.5, fc="#222"))
# USB
rect(b.USB_X - 7, -1, b.USB_X + 7, WL + 1, "#222")
ax.annotate("USB mini-B (front)", (b.USB_X, 0), (b.USB_X, -20), ha="center", fontsize=8, arrowprops=dict(arrowstyle="->"))
# socket + cable hole
ox0, oy0, ox1, oy1 = rep["forearm_socket"]["outline_bbox"]
ax.add_patch(pt.Ellipse(((ox0 + ox1) / 2, (oy0 + oy1) / 2), ox1 - ox0, oy1 - oy0, fc="none", ec="#2b6cd9", lw=2, ls="--"))
sx, sy = b.SOCK_C
rect(sx - b.CABLE_HOLE[0] / 2, sy - b.CABLE_HOLE[1] / 2, sx + b.CABLE_HOLE[0] / 2, sy + b.CABLE_HOLE[1] / 2, "none", ec="#2b6cd9", lw=1.5)
ax.annotate("forearm socket on the lid (dashed)\n+ cable hole 40 x 20; the cable runs\nover the SMPS (" + f"{b.H - hi[2]:.0f}" + " mm free)", ((ox0 + ox1) / 2, oy1 - 4), (W + 10, D - 15),
            ha="left", va="top", fontsize=8, color="#2b6cd9", arrowprops=dict(arrowstyle="->", color="#2b6cd9"))
# wiring
kw = dict(arrowstyle="->", lw=1.8)
ax.annotate("", (hi[0] + 7, lo[1] + 25), (W - WL - b.IEC_BODY_DEPTH + 6, cy + b.IEC_BODY[0] / 2), arrowprops=dict(color="#c33", **kw))
ax.text(W - WL - 6, lo[1] + 6, "AC\nL N PE", color="#c33", fontsize=7, ha="right")
ax.annotate("", (x0 + b.PCB[0] - 6, y0 + b.PCB[1] - 4), (hi[0] - 4, lo[1] + 4), arrowprops=dict(color="#d98a00", **kw))
ax.text(x0 + b.PCB[0] + 6, y0 + 22, "12 V to board", color="#d98a00", fontsize=8)
ax.annotate("", (sx - 8, sy - 6), (x0 + b.PCB[0] - 25, y0 + b.PCB[1]), arrowprops=dict(color="#2b6cd9", **kw))
ax.text(x0 + 2, y0 + b.PCB[1] + 4, "servo bus up the arm (12 V, GND, data)", color="#2b6cd9", fontsize=8)
for (x, y) in b.BOSSES: ax.add_patch(pt.Circle((x, y), b.BOSS_D / 2, fc="#bbb", ec="#777"))
ax.set_xlim(-12, W + 120); ax.set_ylim(-32, D + 12); ax.set_aspect("equal")
ax.set_title(f"P1 base, top view, lid removed - {W:.0f} x {D:.0f} x {b.H:.0f} mm (front at the bottom)", fontsize=11)
ax.set_xlabel("mm"); ax.grid(alpha=0.25)
plt.tight_layout(); plt.savefig(F("img_13_base_layout.png"), dpi=110)
print("ok")
