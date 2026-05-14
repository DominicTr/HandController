import cv2
import mediapipe as mp
import time
import pyautogui
import pydirectinput
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

import ctypes
import sys

pyautogui.FAILSAFE = False

# Hides all non-critical C++ backend logs (like Clearcut/TensorFlow)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['MEDIAPIPE_DISABLE_GPU'] = '1' # Sometimes helps stabilize logs on school PCs

# --- ADMIN ELEVATION CHECK ---
#COMMENT OUT THIS BLOCK IF YOU DON'T WANT THE PROGRAM TO REQUEST ADMIN RIGHTS (required for OSK toggle and some input features)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Requesting Administrator privileges...")
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()
# -----------------------------

# --- CONFIGURATION ---
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SMOOTHING = 5
SCROLL_SPEED = 300
MOVE_THRESHOLD = 50
SCREEN_MARGIN = 100 # change this if you want to adjust the active area for mouse movement (default 300px margin on all sides)
SCREENSHOT_FOLDER = 'screenshots'

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),    # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),    # Index
    (9, 10), (10, 11), (11, 12),       # Middle
    (13, 14), (14, 15), (15, 16),      # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17)          # Palm
]

# Global state
latest_landmarks = None
latest_gesture = None

# Gesture action state (debounce flags)
is_clicking = False
is_right_clicking = False
mouse_pressed = False
is_scrolling_up = False
is_scrolling_down = False
is_capping = False
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# --- MediaPipe Callback ---

def result_callback(result: vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global latest_landmarks, latest_gesture
    latest_landmarks = result.hand_landmarks if result.hand_landmarks else None
    if result.gestures:
        latest_gesture = result.gestures[0][0].category_name


# --- create screenshots folder if it doesn't exist ---

if not os.path.exists(SCREENSHOT_FOLDER):
    os.makedirs(SCREENSHOT_FOLDER)

# --- Gesture Action Handlers ---

def on_left_click():
    pydirectinput.click()


def on_right_click():
    pydirectinput.click(button='right')


def on_scroll_up():
    pyautogui.scroll(SCROLL_SPEED)


def on_scroll_down():
    pyautogui.scroll(-SCROLL_SPEED)

def on_screenshot():
    pyautogui.screenshot(f'{SCREENSHOT_FOLDER}/screenshot_{int(time.time())}.png')


# --- UI Functions ---

def draw_hand_skeleton(frame, frame_h, frame_w):
    if latest_landmarks:
        for hand_landmarks in latest_landmarks:
            for connection in HAND_CONNECTIONS:
                p1 = hand_landmarks[connection[0]]
                p2 = hand_landmarks[connection[1]]
                cv2.line(frame,
                         (int(p1.x * frame_w), int(p1.y * frame_h)),
                         (int(p2.x * frame_w), int(p2.y * frame_h)),
                         (0, 255, 0), 2)
            for lm in hand_landmarks:
                cv2.circle(frame,
                           (int(lm.x * frame_w), int(lm.y * frame_h)),
                           4, (0, 0, 255), -1)


def draw_cursor(frame, palm_hand, frame_h, frame_w):
    screen_x = int(palm_hand.x * frame_w)
    screen_y = int(palm_hand.y * frame_h)
    cv2.circle(frame, (screen_x, screen_y), 15, (255, 0, 255), -1)


def draw_gesture_label(frame, current_gesture):
    cv2.putText(frame, f"Gesture: {current_gesture}", (20, 60),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)


def draw_no_hand(frame):
    cv2.putText(frame, "No hand detected", (20, 60),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 100, 100), 2)
    
def draw_screenshot(frame):
    cv2.putText(frame, "Screenshot Taken!", (20, 80),
                cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 0), 2)

