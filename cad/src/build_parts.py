"""HAEBOT Hand i2 V1 - parametric parts (CadQuery).

Generates real B-rep STEP + STL for every new part, driven by cad/parameters.yaml.
Run:  python cad/src/build_parts.py
Servo-local frame used everywhere: output-shaft axis = +Z through origin,
servo case bottom at z=0 when seated, +X = from shaft toward the far end of the body.
"""
import pathlib, yaml
import cadquery as cq

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = yaml.safe_load((ROOT / "parameters.yaml").read_text())
OUT = ROOT / "02_haebot_modified"
RIG = ROOT / "03_one_finger_test"


def v(d):  # measured value wins over nominal
    return d["measured"] if d.get("measured") is not None else d["nominal"]


S = {k: v(d) for k, d in P["es08ma_ii"].items()}
H = {k: v(d) for k, d in P["stock_horn"].items()}
C = P["clearance"]
LEDGE = P["servo_seat"]["ledge_z"]
PLATE_TOP = P["servo_seat"]["block_height"]

L, W = S["body_length"], S["body_width"]
x0, x1 = -S["shaft_from_end"], L - S["shaft_from_end"]   # body x-range in local frame
xc = (x0 + x1) / 2                                        # body centre


def cyl(r, h, p, d):
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(r, h, cq.Vector(*p), cq.Vector(*d)))


def box(xa, xb, ya, yb, za, zb):
    return cq.Workplane("XY").box(xb - xa, yb - ya, zb - za, centered=False).translate((xa, ya, za))


# ---------------------------------------------------------------- servo dummy (reference only)
def servo_dummy():
    case = box(x0, x1, -W / 2, W / 2, 0, S["case_height"])
    tabs = box(xc - S["tab_span"] / 2, xc + S["tab_span"] / 2, -W / 2, W / 2,
               S["tab_bottom_z"], S["tab_bottom_z"] + S["tab_thickness"])
    for sx in (-1, 1):
        tabs = tabs.cut(cq.Workplane("XY").circle(S["tab_hole_dia"] / 2).extrude(10)
                        .translate((xc + sx * S["tab_hole_pitch"] / 2, 0, S["tab_bottom_z"] - 1)))
    boss = cq.Workplane("XY").circle(3.0).extrude(1.5).translate((0, 0, S["case_height"]))
    shaft = cq.Workplane("XY").circle(S["spline_dia"] / 2).extrude(S["shaft_above_case"]) \
        .translate((0, 0, S["case_height"]))
    cable = box(x1, x1 + 3.0, -1.5, 1.5, 1, 3)   # cable bends down into the channel
    return case.union(tabs).union(boss).union(shaft).union(cable)


# ---------------------------------------------------------------- pocket cutter (servo seat)
def pocket_cutter(top=PLATE_TOP + 0.6):
    """Negative volume for an ES08MA II seat in a plate whose bottom is z=0, ledge at LEDGE."""
    body = box(x0 - C, x1 + C, -W / 2 - C, W / 2 + C, -1.0, LEDGE + 0.01)
    tabs = box(xc - S["tab_span"] / 2 - C, xc + S["tab_span"] / 2 + C,
               -W / 2 - C, W / 2 + C, LEDGE, top)
    cable = box(x1, x1 + 3.2, -2.2, 2.2, -1.0, top)   # vertical channel: cable exits the far end
    cut = body.union(tabs).union(cable)
    for sx in (-1, 1):  # self-tapping pilot holes for the tab screws
        cut = cut.union(cq.Workplane("XY").circle(0.9).extrude(9)
                        .translate((xc + sx * S["tab_hole_pitch"] / 2, 0, LEDGE - 9)))
    return cut


# ---------------------------------------------------------------- fit coupon (print FIRST)
def fit_coupon():
    blk = box(xc - S["tab_span"] / 2 - 4, xc + S["tab_span"] / 2 + 4, -W / 2 - 4, W / 2 + 4, 0, PLATE_TOP)
    blk = blk.cut(pocket_cutter())
    return blk


# ---------------------------------------------------------------- tendon pulley for ES08MA II
def pulley():
    D, Hh = P["inmoov_i2"]["pulley"]["dia"], P["inmoov_i2"]["pulley"]["height"]
    hub_h = max(H["hub_height"] + 0.5, 2.0)
    total = Hh + hub_h * 0  # keep official 10 mm envelope
    p = cq.Workplane("XY").circle(D / 2).extrude(total)
    # V/U groove for the 0.8 mm line, mid-height of the upper half
    gz = total - 3.0
    groove = cq.Solid.makeTorus(D / 2, 1.0, cq.Vector(0, 0, gz), cq.Vector(0, 0, 1))
    p = p.cut(cq.Workplane("XY").add(groove))
    # horn seat on the underside: hub + single arm, plus clearance
    cl = 0.15
    seat = cq.Workplane("XY").circle(H["hub_dia"] / 2 + cl).extrude(H["hub_height"])
    arm = (cq.Workplane("XY")
           .polyline([(0, -H["arm_width_hub"] / 2 - cl), (H["arm_length"] - 1, -H["arm_width_tip"] / 2 - cl),
                      (H["arm_length"] - 1, H["arm_width_tip"] / 2 + cl), (0, H["arm_width_hub"] / 2 + cl)]).close()
           .extrude(H["arm_thickness"] + cl))
    # arm longer than the pulley radius -> it is trimmed by the pulley outline; arm tip stays visible
    p = p.cut(seat).cut(arm)
    p = p.cut(cq.Workplane("XY").circle(H["screw_dia"] / 2).extrude(total + 1))          # horn screw
    p = p.cut(cq.Workplane("XY").circle(2.4).extrude(2).translate((0, 0, total - 2)))     # screw head
    # line anchor: radial hole into the groove + vertical tie-off hole
    p = p.cut(cyl(0.6, D, (0, 0, gz), (1, 0, 0)))
    p = p.cut(cq.Workplane("XY").circle(0.8).extrude(total + 1).translate((5.0, 0, 0)))
    return p


