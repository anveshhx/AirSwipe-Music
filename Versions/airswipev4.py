
import cv2
import mediapipe as mp
import pyautogui
import time

# ---------------------------
# HAND DETECTION SETUP
# ---------------------------

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# ---------------------------
# OPEN PALM DETECTION
# ---------------------------

def is_palm_open(hand_landmarks):

    fingertips = [8, 12, 16, 20]
    lower_joints = [6, 10, 14, 18]

    extended_fingers = 0

    for tip, joint in zip(fingertips, lower_joints):

        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
            extended_fingers += 1

    return extended_fingers >= 4


# ---------------------------
# PEACE SIGN DETECTION
# ---------------------------

def is_peace_sign(hand_landmarks):

    index_up = (
        hand_landmarks.landmark[8].y
        < hand_landmarks.landmark[6].y
    )

    middle_up = (
        hand_landmarks.landmark[12].y
        < hand_landmarks.landmark[10].y
    )

    ring_down = (
        hand_landmarks.landmark[16].y
        > hand_landmarks.landmark[14].y
    )

    pinky_down = (
        hand_landmarks.landmark[20].y
        > hand_landmarks.landmark[18].y
    )

    return (
        index_up
        and middle_up
        and ring_down
        and pinky_down
    )


# ---------------------------
# WEBCAM
# ---------------------------

cap = cv2.VideoCapture(0)

# ---------------------------
# SWIPE SETTINGS
# ---------------------------

swipe_start_x = None
swipe_threshold = 150

# ---------------------------
# DISPLAY
# ---------------------------

gesture_text = ""
gesture_time = 0

# ---------------------------
# COOLDOWNS
# ---------------------------

last_swipe_time = 0
swipe_cooldown = 1.0

last_palm_time = 0
palm_cooldown = 2.0

last_volume_time = 0
volume_cooldown = 0.8

# ---------------------------
# PALM HOLD
# ---------------------------

palm_start_time = None
palm_hold_time = 1.0

# ---------------------------
# VOLUME CONTROL
# ---------------------------

peace_reference_y = None
volume_threshold = 60

# ---------------------------
# MAIN LOOP
# ---------------------------

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb_frame)

    current_time = time.time()

    if results.multi_hand_landmarks:

        hand_landmarks = results.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

        h, w, c = frame.shape

        palm = hand_landmarks.landmark[9]

        palm_x = int(palm.x * w)
        palm_y = int(palm.y * h)

        cv2.circle(
            frame,
            (palm_x, palm_y),
            10,
            (0, 255, 0),
            -1
        )

        # ---------------------------
        # PEACE SIGN VOLUME CONTROL
        # ---------------------------

        if is_peace_sign(hand_landmarks):

            if peace_reference_y is None:
                peace_reference_y = palm_y

            movement_y = peace_reference_y - palm_y

            # HAND MOVED UP
            if (
                movement_y > volume_threshold
                and current_time - last_volume_time > volume_cooldown
            ):

                pyautogui.press("volumeup")

                gesture_text = "VOLUME UP"
                gesture_time = current_time

                last_volume_time = current_time

                peace_reference_y = palm_y

            # HAND MOVED DOWN
            elif (
                movement_y < -volume_threshold
                and current_time - last_volume_time > volume_cooldown
            ):

                pyautogui.press("volumedown")

                gesture_text = "VOLUME DOWN"
                gesture_time = current_time

                last_volume_time = current_time

                peace_reference_y = palm_y

        else:

            peace_reference_y = None

        # ---------------------------
        # PLAY / PAUSE
        # ---------------------------

        if (
            is_palm_open(hand_landmarks)
            and not is_peace_sign(hand_landmarks)
        ):

            if palm_start_time is None:
                palm_start_time = current_time

            elif (
                current_time - palm_start_time > palm_hold_time
                and current_time - last_palm_time > palm_cooldown
            ):

                pyautogui.press("playpause")

                gesture_text = "PLAY / PAUSE"
                gesture_time = current_time

                last_palm_time = current_time

                palm_start_time = None

        else:
            palm_start_time = None

        # ---------------------------
        # SWIPE DETECTION
        # ---------------------------

        if not is_peace_sign(hand_landmarks):

            if swipe_start_x is None:
                swipe_start_x = palm_x

            movement = palm_x - swipe_start_x

            # RIGHT SWIPE
            if (
                movement > swipe_threshold
                and current_time - last_swipe_time > swipe_cooldown
            ):

                pyautogui.press("nexttrack")

                gesture_text = "NEXT SONG"
                gesture_time = current_time

                last_swipe_time = current_time

                swipe_start_x = palm_x

            # LEFT SWIPE
            elif (
                movement < -swipe_threshold
                and current_time - last_swipe_time > swipe_cooldown
            ):

                pyautogui.press("prevtrack")

                gesture_text = "PREVIOUS SONG"
                gesture_time = current_time

                last_swipe_time = current_time

                swipe_start_x = palm_x

    else:

        swipe_start_x = None
        palm_start_time = None
        peace_reference_y = None

    # ---------------------------
    # DISPLAY GESTURE
    # ---------------------------

    if current_time - gesture_time < 2:

        cv2.putText(
            frame,
            gesture_text,
            (40, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

    cv2.imshow(
        "AirSwipe Music Controller",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    

# ---------------------------
# CLEANUP
# ---------------------------

cap.release()
cv2.destroyAllWindows()

