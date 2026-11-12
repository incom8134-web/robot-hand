"""Single source of truth for the HAEBOT Hand Controller v2 concept placement.

Units: mm. Origin is the bottom-left corner of the controller board, seen from the TOP.
x runs along the 115 mm length and y across the 56 mm width.
The Raspberry Pi 5 sits on 18 mm standoffs over x = 30..115. The left 30 mm is the "open zone":
it holds the power entry, the fuse, the servo headers and the parts students touch.
Every part under the Pi must be <= 12 mm tall.

Sizes are real package / body sizes from the BOM (bom_controller_v2.csv) datasheets.
Clusters of 0603 passives that serve one IC are drawn as one small box ("cluster") and labelled
with every reference designator they contain.
This is a CONCEPT placement for drawings and the 3D mock-up. It is NOT a routed PCB.
"""

BOARD_L, BOARD_W, BOARD_T = 115.0, 56.0, 1.6
PI_X0 = 30.0
PI_L, PI_W = 85.0, 56.0
STANDOFF_H = 18.0
PI_HOLES = [(PI_X0 + 3.5, 3.5), (PI_X0 + 61.5, 3.5), (PI_X0 + 3.5, 52.5), (PI_X0 + 61.5, 52.5)]
EXTRA_HOLES = [(3.5, 52.5), (16.5, 25.0)]        # H5, H6: support the open zone
PI_HDR = dict(x=PI_X0 + 7.0, y=49.9, w=50.8, h=5.1)   # Pi 40-pin header on the Pi's top side

# net colours (also used by the wiring diagram)
NET = {
    "12V": "#e03131", "6V": "#f76707", "5V1": "#f5d000", "5V_MCU": "#f5d000", "3V3": "#c9a227",
    "GND": "#2f9e44", "I2C": "#1c7ed6", "UART": "#9c36b5", "STEP": "#15aabf", "USB": "#e64980", "OTHER": "#868e96",
}

C = dict(ic="#24282d", mod="#3a3f45", cap_e="#20304a", cap_p="#5b2c83", mlcc="#b8936a", res="#1b1b1b",
         hdr="#151515", pin="#d4af37", xt60="#f2c200", fuse_h="#1d1d1d", fuse="#e8590c", conn="#efe6cf",
         mfit="#e9e2d0", usb="#c0c0c0", sw="#2b2b2b", led_r="#ff3030", led_o="#ff9a1f", led_y="#ffd21f",
         led_g="#2fd34a", led_b="#2f7bff", ind="#3b3b3b", tvs="#303030")

P = []
def add(ref, name, purpose, x, y, w, h, z, color, net, kind="box", cluster=False, label=True):
    P.append(dict(ref=ref, name=name, purpose=purpose, x=x, y=y, w=w, h=h, z=z, color=color, net=net,
                  kind=kind, cluster=cluster, label=label,
                  zone="open" if x + w / 2 < PI_X0 else "underpi"))

