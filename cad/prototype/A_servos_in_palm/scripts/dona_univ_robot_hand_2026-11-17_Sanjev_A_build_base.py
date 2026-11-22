"""
HAEBOT Hand - PROTOTYPE A (P1) BASE: power base under the InMoov forearm.
Concept CAD, not printed. Units mm. CadQuery 2.x.

Holds (user decisions 2026-11-17): Mean Well LRS-350-12 (12 V 29 A), PC-style mains inlet (IEC C14 with fuse + switch),
panel USB mini-B, mains / low-voltage partition, vents, cable strain relief, and a socket for the lower end of the
stock-size InMoov forearm. The controller board (100 x 60) sits in the base (user 2026-11-17), flat on 4 standoffs in
front of the PSU; only the servo bus cable (STS3215 = serial bus, 3 wires) goes up through the lid hole into the arm.

Frame: x = width (left -> right), y = depth (front y = 0 -> back), z up, z = 0 = table.
Run: python dona_univ_robot_hand_2026-11-17_Sanjev_A_base_build.py   (cadquery)
"""
import json, os, sys
sys.dont_write_bytecode = True
import numpy as np
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util as _iu
_ps = _iu.spec_from_file_location("p1paths", os.path.join(HERE, "dona_univ_robot_hand_2026-11-17_Sanjev_A_paths.py"))
paths = _iu.module_from_spec(_ps); _ps.loader.exec_module(paths); F = paths.F
P = "dona_univ_robot_hand_2026-11-17_Sanjev_A_"

# ---------------------------------------------------------------- PARAMETERS
# LAYOUT v2 (user 2026-11-17: smaller base, board beside the inlet): SMPS along the back, board front-left,
# mains corner front-right with the user's screw-mount inlet in the RIGHT side wall. Width/depth follow from the parts.
H = 66.0                             # pan outer height (inlet flange ~58 tall + floor)
WALL, FLOOR, R_OUT = 3.0, 3.0, 10.0
LID_T = 4.0
# Mean Well LRS-350-12 (datasheet: 215 x 115 x 30 mm, built-in fan, 4 x M4 side holes)
PSU = (215.0, 115.0, 30.0)
PSU_CLR, PSU_STANDOFF = 0.8, 5.0     # air gap under the PSU
TERM_ROOM = 14.0                     # wire room at the PSU terminal end (+x)
BACK_ROOM = 13.0                     # behind the PSU: rear strap bosses
FRONT_STRIP = 83.0                   # front strip depth (inside, y) for the board / inlet zone
PSU_X0 = WALL + 3.0
W = PSU_X0 + PSU[0] + TERM_ROOM + WALL
Dp = WALL + FRONT_STRIP + PSU[1] + BACK_ROOM + WALL
PSU_Y1 = Dp - WALL - BACK_ROOM       # PSU at the back; terminal block at its +x end (VERIFY on the real unit)
# user's inlet: makePCB P087, IEC C14 + fuse + lit rocker, SCREW mount (hex flange, 2 x M3). Sizes = typical for this
# generic 3-in-1 module - ESTIMATE, MEASURE THE REAL PART: body 48 x 27.5 (long axis along y), holes 40 mm apart (along z)
IEC_BODY = (48.0, 27.5)
IEC_CLR = 0.4                        # wiggle room per side in the cutout
IEC_CUT = (IEC_BODY[0] + 2 * IEC_CLR, IEC_BODY[1] + 2 * IEC_CLR)
IEC_HOLE_PITCH, IEC_FLANGE = 40.0, (50.0, 58.0)      # flange y x z (estimate)
IEC_BODY_DEPTH = 34.0 + 15.0         # body behind the panel + 4.8 mm faston terminals + wire bend (estimate)
# USB mini-B panel-mount extension (generic: body hole + 2 x M3 at 28 mm) - set to the bought part
USB_HOLE, USB_SCREW_PITCH = (14.0, 9.0), 28.0
# socket for the elbow end of the InMoov forearm (robpart4V4/5V4, assembled + scaled by ..._A_build_forearm.py):
# the socket follows the real outline (union of the forearm sections z 0..SOCK_H) + SOCK_CLR
SOCK_CLR = 1.0                        # per side; take up with tape / TPU shims
SOCK_WALL, SOCK_H = 5.0, 20.0        # lower collar shows more of the arm
SOCK_C = (W / 2, Dp / 2 + 6.0)        # where the forearm outline centre sits on the lid
CABLE_HOLE = (40.0, 20.0)             # servo bus cable (+ spare) up into the forearm
M3_INSERT_D, M3_CLR, BOSS_D = 4.0, 3.4, 10.0
FOOT_D, FOOT_RECESS = 20.0, 1.5
# controller board (100 x 60) in the base, flat, components up - holes TBD (set to the real board)
PCB = (100.0, 60.0, 1.6)
PCB_X0, PCB_Y0 = WALL + 12.0, WALL + 9.0  # front-left, beside the mains corner (inlet)
PCB_STANDOFF, PCB_HOLE_INSET, PCB_COMP_H = 8.0, 3.5, 20.0

