"""
HAEBOT Hand - PROTOTYPE A (P1) FOREARM: official InMoov right forearm (robpart2V4..5V4) scaled 1.28x to match the P1 hand,
with the controller board (100 x 60) inside, just below the wrist. Fixed wrist. Concept CAD, not printed.

InMoov forearm files: cad/original/inmoov_forearm/ (SHA-256 checked). They come in PRINT orientation; this script assembles them:
  wrist half  = robpart2V4 + robpart3V4 tilted 1.0 deg about x, moved y -40.47 / z +1.0  (fitted: seam gap <= 1.1 mm all along, overlap < 20 mm3)
  elbow half  = robpart5V4 + robpart4V4 moved -42.5 mm in y
  forearm     = elbow half z 0..105.6, wrist half on top (z + 105.6); wrist end at the top. Then x SCALE.
Modifications (only):
  - 4 x M3 radial screw holes in the wrist-half shells for the wrist block
  - inner ribs removed only where the board + tray + cables need room (checked by collision)
New parts (small): 06 wrist block (plug in the forearm top + tongue for the hand's wrist pin, M10), 07 board tray (hangs from the block).
Frame (arm): z along the arm (elbow z = 0, wrist up), x = across (same as the hand's x), y = front/back.
Run: python dona_univ_robot_hand_2026-11-17_Sanjev_A_forearm_build.py   (numpy trimesh manifold3d shapely)
"""
import hashlib, json, math, os, sys
sys.dont_write_bytecode = True
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as _iu
_ps = _iu.spec_from_file_location("p1paths", os.path.join(HERE, "dona_univ_robot_hand_2026-11-17_Sanjev_A_paths.py"))
paths = _iu.module_from_spec(_ps); _ps.loader.exec_module(paths); F = paths.F
ORIG = paths.ORIG
P = "dona_univ_robot_hand_2026-11-17_Sanjev_A_"
FA = os.path.join(ORIG, "inmoov_forearm")
SRC = {"robpart2V4": "79f1370883eec88174f94559b28aef12e692a1d613b8ac207e80ff8390f8bc77",
       "robpart3V4": "70fc6d585fa35552538235580b596eed4db61e402ca66f241bab9f55765e98ad",
       "robpart4V4": "ead9ad6a33158e0a358b36bb5e2be1e4d4cb09632009a63da26a03838030e49a",
       "robpart5V4": "a0730c35e383cf99f3fb8616a755ceefbefb49f158604e0531666f6d9dca3798"}

# ---------------------------------------------------------------- PARAMETERS
SCALE = 1.28                       # hand scale (P1 hand = InMoov i2 x1.28)
# Forearm = stock InMoov shape scaled EVENLY by FA_SCALE (user 2026-11-17: slim like the reference, keep the InMoov cone;
# the hand may overhang the wrist a little, as on the stock InMoov). Override for comparisons: env P1_FA_SCALE.
FA_SCALE = float(os.environ.get("P1_FA_SCALE", "1.0"))
# length stretch per half (user 2026-11-17: arm a bit longer, and the lower/elbow half longer so it looks in proportion)
FA_LEN_ELBOW = float(os.environ.get("P1_FA_LEN_ELBOW", "1.35"))   # robpart4/5 (elbow half)
FA_LEN_WRIST = float(os.environ.get("P1_FA_LEN_WRIST", "1.10"))   # robpart2/3 (wrist half, the cone)
S_ELBOW, S_WRIST, LEN_SCALE = FA_SCALE, FA_SCALE, FA_SCALE         # (set S_ELBOW != S_WRIST for a taper)
BOARD_IN_ARM = False               # user 2026-11-17: the 100 x 60 board moves to the base -> no tray, no shell cuts
WARP_MAX_EDGE = 6.0                # subdivide shells before warping so curved InMoov surfaces follow the taper (mm)
RIB_LIMIT_CM3 = 2.0                # max shell material the board/tray may remove (only inner ribs) - else move the board lower
ASM_3 = (1.0, -40.47, 1.0)         # robpart3: tilt about x (deg), dy, dz  (fitted so the seam closes)
DY_4 = -42.5                       # robpart4: dy (seam closes along the length; the top-end side openings are InMoov features)
ELBOW_LEN = 105.6                  # robpart4/5 length (stock)
# hand wrist interface: MEASURED on the P1 palm frame (..._A_01_palm_frame.stl = i2_WristLargeV2 x1.28), hand frame
HAND_PRONG = dict(gap=41.84, centre_x=-17.41, z0=0.0, z1=25.27, pin_y=106.12, pin_z=13.96, root_y=95.36, hole_d=10.2)
HAND_GAP = HAND_PRONG["gap"]
TONGUE_CLR = 0.5                   # per side in the prong gap and inside the prong height
TONGUE_BORE = 10.5                 # M10 bolt (hand hole ~10.2-11.5)
PIN_ABOVE_TOP = 18.0               # wrist pin centre above the forearm top
PIN_TO_ROOT = HAND_PRONG["pin_y"] - HAND_PRONG["root_y"]   # 10.76
TONGUE_END_R = PIN_TO_ROOT - 1.0     # rounded tongue end stays 1 mm short of the palm
# board (user: 100 x 60, in the forearm just below the wrist)
PCB = (60.0, 100.0, 1.6)           # x (across) , z (along the arm), thickness
PCB_COMP_H, PCB_UNDER = 20.0, 5.0  # component height above the board, standoff height below - ESTIMATE
PCB_HOLES_INSET = 3.5              # mounting holes 3.5 mm from the edges (TBD: set to the real board)
TRAY_T, TRAY_MARGIN = 3.0, 3.0
PLUG_H = 14.0                      # wrist block plug depth inside the forearm top
CLR = 0.4
M3_CLR, M3_INSERT = 3.4, 4.0

