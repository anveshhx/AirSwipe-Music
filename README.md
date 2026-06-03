# AirSwipe Music

A computer vision based gesture-controlled music system that allows users to control media playback using hand gestures captured through a webcam.

Built using Python, OpenCV, and MediaPipe, AirSwipe eliminates the need for physical interaction by translating hand movements into media commands in real time.

---

## Features

### Version 1

* Hand detection using MediaPipe
* Real-time webcam tracking

### Version 2

* Swipe gesture recognition
* Next Track
* Previous Track

### Version 3

* Open palm detection
* Play / Pause control
* Gesture cooldown system

### Version 4

* Peace sign recognition
* Volume Up control
* Volume Down control

## Version 5 (Final Version)

* Added a modern on-screen user interface overlay
* Integrated real-time Spotify song and artist display
* Added playback progress tracking
* Added gesture status notifications
* Improved overall visual experience and usability
* Enhanced project structure and code organization
* Combined computer vision controls with live media information into a single application

---

## Gesture Controls

| Gesture                   | Action             |
| ------------------------- | ------------------ |
| ✋ Open Palm (hold)        | Play / Pause Music |
| 👉 Swipe Right            | Next Track         |
| 👈 Swipe Left             | Previous Track     |
| ✌️ Peace Sign + Move Up   | Volume Up          |
| ✌️ Peace Sign + Move Down | Volume Down        |




---

## Technologies Used

* Python
* OpenCV
* MediaPipe
* PyAutoGUI
* WinSDK
* NumPy

---

## Project Structure

```text
AirSwipe/
│
├── README.md
├── requirements.txt
│
├── Versions/
│   ├── airswipev1.py
│   ├── airswipev2.py
│   ├── airswipev3_stable.py
│   ├── airswipev4.py
│   └── AirSwipe_V5.py
│
└── Experiments/
    ├── spotify_test.py
    ├── spotify_live_test.py
    ├── spotify_advanced_test.py
    └── camera_test.py
```

---

## Installation

Clone the repository:

```bash
git clone <your-github-link>
cd AirSwipe
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python AirSwipe_V5.py
```

---

## Future Improvements

* Album artwork integration
* Dynamic gesture customization
* Multi-hand support
* Custom themes
* Gesture analytics dashboard
* Cross-platform support
* Smart gesture calibration

---

## Author

**Anvesh**

Computer Vision • Python • AI Projects

Developed as a practical exploration of gesture recognition, human-computer interaction, and real-time media control using computer vision.
