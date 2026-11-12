"""HAEBOT Hand Controller v2 (final component selection) - power budget calculator.

Run:  /workspace/venv/bin/python concept/power_budget_calc.py  ->  ../power_budget.csv + printed summary
Sources [S..] are listed in power_budget.md.  ASSUMPTION = no datasheet figure, must be measured.
"""
import csv, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "power_budget.csv")
VIN = 12.0

# ---------------- rail set-points
V6 = 1.1 * (1 + 4420 / 1000)          # TPSM41625: VREF 1.1 V (RVSEL 187k) + RADJ 4.42k over internal 1k  [S1 Table 7-2]
V5 = 0.6 * (1 + 75.0 / 10.0)          # TPS56837: VFB 0.6 V, R_top 75.0k / R_bot 10.0k               [S2]
V3 = 3.3                              # TLV75533P fixed                                                [S3]

# ---------------- regulator loss models
# TPSM41625 power dissipation, PVIN 12 V, VOUT 5-7 V curves read from datasheet Fig. 6-2 [S1]
TPSM_LOSS = [(0, 1.9), (5, 2.0), (10, 3.0), (15, 4.3), (20, 6.0), (22, 6.6)]
def tpsm_loss(i):
    for (a, pa), (b, pb) in zip(TPSM_LOSS, TPSM_LOSS[1:]):
        if i <= b:
            return pa + (pb - pa) * (i - a) / (b - a)
    return TPSM_LOSS[-1][1]
def tps568_loss(pout, worst):        # efficiency read from TI Fig. 5-17 (12->5 V, 500 kHz); ASSUMPTION +-1 %
    eff = 0.94 if worst else 0.95
    return pout / eff - pout, eff
RJA_TPSM_TI, RJA_TPSM_OURS = 13.8, 20.0  # TI: 6-layer 90x90 mm 2 oz. Ours (4-layer 115x56, Pi above): ASSUMPTION
RJA_TPS568 = 30.0                        # TI "effective" RthJA on 4-layer EVM [S2]
TA = 40.0                                # air under the Pi inside the case: ASSUMPTION

# ---------------- loads: (rail, ref, item, qty, typ_each, worst_each, source, note)
LOADS = [
 ("6V servo", "J2 CH0-CH5", "MG996R servo (5 fingers + wrist) @ 5.96 V", 6, 0.70, 2.50, "S4,S5",
  "datasheet @6 V: running 0.5-0.9 A, stall 2.5 A (TowerPro site lists 1.4 A stall; we use the higher 2.5 A). typ 0.70 A = mid of running range (ASSUMPTION for tendon load)."),
 ("6V servo", "D5 R", "6V rail LED (2.2 k)", 1, 0.002, 0.002, "-", "(6 - 2 V) / 2.2 k"),
 ("6V servo", "R A1", "6V sense divider 10k/10k -> A1", 1, 0.0003, 0.0003, "-", "6 / 20 k"),
 ("5V1 Pi", "J5", "Raspberry Pi 5 board, MediaPipe Hands (4 cores busy)", 1, 2.00, 3.00, "S6,S7",
  "typ: stress-ng measured 8.9-9.8 W = ~2.0 A [S7]; worst: board share of the official 5 A budget [S6]"),
 ("5V1 Pi", "J5", "Camera Module 3 (powered by the Pi)", 1, 0.30, 0.30, "S8", "ASSUMPTION ~0.3 A"),
 ("5V1 Pi", "J5", "Pi 5 Active Cooler fan", 1, 0.10, 0.10, "-", "ASSUMPTION"),
 ("5V1 Pi", "J5", "Pi USB ports", 1, 0.00, 1.60, "S6",
  "worst = 1.6 A (usb_max_current_enable=1). Default config limits USB to 0.6 A -> Pi 4.0 A. 5.0 A is the official Pi 5 maximum."),
 ("5V1 logic", "U1", "ATmega328P-AU 16 MHz", 1, 0.0092, 0.014, "S9", "active 9.2 mA typ / 14 mA max"),
 ("5V1 logic", "U6", "CH340C (only with USB plugged)", 1, 0.007, 0.020, "S10", "ICC 7-20 mA"),
 ("5V1 logic", "U5", "TMC2209 VCC_IO + logic", 1, 0.002, 0.005, "S11", "VCC_IO / internal logic supplied mostly from VS; IO few mA"),
 ("5V1 logic", "U7 U8", "2x SN74LVC1T45", 2, 0.0001, 0.0005, "S12", "static ICC <= 10 uA, dynamic at 115 kbaud negligible"),
 ("5V1 logic", "D6 D8 R", "LEDs 5V1 + STAT (1 k)", 2, 0.003, 0.003, "-", "(5.1 - 2 V)/1 k"),
 ("5V1 logic", "R I2C", "I2C 4.7 k pull-ups to 5 V, limit-switch pull-up", 1, 0.002, 0.003, "-", "calculated"),
 ("5V1 logic", "J6", "spare I2C connector 5 V", 1, 0.0, 0.10, "-", "allowance; print '5V 100 mA max'"),
 ("5V1 logic", "U9 in", "TLV75533P input = 3.3 V rail load", 1, None, None, "S3", "see 3V3 rows"),
 ("3V3", "U2", "PCA9685PW at 3.3 V (16 ch)", 1, 0.006, 0.010, "S13", "IDD 6-10 mA; outputs only drive servo signal inputs"),
 ("3V3", "D7 R", "3V3 LED (680 R)", 1, 0.002, 0.002, "-", "(3.3 - 2 V)/680"),
 ("3V3", "R VREF", "TMC2209 VREF divider 10k/7.5k", 1, 0.0002, 0.0002, "-", "3.3 / 17.5 k"),
 ("3V3", "R", "Pi-TX idle pull-up 100 k, misc", 1, 0.0001, 0.0001, "-", ""),
 ("3V3", "", "3.3 V allowance (future sensor)", 1, 0.0, 0.030, "-", "allowance"),
 ("12V motor", "U5 J3", "NEMA 17 17HS4401S via TMC2209, I_RMS 1.0 A (1.2 A max)", 1, None, None, "S11,S14", "computed below"),
 ("12V direct", "D4 R", "12V LED (4.7 k)", 1, 0.002, 0.002, "-", "(12 - 2 V)/4.7 k"),
 ("12V direct", "R A0", "12 V sense divider 47k/10k -> A0", 1, 0.0002, 0.0002, "-", ""),
]

