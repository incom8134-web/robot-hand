# Electronics version 2: USB-only board, 3 smart servos

Current plan. Pre-schematic. Values marked "not verified" in the study guide are still open.

## Idea
- A Windows PC runs Python, OpenCV and MediaPipe hand tracking and sends a few numbers per frame over **one USB cable**.
- The custom board turns them into servo commands. The Waveshare Bus Servo Adapter (A) and the 12 V servo supply are **separate modules, not on the board**.
- Modes: follow the PC (mirror the hand, rock-paper-scissors) and idle (stored gestures when no PC data arrives).

## Data path
PC (USB) > CH340C > ATmega328P > SPI > SC16IS750 > UART > Waveshare Adapter (A, jumper A) > 3 x STS3215 (IDs 1, 2, 3, 12 V)

## Hand grouping (3 servos)
| Servo | Fingers |
|---|---|
| 1 | Thumb |
| 2 | Index + middle |
| 3 | Ring + pinky |

Rock, paper and scissors work. Pointing with one finger does not.

## Files
| File | What |
|---|---|
| [HAEBOT_controller_board_EN.docx](HAEBOT_controller_board_EN.docx) | Wiring, block and power diagrams with explanation (English) |
| [HAEBOT_controller_board_KO.docx](HAEBOT_controller_board_KO.docx) | Same document in Korean |
| [HAEBOT_Robot_Hand_Study_Guide.docx](HAEBOT_Robot_Hand_Study_Guide.docx) | Browsable study guide from electronics to software, with diagrams and source links |

## Open items
- SC16IS750 clock range for exactly 1 Mbps (derived, not read from the datasheet).
- SC16IS750 5 V input tolerance when unpowered.
- Current rating of the adapter's DC jack and terminal (not published).
- Palm width for the 3-servo layout (check against CAD).
- The board developer's sketch differs from this plan (single board, no separate adapter). To be reconciled.

Version 1 (archived): [../version_1/](../version_1/)
