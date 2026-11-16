# Electronics version 2: USB-only board, 3 smart servos

Current plan. Pre-schematic. Values marked "not verified" in the study guide are still open.

## Idea
- A Windows PC runs Python, OpenCV and MediaPipe hand tracking and sends a few numbers per frame over **one USB cable**.
- The custom board turns them into servo commands and drives the servo bus directly. The 12 V supply and the servos are outside the board.
- Modes: follow the PC (mirror the hand, rock-paper-scissors) and idle (stored gestures when no PC data arrives).

## Data path
PC (USB) > CH340C > ATmega328PB UART0 | ATmega328PB UART1 > half-duplex TTL circuit (tri-state buffer) > servo bus P1, P2 > 5 x STS3215 (IDs 1 to 5, 12 V)

The SC16IS750 and the separate Waveshare adapter were removed on 2026-11-16 (board developer's proposal). The 12 V input, fuse and servo connectors are now on the board.

## Motors
Current direction (2026-11-16): **5 x STS3215, one per finger, in the forearm**, controller board in the base. Details in [dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md](dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md).

The earlier 3-servo grouping (thumb; index + middle; ring + pinky) stays possible in firmware. It makes rock, paper and scissors work, but pointing with one finger needs 5 servos.

## Files
| File | What |
|---|---|
| [dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md](dona_univ_robot_hand_2026-11-16_Sanjev_decisions.md) | Motors, forearm size, board location, board spec for the developer |
| [dona_univ_robot_hand_2026-11-16_Sanjev_wiring_diagrams.docx](dona_univ_robot_hand_2026-11-16_Sanjev_wiring_diagrams.docx) | Wiring, block and power diagrams with explanation (English). |
| [동아대_robot_hand_2026-11-16_산지브_wiring_diagrams.docx](동아대_robot_hand_2026-11-16_산지브_wiring_diagrams.docx) | Same document in Korean |
| [dona_univ_robot_hand_2026-11-14_Sanjev_haebot_robot_hand_study_guide.docx](dona_univ_robot_hand_2026-11-14_Sanjev_haebot_robot_hand_study_guide.docx) | Browsable study guide from electronics to software, with diagrams and source links |

## Open items
- Half-duplex circuit details (buffer part, data-line pull-up) to be set by the board developer against the STS3215 manual.
- Bus logic level and speed with an ATmega328PB at 5 V (1 Mbps default) to be verified.
- 12 V path on the board: copper, DC jack, fuse and P1, P2 connectors rated for stall current (about 13.5 A for 5 servos).
- USB connector type (C or B) pending the board developer's question.
- Fit of 5 STS3215 in a new forearm servo bed (check in CAD).

Version 1 (archived): [../version_1/](../version_1/)
