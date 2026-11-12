"""Draw the to-scale top-view layout sketch and the power-tree diagram."""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, FancyArrowPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
sys.path.insert(0, os.path.dirname(__file__))
from layout import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "renders")
LOGO = os.path.join(HERE, "..", "..", "cad", "04_jinie_branding", "assets", "company_logo_solo.png")
plt.rcParams["font.family"] = "DejaVu Sans"

PCB = "#0f1a14"; SILK = "#f2f2f2"
GROUP_EDGE = dict(power="#ff6b6b", servo="#4dabf7", stepper="#ffa94d", mcu="#69db7c", pi="#da77f2", io="#ffd43b", led="#aaaaaa")

def layout_png(path):
    fig, ax = plt.subplots(figsize=(19, 11.5), dpi=130)
    fig.patch.set_facecolor("white")
    ax.set_aspect("equal")
    ax.set_xlim(-22, BOARD_L + 22); ax.set_ylim(-20, BOARD_W + 24)
    ax.axis("off")
    # mm grid (over the board area + margin)
    for gx in np.arange(-10, BOARD_L + 11, 5):
        ax.plot([gx, gx], [-10, BOARD_W + 10], color="#d0d7de" if gx % 10 else "#a9b4bf", lw=0.4 if gx % 10 else 0.7, zorder=0)
        if gx % 10 == 0 and 0 <= gx <= BOARD_L: ax.text(gx, -12.5, f"{gx:.0f}", ha="center", va="center", fontsize=8, color="#57606a")
    for gy in np.arange(-10, BOARD_W + 11, 5):
        ax.plot([-10, BOARD_L + 10], [gy, gy], color="#d0d7de" if gy % 10 else "#a9b4bf", lw=0.4 if gy % 10 else 0.7, zorder=0)
        if gy % 10 == 0 and 0 <= gy <= BOARD_W: ax.text(-13, gy, f"{gy:.0f}", ha="center", va="center", fontsize=8, color="#57606a")
    ax.text(BOARD_L / 2, -16, "x [mm]  (grid 5 mm, bold 10 mm)", ha="center", fontsize=9, color="#57606a")
    # board
    ax.add_patch(FancyBboxPatch((0, 0), BOARD_L, BOARD_W, boxstyle="round,pad=0,rounding_size=2.5", fc=PCB, ec="#000", lw=1.5, zorder=1))
    # open zone tint
    ax.add_patch(Rectangle((0, 0), PI_X0, BOARD_W, fc="#ffffff", alpha=0.05, ec="none", zorder=1.1))
    ax.plot([PI_X0, PI_X0], [0, BOARD_W], color="#7ee0a1", lw=0.8, ls=(0, (2, 2)), zorder=1.2)
    ax.text(PI_X0 / 2, BOARD_W + 1.6, "OPEN ZONE (not covered by Pi)", ha="center", va="bottom", fontsize=9, color="#1a7f37", weight="bold")
    # holes
    for hx, hy in PI_HOLES + EXTRA_HOLES:
        ax.add_patch(Circle((hx, hy), 2.6, fc="#c9a227", ec="none", zorder=2))
        ax.add_patch(Circle((hx, hy), 1.35, fc="white", ec="none", zorder=2.1))
    # parts
    for p in P:
        if p["ref"] == "JP1":
            continue
        ec = GROUP_EDGE[p["group"]]
        if p["kind"] == "cyl":
            ax.add_patch(Circle((p["x"] + p["w"] / 2, p["y"] + p["h"] / 2), p["w"] / 2, fc=p["color"], ec=ec, lw=1.6, zorder=3))
        else:
            ax.add_patch(Rectangle((p["x"], p["y"]), p["w"], p["h"], fc=p["color"], ec=ec, lw=1.6, zorder=3))
    # A4988 details: sockets, heatsink, jumpers (dashed, under module)
    u5 = part("U5")
    for yy in (u5["y"], u5["y"] + u5["h"] - 2.5):
        ax.add_patch(Rectangle((u5["x"], yy), u5["w"], 2.5, fc="#111", ec="none", zorder=3.2))
        for k in range(8):
            ax.add_patch(Circle((u5["x"] + 1.27 + k * 2.54, yy + 1.25), 0.45, fc=C["pin"], ec="none", zorder=3.3))
    ax.add_patch(Rectangle((u5["x"] + 6, u5["y"] + 3.6), 9, 8, fc=C["sink"], ec="#666", lw=0.8, zorder=3.4))
    for k in range(5): ax.plot([u5["x"] + 6.9 + k * 1.8] * 2, [u5["y"] + 3.9, u5["y"] + 11.3], color="#7d828a", lw=0.8, zorder=3.5)
    jp = part("JP1")
    ax.add_patch(Rectangle((jp["x"], jp["y"]), jp["w"], jp["h"], fc="none", ec="#ffa94d", ls="--", lw=0.8, zorder=3.6))
    ax.text(u5["x"] + u5["w"] / 2, u5["y"] - 1.3, "U5 A4988 (socketed)  ·  MS1-3 jumpers underneath", ha="center", va="top", fontsize=6.3, color=SILK, zorder=6)
    # servo header pins + silkscreen labels
    j = part("J10")
    for i, nm in enumerate(SERVO_CH):
        yy = j["y"] + j["h"] - 1.27 - i * 2.54
        for k in range(3):
            ax.add_patch(Rectangle((j["x"] + 0.4 + k * 2.54, yy - 0.9), 1.8, 1.8, fc="#000", ec="none", zorder=3.4))
            ax.add_patch(Circle((j["x"] + 1.3 + k * 2.54, yy), 0.32, fc=C["pin"], ec="none", zorder=3.5))
        ax.text(j["x"] - 0.6, yy, f"{i} {nm}", ha="right", va="center", fontsize=6.1, color=SILK, family="DejaVu Sans Mono", zorder=6)
    for k, t in enumerate(["S", "V+", "G"]):
        ax.text(j["x"] + 1.3 + k * 2.54, j["y"] - 1.0, t, ha="center", va="top", fontsize=5.5, color=SILK, zorder=6)
    ax.text(j["x"] + j["w"] / 2, j["y"] + j["h"] + 0.6, "SERVO 6V", ha="center", va="bottom", fontsize=6, color=SILK, weight="bold", zorder=6)
    # logo + vertical brand text in the open zone
    if os.path.exists(LOGO):
        img = plt.imread(LOGO)
        if img.shape[-1] == 4:   # make the icon white (silkscreen)
            a = img[..., 3]
        else:
            a = (img[..., :3].mean(-1) < 0.8).astype(float)
        silk = np.ones(img.shape[:2] + (4,)); silk[..., 3] = a * (img[..., :3].mean(-1) < 0.85)
        ax.imshow(silk, extent=(1.3, 8.3, 31.0, 38.0), zorder=6)
    ax.text(4.8, 22.0, "JINIE EDUTECH", rotation=90, ha="center", va="center", fontsize=10.5, color=SILK, weight="bold", zorder=6)
    ax.text(15.8, 11.0, "HAEBOT HC v1.0", ha="center", va="center", fontsize=6.5, color=SILK, weight="bold", zorder=6)
    # part labels (on-part, white)
    skip = {"J10", "U5", "JP1"} | {f"D{i}" for i in range(1, 7)}
    for p in P:
        if p["ref"] in skip:
            continue
        cx, cy = p["x"] + p["w"] / 2, p["y"] + p["h"] / 2
        small = p["w"] < 7 or p["h"] < 4
        fc = "#000" if p["color"] in (C["conn"], C["usb"], C["sink"]) else SILK
        txt = f"{p['ref']}\n{p['label']}"
        if p["ref"] in ("U3", "U4"):
            txt = f"{p['ref']}\n{p['label']}\n(solder-on\nmodule, v1)"
        rot = 90 if (p["h"] > p["w"] * 1.4 and p["w"] < 8) else 0
        if small and p["ref"] not in ("U2", "J8", "C2", "Q1", "U6", "D7", "SW3"):
            ax.annotate(txt.replace("\n", " "), (cx, cy), xytext=(cx, cy + (3.2 if cy < 45 else -3.2)), ha="center", va="center", fontsize=5.6, color=SILK,
                        arrowprops=dict(arrowstyle="-", color=SILK, lw=0.5), zorder=7)
        else:
            ax.text(cx, cy, txt, ha="center", va="center", fontsize=6.4 if not small else 5.3, color=fc, rotation=rot, zorder=7, linespacing=1.05,
                    weight="bold" if p["ref"] in ("U1", "U2", "U3", "U4", "J6") else "normal")
    # LEDs
    for i in range(1, 7):
        p = part(f"D{i}")
        ax.text(p["x"] + 0.8, p["y"] + 2.0, p["label"], rotation=90, ha="center", va="bottom", fontsize=5.2, color=SILK, zorder=7)
    # Pi outline (dashed) + header + ports
    ax.add_patch(FancyBboxPatch((PI_X0, 0), PI_L, PI_W, boxstyle="round,pad=0,rounding_size=3", fc="#c51a4a", alpha=0.07, ec="#c51a4a", lw=2.2, ls=(0, (6, 3)), zorder=8))
    ax.add_patch(Rectangle((PI_HDR["x"], PI_HDR["y"]), PI_HDR["w"], PI_HDR["h"], fc="none", ec="#c51a4a", lw=1.3, ls=(0, (2, 2)), zorder=8))
    ax.text(PI_HDR["x"] - 1.5, BOARD_W + 1.2, "Pi 5 40-pin header outline (on the Pi's TOP side, pin 1 left)", ha="left", va="bottom", fontsize=6.8, color="#c51a4a", zorder=8)
    for (x, y, w, h, t) in [(PI_X0 + 66, 38, 21.5, 16, "Pi ETH"), (PI_X0 + 70, 20.5, 17.5, 13.1, "Pi USB3"), (PI_X0 + 70, 2.5, 17.5, 13.1, "Pi USB2")]:
        ax.add_patch(Rectangle((x, y), w, h, fc="none", ec="#c51a4a", lw=0.9, ls=(0, (1, 2)), zorder=8))
        ax.text(x + w - 0.8, y + h - 0.8, t, ha="right", va="top", fontsize=6.5, color="#ff8fab", zorder=8)
    for (x, t) in [(PI_X0 + 11.2, "Pi USB-C"), (PI_X0 + 25.8, "HDMI0"), (PI_X0 + 39.2, "HDMI1")]:
        ax.plot([x], [-1.2], marker="^", color="#c51a4a", ms=5, zorder=8)
        ax.text(x, -2.6, t, ha="center", va="top", fontsize=6.3, color="#c51a4a", zorder=8)
    ax.text(PI_X0 + PI_L / 2, BOARD_W + 8.4, "RASPBERRY PI 5 FOOTPRINT  (85 × 56 mm, stacked on 4 × M2.5 × 18 mm standoffs)", ha="center", fontsize=10.5, color="#c51a4a", weight="bold")
    # PI-LINK cable
    j6 = part("J6")
    ax.add_patch(FancyArrowPatch((j6["x"] + j6["w"] / 2, BOARD_W), (PI_HDR["x"] + 6.4, PI_HDR["y"] + PI_HDR["h"]),
                                 connectionstyle="arc3,rad=0.5", arrowstyle="-|>", mutation_scale=10, color="#8250df", lw=1.8, zorder=9))
    ax.text(81, BOARD_W + 4.3, "← 7-wire PI-LINK cable to Pi pins 1-10\n   (5V,5V,GND,GND,TXD,RXD,GPIO4)", ha="left", va="center", fontsize=7.4, color="#8250df", zorder=9)
    # dimensions
    def dim(x0, y0, x1, y1, t, off, horiz=True):
        if horiz:
            ax.annotate("", (x0, y0 + off), (x1, y1 + off), arrowprops=dict(arrowstyle="<->", color="#24292f", lw=0.9))
            ax.text((x0 + x1) / 2, y0 + off + (1.2 if off > 0 else -1.2), t, ha="center", va="bottom" if off > 0 else "top", fontsize=9, color="#24292f")
        else:
            ax.annotate("", (x0 + off, y0), (x1 + off, y1), arrowprops=dict(arrowstyle="<->", color="#24292f", lw=0.9))
            ax.text(x0 + off + (1.2 if off > 0 else -1.2), (y0 + y1) / 2, t, ha="left" if off > 0 else "right", va="center", fontsize=9, color="#24292f", rotation=90)
    dim(0, 0, BOARD_L, 0, "115.0 mm", -7.0)
    dim(BOARD_L, 0, BOARD_L, BOARD_W, "56.0 mm (= Pi 5 width)", 9.5, horiz=False)
    dim(0, BOARD_W, PI_X0, BOARD_W, "30.0", 13.5)
    dim(PI_X0, BOARD_W, BOARD_L, BOARD_W, "85.0 (Pi overlap)", 13.5)
    # edge call-outs
    ax.text(-3, 7, "12 V IN\n(from SMPS)", ha="right", va="center", fontsize=7.5, color="#cf222e", weight="bold")
    ax.annotate("", (0, 6.6), (-2.5, 6.6), arrowprops=dict(arrowstyle="-|>", color="#cf222e"))
    ax.text(-3, 25.7, "servo cables\nplug in from\nabove", ha="right", va="center", fontsize=7.2, color="#0969da")
    ax.text(-3, 47.8, "NEMA 17 driver,\ntrim-pot reachable", ha="right", va="center", fontsize=7.2, color="#bc4c00")
    ax.text(BOARD_L + 1.5, 9.5, "USB-C (PC)", ha="left", va="center", fontsize=7, color="#1a7f37")
    ax.text(BOARD_L + 1.5, 20, "RESET", ha="left", va="center", fontsize=7, color="#1a7f37")
    ax.text(BOARD_L + 1.5, 30.5, "USB | Pi\nselect", ha="left", va="center", fontsize=7, color="#1a7f37")
    ax.text(43, -5.6, "side-entry power switch + LED bar (visible from the edge)", ha="left", va="center", fontsize=6.8, color="#57606a")
    # legend
    from matplotlib.lines import Line2D
    items = [("12V / power", "power"), ("Servo (PCA9685, 6 V)", "servo"), ("Stepper (A4988, 12 V)", "stepper"), ("MCU / USB (5 V)", "mcu"), ("Pi link", "pi"), ("Spare I2C", "io")]
    handles = [Line2D([0], [0], marker="s", color="w", markerfacecolor="#333", markeredgecolor=GROUP_EDGE[g], markeredgewidth=2, ms=11, label=l) for l, g in items]
    handles += [Line2D([0], [0], color="#c51a4a", ls="--", lw=2, label="Raspberry Pi 5 outline (above)"), Line2D([0], [0], marker="o", color="w", markerfacecolor="#c9a227", ms=10, label="M2.5 mounting hole")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, 0.0), ncol=4, fontsize=8.5, frameon=False)
    fig.suptitle("HAEBOT Hand Controller v1.0  —  top-view concept layout (1 : 1 mm grid)", fontsize=16, weight="bold", y=0.975)
    fig.text(0.5, 0.935, "Jinie EduTech  ·  115 × 56 mm, 2-layer, 2 oz Cu  ·  Pi 5 stacks on top  ·  all under-Pi parts ≤ 12 mm tall  ·  concept placement, not routed",
             ha="center", fontsize=10, color="#57606a")
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white"); plt.close(fig)

