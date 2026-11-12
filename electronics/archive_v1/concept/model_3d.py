"""CadQuery 3D mock-up of the HAEBOT Hand Controller v1.0 (+ simplified Raspberry Pi 5),
STEP export and offscreen renders (numpy z-buffer rasteriser, no GPU needed).

Run:  python model_3d.py            -> ../HAEBOT_HandController_v1_concept.step (+ _with_Pi5.step)
                                       ../renders/3d_top.png, 3d_iso_with_pi.png, 3d_iso_no_pi.png
"""
import os, sys, math, numpy as np, cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(__file__))
from layout import *

HERE = os.path.dirname(os.path.abspath(__file__))
ELEC = os.path.abspath(os.path.join(HERE, ".."))
REND = os.path.join(ELEC, "renders")
LOGO_DXF = os.path.join(ELEC, "..", "cad", "04_jinie_branding", "dxf", "JE_HandCoverV1_JinieIconOnly_logo2d.dxf")
T = BOARD_T
FONT = "DejaVu Sans"

def hexc(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

ITEMS = []          # (name, shape, rgb, group)  group: board | pi
LABELS = []         # (text, (x,y,z), group)

def box(x, y, z, w, h, d):
    return cq.Workplane("XY").box(w, h, d, centered=False).translate((x, y, z)).val()

def cyl(cx, cy, z, r, d):
    return cq.Workplane("XY").circle(r).extrude(d).translate((cx, cy, z)).val()

def add(name, shape, color, group="board"):
    ITEMS.append((name, shape, hexc(color) if isinstance(color, str) else color, group))

def silk_text(txt, x, y, size, rot=0, halign="center", valign="center", bold=True, color="#f4f4f4", group="board", z=T):
    w = cq.Workplane("XY").text(txt, size, 0.05, font=FONT, kind="bold" if bold else "regular", halign=halign, valign=valign)
    s = w.val()
    if rot: s = s.rotate((0, 0, 0), (0, 0, 1), rot)
    add("silk:" + txt, s.translate((x, y, z)), color, group)

# ------------------------------------------------------------------ board
pcb = (cq.Workplane("XY").box(BOARD_L, BOARD_W, T, centered=False).edges("|Z").fillet(2.5))
for hx, hy in PI_HOLES + EXTRA_HOLES:
    pcb = pcb.cut(cq.Workplane("XY").circle(1.35).extrude(T).translate((hx, hy, 0)))
add("PCB", pcb.val(), "#121614")
for hx, hy in PI_HOLES + EXTRA_HOLES:   # gold annular rings
    ring = cq.Workplane("XY").circle(2.6).circle(1.35).extrude(0.04).translate((hx, hy, T))
    add("ring", ring.val(), "#c9a227")
# open-zone divider line (silk)
add("silk:divider", box(PI_X0 - 0.15, 1.0, T, 0.3, BOARD_W - 2, 0.03), "#9aa59f")

def lab(ref, text=None, dz=0.0, group="board"):
    p = part(ref)
    LABELS.append((text or f"{p['ref']} {p['label']}", (p["x"] + p["w"] / 2, p["y"] + p["h"] / 2, T + p["z"] + dz), group))

for p in P:
    r, x, y, w, h, z, col = p["ref"], p["x"], p["y"], p["w"], p["h"], p["z"], p["color"]
    if r == "J1":   # screw terminal with screw wells + wire openings
        add(r, box(x, y, T, w, h, z), col)
        for k in range(2):
            add(r + "s", cyl(x + w * 0.62, y + 2.55 + k * 5.08, T + z, 1.6, 0.05), "#9aa0a6")
            add(r + "o", box(x - 0.01, y + 1.0 + k * 5.08, T + 2.0, 0.3, 3.1, 3.0), "#0b3d20")
        lab(r, "J1 12V IN (screw terminal)")
    elif r == "F1":
        add(r, box(x, y, T, w, h, z), col)
        add(r + "b", box(x + 1.2, y + 1.5, T + z, 10.6, 3.5, 7.5), C["fuse"])
        lab(r, "F1 10A blade fuse", dz=7.5)
    elif r == "J10":
        add(r, box(x, y, T, w, h, 2.5), col)
        for i in range(10):
            for k in range(3):
                add("pin", box(x + 1.0 + k * 2.54, y + 0.95 + i * 2.54, T + 2.5, 0.64, 0.64, 6.0), C["pin"])
        lab(r, "J10 servo headers x10 (S/V+/G)", dz=-2)
    elif r == "U5":
        for yy in (y, y + h - 2.5):
            add("sock", box(x, yy, T, w, 2.5, 8.5), "#101010")
        add(r, box(x, y, T + 8.5, w, h, 1.6), col)
        add("chip", box(x + 6, y + 4, T + 10.1, 5, 5, 0.9), "#111")
        add("sink", box(x + 5.5, y + 3.6, T + 11.0, 9, 8, 1.0), C["sink"])
        for k in range(5):
            add("fin", box(x + 5.8 + k * 1.85, y + 3.6, T + 12.0, 0.8, 8, 5.0), C["sink"])
        add("pot", cyl(x + 17.5, y + 7.6, T + 10.1, 1.5, 1.6), "#e8e8e8")
        lab(r, "U5 A4988 in socket + heatsink", dz=-1)
    elif r == "JP1":
        add(r, box(x, y, T, w, h, 2.5), col)   # hidden under module
    elif p["kind"] == "cyl":
        cx, cy, rr = x + w / 2, y + h / 2, w / 2
        add(r, cyl(cx, cy, T, rr, z), col)
        add(r + "top", cyl(cx, cy, T + z, rr * 0.85, 0.05), "#9aa0a6")
        lab(r, f"{r} {p['label']}")
    elif r in ("U3", "U4"):
        for (px, py) in ((x + 1.27, y + 1.27), (x + w - 2.5, y + 1.27), (x + 1.27, y + h - 2.5), (x + w - 2.5, y + h - 2.5)):
            add("hdr", box(px, py, T, 1.3, 1.3, 2.5), "#111")
        add(r, box(x, y, T + 2.5, w, h, 1.6), col)
        add("ind", box(x + 6, y + 6, T + 4.1, 11, 11, 6.5), "#2a2a2a")
        add("ic", box(x + 18.5, y + 8, T + 4.1, 4, 5, 1.0), "#111")
        for k in range(3):
            add("cap", box(x + 3 + k * 4, y + 19.5, T + 4.1, 3.2, 1.6, 1.6), "#b8936a")
        lab(r, f"{r} buck {p['label'][5:]} (module)", dz=-1.5)
    elif r.startswith("J") and r in ("J4", "J5", "J6", "J7"):
        add(r, box(x, y, T, w, h, z), col)
        add(r + "o", box(x + 0.8, y + h - 0.02, T + 1.2, w - 1.6, 0.05, z - 2.4), "#3b3428")
        lab(r)
    elif r == "J9":
        add(r, box(x, y, T, w + 0.6, h, z), col)
        add(r + "o", box(x + w + 0.58, y + 1.0, T + 0.6, 0.05, h - 2, z - 1.2), "#222")
        lab(r, "J9 USB-C (CH340)")
    elif r in ("SW1", "SW2", "SW3"):
        add(r, box(x, y, T, w, h, z), col)
        if r == "SW1":
            add(r + "a", box(x + 3, y - 1.5, T + 1.2, 3, 1.5, 1.8), C["sw_act"])
        else:
            add(r + "a", box(x + w, y + h / 2 - 1.5, T + 1.0, 1.5, 3, 2.0), C["sw_act"] if r == "SW2" else "#d33")
        lab(r, {"SW1": "SW1 power switch", "SW2": "SW2 serial select USB/Pi", "SW3": "SW3 reset"}[r])
    elif r.startswith("D") and r[1:].isdigit() and int(r[1:]) <= 6:
        add(r, box(x, y, T, w, h, z), col)
    else:
        add(r, box(x, y, T, w, h, z), col)
        if r in ("U1", "U2", "U6"):
            add(r + "dot", cyl(x + 1.2, y + h - 1.2, T + z, 0.4, 0.03), "#777")
        if r in ("U1", "U2", "U6", "Q1", "D7", "J8", "U7"):
            lab(r)
LABELS.append(("D1-D6 LED bar (12V 6V 5V STAT TX RX)", (55.0, 0.6, T + 0.9), "board"))
LABELS.append(("Jinie EduTech logo (silkscreen)", (4.8, 30.0, T), "board"))

# silkscreen texts
j = part("J10")
for i, nm in enumerate(SERVO_CH):
    silk_text(f"{i} {nm}", j["x"] - 0.7, j["y"] + j["h"] - 1.27 - i * 2.54, 1.25, halign="right")
for k, t in enumerate(["S", "V+", "G"]):
    silk_text(t, j["x"] + 1.3 + k * 2.54, j["y"] - 1.1, 1.0)
silk_text("SERVO 6V", j["x"] + j["w"] / 2, j["y"] + j["h"] + 1.0, 1.1)
silk_text("JINIE EDUTECH", 4.8, 22.0, 2.2, rot=90)
silk_text("HAEBOT HC v1.0", 15.8, 11.0, 1.3)
silk_text("12V IN", 8.55, 6.6, 0.95, rot=90)
silk_text("MS1 MS2 MS3", 14.5, 38.3, 0.9)
for ref, t in [("J4", "MOTOR"), ("J5", "LIMIT"), ("J6", "PI-LINK"), ("J7", "I2C 5V")]:
    p = part(ref); silk_text(t, p["x"] + p["w"] / 2, p["y"] - 1.0, 1.2)
silk_text("POWER", 41.5, 6.3, 1.1)
silk_text("12V 6V 5V ST TX RX", 55.0, 2.4, 0.75)
silk_text("HAEBOT Hand Controller v1.0", 67.0, 35.6, 1.6)
silk_text("Jinie EduTech  ·  Robot-hand edu kit  ·  2026", 67.0, 5.8, 1.1, bold=False)
silk_text("USB", 104.5, 9.5, 1.0, rot=90); silk_text("RST", 106.0, 20.0, 1.0, rot=90); silk_text("USB|PI", 105.5, 30.5, 1.0, rot=90)
# logo icon from the branding DXF
try:
    lw = cq.importers.importDXF(LOGO_DXF)
    wires = lw.wires().vals()
    bb = cq.Compound.makeCompound(wires).BoundingBox()
    s = 6.0 / max(bb.xlen, bb.ylen)
    faces = cq.Workplane("XY").add(wires).toPending().extrude(0.05).val()
    faces = faces.translate((-bb.center.x, -bb.center.y, 0)).scale(s).translate((4.8, 34.6, T))
    add("silk:logo", faces, "#2f9be0")
except Exception as e:
    print("logo DXF skipped:", e)

# ------------------------------------------------------------------ Pi 5 (simplified) + standoffs + cable
ZP = T + STANDOFF_H
for hx, hy in PI_HOLES:
    add("standoff", cq.Workplane("XY").polygon(6, 5.0).extrude(STANDOFF_H).translate((hx, hy, T)).val(), "#c8a24a", "pi")
pi = cq.Workplane("XY").box(PI_L, PI_W, 1.4, centered=False).edges("|Z").fillet(3).translate((PI_X0, 0, ZP))
for hx, hy in PI_HOLES:
    pi = pi.cut(cq.Workplane("XY").circle(1.35).extrude(1.4).translate((hx, hy, ZP)))
add("Pi5 PCB", pi.val(), "#1e7b3a", "pi")
Zt = ZP + 1.4
add("Pi hdr", box(PI_HDR["x"], PI_HDR["y"], Zt, PI_HDR["w"], PI_HDR["h"], 2.5), "#111", "pi")
for k in range(20):
    for rr in range(2):
        add("pin", box(PI_HDR["x"] + 1.0 + k * 2.54, PI_HDR["y"] + 1.0 + rr * 2.54, Zt + 2.5, 0.64, 0.64, 6.0), C["pin"], "pi")
add("Pi ETH", box(PI_X0 + 66, 38, Zt, 23.5, 16, 13.5), "#c9ccd1", "pi")
add("Pi USB3", box(PI_X0 + 70, 20.5, Zt, 19.5, 13.1, 16), "#1f5fbf", "pi")
add("Pi USB2", box(PI_X0 + 70, 2.5, Zt, 19.5, 13.1, 16), "#202020", "pi")
add("Pi cooler", box(PI_X0 + 22, 14, Zt, 38, 30, 8.5), "#30343a", "pi")
add("Pi fan", cyl(PI_X0 + 41, 29, Zt + 8.5, 11, 0.4), "#15171a", "pi")
for (px, w) in ((PI_X0 + 7.5, 9.0), (PI_X0 + 22.5, 6.6), (PI_X0 + 35.9, 6.6)):
    add("Pi port", box(px, -1.0, Zt, w, 7.5, 3.2), "#c9ccd1", "pi")
for py in (14.5, 33.0):
    add("Pi CSI", box(PI_X0 + 62, py, Zt, 3.0, 9.0, 1.5), "#f0e6c8", "pi")
silk_text("Raspberry Pi 5", PI_X0 + 13, 45.0, 2.4, color="#f4f4f4", group="pi", z=Zt)
LABELS.append(("Raspberry Pi 5 (stacked)", (PI_X0 + 41, 29, Zt + 8.9), "pi"))
LABELS.append(("M2.5 x 18 mm standoffs", (PI_HOLES[0][0], PI_HOLES[0][1], T + STANDOFF_H / 2), "pi"))
LABELS.append(("Pi 40-pin header", (PI_HDR["x"] + 40, PI_HDR["y"] + 2.5, Zt + 8.5), "pi"))
# PI-LINK cable: J6 front -> loop up beside the board edge -> Dupont 2x5 on Pi pins 1-10
j6 = part("J6")
pts = [(j6["x"] + 10, BOARD_W + 0.2, T + 3.5), (j6["x"] + 8, BOARD_W + 5.0, T + 6), (60, BOARD_W + 7.5, ZP - 2),
       (46, BOARD_W + 5.0, Zt + 12), (PI_HDR["x"] + 6.35, PI_HDR["y"] + 2.55, Zt + 13.0)]
try:
    path = cq.Workplane("XY").spline(pts, includeCurrent=False)
    prof = cq.Workplane(cq.Plane(origin=pts[0], xDir=(1, 0, 0), normal=(0, 1, 0))).rect(4.5, 1.6)
    cable = prof.sweep(path, transition="round").val()
    add("PI-LINK cable", cable, "#7d4fd6", "pi")
except Exception as e:
    print("cable sweep skipped:", e)
add("Dupont 2x5", box(PI_HDR["x"], PI_HDR["y"] - 0.2, Zt + 2.5, 12.9, 5.5, 10.5), "#151515", "pi")
LABELS.append(("PI-LINK cable (5V, GND, UART, RST)", pts[2], "pi"))

for txt, p3, g in list(LABELS):
    if g == "board" and txt.split()[0] in ("J1", "U5", "J10", "D1-D6", "SW1", "U3", "C1"):
        LABELS.append((txt, p3, "key"))

# ------------------------------------------------------------------ STEP export
def export_step(groups, path, silk=True):
    asm = cq.Assembly(name="HAEBOT_HandController_v1")
    for i, (n, s, c, g) in enumerate(ITEMS):
        if g in groups and (silk or not n.startswith("silk:") or n == "silk:logo"):
            asm.add(s, name=f"{i:03d}_{n}".replace(" ", "_").replace(":", "_")[:60], color=cq.Color(*c, 1.0))
    asm.save(path, "STEP")

# ------------------------------------------------------------------ renderer
def tess(shape, tol=0.08):
    v, t = shape.tessellate(tol, 0.3)
    return np.array([(p.x, p.y, p.z) for p in v], float), np.array(t, int)

def render(groups, view, up, path, W=2200, H=1450, title="", ss=2, label_groups=None, ortho_top=False, subtitle=""):
    view = np.array(view, float); view /= np.linalg.norm(view)
    upv = np.array(up, float)
    r = np.cross(upv, view); r /= np.linalg.norm(r); u = np.cross(view, r)
    tris, cols, oid = [], [], []
    for i, (n, s, c, g) in enumerate(ITEMS):
        if g not in groups: continue
        v, t = tess(s)
        if len(t) == 0: continue
        tris.append(v[t]); cols.append(np.tile(c, (len(t), 1))); oid.append(np.full(len(t), i))
    tris = np.concatenate(tris); cols = np.concatenate(cols); oid = np.concatenate(oid)
    nrm = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(nrm, axis=1); good = ln > 1e-12
    tris, cols, oid, nrm = tris[good], cols[good], oid[good], nrm[good] / ln[good, None]
    facing = nrm @ view
    keep = facing > 1e-6
    tris, cols, oid, nrm = tris[keep], cols[keep], oid[keep], nrm[keep]
    L1 = np.array([0.35, -0.45, 0.82]); L1 /= np.linalg.norm(L1)
    L2 = np.array([-0.6, 0.5, 0.4]); L2 /= np.linalg.norm(L2)
    dif = np.clip(nrm @ L1, 0, 1) * 0.62 + np.clip(nrm @ L2, 0, 1) * 0.18
    hv = L1 + view; hv /= np.linalg.norm(hv)
    spec = np.clip(nrm @ hv, 0, 1) ** 40 * 0.25
    shade = np.clip(cols * (0.30 + dif)[:, None] + spec[:, None], 0, 1)
    # projection
    P2 = np.stack([tris @ r, tris @ u, tris @ view], -1)        # (n,3,3) screen x,y,depth
    allp = P2.reshape(-1, 3)
    Ws, Hs = W * ss, H * ss
    mx0, mx1 = allp[:, 0].min(), allp[:, 0].max(); my0, my1 = allp[:, 1].min(), allp[:, 1].max()
    margin = 0.19 if label_groups is not None else 0.06
    sc = min(Ws * (1 - 2 * margin) / (mx1 - mx0), Hs * 0.80 / (my1 - my0))
    ox = Ws / 2 - sc * (mx0 + mx1) / 2; oy = Hs * 0.52 + sc * (my0 + my1) / 2
    def to_px(p):
        return np.stack([ox + sc * p[..., 0], oy - sc * p[..., 1]], -1)
    S = to_px(P2[..., :2]); D = P2[..., 2]
    zbuf = np.full((Hs, Ws), -1e9); img = np.zeros((Hs, Ws, 3)); ids = np.full((Hs, Ws), -1)
    for k in range(len(S)):
        (x0, y0), (x1, y1), (x2, y2) = S[k]
        xmin = max(int(math.floor(min(x0, x1, x2))), 0); xmax = min(int(math.ceil(max(x0, x1, x2))), Ws - 1)
        ymin = max(int(math.floor(min(y0, y1, y2))), 0); ymax = min(int(math.ceil(max(y0, y1, y2))), Hs - 1)
        if xmax < xmin or ymax < ymin: continue
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9: continue
        xs, ys = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
        a = ((y1 - y2) * (xs - x2) + (x2 - x1) * (ys - y2)) / den
        b = ((y2 - y0) * (xs - x2) + (x0 - x2) * (ys - y2)) / den
        c = 1 - a - b
        m = (a >= -1e-6) & (b >= -1e-6) & (c >= -1e-6)
        if not m.any(): continue
        z = a * D[k, 0] + b * D[k, 1] + c * D[k, 2]
        sub = zbuf[ymin:ymax + 1, xmin:xmax + 1]
        upd = m & (z > sub)
        sub[upd] = z[upd]
        img[ymin:ymax + 1, xmin:xmax + 1][upd] = shade[k]
        ids[ymin:ymax + 1, xmin:xmax + 1][upd] = oid[k]
    bgm = ids < 0
    # background gradient
    gy = np.linspace(0, 1, Hs)[:, None, None]
    bg = (1 - gy) * np.array([0.97, 0.975, 0.985]) + gy * np.array([0.86, 0.88, 0.91])
    img = np.where(bgm[..., None], np.broadcast_to(bg, img.shape), img)
    # outline: object-id edges + depth jumps
    e = np.zeros((Hs, Ws), bool)
    e[:, 1:] |= ids[:, 1:] != ids[:, :-1]; e[1:, :] |= ids[1:, :] != ids[:-1, :]
    zz = np.where(bgm, zbuf.min(), zbuf)
    e[:, 1:] |= np.abs(zz[:, 1:] - zz[:, :-1]) > 0.6 / sc * 0 + 0.6
    e[1:, :] |= np.abs(zz[1:, :] - zz[:-1, :]) > 0.6
    silk = np.array([n.startswith("silk:") or n == "pin" for (n, s, c, g) in ITEMS])
    ee = e & ~(np.where(ids >= 0, silk[np.clip(ids, 0, None)], False))
    img[ee] = img[ee] * 0.35
    # downsample
    img = img.reshape(H, ss, W, ss, 3).mean((1, 3))
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    ax.text(W / 2, 46, title, ha="center", va="center", fontsize=22, weight="bold", color="#1f2328")
    if subtitle: ax.text(W / 2, 86, subtitle, ha="center", va="center", fontsize=12.5, color="#57606a")
    ax.text(W - 20, H - 18, "Jinie EduTech  ·  HAEBOT Hand Controller v1.0  ·  concept mock-up, not a routed PCB", ha="right", va="bottom", fontsize=10, color="#6e7781")
    if label_groups:
        items = []
        for (txt, p3, g) in LABELS:
            if g not in label_groups: continue
            p3 = np.array(p3, float)
            sp = to_px(np.array([p3 @ r, p3 @ u])) / ss
            items.append((txt, sp))
        cx = W / 2
        left = sorted([it for it in items if it[1][0] < cx], key=lambda t: t[1][1])
        right = sorted([it for it in items if it[1][0] >= cx], key=lambda t: t[1][1])
        for side, lst in (("L", left), ("R", right)):
            n = len(lst)
            if n == 0: continue
            gap, top, bot = 40.0, 130.0, H - 60.0
            ys = np.array([sp[1] for _, sp in lst], float)
            ys = np.clip(ys, top, bot)
            for _ in range(200):                      # relax: enforce min gap, stay in range
                for i in range(1, n):
                    if ys[i] - ys[i - 1] < gap:
                        d = (gap - (ys[i] - ys[i - 1])) / 2
                        ys[i - 1] -= d; ys[i] += d
                ys = np.clip(ys, top, bot)
                if n * gap > bot - top: break
            for (txt, sp), yl in zip(lst, ys):
                xl = 28 if side == "L" else W - 28
                ax.annotate(txt, xy=(sp[0], sp[1]), xytext=(xl, yl), ha="left" if side == "L" else "right", va="center",
                            fontsize=12, color="#1f2328",
                            bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="#8c959f", lw=0.8, alpha=0.95),
                            arrowprops=dict(arrowstyle="-", color="#57606a", lw=0.9, shrinkA=0, shrinkB=0))
                ax.plot([sp[0]], [sp[1]], "o", ms=4, color="#cf222e")
    fig.savefig(path, dpi=100); plt.close(fig)
    print("wrote", path)

