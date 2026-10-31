# System architecture and workflow

The system is organized into three cooperating parts:

1. **Python desktop application** — Tkinter GUI, six-face color entry and preview, camera calibration/scanning with OpenCV and NumPy, Kociemba solution generation, and serial command transmission/monitoring.
2. **Arduino firmware** — receives a newline-terminated move string at 115200 baud, parses individual face moves, and drives five stepper-driver channels (B, R, D, L, F).
3. **Mechanical assembly** — five motor-driven cube interfaces mounted around the cube, with a base and coupler represented by the supplied STL models and a laser-cut layout PDF.

## Main application workflow

1. Initialize the GUI and default six-face color grids.
2. Optionally calibrate the camera against W, Y, G, B, R, and O reference colors.
3. Capture the six faces in `U, D, L, R, F, B` order or enter them manually.
4. Convert the colors to Kociemba face letters and build the cube string in `U, R, F, D, L, B` order.
5. Validate and solve the cube, or derive inverse moves for scrambling.
6. Send the move sequence to the Arduino over serial and monitor Arduino messages.

See `images/application-flowchart.png` and `images/state-machine-diagram.png` for the supplied diagrams. These diagrams document the intended workflow; the source code remains the executable reference.