# ---------------------------------------------------------------- helpers
def safe_export(mesh, path):
    """export STL and make sure the saved file reloads as a closed volume (manifold re-merge after float32 rounding)."""
    import manifold3d as mf
    m = mesh.copy(); m.merge_vertices()
    M = mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))
    o = M.to_mesh(); out = trimesh.Trimesh(o.vert_properties[:, :3], o.tri_verts)
    out.export(path)
    chk = trimesh.load(path)
    assert chk.is_watertight and chk.is_volume, f"export not watertight: {path}"
    return out

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def U(ms): return trimesh.boolean.union(ms, engine="manifold")
def D(a, bs):
    bs = list(bs)
    return trimesh.boolean.difference([a] + bs, engine="manifold") if bs else a
def I(a, b): return trimesh.boolean.intersection([a, b], engine="manifold")
def box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0]); m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); return m
def cyl(p0, p1, d): return trimesh.creation.cylinder(radius=d / 2, segment=[p0, p1], sections=48)
def load(n):
    p = os.path.join(FA, n + ".stl"); assert sha(p) == SRC[n], f"{n}: checksum mismatch"; return trimesh.load(p)

def asm_matrix(name):
    """4x4: exported print-orientation STL -> assembled arm frame (written by this script into the forearm report)."""
    rep = json.load(open(F("forearm_report.json")))
    return np.array(rep["print_to_assembly"][name])

def warp(m, centre, L0):
    """taper: xy scaled about the wrist axis by s(z) = S_ELBOW..S_WRIST, z scaled by LEN_SCALE."""
    v = m.vertices.copy()
    t = np.clip(v[:, 2] / L0, 0, 1)
    s = S_ELBOW + (S_WRIST - S_ELBOW) * t
    v[:, 0] = centre[0] + (v[:, 0] - centre[0]) * s
    v[:, 1] = centre[1] + (v[:, 1] - centre[1]) * s
    zs = ELBOW_LEN                                                      # seam between the two halves (stock)
    z = v[:, 2]
    v[:, 2] = LEN_SCALE * np.where(z <= zs, z * FA_LEN_ELBOW, zs * FA_LEN_ELBOW + (z - zs) * FA_LEN_WRIST)
    return trimesh.Trimesh(v, m.faces.copy(), process=False)

def print_transform(name, m):
    """4x4 assembled -> print orientation: undo the robpart3 tilt, stand on z = 0, centre x/y."""
    T = np.eye(4)
    if name.endswith("robpart3"):
        T = trimesh.transformations.rotation_matrix(-math.radians(ASM_3[0]), [1, 0, 0])
    b = trimesh.transform_points(m.vertices, T)
    lo, hi = b.min(0), b.max(0)
    return trimesh.transformations.translation_matrix([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]]) @ T

