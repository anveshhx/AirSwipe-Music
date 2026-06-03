import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils


def is_palm_open(hand_landmarks):

    fingertips = [8, 12, 16, 20]
    lower_joints = [6, 10, 14, 18]

    extended = 0

    for tip, joint in zip(
        fingertips,
        lower_joints
    ):

        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
            extended += 1

    return extended >= 4


cap = cv2.VideoCapture(0)

swipe_start_x = None
swipe_threshold = 150

palm_start_time = None
palm_hold_time = 1

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb)

    current_time = time.time()

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )

        h, w, _ = frame.shape

        palm = hand.landmark[9]

        palm_x = int(palm.x * w)

        if is_palm_open(hand):

            if palm_start_time is None:
                palm_start_time = current_time

            elif current_time - palm_start_time > palm_hold_time:

                pyautogui.press("playpause")
                palm_start_time = None

        else:
            palm_start_time = None

        if swipe_start_x is None:
            swipe_start_x = palm_x

        movement = palm_x - swipe_start_x

        if movement > swipe_threshold:

            pyautogui.press("nexttrack")
            swipe_start_x = palm_x

        elif movement < -swipe_threshold:

            pyautogui.press("prevtrack")
            swipe_start_x = palm_x

    else:

        swipe_start_x = None
        palm_start_time = None

    cv2.imshow(
        "AirSwipe V2",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()