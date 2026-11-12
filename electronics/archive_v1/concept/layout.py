"""Single source of truth for the HAEBOT Hand Controller v1.0 concept layout.

All coordinates in mm, origin = bottom-left corner of the controller board (top view).
x runs along the 115 mm length, y across the 56 mm width.  The Raspberry Pi 5 sits on
top of the right-hand 85 mm (x = 30 .. 115); the left 30 mm (the "open zone") is not
covered by the Pi and holds everything a student touches or that runs hot / tall.

This is a CONCEPT placement for drawings and the 3D mock-up, not a routed PCB.
"""

BOARD_L, BOARD_W, BOARD_T = 115.0, 56.0, 1.6
PI_X0 = 30.0                        # Pi 5 left edge (SD-card end) on our board
PI_L, PI_W = 85.0, 56.0
STANDOFF_H = 18.0                   # M2.5 x 18 mm brass standoffs
PI_HOLES = [(PI_X0 + 3.5, 3.5), (PI_X0 + 61.5, 3.5), (PI_X0 + 3.5, 52.5), (PI_X0 + 61.5, 52.5)]
EXTRA_HOLES = [(27.5, 7.0), (27.5, 49.0)]   # support the open zone (M2.5)

# Pi 5 40-pin header (on the Pi's TOP side): pin 1 at Pi (8.37, 51.27) approx.
PI_HDR = dict(x=PI_X0 + 7.0, y=49.9, w=50.8, h=5.1)

# colours
C = dict(
    term="#1f9d55", fuse_h="#222222", fuse="#d62828", hdr="#151515", pin="#d4af37",
    ic="#2a2e33", conn="#efe6cf", usb="#c0c0c0", mod_red="#b3202a", mod_blue="#1d4f91",
    sink="#b8bcc2", cap="#20304a", cap2="#3a3a3a", sw="#2b2b2b", sw_act="#e5e5e5",
    tvs="#303030", led_r="#ff3030", led_o="#ff9a1f", led_g="#2fd34a", led_b="#2f7bff", led_y="#ffd21f",
)

# kind: box | cyl ; group used for colouring in 2D sketch and legend
# fields: ref, label, x, y, w, h, z(height above PCB), color, group, zone(open|underpi), note
P = []
def add(ref, label, x, y, w, h, z, color, group, note="", kind="box"):
    P.append(dict(ref=ref, label=label, x=x, y=y, w=w, h=h, z=z, color=color, group=group, note=note, kind=kind,
                  zone="open" if x + w / 2 < PI_X0 else "underpi"))

# ---- open zone (x 0..30) ----
add("J1", "12V IN", 0.0, 1.5, 7.6, 10.2, 10.0, C["term"], "power", "2P 5.08 mm screw terminal, wire entry from the left")
add("F1", "FUSE 10A", 9.5, 2.5, 13.0, 6.5, 6.0, C["fuse_h"], "power", "ATM mini-blade fuse holder, 10 A blade")
add("J10", "SERVO x10", 19.6, 13.0, 7.8, 25.4, 8.5, C["hdr"], "servo", "10 x 3-pin 2.54 mm (S / V+ / G), CH0..CH9")
add("U5", "A4988", 4.0, 40.2, 20.3, 15.2, 18.0, C["mod_red"], "stepper", "StepStick A4988 in 2 x 1x8 female sockets + heatsink")
add("JP1", "MS1-3", 9.0, 44.5, 5.1, 7.6, 8.5, C["hdr"], "stepper", "micro-step jumpers (under the driver, CNC-shield style)")