def shells():
    """the 4 InMoov shells, assembled + scaled, as a dict"""
    r2, r3, r4, r5 = (load(f"robpart{i}V4") for i in (2, 3, 4, 5))
    T3 = trimesh.transformations.rotation_matrix(math.radians(ASM_3[0]), [1, 0, 0]); T3[:3, 3] = [0, ASM_3[1], ASM_3[2]]
    r3.apply_transform(T3); r4.apply_translation([0, DY_4, 0])
    for m in (r2, r3): m.apply_translation([0, 0, ELBOW_LEN])
    out = {"05a_forearm_robpart2": r2, "05b_forearm_robpart3": r3, "05c_forearm_robpart4": r4, "05d_forearm_robpart5": r5}
    # taper axis = centre of the stock wrist opening; L0 = stock assembled length
    L0 = max(m.bounds[1][2] for m in (r2, r3))
    top = section_union([r2, r3], min(r2.bounds[1][2], r3.bounds[1][2]) - 3.0).bounds
    centre = ((top[0] + top[2]) / 2, (top[1] + top[3]) / 2)
    for k, m in out.items():
        if S_ELBOW != S_WRIST:
            v, f = trimesh.remesh.subdivide_to_size(m.vertices, m.faces, max_edge=WARP_MAX_EDGE); m = trimesh.Trimesh(v, f)
        out[k] = warp(m, centre, L0)
        assert out[k].is_volume, k
    return out

def section_union(meshes, z):
    polys = []
    for m in meshes:
        s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if s is None: continue
        polys += [Polygon(e[:, :2]).buffer(0) for e in s.discrete if len(e) > 3]
    return unary_union(polys)

def inner_region(meshes, zs):
    """free inside region common to all sections zs (largest hole of the ring)"""
    reg = None
    for z in zs:
        u = section_union(meshes, z)
        free = u.convex_hull.difference(u.buffer(0.01))     # works for the 2 half-shells even if a seam is open ~1 mm
        hole = max(getattr(free, "geoms", [free]), key=lambda p: p.area)
        reg = hole if reg is None else reg.intersection(hole)
    return reg