def draw_legend(img):
    # The list of controls (OSK removed)
    controls = [
        "CONTROLS:",
        "Point Up : L-Click",
        "Victory  : R-Click",
        "Palm     : Drag/Hold",
        "Fist     : Drop/Release",
        "Thumb Up : Scroll Up",
        "Thumb Dn : Scroll Down",
        "OK       : Screenshot",
        "I Love You : Toggle OSK",
        "Press 'q' to quit"
    ]
    
    # Starting Y position (below your current Gesture label)
    start_y = 120
    line_spacing = 30
    
    # Optional: Draw a semi-transparent background box so text is always readable
    # (cv2 doesn't do transparency easily, so we draw a solid dark rectangle)
    cv2.rectangle(img, (10, start_y - 25), (320, start_y + (len(controls) * line_spacing)), (30, 30, 30), -1)

    # Draw each line of text
    for i, text in enumerate(controls):
        y = start_y + (i * line_spacing)
        # Make the title stand out with a different color
        color = (0, 255, 255) if i == 0 else (200, 200, 200)
        cv2.putText(img, text, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


# --- Main ---

def main():
    global is_clicking, is_right_clicking, mouse_pressed
    global is_scrolling_up, is_scrolling_down, osk_active
    global prev_was_ilove, is_capping, plocX, plocY, clocX, clocY

    # --- Load model ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, 'gesture_recognizer.task')
    try:
        base_options = python.BaseOptions(model_asset_path=model_path)
    except Exception as e:
        print(f"[ERROR] Failed to load model '{model_path}': {e}")
        input("Press Enter to exit...")
        return

    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        result_callback=result_callback
    )

    try:
        recognizer = vision.GestureRecognizer.create_from_options(options)
    except Exception as e:
        print(f"[ERROR] Failed to create gesture recognizer: {e}")
        input("Press Enter to exit...")
        return

    # --- Open camera ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open camera. Check webcam connection.")
        input("Press Enter to exit...")
        return

    print("AI Virtual Mouse — Hand Gesture Controller")
    print("Controls:")
    print("  Pointing_Up   : Left Click")
    print("  Victory       : Right Click")
    print("  Open_Palm     : Hold (mouseDown)")
    print("  Closed_Fist   : Release (mouseUp)")
    print("  Thumb_Up      : Scroll Up")
    print("  Thumb_Down    : Scroll Down")
    print("  ILoveYou      : Toggle On-Screen Keyboard")
    print("  OK            : Take Screenshot")
    print("  Press 'q' to quit.")
    print()

    with recognizer:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            timestamp = int(time.time() * 1000)
            recognizer.recognize_async(mp_image, timestamp)

            current_gesture = latest_gesture
            
            if latest_landmarks:
                hand = latest_landmarks[0]
                palm_hand = hand[0]

                # --- Mouse movement ---
                margin = SCREEN_MARGIN
                screen_x = int((palm_hand.x * w - margin) * SCREEN_WIDTH / (w - 2 * margin))
                screen_y = int(((palm_hand.y * h - margin)) * SCREEN_HEIGHT / (h - 2 * margin))

                clocX = plocX + (screen_x - plocX) / SMOOTHING
                clocY = plocY + (screen_y - plocY) / SMOOTHING

                pyautogui.moveTo(clocX, clocY, _pause=False)
                plocX, plocY = clocX, clocY

                # --- Gesture actions ---

                # Left Click
                if current_gesture == "Pointing_Up":
                    if not is_clicking:
                        on_left_click()
                        is_clicking = True
                else:
                    is_clicking = False

                # Right Click
                if current_gesture == "Victory":
                    if not is_right_clicking:
                        on_right_click()
                        is_right_clicking = True
                else:
                    is_right_clicking = False

                # Grab / Release
                if current_gesture == "Open_Palm":
                    if not mouse_pressed:
                        pyautogui.mouseDown(button='left')
                        mouse_pressed = True
                if current_gesture == "Closed_Fist":
                    if mouse_pressed:
                        pyautogui.mouseUp(button='left')
                        mouse_pressed = False

                # Scroll Up
                if current_gesture == "Thumb_Up":
                    if not is_scrolling_up:
                        on_scroll_up()
                        is_scrolling_up = True
                else:
                    is_scrolling_up = False

                # Scroll Down
                if current_gesture == "Thumb_Down":
                    if not is_scrolling_down:
                        on_scroll_down()
                        is_scrolling_down = True
                else:
                    is_scrolling_down = False

                # Open on screen keyboard
                if latest_gesture == "ILoveYou":
                    if not is_Open:
                        pyautogui.hotkey('win', 'ctrl', 'o')
                        is_Open = True
                else:
                    is_Open = False

                # Take screenshot
                if current_gesture == "OK":
                    if not is_capping:
                        on_screenshot()
                        draw_screenshot(frame)
                        is_capping = True
                else:
                    is_capping = False

                # --- Draw UI ---
                draw_hand_skeleton(frame, h, w)
                draw_cursor(frame, palm_hand, h, w)
                draw_gesture_label(frame, current_gesture)
                draw_legend(frame)
            else:
                draw_no_hand(frame)
                draw_legend(frame)

            cv2.imshow('AI Virtual Mouse', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