# ------------------------------------------------------------ open zone (x 0..30)
add("J1", "XT60 12V IN", "12 V from Mean Well LRS-350-12, 30 A, polarized", 0.0, 3.0, 10.6, 15.8, 8.3, C["xt60"], "12V")
add("F1/XF1", "20 A blade fuse", "main fuse; blows before the SMPS overload point", 12.0, 1.0, 6.9, 19.5, 8.0, C["fuse_h"], "12V")
add("Q1", "P-MOSFET", "reverse-polarity protection + soft power switch", 21.5, 1.0, 6.0, 5.0, 1.0, C["ic"], "12V")
add("DZ1,R1,R2", "Q1 gate parts", "15 V gate clamp, OFF pull-up, ON pull-down", 28.0, 1.0, 1.8, 5.0, 0.6, C["res"], "OTHER", cluster=True)
add("D1", "TVS SMBJ13A", "clamps 12 V input surges", 21.5, 7.0, 5.3, 3.6, 2.3, C["tvs"], "12V")
add("C1", "470 µF 35 V", "12 V input bulk: holds the rail during servo steps", 20.0, 11.2, 10.0, 10.0, 10.5, C["cap_e"], "12V", kind="cyl")
add("C2", "470 µF 35 V", "12 V input bulk (2nd)", 20.0, 21.7, 10.0, 10.0, 10.5, C["cap_e"], "12V", kind="cyl")
add("SW1", "POWER slide", "board on/off (switches only Q1 gate, mA)", 0.0, 21.5, 3.6, 8.6, 3.5, C["sw"], "OTHER")
add("J2", "SERVO 3x8", "6 MG996R: CH0-4 fingers, CH5 wrist, CH6-7 spare", 21.0, 33.5, 7.62, 20.32, 8.5, C["hdr"], "6V")
for i, (r, nm, col, net) in enumerate([("D4", "12V", C["led_r"], "12V"), ("D5", "6V", C["led_o"], "6V"),
                                       ("D6", "5V1", C["led_y"], "5V1"), ("D7", "3V3", C["led_g"], "3V3"),
                                       ("D8", "STAT", C["led_b"], "OTHER")]):
    add(r, f"LED {nm}", {"D4": "12 V present", "D5": "6 V servo rail on", "D6": "Pi 5.1 V rail on",
                         "D7": "3.3 V logic on", "D8": "firmware heartbeat (D13)"}[r],
        1.0, 33.0 + i * 2.6, 1.6, 0.8, 0.6, col, net)
add("R3,R12,R29,R30,R32", "LED resistors", "current limits for D4-D8 (~2-4 mA)", 1.0, 46.5, 2.6, 2.8, 0.5, C["res"], "OTHER", cluster=True)

# ------------------------------------------------------------ under the Pi: 6 V servo power (U3)
add("C7", "100 µF hybrid", "U3 input bulk (TI recommended EEHZA1H101P)", 30.6, 7.0, 10.3, 10.3, 10.2, C["cap_p"], "12V", kind="cyl")
for k in range(4):
    add(f"C{3+k}", "22 µF 25 V", "U3 input MLCC", 41.2, 7.5 + 4.0 * k, 2.5, 3.2, 2.5, C["mlcc"], "12V", label=False)