if __name__ == "__main__":
    os.makedirs(REND, exist_ok=True)
    import zipfile, tempfile
    # light raw STEP (no silkscreen text) + zip with the full-detail versions (repo keeps huge STEPs zipped)
    export_step({"board"}, os.path.join(ELEC, "HAEBOT_HandController_v1_concept.step"), silk=False)
    tmp = tempfile.mkdtemp()
    full = [("HAEBOT_HandController_v1_concept_full_silk.step", {"board"}),
            ("HAEBOT_HandController_v1_concept_with_Pi5.step", {"board", "pi"})]
    with zipfile.ZipFile(os.path.join(ELEC, "HAEBOT_HandController_v1_concept_STEP_full.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for fn, g in full:
            export_step(g, os.path.join(tmp, fn)); z.write(os.path.join(tmp, fn), fn)
    print("STEP ok")
    which = sys.argv[1:] or ["top", "iso_pi", "iso"]
    if "top" in which:
        render({"board"}, (0, 0, 1), (0, 1, 0), os.path.join(REND, "3d_top.png"), W=2400, H=1450, label_groups={"board"},
               title="HAEBOT Hand Controller v1.0 — 3D top view (Pi removed)", subtitle="115 × 56 mm · black solder mask, white silkscreen · Pi 5 mounts on the four gold holes")
    if "iso_pi" in which:
        render({"board", "pi"}, (-0.62, -0.95, 0.85), (0, 0, 1), os.path.join(REND, "3d_iso_with_pi.png"), W=2400, H=1550, label_groups={"pi", "key"},
               title="HAEBOT Hand Controller v1.0 + Raspberry Pi 5 — stacked", subtitle="Pi 5 on M2.5 × 18 mm standoffs · open zone (left) keeps servo headers, A4988 and power entry accessible")
    if "iso" in which:
        render({"board"}, (-0.62, -0.95, 0.85), (0, 0, 1), os.path.join(REND, "3d_iso_no_pi.png"), W=2400, H=1550, label_groups={"board"},
               title="HAEBOT Hand Controller v1.0 — isometric (Pi removed)", subtitle="all parts under the Pi ≤ 12 mm tall · tall / hot / hands-on parts in the open zone")
