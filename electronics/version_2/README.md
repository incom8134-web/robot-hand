# Electronics version 2: USB-only board, 3 smart servos

Current plan. Pre-schematic. Values marked "not verified" in the study guide are still open.

## Idea
- A Windows PC runs Python, OpenCV and MediaPipe hand tracking and sends a few numbers per frame over **one USB cable**.
- The custom board turns them into servo commands. The Waveshare Bus Servo Adapter (A) and the 12 V servo supply are **separate modules, not on the board**.
- Modes: follow the PC (mirror the hand, rock-paper-scissors) and idle (stored gestures when no PC data arrives).

## Data path
PC (USB) > CH340C > ATmega328P > SPI > SC16IS750 > UART > Waveshare Adapter (A, jumper A) > 3 x STS3215 (IDs 1, 2, 3, 12 V)

## Motors
Current direction (2026-11-16): **5 x STS3215, one per finger, in the forearm**, controller board in the base. Details in [HAEBOT_2026-11-16_Khurshidbek_design-decisions.md](HAEBOT_2026-11-16_Khurshidbek_design-decisions.md).

The earlier 3-servo grouping (thumb; index + middle; ring + pinky) stays possible in firmware. It makes rock, paper and scissors work, but pointing with one finger needs 5 servos.

## Files
| File | What |
|---|---|
| [HAEBOT_2026-11-16_Khurshidbek_design-decisions.md](HAEBOT_2026-11-16_Khurshidbek_design-decisions.md) | Motors, forearm size, board location, board spec for the developer |
| [HAEBOT_controller_board_EN.docx](HAEBOT_controller_board_EN.docx) | Wiring, block and power diagrams with explanation (English). Drawn for 3 servos; to be updated for 5. |
| [HAEBOT_controller_board_KO.docx](HAEBOT_controller_board_KO.docx) | Same document in Korean |
| [HAEBOT_Robot_Hand_Study_Guide.docx](HAEBOT_Robot_Hand_Study_Guide.docx) | Browsable study guide from electronics to software, with diagrams and source links |

## Open items
- SC16IS750 clock range for exactly 1 Mbps (derived, not read from the datasheet).
- SC16IS750 5 V input tolerance when unpowered.
- Current rating of the adapter's DC jack and terminal (not published).
- Fit of 5 STS3215 in a new forearm servo bed (check in CAD).
- The board developer's sketch differs from this plan (single board, no separate adapter). To be reconciled.

Version 1 (archived): [../version_1/](../version_1/)
