"""Where every P1 file lives. All P1 scripts load this file, so the folder layout is defined only here.

  A_servos_in_palm/
    README.md
    print/1_hand/      00..04   parts to print (short names)
    print/2_forearm/   05..07
    print/3_base/      10..12
    reference/         ref_*    servo / board / PSU envelopes - do NOT print
    assembly/          asm_*    full-arm STEP assembly for viewing in Fusion 360 / SolidWorks
    reports/           dona_univ_robot_hand_<date>_Sanjev_A_report_*.json
    images/            dona_univ_robot_hand_<date>_Sanjev_A_img_*.png
    scripts/           dona_univ_robot_hand_<date>_Sanjev_A_*.py
3D parts use short names; documents, reports, images and scripts follow the repo naming convention.
"""
import os
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)                                     # cad/prototype/A_servos_in_palm
ORIG = os.path.normpath(os.path.join(ROOT, "..", "..", "original"))
BRAND = os.path.normpath(os.path.join(ROOT, "..", "..", "..", "docs", "brand"))
DOC = "dona_univ_robot_hand_2026-11-17_Sanjev_A_"
_REPORTS = {"report.json": "report_hand.json", "forearm_report.json": "report_forearm.json",
            "base_report.json": "report_base.json", "assembly_report.json": "report_assembly.json"}
_SCRIPTS = {"build.py": "build_hand.py", "forearm_build.py": "build_forearm.py", "base_build.py": "build_base.py",
            "render.py": "render_hand.py", "base_render.py": "render_base.py", "assembly_render.py": "render_assembly.py",
            "assembly_step.py": "build_assembly_step.py"}

def F(name):
    """full path for a P1 file given its short key (e.g. '01_palm_frame.stl', 'report.json', 'img_20_full_arm.png')."""
    ext = os.path.splitext(name)[1].lower()
    if ext in (".stl", ".step"):
        if name.startswith("ref_"): sub = "reference"
        elif name.startswith("asm_"): sub = "assembly"
        else:
            n = int(name[:2])
            sub = os.path.join("print", "1_hand" if n <= 4 else "2_forearm" if n <= 9 else "3_base")
        path = os.path.join(ROOT, sub, name)
    elif ext == ".json": path = os.path.join(ROOT, "reports", DOC + _REPORTS.get(name, name))
    elif ext == ".png": path = os.path.join(ROOT, "images", DOC + name)
    elif ext == ".py": path = os.path.join(SCRIPTS, DOC + _SCRIPTS.get(name, name))
    else: path = os.path.join(ROOT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path