# derived
PSU_LO = (PSU_X0, PSU_Y1 - PSU[1], FLOOR + PSU_STANDOFF)
PSU_HI = (PSU_X0 + PSU[0], PSU_Y1, FLOOR + PSU_STANDOFF + PSU[2])
PART_X = W - WALL - IEC_BODY_DEPTH - 6.0          # mains partition (front-right corner)
MAINS = (PART_X + 2.0, W - WALL, WALL, PSU_LO[1] - 1.0)   # mains zone x0,x1,y0,y1 (+ the wire channel at the PSU terminal end)
IEC_C = (WALL + 6.0 + IEC_FLANGE[0] / 2, FLOOR + 4.0 + IEC_FLANGE[1] / 2)   # (y, z) centre on the RIGHT wall
USB_X = (PCB_X0 + PCB[0] + PART_X) / 2                                       # front wall, between board and mains zone
# lid-screw bosses: centres 4 mm from the inner wall so the D10 boss merges into the wall (no tangent faces)
BOSSES = [(WALL + 6, WALL + 6), (PART_X - 6, WALL + 4), (W - WALL - 6, PSU_LO[1] - 7),
          (WALL + 6, Dp - WALL - 6), (W / 2, Dp - WALL - 4), (W - WALL - 6, Dp - WALL - 6)]

def pcb_holes():
    return [(PCB_X0 + sx, PCB_Y0 + sy) for sx in (PCB_HOLE_INSET, PCB[0] - PCB_HOLE_INSET) for sy in (PCB_HOLE_INSET, PCB[1] - PCB_HOLE_INSET)]

def pcb_env():
    z0 = FLOOR + PCB_STANDOFF
    return box(PCB_X0, PCB_Y0, z0, PCB_X0 + PCB[0], PCB_Y0 + PCB[1], z0 + PCB[2] + PCB_COMP_H)

def rbox(w, d, h, r):
    return cq.Workplane("XY").box(w, d, h, centered=False).edges("|Z").fillet(r)