def build():
    S = shells()
    wrist = [S["05a_forearm_robpart2"], S["05b_forearm_robpart3"]]
    top = min(m.bounds[1][2] for m in wrist)     # both shells present below this height
    # ---------------- wrist block: plug + tongue
    plug_reg = inner_region(wrist, np.linspace(top - PLUG_H, top - 0.3, 6)).buffer(-CLR)
    c = plug_reg.envelope.centroid; cx, cy = c.x, c.y              # wrist axis = centre of the forearm opening
    plug = trimesh.creation.extrude_polygon(plug_reg, PLUG_H); plug.apply_translation([0, 0, top - PLUG_H])
    cap = trimesh.creation.extrude_polygon(plug_reg.buffer(-1.0), 4.0); cap.apply_translation([0, 0, top])   # stays inside the rim outline
    pin_z = top + PIN_ABOVE_TOP
    tw = HAND_GAP - 2 * TONGUE_CLR
    # tongue depth (arm y) = prong height (hand z) minus clearance; arm y = hand z - pin_z + cy
    ty0 = cy + (HAND_PRONG["z0"] - HAND_PRONG["pin_z"]) + TONGUE_CLR
    ty1 = cy + (HAND_PRONG["z1"] - HAND_PRONG["pin_z"]) - TONGUE_CLR
    tongue = box(cx - tw / 2, cx + tw / 2, ty0, ty1, top, pin_z)
    tongue = U([tongue, I(cyl([cx - tw / 2, cy, pin_z], [cx + tw / 2, cy, pin_z], 2 * TONGUE_END_R),
                          box(cx - tw, cx + tw, ty0, ty1, pin_z - 1, pin_z + TONGUE_END_R + 1))])
    block = U([plug, cap, tongue])
    block = D(block, [cyl([cx - tw, cy, pin_z], [cx + tw, cy, pin_z], TONGUE_BORE)])
    # cable slots through the block, in front of and behind the tongue (servo cables from the palm come down here)
    # slot positions avoid the two InMoov inner ribs of robpart2 (x -8..-3 and 11..16 at the back)
    holes = [box(cx - 20.0, cx - 1.0, ty1 + 1.5, ty1 + 11.0, top - PLUG_H - 1, top + 5),
             box(cx - 14.0, cx + 14.0, ty0 - 10.5, ty0 - 1.5, top - PLUG_H - 1, top + 5)]
    # smaller fallbacks for a slim forearm: STS3215 is a serial bus, so ONE 3-wire cable (+ spare) is enough
    holes += [box(cx - 8.0, cx + 8.0, ty1 + 1.0, ty1 + 6.0, top - PLUG_H - 1, top + 5),
              box(cx - 8.0, cx + 8.0, ty0 - 6.0, ty0 - 1.0, top - PLUG_H - 1, top + 5),
              box(cx - tw / 2 - 6.5, cx - tw / 2 - 1.0, cy - 7.0, cy + 7.0, top - PLUG_H - 1, top + 5),     # beside the tongue
              box(cx + tw / 2 + 1.0, cx + tw / 2 + 6.5, cy - 7.0, cy + 7.0, top - PLUG_H - 1, top + 5)]
    holes = [h for h in holes if plug_reg.buffer(-1.2).contains(Polygon([(h.bounds[0][0], h.bounds[0][1]), (h.bounds[1][0], h.bounds[0][1]), (h.bounds[1][0], h.bounds[1][1]), (h.bounds[0][0], h.bounds[1][1])]))]
    big = [h for h in holes if h.extents[0] > 17]
    holes = big if big else holes[:4]
    if not holes:                       # slim forearm: use the free plug area around the tongue (3 mm wall kept)
        free = plug_reg.buffer(-3.0).difference(sbox(cx - tw / 2, ty0, cx + tw / 2, ty1).buffer(1.5))
        for g in sorted(getattr(free, "geoms", [free]), key=lambda g: -g.area)[:2]:
            if g.area > 30:
                pr = trimesh.creation.extrude_polygon(g, PLUG_H + 6); pr.apply_translation([0, 0, top - PLUG_H - 1]); holes.append(pr)
    assert holes, "no room for cable slots in the wrist block"
    CABLE_SLOTS = len(holes)
    block = D(block, holes)
    # radial screws: 4 x M3 through the shells into heat-set inserts in the plug
    zc = top - PLUG_H / 2
    bx0, by0, bx1, by1 = plug_reg.bounds
    screw_axes = [((bx0 - 8, cy, zc), (bx0 + 7, cy, zc)), ((bx1 + 8, cy, zc), (bx1 - 7, cy, zc)),
                  ((cx, by0 - 8, zc), (cx, by0 + 7, zc)), ((cx, by1 + 8, zc), (cx, by1 - 7, zc))]
    inserts = [cyl(a, b, M3_INSERT) for a, b in screw_axes]
    clear = [cyl(a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, zc), M3_CLR) for a, b in screw_axes]
    block = D(block, inserts)
    if not BOARD_IN_ARM:
        mod = {n: D(m, clear) for n, m in S.items()}
        meta = dict(shell_cut_cm3=0.0, cable_slots=CABLE_SLOTS, top=top, cx=cx, cy=cy, pin_z=pin_z, tongue_w=tw, board_y=None, tray_z=None, plug_bounds=plug_reg.bounds)
        return mod, block, None, None, meta, S
    # ---------------- board tray hanging below the plug; board plane = xz, components toward +y
    board_y = cy - 6.0                          # board front face plane
    tz1 = top - PLUG_H; tz0 = tz1 - (PCB[1] + 2 * TRAY_MARGIN)
    tray = box(cx - PCB[0] / 2 - TRAY_MARGIN, cx + PCB[0] / 2 + TRAY_MARGIN, board_y - PCB_UNDER - TRAY_T, board_y - PCB_UNDER, tz0, tz1 + 0.01)
    holes_xz = [(cx + sx * (PCB[0] / 2 - PCB_HOLES_INSET), tz0 + TRAY_MARGIN + PCB[1] / 2 + sz * (PCB[1] / 2 - PCB_HOLES_INSET)) for sx in (-1, 1) for sz in (-1, 1)]
    stand = [cyl([x, board_y - PCB_UNDER - 0.01, z], [x, board_y, z], 6.5) for x, z in holes_xz]
    tray = U([tray] + stand)
    tray = D(tray, [cyl([x, board_y - PCB_UNDER - TRAY_T - 1, z], [x, board_y + 1, z], 2.6) for x, z in holes_xz])   # M3 self-tap / heat-set 2.6
    tray = D(tray, [box(cx - 15, cx + 15, board_y - 20, board_y + 1, tz0 + 25, tz1 - 25)])                          # cable window
    # tray hangs on the plug: tongue on the tray top goes into a slot in the plug + 2 M3
    hook = box(cx - 20, cx + 20, board_y - PCB_UNDER - TRAY_T, board_y - PCB_UNDER, tz1 - 0.01, tz1 + PLUG_H - 4)
    tray = U([tray, hook])
    block = D(block, [box(cx - 20.3, cx + 20.3, board_y - PCB_UNDER - TRAY_T - 0.3, board_y - PCB_UNDER + 0.3, tz1 - 1, tz1 + PLUG_H - 3.7)])
    for sx in (-12, 12):
        a = (cx + sx, board_y - PCB_UNDER - TRAY_T - 12, tz1 + PLUG_H / 2); b = (cx + sx, board_y + 8, tz1 + PLUG_H / 2)
        tray = D(tray, [cyl(a, b, M3_CLR)]); block = D(block, [cyl(a, b, M3_INSERT)])
    board_env = box(cx - PCB[0] / 2, cx + PCB[0] / 2, board_y - PCB_UNDER, board_y + PCB[2] + PCB_COMP_H, tz0 + TRAY_MARGIN, tz0 + TRAY_MARGIN + PCB[1])
    # ---------------- modify shells: screw holes + rib clearance for tray/board/hook (only where they collide)
    keep_out = U([board_env, tray.convex_hull])
    hit_total = sum(float(I(m, keep_out).volume) for m in S.values()) / 1000.0
    assert hit_total <= RIB_LIMIT_CM3, f"board/tray would cut {hit_total:.1f} cm3 of shell (> rib limit) - move the board lower"
    mod = {}
    for n, m in S.items():
        cuts = [c for c in clear]
        hit = I(m, keep_out)
        if hit.volume > 0.01: cuts.append(keep_out)
        mod[n] = D(m, cuts)
    meta = dict(shell_cut_cm3=round(hit_total, 2), cable_slots=CABLE_SLOTS, top=top, cx=cx, cy=cy, pin_z=pin_z, tongue_w=tw, board_y=board_y, tray_z=[tz0, tz1], plug_bounds=plug_reg.bounds)
    return mod, block, tray, board_env, meta, S