def stepper(irms, pmech):
    r_ph, r_drv = 1.5, 0.17 * 2           # 17HS4401S 1.5 ohm [S14]; TMC2209 RDSon 0.17 ohm HS + LS [S11]
    p_cu = 2 * irms ** 2 * r_ph            # TMC2209 sets RMS coil current directly
    p_drv = 2 * irms ** 2 * r_drv
    p = p_cu + p_drv + pmech + VIN * 0.002
    return p, p / VIN, p_cu, p_drv
ST_T, ST_W, ST_ALLOW = stepper(1.0, 1.0), stepper(1.2, 3.0), 1.0

def rail(r, col):
    return sum(q * (t if col == "t" else w) for (rr, _, _, q, t, w, _, _) in LOADS if rr == r and t is not None)

def ipc2221(i, dt=10, oz=2.0, internal=False):
    k = 0.024 if internal else 0.048
    area = (i / (k * dt ** 0.44)) ** (1 / 0.725)
    return area / (1.37 * oz) * 0.0254

if __name__ == "__main__":
    i6t, i6w = rail("6V servo", "t"), rail("6V servo", "w")
    i3t, i3w = rail("3V3", "t"), rail("3V3", "w")
    i5t = rail("5V1 Pi", "t") + rail("5V1 logic", "t") + i3t
    i5w = rail("5V1 Pi", "w") + rail("5V1 logic", "w") + i3w
    i5w_def = i5w - 1.0                    # USB left at 600 mA (default)
    i6clone = 6 * 3.0                      # ASSUMPTION: clone MG996R start/stall peaks ~3 A
    rows = []
    hdr = ["section", "rail", "ref", "item", "qty", "typ_A_each", "worst_A_each", "typ_A_total", "worst_A_total",
           "volts", "typ_W", "worst_W", "source", "note"]
    vmap = {"6V servo": V6, "5V1 Pi": V5, "5V1 logic": V5, "3V3": V3, "12V direct": VIN}
    for (r, ref, item, q, t, w, src, note) in LOADS:
        if r == "12V motor":
            rows.append(["load", r, ref, item, q, "", "", round(ST_T[1], 3), ST_ALLOW, VIN, round(ST_T[0], 2), ST_ALLOW * VIN, src,
                         f"I_RMS 1.0 A: Cu {ST_T[2]:.2f} W + driver {ST_T[3]:.2f} W + 1 W mech (ASSUMPTION) = {ST_T[1]:.2f} A; "
                         f"1.2 A + 3 W mech = {ST_W[1]:.2f} A; sized with a 1.0 A allowance"])
            continue
        if t is None:
            continue
        v = vmap[r]
        rows.append(["load", r, ref, item, q, t, w, round(q * t, 4), round(q * w, 4), round(v, 3), round(q * t * v, 3), round(q * w * v, 3), src, note])

    # regulators
    p6t, p6w = i6t * V6, i6w * V6
    l6t, l6w = tpsm_loss(i6t), tpsm_loss(i6w)
    p5t, p5w = i5t * V5, i5w * V5
    l5t, e5t = tps568_loss(p5t, False); l5w, e5w = tps568_loss(p5w, True)
    l3t, l3w = (V5 - V3) * i3t, (V5 - V3) * i3w
    reg = [
        ("U3 TPSM41625 6V", i6t, i6w, p6t + l6t, p6w + l6w, l6t, l6w, f"{100*p6t/(p6t+l6t):.1f}% / {100*p6w/(p6w+l6w):.1f}%",
         f"rating at 6 V = 20 A (TI Fig 7-3), worst {i6w:.1f} A = {100*i6w/20:.0f}%; Tj worst ~{TA+l6w*RJA_TPSM_OURS:.0f} C (ours 20 C/W ASSUMPTION) / {TA+l6w*RJA_TPSM_TI:.0f} C (TI board)"),
        ("U4 TPS56837 5V1", i5t, i5w, p5t + l5t, p5w + l5w, l5t, l5w, f"{100*e5t:.0f}% / {100*e5w:.0f}%",
         f"8 A part, worst {i5w:.2f} A = {100*i5w/8:.0f}% (USB 1.6 A) / {i5w_def:.2f} A with default USB 0.6 A; Tj ~{TA+l5w*RJA_TPS568:.0f} C"),
    ]
    for (nm, it, iw, pint, pinw, lt, lw, eff, note) in reg:
        rows.append(["regulator (12V side)", nm, nm.split()[0], nm, 1, "", "", round(pint / VIN, 3), round(pinw / VIN, 3), VIN,
                     round(pint, 2), round(pinw, 2), "S1,S2", f"Iout typ {it:.2f} / worst {iw:.2f} A; eff {eff}; loss {lt:.2f} / {lw:.2f} W; {note}"])
    rows.append(["regulator", "U9 TLV75533P 3V3", "U9", "LDO 5.1 -> 3.3 V (load already in 5V1 total)", 1, "", "", round(i3t, 4), round(i3w, 4), V5,
                 round(l3t, 3), round(l3w, 3), "S3", f"500 mA part, worst {1000*i3w:.0f} mA = {100*i3w/0.5:.0f}%; loss {l3w*1000:.0f} mW"])

    st_t, st_w = ST_T[0], ST_ALLOW * VIN
    misc = VIN * 0.0022
    q1t = ((p6t + l6t + p5t + l5t + st_t) / VIN) ** 2 * 0.005
    p12t = p6t + l6t + p5t + l5t + st_t + misc + q1t
    q1w = ((p6w + l6w + p5w + l5w + st_w) / VIN) ** 2 * 0.005
    p12w = p6w + l6w + p5w + l5w + st_w + misc + q1w
    # clone-peak scenario
    p6c = i6clone * V6; l6c = tpsm_loss(i6clone)
    p12c = p6c + l6c + p5w + l5w + st_w + misc + ((p6c + l6c + p5w + l5w + st_w) / VIN) ** 2 * 0.005
    rows.append(["total", "12V input", "J1", "12 V input (bucks + stepper + Q1 + misc)", "", "", "", round(p12t / VIN, 2), round(p12w / VIN, 2), VIN,
                 round(p12t, 1), round(p12w, 1), "", f"worst = 6 servos stalled at 2.5 A + Pi 5 A + stepper allowance; clone-peak case 6 x 3 A = {p12c/VIN:.1f} A / {p12c:.0f} W"])
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f); w.writerow(hdr); w.writerows(rows)

    print(f"V6 {V6:.3f}  V5 {V5:.3f}")
    print(f"6V  typ {i6t:.2f} A {p6t:.1f} W | worst {i6w:.2f} A {p6w:.1f} W | loss {l6t:.2f}/{l6w:.2f} W | clone {i6clone} A loss {l6c:.1f}")
    print(f"5V1 typ {i5t:.2f} A {p5t:.1f} W | worst {i5w:.2f} A {p5w:.1f} W (default USB {i5w_def:.2f} A) | loss {l5t:.2f}/{l5w:.2f}")
    print(f"3V3 typ {1000*i3t:.1f} mA worst {1000*i3w:.1f} mA")
    print(f"stepper typ {ST_T[1]:.3f} A ({ST_T[0]:.2f} W) calc-worst {ST_W[1]:.3f} A ({ST_W[0]:.2f} W) allowance {ST_ALLOW} A; drv loss {ST_T[3]:.2f}/{ST_W[3]:.2f}")
    print(f"12V IN typ {p12t/VIN:.2f} A {p12t:.1f} W | worst {p12w/VIN:.2f} A {p12w:.1f} W | clone {p12c/VIN:.2f} A {p12c:.0f} W | Q1 {q1t:.2f}/{q1w:.2f} W")
    print(f"AC @85%: typ {p12t/0.85:.0f} W worst {p12w/0.85:.0f} W clone {p12c/0.85:.0f} W")
    print(f"TPSM Tj worst ours {TA+l6w*RJA_TPSM_OURS:.0f} TI {TA+l6w*RJA_TPSM_TI:.0f}; typ {TA+l6t*RJA_TPSM_OURS:.0f}; TPS568 Tj worst {TA+l5w*RJA_TPS568:.0f}")
    for nm, i, ext in (("12V in", p12w / VIN, True), ("12V in clone", p12c / VIN, True), ("6V servo bus", i6w, True), ("6V clone", i6clone, True),
                       ("5V1 Pi", i5w, True), ("servo 1 ch", 2.5, True), ("motor phase", 1.7, True), ("12V TMC branch", 2.0, True)):
        print(f"IPC {nm:14s} {i:5.2f} A  ext 2oz {ipc2221(i):6.2f} mm | int 1oz {ipc2221(i, oz=1, internal=True):6.2f} mm")
    print("wrote", OUT)
