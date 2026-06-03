
import cv2
import mediapipe as mp
import pyautogui
import time
import asyncio

from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager
    as MediaManager
)

# ==========================================
# SPOTIFY
# ==========================================

def get_spotify_info():

    try:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        sessions = loop.run_until_complete(
            MediaManager.request_async()
        )

        current = sessions.get_current_session()

        if current:

            info = loop.run_until_complete(
                current.try_get_media_properties_async()
            )

            timeline = current.get_timeline_properties()

            return {
                "title": info.title,
                "artist": info.artist,
                "position": timeline.position.seconds,
                "duration": max(
                    timeline.end_time.seconds,
                    1
                )
            }

    except:
        pass

    return None


# ==========================================
# HAND DETECTION
# ==========================================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils


# ==========================================
# OPEN PALM
# ==========================================

def is_palm_open(hand_landmarks):

    fingertips = [8, 12, 16, 20]
    lower_joints = [6, 10, 14, 18]

    count = 0

    for tip, joint in zip(
        fingertips,
        lower_joints
    ):

        if (
            hand_landmarks.landmark[tip].y
            <
            hand_landmarks.landmark[joint].y
        ):
            count += 1

    return count >= 4


# ==========================================
# PEACE SIGN
# ==========================================

def is_peace_sign(hand_landmarks):

    index_up = (
        hand_landmarks.landmark[8].y
        <
        hand_landmarks.landmark[6].y
    )

    middle_up = (
        hand_landmarks.landmark[12].y
        <
        hand_landmarks.landmark[10].y
    )

    ring_down = (
        hand_landmarks.landmark[16].y
        >
        hand_landmarks.landmark[14].y
    )

    pinky_down = (
        hand_landmarks.landmark[20].y
        >
        hand_landmarks.landmark[18].y
    )

    return (
        index_up
        and middle_up
        and ring_down
        and pinky_down
    )


# ==========================================
# CAMERA
# ==========================================

cap = cv2.VideoCapture(0)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    640
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    480
)


# ==========================================
# SWIPE
# ==========================================

swipe_start_x = None
swipe_threshold = 150


# ==========================================
# GESTURE DISPLAY
# ==========================================

gesture_text = ""
gesture_time = 0


# ==========================================
# COOLDOWNS
# ==========================================

last_swipe_time = 0
swipe_cooldown = 1.0

last_palm_time = 0
palm_cooldown = 2.0

last_volume_time = 0
volume_cooldown = 0.8


# ==========================================
# PALM HOLD
# ==========================================

palm_start_time = None
palm_hold_time = 1.0


# ==========================================
# VOLUME
# ==========================================

peace_reference_y = None
volume_threshold = 60


# ==========================================
# SPOTIFY DATA
# ==========================================

spotify_timer = 0

song_title = "Nothing Playing"
artist_name = ""

song_position = 0
song_duration = 1