# ---- under the Pi (x 30..115), everything <= 12 mm tall ----
add("Q1", "REV-POL PFET", 31.5, 8.0, 5.0, 6.0, 1.7, C["ic"], "power", "AO4407A P-MOSFET: reverse-polarity + soft power switch")
add("D7", "TVS", 31.5, 15.0, 5.4, 3.6, 2.3, C["tvs"], "power", "SMBJ15A on the 12 V input")
add("U2", "PCA9685", 31.3, 19.5, 6.4, 9.7, 1.2, C["ic"], "servo", "16-ch PWM, TSSOP-28, I2C addr 0x40")
add("C1", "1000uF", 30.5, 30.0, 8.0, 8.0, 11.5, C["cap"], "servo", "servo rail bulk cap 1000 uF / 10 V low-ESR", kind="cyl")
add("C2", "100uF", 31.35, 41.35, 6.3, 6.3, 7.7, C["cap2"], "stepper", "VMOT cap 100 uF / 25 V next to the A4988", kind="cyl")
add("U3", "BUCK 6V 5A", 41.0, 9.0, 25.4, 25.4, 12.0, C["mod_blue"], "power", "Pololu D36V50F6 footprint (v1) - servo rail")
add("U4", "BUCK 5V 5A", 68.0, 9.0, 25.4, 25.4, 12.0, C["mod_blue"], "power", "Pololu D36V50F5 footprint (v1) - Pi + logic")
add("F2", "PTC 6V", 41.0, 37.0, 7.5, 5.0, 1.5, C["ic"], "power", "servo rail fuse (2920 PTC / SMD fuse)")
add("F3", "PTC 5V", 50.0, 37.0, 7.5, 5.0, 1.5, C["ic"], "power", "5 V rail fuse")
add("F4", "F 3A", 59.0, 37.5, 3.2, 1.6, 1.0, C["ic"], "power", "12 V motor branch fuse")
add("U7", "LVL", 60.0, 43.0, 3.0, 3.0, 1.1, C["ic"], "mcu", "74AHCT1G125 (Pi TX -> MCU RX) + 1k/2k divider (MCU TX -> Pi RX)")
add("U1", "ATmega328P", 66.0, 38.0, 9.0, 9.0, 1.2, C["ic"], "mcu", "TQFP-32, 16 MHz, Nano-compatible bootloader")
add("Y1", "16MHz", 77.0, 41.0, 3.2, 2.5, 0.8, C["usb"], "mcu", "16 MHz crystal")
add("J8", "ICSP", 82.0, 38.0, 5.1, 7.6, 8.5, C["hdr"], "mcu", "2x3 ICSP (bootloader burn)")
add("U6", "CH340C", 97.0, 14.0, 6.0, 10.0, 1.7, C["ic"], "mcu", "USB-UART, SOP-16, no crystal needed")
add("D8", "OR", 95.0, 27.5, 2.7, 1.6, 1.1, C["ic"], "power", "2x Schottky diode-OR: USB VBUS / 5 V rail -> MCU 5 V")
add("J9", "USB-C", 107.65, 5.0, 7.35, 8.94, 3.2, C["usb"], "mcu", "USB-C (CH340) - program / debug")
add("SW3", "RESET", 109.0, 17.0, 6.0, 6.0, 3.5, C["sw"], "mcu", "right-angle tact switch")
add("SW2", "SERIAL SEL", 108.0, 26.0, 7.0, 9.0, 4.0, C["sw"], "mcu", "DPDT slide: MCU UART <-> USB (CH340) or Pi")
add("J4", "MOTOR", 37.0, 49.5, 12.4, 6.5, 7.0, C["conn"], "stepper", "JST-XH 4P side-entry: NEMA17 A+ A- B+ B-")
add("J5", "LIMIT", 51.0, 49.5, 9.9, 6.5, 7.0, C["conn"], "stepper", "JST-XH 3P side-entry: 5V / SIG / GND (base home switch)")
add("J6", "PI-LINK", 63.0, 49.5, 19.9, 6.5, 7.0, C["conn"], "pi", "JST-XH 7P side-entry: 5V 5V GND GND TX RX RST -> Pi pins 1-10")
add("J7", "I2C", 95.0, 49.5, 12.4, 6.5, 7.0, C["conn"], "io", "JST-XH 4P side-entry: 5V SDA SCL GND (spare)")
add("SW1", "POWER", 37.0, 0.0, 9.0, 5.0, 4.0, C["sw"], "power", "slide switch drives Q1 gate (logic-level, not load current)")
for i, (nm, col) in enumerate([("12V", C["led_r"]), ("6V", C["led_o"]), ("5V", C["led_g"]),
                               ("STAT", C["led_b"]), ("TX", C["led_y"]), ("RX", C["led_y"])]):
    add(f"D{i+1}", nm, 49.0 + i * 2.4, 0.0, 1.6, 1.2, 0.9, col, "led", "side-view LED, visible from the board edge")

SERVO_CH = ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY", "WRIST", "SP1", "SP2", "SP3", "SP4"]

def part(ref):
    return next(p for p in P if p["ref"] == ref)

if __name__ == "__main__":
    # crude overlap check
    boxes = [p for p in P if p["ref"] not in ("JP1",)]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]:
                print("OVERLAP", a["ref"], b["ref"])
        if a["x"] < 0 or a["y"] < 0 or a["x"] + a["w"] > BOARD_L + 0.01 or a["y"] + a["h"] > BOARD_W + 0.01:
            print("OUTSIDE", a["ref"])
    for hx, hy in PI_HOLES + EXTRA_HOLES:
        for a in boxes:
            if a["x"] - 2.6 < hx < a["x"] + a["w"] + 2.6 and a["y"] - 2.6 < hy < a["y"] + a["h"] + 2.6:
                print("HOLE CLASH", (hx, hy), a["ref"])
    print(len(P), "parts")
