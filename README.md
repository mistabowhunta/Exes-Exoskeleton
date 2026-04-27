# Project Exes: Voice-Activated Distributed Exoskeleton (Archived Prototype)

<div style="display: flex; justify-content: center; gap: 20px;">
  <figure style="text-align: center; width: 45%;">
    <img src="/src/images/Exes-ExoSkeleton-Combined-Cropped.png" alt="Components" style="width: 100%; border-radius: 8px;">
    <figcaption><em>Components (Load-Testing Configuration)</em></figcaption>
  </figure>
</div>

## Overview
**Exes** is an archived hardware and software R&D project focused on building a high-torque, voice-controlled robotic exoskeleton. 

The physical framework was built upon a rigid motocross chassis using 2020 aluminum extrusions, actuated by 550KG servo motors. To handle the massive computational and telemetry overhead, the software architecture utilizes a distributed IoT network, replacing standard synchronous serial loops with an asynchronous MQTT broker and a multi-tiered power delivery system.

> **Status: Archived.** The electrical and software architectures successfully drove the physical hardware; however, the physical project was decommissioned after the 550KG servos exceeded the yield strength of the custom 3D-printed PLA mounting hardware. Read the **Post-Mortem** below for details.

## System Architecture

### 1. Distributed Telemetry (MQTT & Pico W)
To eliminate heavy sensor wiring across the suit's joints, the exoskeleton operates on a localized wireless network.
* **Peripheral Nodes:** Raspberry Pi Pico W microcontrollers are embedded in the extremities. They interface via I2C with BNO085 sensor fusion modules (handling complex quaternion/Euler math on-chip) and publish kinematic data to a localized MQTT broker.
* **Central Command:** A Raspberry Pi 4b acts as the master hub. It runs a non-blocking, thread-safe queue worker (`code.py`) that subscribes to the MQTT sensor streams, maps the telemetry to calibrated limits, and commands the localized servos without bottlenecking the OS.

### 2. Offline Voice Pipeline (Picovoice)
The suit features a fully localized, zero-latency voice command interface, eliminating the need for cloud API calls.
* **Wake Word:** Picovoice *Porcupine* continuously listens for the wake word "Exes" with minimal CPU overhead.
* **Intent Inference:** Picovoice *Rhino* translates complex spoken commands (e.g., Calibrate, Deactivate, Battery Status, Move Up Left Up, many more..) into actionable JSON state-machine transitions. 
* **Audio Feedback:** A dedicated `audio_controller` feeds synthesized status updates, warnings, and acknowledgments back to the user via a mounted speaker.

### 3. Power & Actuation Isolation
High-torque robotics require strict power segregation to prevent logic board brownouts during actuation.
* **Dual Power Delivery:** Two independent 20V batteries power the suit. One is dedicated entirely to the logic; the other is dedicated solely to the servo load.
* **Regulation & Monitoring:** 20A 300W Buck Converters step down the voltage. An ACS712 current sensor and an ADS1115 ADC allow the Pi to digitally monitor battery health and trigger audio warnings before voltage drops critically low.
* **PWM Offloading:** To prevent Linux kernel jitter from causing erratic joint movements, a PCA9685 16-channel I2C controller handles all precise PWM signal generation for the 550KG servos.

## Post-Mortem & Mechanical Yield
This repository is archived due to a material science limitation encountered during physical load testing.

The asynchronous software queue, the MQTT telemetry pipeline, and the dual-isolated power delivery systems functioned flawlessly under load. However, the 550KG servos generated torque that vastly exceeded the physical limits of the chassis integration. The custom 3D-printed PLA flange plates and lazy susans (designed to distribute the load across the fabric motocross jacket) suffered mechanical yield and catastrophic pull-out. 

Future iterations of this platform would require CNC-machined aluminum mounting brackets and a rigid, non-fabric backplate to safely harness the output of the actuators.

## Repository Structure
* `code.py`: The main execution loop, utilizing a thread-safe Queue to handle rapid MQTT sensor telemetry without OS process fork-bombing.
* `/src/controllers`: Modularized logic for Audio, Sensors, Servos, and Error handling.
* `/src/lib`: Hardware abstraction, environment configuration, and dynamic calibration math.
* `/src/images`: Main image.