if __name__ == "__main__":
    mod, block, tray, board_env, meta, raw = build()
    p2a = {}
    for n in list(mod):                                   # export in PRINT orientation (standing, z = 0); assembly scripts re-place them
        T = print_transform(n, mod[n]); pm = mod[n].copy(); pm.apply_transform(T)
        safe_export(pm, F(n + ".stl")); p2a[n] = np.linalg.inv(T).tolist()
    block = safe_export(block, F("06_wrist_block.stl"))
    if BOARD_IN_ARM:
        tray = safe_export(tray, F("07_board_tray.stl")); board_env.export(F("ref_board_100x60.stl"))
    # checks
    shells_all = trimesh.util.concatenate(list(mod.values()))
    def ov(a, b):
        if b is None or a is None: return None
        return round(sum(float(I(x, b).volume) for x in (a if isinstance(a, list) else [a])), 2)
    rib_removed = {n: round(float(raw[n].volume - mod[n].volume) / 1000, 2) for n in mod}
    bb = shells_all.bounds
    sec_mid = section_union(list(mod.values())[:2], meta["top"] - 60)
    elbow_band = [section_union([mod["05c_forearm_robpart4"], mod["05d_forearm_robpart5"]], z).bounds for z in (2.0, 15.0, 30.0)]
    rep = dict(status="CONCEPT - P1 forearm, not printed", scale=SCALE,
               forearm_scale=dict(width=FA_SCALE, length_elbow_half=FA_LEN_ELBOW, length_wrist_half=FA_LEN_WRIST),
               board_tray_cuts_shell_cm3=meta["shell_cut_cm3"], print_to_assembly=p2a, sources={k: "sha256 OK" for k in SRC},
               forearm_bbox_mm=[round(float(v), 1) for v in (bb[1] - bb[0])], forearm_length=round(meta["top"], 1),
               wrist=dict(type="fixed (tongue for the hand's M10 wrist pin)", pin_z=round(meta["pin_z"], 1), pin_xy=[round(meta["cx"], 1), round(meta["cy"], 1)], tongue_width=round(meta["tongue_w"], 2), hand_prong_gap=round(HAND_GAP, 2), bore=TONGUE_BORE),
               board="in the BASE (see report_base)" if not BOARD_IN_ARM else dict(size=PCB, plane="xz (stands along the arm)", component_side="+y", height_reserved=PCB_COMP_H, tray_z=[round(v, 1) for v in meta["tray_z"]], holes="4 x M3 at 3.5 mm from the edges (TBD)"),
               wrist_block_cable_slots=meta["cable_slots"],
               overlaps_mm3=dict(board_vs_shells=ov(list(mod.values()), board_env), tray_vs_shells=ov(list(mod.values()), tray), block_vs_shells=ov(list(mod.values()), block), block_vs_tray=ov(block, tray)),
               inner_ribs_removed_cm3=rib_removed,
               elbow_end_outer_bounds_for_base_socket=[[round(v, 1) for v in b] for b in elbow_band],
               watertight={n: bool(m.is_watertight) for n, m in list(mod.items()) + [("06_wrist_block", block)] + ([("07_board_tray", tray)] if tray is not None else [])})
    json.dump(rep, open(F("forearm_report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))