def box(ax, x, y, w, h, title, lines, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.25", fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="top", fontsize=11.5, weight="bold", color="#111")
    ax.text(x + w / 2, y + h - 0.95, "\n".join(lines), ha="center", va="top", fontsize=8.6, color="#222", linespacing=1.35)

def arrow(ax, a, b, txt="", col="#444", rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=16, lw=2, color=col, connectionstyle=f"arc3,rad={rad}"))
    if txt:
        ax.text((a[0] + b[0]) / 2 + 0.12, (a[1] + b[1]) / 2, txt, fontsize=8.2, color=col, ha="left", va="center", weight="bold")

def power_png(path):
    fig, ax = plt.subplots(figsize=(17, 10.5), dpi=130)
    ax.set_xlim(0, 17); ax.set_ylim(-0.9, 10.5); ax.axis("off")
    R, O, G, B, Pp, Y = ("#ffe3e3", "#d6336c"), ("#fff0db", "#e8590c"), ("#e6fcf5", "#2b8a3e"), ("#e7f5ff", "#1c7ed6"), ("#f8f0fc", "#ae3ec9"), ("#fff9db", "#f08c00")
    box(ax, 0.3, 8.0, 3.2, 2.1, "AC 220 V", ["IEC C14 inlet", "with fuse + rocker switch", "(in the base, enclosed)"], "#f1f3f5", "#495057")
    box(ax, 4.2, 8.0, 3.4, 2.1, "SMPS 12 V", [">= 10 A (20 A OK)", "enclosed, in the base", "18 AWG to the board"], "#f1f3f5", "#495057")
    box(ax, 8.4, 8.0, 4.0, 2.1, "INPUT PROTECTION", ["J1 screw terminal -> F1 10 A blade", "Q1 P-MOSFET (rev-pol + SW1 on/off)", "D7 SMBJ15A TVS  ·  LED 12V"], *R)
    arrow(ax, (3.5, 9.05), (4.2, 9.05)); arrow(ax, (7.6, 9.05), (8.4, 9.05))
    box(ax, 13.2, 8.0, 3.5, 2.1, "12 V RAIL", ["peak ~6 A from SMPS", "wide pour, 2 oz Cu", "main fuse 10 A"], *R)
    arrow(ax, (12.4, 9.05), (13.2, 9.05))
    # branches
    box(ax, 0.3, 3.9, 5.0, 3.0, "BUCK 1  12 V -> 6 V", ["U3 Pololu D36V50F6 (5.5 A class)", "F2 PTC 6 V  ·  C1 1000 uF bulk", "LED 6V", "budget: 3 A typical / 6.5 A worst"], *B)
    box(ax, 6.0, 3.9, 5.0, 3.0, "BUCK 2  12 V -> 5 V", ["U4 Pololu D36V50F5 (5.5 A class)", "F3 PTC 5 V  ·  LED 5V", "set 5.1 V if trimmable", "budget: 3.3 A typical / 5 A max"], *G)
    box(ax, 11.7, 3.9, 5.0, 3.0, "12 V DIRECT", ["F4 3 A  ->  A4988 VMOT", "C2 100 uF / 25 V at the driver", "NEMA 17 @ 1.0-1.5 A/phase (Vref)", "budget: ~1 A from 12 V"], *O)
    ax.plot([14.95, 14.95], [8.0, 7.45], color="#c92a2a", lw=2.2)
    ax.plot([2.8, 14.95], [7.45, 7.45], color="#c92a2a", lw=2.2)
    ax.text(5.6, 7.55, "12 V bus", fontsize=8.5, color="#c92a2a", weight="bold", va="bottom")
    for x in (2.8, 8.5, 14.2):
        arrow(ax, (x, 7.45), (x, 6.9), col="#c92a2a")
    # loads
    box(ax, 0.3, 0.3, 5.0, 3.0, "SERVO LOADS (PCA9685 V+)", ["5 x ES08MA II fingers  ~0.3 A avg, 0.8 A stall", "1 x MG996R wrist  ~0.6 A avg, 2.5 A stall", "+ 4 spare channels", "-> stagger moves in firmware"], *B)
    box(ax, 6.0, 0.3, 5.0, 3.0, "5 V LOADS", ["Raspberry Pi 5 + Camera 3: 2.5-3 A,", "    up to 4 A peak (via GPIO pins 2/4)", "MCU / CH340 / PCA9685 logic: <0.1 A", "A4988 logic: <10 mA"], *G)
    box(ax, 11.7, 0.3, 5.0, 3.0, "MOTOR LOAD", ["NEMA 17 base (A4988)", "chopper draws < phase current", "from 12 V (~0.6-1 A avg)", "EN pin lets firmware cut torque"], *O)
    arrow(ax, (2.8, 3.9), (2.8, 3.3), col="#1c7ed6"); arrow(ax, (8.5, 3.9), (8.5, 3.3), col="#2b8a3e"); arrow(ax, (14.2, 3.9), (14.2, 3.3), col="#e8590c")
    # MCU 5V OR note
    ax.text(8.5, -0.25, "MCU 5 V = diode-OR( 5 V rail , USB VBUS )  ->  USB alone can program the MCU but never back-powers the Pi",
            ha="center", fontsize=9, color="#2b8a3e", style="italic")
    ax.text(8.5, -0.65, "12 V draw at worst case ≈ 6 V·6.5 A/0.9/12 + 5 V·5 A/0.9/12 + 1 A ≈ 6.9 A  (typical ≈ 3.5 A)  ->  10 A SMPS is enough, 20 A gives headroom",
            ha="center", fontsize=9, color="#c92a2a", style="italic")
    fig.suptitle("HAEBOT Hand Controller v1.0  —  power tree & current budget", fontsize=16, weight="bold", y=0.99)
    fig.text(0.5, 0.945, "Jinie EduTech  ·  one 12 V input, three rails (12 V / 6 V / 5 V), all grounds common  ·  Pi 3.3 V GPIO is the 4th level (level-shifted UART)", ha="center", fontsize=10, color="#57606a")
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white"); plt.close(fig)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    layout_png(os.path.join(OUT, "layout_top.png"))
    power_png(os.path.join(OUT, "power_tree.png"))
    print("ok")
