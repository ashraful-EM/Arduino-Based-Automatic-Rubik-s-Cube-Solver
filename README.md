# Arduino-Based Automatic Rubik's Cube Solver

An automated Rubik's Cube solving system developed using **Python, Arduino Mega 2560, computer vision, and a five-stepper-motor mechanical mechanism**.

The system captures cube colours through a camera, processes the cube configuration using the Kociemba solving algorithm, and sends motor-control commands to an Arduino Mega 2560 through serial communication.

**GitHub Repository:** [Arduino-Based Automatic Rubik's Cube Solver](https://github.com/ashraful-EM/Arduino-Based-Automatic-Rubik-s-Cube-Solver)

---

## Project Overview

This project implements an automatic Rubik's Cube solver combining computer vision, embedded systems, mechanical engineering, and software development.

The Python desktop application provides a graphical interface for cube generation, colour calibration, camera-based face scanning, solving, scrambling, and serial monitoring.

The Arduino controls five stepper motors through A4988 motor drivers to perform the required cube rotations.

### Key Features

- Camera-based Rubik's Cube colour detection.
- Six-colour HSV calibration.
- Automatic scanning of all six cube faces.
- Interactive graphical user interface.
- 3×3 cube face previews.
- Cube-state generation and validation through the solving process.
- Kociemba-based cube solving.
- Automatic scramble generation.
- Five-motor stepper control.
- Arduino serial communication at 115200 baud.
- Real-time serial monitoring.

---

## Project Demonstration

### Desktop Application

![Arduino Rubik's Cube Solver GUI](User%20Interface%281%29.png)

### Mechanical Design and Assembly

The following images show the supplied mechanical design and rendered views of the Rubik's Cube solver.

![Mechanical Design 1](IMG_0020%281%29.PNG)

![Mechanical Design 2](IMG_0021%281%29.PNG)

![Mechanical Design 3](IMG_0022.PNG)

![Mechanical Design 4](IMG_0023%281%29.PNG)

![Mechanical Design 5](IMG_0024.PNG)

![Mechanical Design 6](IMG_0025%281%29.PNG)

![Mechanical Design 7](IMG_0026.PNG)

---

## System Architecture

The project consists of two main software components:

**1. Python Desktop Application**
- Tkinter GUI
- OpenCV camera processing
- NumPy-based HSV colour calculations
- Kociemba solving algorithm
- PySerial communication
- Background serial-monitor thread

**2. Arduino Controller**
- Arduino Mega 2560
- Five A4988 motor drivers
- Five stepper motors
- Serial command processing
- Motor rotation control

### System Flowchart

![Project Flowchart](Flowchart%284%29.png)

### State Machine Diagram

![State Machine Diagram](State%20Machine%20Diagram%282%29.png)

---

## Hardware Components

| Component | Quantity |
|---|---:|
| Arduino Mega 2560 | 1 |
| A4988 Stepper Motor Driver | 5 |
| Stepper Motors | 5 |
| Webcam / Camera | 1 |
| Mechanical Cube Holder | 1 |
| 3D-Printed Base | 1 |
| Mechanical Couplers | As required |

### Motor Configuration

The Arduino firmware defines five motor channels:

| Cube Face | STEP | DIR | ENABLE |
|---|---:|---:|---:|
| Back (B) | 54 | 55 | 38 |
| Right (R) | 60 | 61 | 56 |
| Down (D) | 46 | 48 | 62 |
| Left (L) | 26 | 28 | 24 |
| Front (F) | 36 | 34 | 30 |

These assignments are taken directly from the supplied Arduino firmware. Verify the actual wiring before operation.

### Circuit Diagram

[Schematic(3).pdf](Schematic%283%29.pdf)

### Mechanical Design Files

- [Base.stl](Base.stl)
- [Coupler.stl](Coupler.stl)
- [laser_cut.pdf](laser_cut.pdf)

---

## Software and Technologies

| Technology | Purpose |
|---|---|
| Python | Main application |
| Tkinter | Graphical user interface |
| OpenCV | Camera and image processing |
| NumPy | HSV colour calculations |
| Kociemba | Rubik's Cube solving algorithm |
| PySerial | Arduino serial communication |
| Pillow | Camera image display |
| Arduino C/C++ | Embedded motor-control firmware |

---

## Working Principle

### 1. Application Initialization

The Python application initializes the GUI, default cube colours, camera controls, and serial-monitor interface.

### 2. Camera Calibration

The camera calibrates six reference colours:

- White (W)
- Yellow (Y)
- Green (G)
- Blue (B)
- Red (R)
- Orange (O)

The application stores the average HSV values of the captured colour samples.

### 3. Cube Scanning

The camera captures each cube face using a 3×3 scanning grid.

The application calculates the average HSV values of individual sticker regions and compares them with the calibrated colours.

The detected face configuration is then displayed in the GUI.

### 4. Cube-State Generation

The application converts the detected colour information into the face notation required by the Kociemba solver.

The cube string is assembled in the order:

`U R F D L B`

### 5. Cube Solving

The application uses:

`kociemba.solve(cube_string)`

The resulting solution is parsed into individual moves and prepared for the Arduino controller.

### 6. Cube Scrambling

The application generates a scramble sequence by reversing and inverting the calculated solution moves.

A special `S` marker is appended to identify scramble commands.

### 7. Motor Control

The Python application sends the move sequence through serial communication.

The Arduino receives the command and activates the corresponding stepper motor to rotate the selected cube face.

### 8. Serial Monitoring

The Python application receives Arduino responses through a background thread and displays the information in the Serial Monitor interface.

---

## Installation and Setup

### Requirements

- Python 3
- Arduino IDE
- Arduino Mega 2560
- Webcam
- Five stepper motors and A4988 drivers

### Install Python Dependencies

Open a terminal and execute:

```bash
python -m pip install kociemba pyserial opencv-python numpy Pillow
```

Tkinter is also required. It is included with many Python installations; some Linux distributions require a separate Tkinter package.

### Run the Python Application

```bash
python "python(2).py"
```

### Upload Arduino Firmware

1. Open `arduino(2).ino` in Arduino IDE.
2. Select Arduino Mega 2560.
3. Select the appropriate COM port.
4. Verify the motor connections and pin assignments.
5. Upload the firmware.

### Operating Procedure

1. Connect the Arduino to the computer.
2. Open the Python application.
3. Select the appropriate serial port.
4. Click Refresh if the port list needs updating.
5. Start camera calibration.
6. Capture all six reference colours.
7. Scan all six Rubik's Cube faces.
8. Review the generated cube previews.
9. Select Solve or Scramble.
10. Monitor the Arduino responses through the Serial Monitor.

---

## Serial Communication

The application and Arduino communicate using serial communication at:

**Baud Rate: 115200**

The Python application sends space-separated move commands terminated by a newline.

For scrambling, the command includes a trailing `S` marker.

The Arduino firmware processes the received command and executes the supported motor movements.

The firmware contains motor handlers for the F, B, L, D, and R faces. The Python application translates U-face turns into sequences of supported face turns before transmission.

---

## Repository Structure

```text
Arduino-Based-Automatic-Rubik-s-Cube-Solver/
│
├── python(2).py
├── arduino(2).ino
│
├── Base.stl
├── Coupler.stl
├── laser_cut.pdf
├── Schematic(3).pdf
│
├── Flowchart(4).png
├── State Machine Diagram(2).png
├── User Interface(1).png
│
├── IMG_0020(1).PNG
├── IMG_0021(1).PNG
├── IMG_0022.PNG
├── IMG_0023(1).PNG
├── IMG_0024.PNG
├── IMG_0025(1).PNG
└── IMG_0026.PNG
```

The original demonstration video was also supplied as `video_20260523_095408.mp4`.

It is approximately 168 MB, exceeding GitHub's 100 MB limit for a regular Git file. It should be published separately using Git LFS or a video-hosting service.

---

## Technical Notes

- The camera is opened using OpenCV device index `0`.
- Serial communication uses 115200 baud.
- The Arduino firmware defines `STEPS_PER_REV` as 200.
- Motor step counts are calculated for quarter, half, and three-quarter turns.
- Cube face input is checked for nine characters and supported colour letters before the cube string is generated.
- The Kociemba solver processes the resulting cube configuration.
- Actual motor accuracy depends on the motor, driver configuration, mechanical alignment, and calibration.

Verify motor wiring, driver current limits, power supply requirements, and mechanical clearances before operating the machine.

---

## Future Improvements

- Improve colour detection under changing lighting conditions.
- Add more comprehensive hardware documentation.
- Improve motor movement calibration.
- Add automated tests for cube-state conversion and move translation.
- Improve the graphical user interface.
- Add detailed troubleshooting documentation.

---

## Acknowledgements

- [Kociemba Rubik's Cube Solver](https://pypi.org/project/kociemba/)
- [OpenCV](https://opencv.org/)
- [Arduino](https://www.arduino.cc/)
- [Python](https://www.python.org/)

---

**Developed as an interdisciplinary engineering project integrating computer vision, embedded systems, mechanical design, and software development.**