# ---------------------------------------------------------------- one-finger test rig
PIN_Z = 55.0      # hinge pin height above table
PIN_Y = 0.0
GAP = P["inmoov_i2"]["finger_proximal_body_width"]["value"] + 0.6   # clevis gap (finger body clears)
KNUCKLE = P["inmoov_i2"]["finger_root_knuckle"]["width"]
PIN_D = 3.2       # M3 screw or 3 mm rod as hinge pin  [EST]
BASE_T = 5.0


def rig_base():
    base = box(-38, 30, -95, 12, 0, BASE_T).edges("|Z").fillet(4)
    for x in (-32, 24):
        for y in (-89, 6):
            base = base.cut(cq.Workplane("XY").circle(1.7).extrude(BASE_T).translate((x, y, 0)))
    # clevis arms
    arm_t = 6.0
    for s in (-1, 1):
        xa = s * GAP / 2 if s > 0 else -GAP / 2 - arm_t
        arm = (cq.Workplane("YZ").workplane(offset=xa)
               .moveTo(PIN_Y - 16, BASE_T).lineTo(PIN_Y + 4, BASE_T).lineTo(PIN_Y + 7, PIN_Z - 2)
               .threePointArc((PIN_Y, PIN_Z + 7), (PIN_Y - 7, PIN_Z)).lineTo(PIN_Y - 16, BASE_T + 10).close()
               .extrude(arm_t))
        base = base.union(arm)
    base = base.cut(cyl(PIN_D / 2, 80, (-40, PIN_Y, PIN_Z), (1, 0, 0)))
    # tendon / PTFE guide tower: holes below (palmar) and above (dorsal) the pin line
    ty = PIN_Y - 22
    tower = box(-9, 9, ty - 4, ty + 4, BASE_T, PIN_Z + 18)
    for dz in (-8, 8):
        tower = tower.cut(cyl(1.35, 12, (0, ty - 6, PIN_Z + dz), (0, 1, 0)))  # 2.5 mm PTFE OD + clearance
    # elastic / spring anchor peg on top
    tower = tower.cut(cyl(1.1, 24, (-12, ty, PIN_Z + 14), (1, 0, 0)))
    base = base.union(tower)
    # servo block: ES08MA II lying on its side, shaft pointing +X, pulley groove in finger plane x=0
    D, Hh = P["inmoov_i2"]["pulley"]["dia"], P["inmoov_i2"]["pulley"]["height"]
    shaft_top = S["case_height"] + S["shaft_above_case"]
    groove_local_z = shaft_top + Hh - 3.0
    blk_local = box(xc - S["tab_span"] / 2 - 4, xc + S["tab_span"] / 2 + 4, -W / 2 - 4, W / 2 + 4, 0, PLATE_TOP)
    blk_local = blk_local.cut(pocket_cutter())
    zc = BASE_T + W / 2 + 4                          # block rests on the base plate
    sy = -62.0                                        # shaft y position
    # local +Z (shaft) -> global +X, local +X (body) -> global -Y, local +Y -> global -Z
    blk = (blk_local.rotate((0, 0, 0), (0, 1, 0), 90)      # z->x, x->-z
           .rotate((0, 0, 0), (1, 0, 0), -90)              # -z->-y, y->-z
           .translate((-groove_local_z, sy, zc)))
    base = base.union(blk)
    return base, dict(shaft=(0.0, sy, zc), groove_x=0.0)


def washer():
    t = (GAP - KNUCKLE - 0.3) / 2
    return cq.Workplane("XY").circle(3.8).circle(PIN_D / 2 + 0.15).extrude(t)


def export(shape, folder, name):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "step").mkdir(exist_ok=True)
    (folder / "stl").mkdir(exist_ok=True)
    cq.exporters.export(shape, str(folder / "step" / f"{name}.step"))
    cq.exporters.export(shape, str(folder / "stl" / f"{name}.stl"), tolerance=0.02, angularTolerance=0.1)
    print("exported", name)


if __name__ == "__main__":
    export(servo_dummy(), OUT, "HB_ES08MA-II_reference_dummy")
    export(pocket_cutter(), OUT, "HB_ES08MA-II_pocket_cutter")
    export(fit_coupon(), OUT, "HB_P00_FitCoupon_ES08MA-II")
    export(pulley(), OUT, "HB_P03_Pulley_ES08MA-II")
    rig, info = rig_base()
    export(rig, RIG, "HB_T01_OneFingerRig_Base")
    export(washer(), RIG, "HB_T02_OneFingerRig_Washer")
    print(info)
