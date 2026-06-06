# AI Virtual Mouse — Hand Gesture Controller

A computer vision-based application that turns your webcam into a fully functional virtual mouse. Built using Python, OpenCV, and Google's MediaPipe, this project tracks your hand in 3D space to control your PC cursor and trigger actions using intuitive hand gestures.

## ✨ Features

* **Full Mouse Emulation:** Supports left-click, right-click, scrolling, and seamless drag-and-drop mechanics.
* **Keyboard Shortcuts & OSK:** Includes gesture triggers for screen capture and the Windows On-Screen Keyboard.
* **Auto-Admin Elevation:** Automatically requests Administrator privileges on startup to ensure PyAutoGUI can interact with elevated Windows elements (like the On-Screen Keyboard). This can be turned off by removing/commenting ADMIN ELEVATION CHECK block

---

## 🛠️ Requirements & Setup

### Prerequisites
* **Python 3.9+** (Tested and recommended for MediaPipe Model Maker compatibility)
* A working webcam
* Windows OS (Required for the On-Screen Keyboard toggle feature)

### Installation (1-Click Method)
1. Clone or download this repository.
2. Double-click the `Install_Setup.bat` file. This will automatically install all required dependencies from the `requirements.txt` file.
3. *Ensure the `gesture_recognizer.task` model file is in the same folder as the Python script.*

### Manual Installation
If you prefer using the command line:
```bash
pip install opencv-python mediapipe pyautogui pydirectinput numpy
```

### Run the script

```Bash

python HandControllerFinal.py
```
Or simply double click the HandControllerFinal.py in File Explorer
The script will request Administrator privileges. Click Yes to allow it to control the Windows On-Screen Keyboard.

### How to use
Position your hand in front of the camera and start gesturing!

To quit, bring focus to the webcam feed window and press 'q'.

**Camera & Gesture Setup:**
- The application uses a fixed camera resolution of 1280x720 for consistent performance
- Adjust `SCREEN_MARGIN_PERCENT` in the code (default: 15%)
  - **10-12%** = Larger usable area, better for gestures near edges
  - **15%** = Balanced (recommended default)
  - **20-25%** = Smaller area, safer for beginners
  - **Set to 0** = 100% coverage (no margin, use with caution)
- Adjust `DISPLAY_WIDTH` and `DISPLAY_HEIGHT` to resize the camera feed window (default: 1024x768)
  - Set to **0** = Use original camera resolution
  - Recommended for laptops: 800x600 or 1024x768
  - Recommended for larger screens: 1280x720 or 1536x1080

To change settings: Edit `HandControllerFinal.py`, find the configuration section, and adjust the values.

### Gesture Control Map

| Gesture | Action | Description |
| :--- | :--- | :--- |
| **Index Pointing Up** | **Left Click** | Triggers a standard left mouse click. |
| **Victory (V-Sign)** | **Right Click** | Triggers a right mouse click (context menu). |
| **Open Palm** | **Grab / Hold** | Triggers `mouseDown` to grab windows or text. |
| **Closed Fist** | **Drop / Release** | Triggers `mouseUp` to release the item. |
| **Thumb Up** | **Scroll Up** | Smoothly scrolls the active page upwards. |
| **Thumb Down** | **Scroll Down** | Smoothly scrolls the active page downwards. |
| **OK Sign** | **Take screenshots** | Take screenshots and save it to the SCREENSHOT_FOLDER. |
| **"I Love You" Sign** | **Toggle Windows OSK** | Opens or closes the Windows On-Screen Keyboard. |
