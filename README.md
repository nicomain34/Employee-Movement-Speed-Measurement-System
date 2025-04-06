Overview
This project is a real-time speed detection system that tracks employee movement on a production line using a camera. The system measures the movement speed of operators, and if the speed exceeds a predefined threshold, an alert sound is triggered. The system helps ensure safety and quality control by detecting potentially damaging movements.

Features
Speed Detection: Tracks employee movement speed in pixels per second.

Alert System: Triggers an alert if the speed exceeds a predefined threshold to minimize the risk of damage to products.

Static Detection: Ignores the alert if the object has not moved significantly.

Real-time Monitoring: Uses OpenCV to process video streams and provides visual feedback for tracking speed.

Interactive Zone: Users can define a specific area on the screen where detection takes place using mouse drag.

Requirements
Python 3.x
OpenCV
Pygame (for sound alerts)
NumPy


How It Works
The program captures the video stream from a camera using RTSP.

A predefined area is set up where movement speed is measured.

The program tracks moving objects and calculates their speed based on the frame difference.

If the speed exceeds the threshold, an alert is triggered via a sound and a visual message on the screen.

You can interactively adjust the detection zone using mouse drag.

License
This project is licensed under the MIT License.

Authors
Dmytro Zavolovych