def box(x0, y0, z0, x1, y1, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

def pan():
    p = rbox(W, Dp, H, R_OUT)
    p = p.cut(rbox(W - 2 * WALL, Dp - 2 * WALL, H, R_OUT - WALL).translate((WALL, WALL, FLOOR)))
    # PSU standoff rails + side stops
    for y in (PSU_LO[1] + 10, PSU_HI[1] - 10):
        p = p.union(box(PSU_LO[0] + 5, y - 4, FLOOR, PSU_HI[0] - 5, y + 4, PSU_LO[2]))
    for (x0, x1) in ((PSU_LO[0] - 0.1, PSU_LO[0] - 0.1), ):
        pass
    p = p.union(box(PSU_LO[0] + 20, PSU_LO[1] - PSU_CLR - 4, FLOOR, PSU_LO[0] + 60, PSU_LO[1] - PSU_CLR, PSU_LO[2] + 12))   # front stops
    p = p.union(box(PSU_HI[0] - 60, PSU_LO[1] - PSU_CLR - 4, FLOOR, PSU_HI[0] - 20, PSU_LO[1] - PSU_CLR, PSU_LO[2] + 12))
    # PSU hold-down strap bosses (2 straps across the PSU, part 12)
    for x in (PSU_LO[0] + 45, PSU_HI[0] - 45):
        for y in (PSU_LO[1] - PSU_CLR - 8, PSU_HI[1] + PSU_CLR + 6):     # front boss merges 1 mm into the stop
            p = p.union(cq.Workplane("XY").circle(5).extrude(PSU_HI[2] + 2 - FLOOR).translate((x, y, FLOOR)))
            p = p.cut(cq.Workplane("XY").circle(M3_INSERT_D / 2).extrude(8).translate((x, y, PSU_HI[2] + 2 - 8)))
    # mains partition: wall from the front to the PSU front face (the PSU closes the rest; wires to its terminal end)
    p = p.union(box(PART_X, WALL - 0.01, FLOOR, PART_X + 2, PSU_LO[1] - PSU_CLR - 0.3, H - 2))
    # user's inlet in the RIGHT wall: cutout (long axis along y) + 2 x M3 at IEC_HOLE_PITCH along z
    cy, cz = IEC_C
    p = p.cut(box(W - WALL - 1, cy - IEC_CUT[0] / 2, cz - IEC_CUT[1] / 2, W + 1, cy + IEC_CUT[0] / 2, cz + IEC_CUT[1] / 2))
    for sz in (-1, 1):
        p = p.cut(cq.Workplane("YZ").circle(M3_CLR / 2).extrude(WALL + 2).translate((W - WALL - 1, cy, cz + sz * IEC_HOLE_PITCH / 2)))
    # USB mini-B on the front wall, between the board and the mains zone
    ux, uz = USB_X, FLOOR + 25.0
    p = p.cut(box(ux - USB_HOLE[0] / 2, -1, uz - USB_HOLE[1] / 2, ux + USB_HOLE[0] / 2, WALL + 1, uz + USB_HOLE[1] / 2))
    for s in (-1, 1):
        p = p.cut(cq.Workplane("XZ").circle(M3_CLR / 2).extrude(-(WALL + 2)).translate((ux + s * USB_SCREW_PITCH / 2, -1, uz)))
    # strain relief: zip-tie bridges behind USB and beside the inlet
    for (x, y) in ((ux, WALL + 14), (MAINS[0] + 10, PSU_LO[1] - 12)):
        p = p.union(box(x - 8, y - 2, FLOOR, x + 8, y + 2, FLOOR + 8).cut(box(x - 4, y - 3, FLOOR - 1, x + 4, y + 3, FLOOR + 5)))
    # vents: left wall (PSU end) and front wall slots
    for i in range(8):
        z0 = FLOOR + 10; y = PSU_LO[1] + 12 + i * 12
        p = p.cut(box(-1, y, z0, WALL + 1, y + 5, z0 + 30))
    for i in range(4):                                                       # front vents only outside the mains zone
        x = USB_X + 14 + i * 9
        if x + 5 < PART_X - 4: p = p.cut(box(x, -1, FLOOR + 30, x + 5, WALL + 1, FLOOR + 52))
    # lid screw bosses (M3 heat-set from the top)
    for (x, y) in BOSSES:
        p = p.union(cq.Workplane("XY").circle(BOSS_D / 2).extrude(H - FLOOR).translate((x, y, FLOOR)))
        p = p.cut(cq.Workplane("XY").circle(M3_INSERT_D / 2).extrude(8).translate((x, y, H - 8)))
    # controller board standoffs (M3 heat-set from the top)
    for (x, y) in pcb_holes():
        p = p.union(cq.Workplane("XY").circle(3.5).extrude(PCB_STANDOFF).translate((x, y, FLOOR)))
        p = p.cut(cq.Workplane("XY").circle(M3_INSERT_D / 2).extrude(6.5).translate((x, y, FLOOR + PCB_STANDOFF - 6.5)))
    # rubber foot recesses
    for (x, y) in ((25, 25), (W - 25, 25), (25, Dp - 25), (W - 25, Dp - 25)):
        p = p.cut(cq.Workplane("XY").circle(FOOT_D / 2).extrude(FOOT_RECESS).translate((x, y, -0.01)))
    return p

def forearm_outline():
    """union of the real forearm sections z 0..SOCK_H, moved so its centre is at SOCK_C. Also returns the shift."""
    import importlib.util
    from shapely.ops import unary_union
    spec = importlib.util.spec_from_file_location("fa", F("forearm_build.py"))
    fa = importlib.util.module_from_spec(spec); spec.loader.exec_module(fa)
    S = fa.shells()
    elbow = [S["05c_forearm_robpart4"], S["05d_forearm_robpart5"]]
    u = unary_union([fa.section_union(elbow, z).convex_hull for z in np.linspace(0.5, SOCK_H, 8)])
    c = u.envelope.centroid
    shift = (SOCK_C[0] - c.x, SOCK_C[1] - c.y)
    from shapely import affinity
    return affinity.translate(u, *shift), shift

def poly_wp(poly, z0, h):
    pts = [tuple(p) for p in np.array(poly.exterior.coords)[:-1]]
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(h)

def lid():
    l = rbox(W, Dp, LID_T, R_OUT).translate((0, 0, H))
    sx, sy = SOCK_C
    outl, _ = forearm_outline()
    inner = outl.buffer(SOCK_CLR, join_style=1).simplify(0.2)
    outer = outl.buffer(SOCK_CLR + SOCK_WALL, join_style=1).simplify(0.2)
    collar = poly_wp(outer, H + LID_T, SOCK_H).cut(poly_wp(inner, H + LID_T - 0.01, SOCK_H + 1))
    ob = outer.bounds; ow, od = ob[2] - ob[0], ob[3] - ob[1]
    l = l.union(collar)
    l = l.cut(box(sx - CABLE_HOLE[0] / 2, sy - CABLE_HOLE[1] / 2, H - 1, sx + CABLE_HOLE[0] / 2, sy + CABLE_HOLE[1] / 2, H + LID_T + 1))
    # forearm retention: 4 x M4 radial screws through the collar (into the forearm shell / shims) - positions TBD after test fit
    for (dx, dy, ax) in ((ow / 2, 0, "x"), (-ow / 2, 0, "x"), (0, od / 2, "y"), (0, -od / 2, "y")):
        wp = cq.Workplane("YZ") if ax == "x" else cq.Workplane("XZ")
        c = wp.circle(2.2).extrude(SOCK_WALL * 3, both=True)
        l = l.cut(c.translate((sx + dx, sy + dy, H + LID_T + SOCK_H / 2)))
    # vents over the PSU (fan side) and the mains zone stays closed
    for i in range(12):
        x = PSU_LO[0] + 15 + i * 15
        if abs(x - sx) < ow / 2 + 4 and PSU_LO[1] < sy + od / 2: pass
        l = l.cut(box(x, PSU_HI[1] - 30, H - 1, x + 6, PSU_HI[1] - 8, H + LID_T + 1))
    for (x, y) in BOSSES:
        l = l.cut(cq.Workplane("XY").circle(M3_CLR / 2).extrude(LID_T + 2).translate((x, y, H - 1)))
        l = l.cut(cq.Workplane("XY").circle(3.2).extrude(2.0).translate((x, y, H + LID_T - 2.0)))
    # warning text over the mains zone (engraved)
    l = l.cut(cq.Workplane("XY").workplane(offset=H + LID_T - 0.8).center((MAINS[0] + MAINS[1]) / 2, (MAINS[2] + MAINS[3]) / 2)
              .text("230V", 8, 1.0, kind="bold"))
    return l

def psu_strap():
    """hold-down strap over the PSU (print 2): M3 into a heat-set boss in front of and behind the PSU."""
    pitch = PSU[1] + 2 * PSU_CLR + 8 + 6
    s = box(0, -6, 0, 14, pitch + 6, 3)
    for y in (0.0, pitch):
        s = s.cut(cq.Workplane("XY").circle(M3_CLR / 2).extrude(4).translate((7, y, -0.5)))
    return s

def ghosts():
    g = box(*PSU_LO, *PSU_HI)
    return g.union(iec_body())

def iec_body():
    cy, cz = IEC_C
    return box(W - WALL - IEC_BODY_DEPTH, cy - IEC_BODY[0] / 2, cz - IEC_BODY[1] / 2, W - WALL, cy + IEC_BODY[0] / 2, cz + IEC_BODY[1] / 2)

if __name__ == "__main__":
    pa, li, st, gh = pan(), lid(), psu_strap(), ghosts()
    out = {"10_base_pan": pa, "11_base_lid": li, "12_psu_strap_x2": st, "ref_base_psu_iec": gh, "ref_board_100x60": pcb_env()}
    import trimesh, manifold3d as mf
    for n, s in out.items():
        stl = F(n + ".stl")
        cq.exporters.export(s, stl, tolerance=0.02, angularTolerance=0.1)
        m = trimesh.load(stl); m.merge_vertices()                     # manifold re-merge so the STL is a closed volume
        M = mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32))).to_mesh()
        trimesh.Trimesh(M.vert_properties[:, :3], M.tri_verts).export(stl)
        chk = trimesh.load(stl); assert chk.is_watertight and chk.is_volume, stl
        if not n.startswith("ref"):
            cq.exporters.export(s, F(n + ".step"))
    # checks
    psu_hit = pa.intersect(box(*PSU_LO, *PSU_HI)).val().Volume()
    _ib = pa.intersect(iec_body()); iec_hit = _ib.val().Volume() if _ib.vals() else 0.0
    pcb_hit = pa.intersect(pcb_env()).val().Volume() if pa.intersect(pcb_env()).vals() else 0.0
    rep = dict(status="CONCEPT - P1 base, not printed",
               pan_mm=[round(W, 1), round(Dp, 1), H], lid_t=LID_T, total_height_with_socket=H + LID_T + SOCK_H,
               psu=dict(model="Mean Well LRS-350-12", size=PSU, at=[list(PSU_LO), list(PSU_HI)], standoff=PSU_STANDOFF, overlap_mm3=round(psu_hit, 2)),
               iec_inlet=dict(part="makePCB P087 (screw mount) - sizes ESTIMATED, measure", cutout_y_z=IEC_CUT, holes="2 x M3, %.0f mm apart (z)" % IEC_HOLE_PITCH, centre_y=round(IEC_C[0], 1), centre_z=round(IEC_C[1], 1), wall="right side, %.0f mm" % WALL,
                              mains_zone=[round(v, 1) for v in MAINS], body_overlap_mm3=round(iec_hit, 2)),
               board=dict(size=PCB, at=[PCB_X0, PCB_Y0, FLOOR + PCB_STANDOFF], component_height_reserved=PCB_COMP_H, holes="4 x M3 heat-set, %.1f mm from the edges (TBD)" % PCB_HOLE_INSET, overlap_mm3=round(pcb_hit, 2)),
               usb=dict(hole=USB_HOLE, pitch=USB_SCREW_PITCH, wall="front"),
               forearm_socket=dict(follows="real InMoov elbow-end outline (robpart4/5 assembled, scaled by forearm_build FA_SCALE) + %.1f mm/side" % SOCK_CLR, height=SOCK_H, centre=SOCK_C,
                                   outline_bbox=[round(v, 1) for v in forearm_outline()[0].bounds], forearm_xy_shift=[round(v, 2) for v in forearm_outline()[1]]),
               cable_hole=CABLE_HOLE, lid_screws=len(BOSSES),
               verify=["LRS-350-12 terminal-block end and fan position", "IEC cutout of the bought inlet", "USB extension hole", "forearm in the socket: test-fit, shim with tape/TPU"])
    json.dump(rep, open(F("base_report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))