add("U3", "TPSM41625", "12 V -> 5.96 V servo rail, ~20 A at 6 V (module)", 45.0, 7.0, 11.0, 16.0, 5.0, C["mod"], "6V")
add("R6-R11,C16", "U3 set parts", "VSEL/ADJ (5.96 V), RT 700 kHz, RAMP, ILIM -30 %, PGOOD", 45.0, 3.2, 11.0, 3.0, 0.6, C["res"], "OTHER", cluster=True)
for k in range(6):
    add(f"C{8+k}", "47 µF 10 V", "U3 output MLCC", 57.0 + 3.0 * (k // 3), 8.0 + 4.5 * (k % 3), 2.5, 3.2, 2.5, C["mlcc"], "6V", label=False)
add("C14", "470 µF 35 V", "6 V servo reservoir near J2", 31.0, 18.0, 10.0, 10.0, 10.5, C["cap_e"], "6V", kind="cyl")
add("C15", "470 µF 35 V", "6 V servo reservoir (2nd)", 31.0, 28.5, 10.0, 10.0, 10.5, C["cap_e"], "6V", kind="cyl")

# ------------------------------------------------------------ servo PWM
add("U2", "PCA9685", "16-ch 12-bit servo PWM from I2C (3.3 V, 5.5 V-tolerant)", 43.0, 25.0, 9.7, 6.4, 1.2, C["ic"], "3V3")
add("C45,C46,R40-R42", "U2 parts", "decoupling, /OE pull-up (servos off at boot), I2C pull-ups to 5 V", 53.5, 25.0, 3.0, 6.4, 0.6, C["res"], "I2C", cluster=True)
add("R15-R22", "220 Ω x8", "series protection on the 8 servo PWM lines", 43.0, 32.5, 9.7, 2.0, 0.6, C["res"], "OTHER", cluster=True)

# ------------------------------------------------------------ stepper (TMC2209, onboard, standalone)
add("U5", "TMC2209", "silent NEMA 17 driver, 1.0 A RMS, 1/16 -> 1/256 step", 44.0, 37.0, 5.0, 5.0, 0.9, C["ic"], "STEP")
add("C48-C53,R45-R49,JP1", "U5 parts", "charge pump, VREF 1.41 V (1.0 A), EN/PDN/MS pulls, UART jumper", 50.0, 36.0, 5.0, 6.0, 0.6, C["res"], "STEP", cluster=True)
add("R43,R44", "0.11 Ω sense", "coil current sense (sets the current scale)", 56.0, 36.0, 3.2, 4.1, 0.6, C["res"], "STEP", cluster=True)
add("F2", "2 A slow fuse", "protects the 12 V motor branch", 56.0, 41.0, 3.2, 1.6, 0.8, C["fuse"], "12V")
add("C47", "100 µF hybrid", "TMC2209 motor-supply bulk", 60.0, 30.5, 10.3, 10.3, 10.2, C["cap_p"], "12V", kind="cyl")

# ------------------------------------------------------------ edge connectors (top edge, side entry)
add("J3", "MOTOR XH-4", "NEMA 17 17HS4401S coils A1 A2 B1 B2", 38.0, 46.2, 12.4, 9.8, 7.0, C["conn"], "STEP")
add("J4", "LIMIT XH-3", "base homing switch (5 V, SIG, GND)", 52.0, 46.2, 9.9, 9.8, 7.0, C["conn"], "OTHER")
add("J5", "PI-LINK Micro-Fit 7P", "locking: 2x 5.1 V, 3x GND, Pi TXD, Pi RXD", 64.0, 45.8, 24.0, 10.2, 9.9, C["mfit"], "5V1")
add("J6", "I2C XH-4", "spare 5 V I2C port (sensor / display)", 95.0, 46.2, 12.4, 9.8, 7.0, C["conn"], "I2C")

# ------------------------------------------------------------ 5.1 V Pi power (U4)
for k in range(2):
    add(f"C{17+k}", "22 µF 25 V", "U4 input MLCC", 66.0, 11.0 + 4.0 * k, 2.5, 3.2, 2.5, C["mlcc"], "12V", label=False)
add("U4", "TPS56837", "12 V -> 5.10 V Pi rail, 8 A synchronous buck", 70.0, 13.0, 3.0, 3.0, 1.0, C["ic"], "5V1")
add("C19,C24-C26,R23-R28", "U4 set parts", "FB 75k/10k (5.10 V), MODE 500 kHz, EN UVLO, SS, BOOT, FF, PG", 66.0, 6.5, 8.0, 3.0, 0.6, C["res"], "OTHER", cluster=True)
add("L1", "3.3 µH 15 A", "U4 power inductor (Würth 744325330)", 75.0, 9.0, 10.5, 10.2, 4.7, C["ind"], "5V1")
for k in range(4):
    add(f"C{20+k}", "22 µF 25 V", "U4 output MLCC", 87.0 + 3.0 * (k // 2), 10.0 + 4.0 * (k % 2), 2.5, 3.2, 2.5, C["mlcc"], "5V1", label=False)

# ------------------------------------------------------------ MCU, USB, UART
add("U1", "ATmega328P", "real-time controller: UART<-Pi, I2C->PCA9685, STEP/DIR->TMC2209", 72.0, 26.0, 9.0, 9.0, 1.2, C["ic"], "5V_MCU")
add("Y1", "16 MHz", "16 MHz MCU clock crystal", 82.5, 30.0, 3.2, 2.5, 0.8, C["usb"], "OTHER")
add("C29-C38,R4,R5,R13,R14,R31", "U1 parts", "crystal load caps, decoupling, reset pull-up, 12 V / 6 V sense dividers -> A0/A1", 72.0, 21.5, 9.0, 3.0, 0.6, C["res"], "OTHER", cluster=True)
add("J7", "ICSP 2x3", "burn the bootloader on new boards", 84.0, 35.0, 7.62, 5.08, 8.5, C["hdr"], "OTHER")
add("U7", "SN74LVC1T45", "Pi TXD 3.3 V -> MCU RXD 5 V", 72.0, 40.0, 2.9, 2.8, 1.1, C["ic"], "UART")
add("U8", "SN74LVC1T45", "MCU TXD 5 V -> Pi RXD 3.3 V (protects the Pi)", 76.0, 40.0, 2.9, 2.8, 1.1, C["ic"], "UART")
add("R39,C41-C44", "U7/U8 parts", "decoupling + Pi-TX idle pull-up", 80.0, 40.0, 3.0, 2.8, 0.6, C["res"], "UART", cluster=True)
add("U9", "TLV75533P", "5.1 V -> 3.3 V LDO for PCA9685, translators, VREF", 96.0, 30.0, 2.9, 2.8, 1.1, C["ic"], "3V3")
add("C27,C28", "1 µF x2", "LDO in/out caps", 99.5, 30.0, 2.0, 2.8, 0.6, C["res"], "3V3", cluster=True)
add("U6", "CH340C", "USB-UART for upload / debug (no crystal)", 94.0, 17.0, 6.0, 10.0, 1.7, C["ic"], "USB")
add("C39,C40", "100 nF x2", "CH340C decoupling", 101.0, 17.0, 2.0, 3.0, 0.6, C["res"], "USB", cluster=True)
add("D2,D3", "B5819W diode-OR", "5V1 / USB VBUS -> MCU 5 V; USB never back-feeds the Pi", 95.0, 9.0, 2.7, 4.1, 1.1, C["ic"], "5V_MCU", cluster=True)
add("R37,R38", "5.1k CC", "USB-C CC pull-downs (5 V source)", 103.5, 6.0, 2.5, 2.0, 0.6, C["res"], "USB", cluster=True)
add("J8", "USB-C", "PC programming / debug of the MCU", 107.65, 5.0, 7.35, 8.94, 3.2, C["usb"], "USB")
add("SW3", "RESET", "manual MCU reset", 109.5, 16.0, 5.1, 5.1, 1.5, C["sw"], "OTHER")
add("SW2", "SERIAL SEL", "MCU RX source: Pi (U7) or USB (U6)", 106.4, 24.0, 8.6, 3.6, 3.5, C["sw"], "UART")

HOLES = [("H1", PI_HOLES[0]), ("H2", PI_HOLES[1]), ("H3", PI_HOLES[2]), ("H4", PI_HOLES[3]),
         ("H5", EXTRA_HOLES[0]), ("H6", EXTRA_HOLES[1])]
SERVO_CH = ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY", "WRIST", "SPARE", "SPARE"]

def part(ref):
    return next(p for p in P if p["ref"] == ref)

def check():
    bad = 0
    for i, a in enumerate(P):
        for b in P[i + 1:]:
            if a["x"] < b["x"] + b["w"] - 1e-6 and b["x"] < a["x"] + a["w"] - 1e-6 and a["y"] < b["y"] + b["h"] - 1e-6 and b["y"] < a["y"] + a["h"] - 1e-6:
                print("OVERLAP", a["ref"], b["ref"]); bad += 1
        if a["x"] < 0 or a["y"] < 0 or a["x"] + a["w"] > BOARD_L + 0.01 or a["y"] + a["h"] > BOARD_W + 0.01:
            print("OUTSIDE", a["ref"]); bad += 1
        if a["zone"] == "underpi" and a["z"] > 12.0:
            print("TOO TALL UNDER PI", a["ref"], a["z"]); bad += 1
        for hn, (hx, hy) in HOLES:
            if a["x"] - 2.6 < hx < a["x"] + a["w"] + 2.6 and a["y"] - 2.6 < hy < a["y"] + a["h"] + 2.6:
                print("HOLE CLASH", hn, a["ref"]); bad += 1
    return bad

if __name__ == "__main__":
    print(check(), "problems,", len(P), "placed items")