# ==========================================
# MAIN LOOP
# ==========================================

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    current_time = time.time()

    # --------------------------------------
    # SPOTIFY REFRESH
    # --------------------------------------

    if current_time - spotify_timer > 2:

        spotify = get_spotify_info()

        if spotify:

            song_title = spotify["title"]
            artist_name = spotify["artist"]
            song_position = spotify["position"]
            song_duration = spotify["duration"]

        spotify_timer = current_time

    # --------------------------------------
    # HAND DETECTION
    # --------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:

        hand_landmarks = (
            results.multi_hand_landmarks[0]
        )

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
            8,
            (0, 255, 0),
            -1
        )

        # ----------------------------------
        # VOLUME CONTROL
        # ----------------------------------

        if is_peace_sign(hand_landmarks):

            if peace_reference_y is None:
                peace_reference_y = palm_y

            movement_y = (
                peace_reference_y - palm_y
            )

            if (
                movement_y > volume_threshold
                and current_time - last_volume_time
                > volume_cooldown
            ):

                pyautogui.press("volumeup")

                gesture_text = "VOLUME UP"

                gesture_time = current_time

                last_volume_time = current_time

                peace_reference_y = palm_y

            elif (
                movement_y < -volume_threshold
                and current_time - last_volume_time
                > volume_cooldown
            ):

                pyautogui.press(
                    "volumedown"
                )

                gesture_text = "VOLUME DOWN"

                gesture_time = current_time

                last_volume_time = current_time

                peace_reference_y = palm_y

        else:

            peace_reference_y = None

        # ----------------------------------
        # PLAY PAUSE
        # ----------------------------------

        if (
            is_palm_open(
                hand_landmarks
            )
            and not
            is_peace_sign(
                hand_landmarks
            )
        ):

            if palm_start_time is None:

                palm_start_time = (
                    current_time
                )

            elif (
                current_time
                - palm_start_time
                > palm_hold_time
                and current_time
                - last_palm_time
                > palm_cooldown
            ):

                pyautogui.press(
                    "playpause"
                )

                gesture_text = (
                    "PLAY / PAUSE"
                )

                gesture_time = (
                    current_time
                )

                last_palm_time = (
                    current_time
                )

                palm_start_time = None

        else:

            palm_start_time = None

        # ----------------------------------
        # SWIPES
        # ----------------------------------

        if not is_peace_sign(
            hand_landmarks
        ):

            if swipe_start_x is None:
                swipe_start_x = palm_x

            movement = (
                palm_x
                - swipe_start_x
            )

            if (
                movement > swipe_threshold
                and current_time
                - last_swipe_time
                > swipe_cooldown
            ):

                pyautogui.press(
                    "nexttrack"
                )

                gesture_text = (
                    "NEXT SONG"
                )

                gesture_time = (
                    current_time
                )

                last_swipe_time = (
                    current_time
                )

                swipe_start_x = palm_x

            elif (
                movement < -swipe_threshold
                and current_time
                - last_swipe_time
                > swipe_cooldown
            ):

                pyautogui.press(
                    "prevtrack"
                )

                gesture_text = (
                    "PREVIOUS SONG"
                )

                gesture_time = (
                    current_time
                )

                last_swipe_time = (
                    current_time
                )

                swipe_start_x = palm_x

    else:

        swipe_start_x = None
        palm_start_time = None
        peace_reference_y = None

    # ======================================
    # GLASS UI
    # ======================================

    overlay = frame.copy()

    # Spotify Card

    cv2.rectangle(
        overlay,
        (15, 360),
        (625, 470),
        (20, 20, 20),
        -1
    )

    # Controls Card

    cv2.rectangle(
        overlay,
        (470, 15),
        (625, 150),
        (20, 20, 20),
        -1
    )

    frame = cv2.addWeighted(
        overlay,
        0.35,
        frame,
        0.65,
        0
    )

    # ======================================
    # TITLE
    # ======================================

    cv2.putText(
        frame,
        "AIRSWIPE MUSIC",
        (20, 40),
        cv2.FONT_HERSHEY_DUPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    # ======================================
    # SPOTIFY SECTION
    # ======================================

    cv2.putText(
        frame,
        "NOW PLAYING",
        (30, 390),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (120, 120, 120),
        1
    )

    cv2.putText(
        frame,
        song_title[:35],
        (30, 420),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        artist_name[:35],
        (30, 445),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (180, 180, 180),
        1
    )

    progress_width = int(
        (
            song_position
            / song_duration
        ) * 540
    )

    cv2.rectangle(
        frame,
        (30, 455),
        (570, 460),
        (60, 60, 60),
        -1
    )

    cv2.rectangle(
        frame,
        (30, 455),
        (30 + progress_width, 460),
        (0, 0, 255),
        -1
    )

    # ======================================
    # CONTROLS
    # ======================================

    cv2.putText(
        frame,
        "GESTURES",
        (490, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255,255,255),
        1
    )

    cv2.putText(
        frame,
        "-> NEXT",
        (490, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (180,180,180),
        1
    )

    cv2.putText(
        frame,
        "<- PREV",
        (490, 85),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (180,180,180),
        1
    )

    cv2.putText(
        frame,
        "PALM",
        (490, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (180,180,180),
        1
    )

    cv2.putText(
        frame,
        "PEACE",
        (490, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (180,180,180),
        1
    )

    # ======================================
    # GESTURE POPUP
    # ======================================

    if (
        current_time
        - gesture_time
        < 2
    ):

        cv2.rectangle(
            frame,
            (180, 30),
            (460, 90),
            (0, 0, 120),
            -1
        )

        cv2.putText(
            frame,
            gesture_text,
            (195, 70),
            cv2.FONT_HERSHEY_DUPLEX,
            0.8,
            (255,255,255),
            2
        )

    # ======================================
    # SHOW WINDOW
    # ======================================

    cv2.imshow(
        "AIRSWIPE MUSIC",
        frame
    )

    if (
        cv2.waitKey(1)
        & 0xFF
        == ord("q")
    ):
        break

# ==========================================
# CLEANUP
# ==========================================

cap.release()
cv2.destroyAllWindows()

