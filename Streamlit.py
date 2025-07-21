import streamlit as st
import cv2
import mediapipe as mp
from threading import Thread
from google.protobuf.json_format import MessageToDict
from comtypes import CoInitialize, CLSCTX_ALL
from ctypes import cast, POINTER
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui
import screen_brightness_control as sbc

# Initialize COM for pycaw
CoInitialize()

# Mediapipe initialization
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.75)
draw = mp.solutions.drawing_utils

# Pycaw setup for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Webcam controls
camera_running = {'brightness': False, 'volume': False, 'mouse': False}


def start_camera(control):
    if camera_running[control]:
        return
    camera_running[control] = True

    cap = cv2.VideoCapture(0)
    while camera_running[control]:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_data = MessageToDict(hand_landmarks)
                landmarks = hand_data['landmark']
                if control == "brightness":
                    adjust_brightness(landmarks)
                elif control == "volume":
                    adjust_volume(landmarks)
                elif control == "mouse":
                    control_mouse(landmarks)

        # Display the frame with Mediapipe hand gestures
        st.image(frame, channels="RGB", use_container_width=True)

    cap.release()
    cv2.destroyAllWindows()


def adjust_brightness(landmarks):
    try:
        y_coordinate = landmarks[8]['y']
        brightness_level = int((1 - y_coordinate) * 100)
        sbc.set_brightness(brightness_level)
    except Exception as e:
        st.error(f"Error adjusting brightness: {e}")


def adjust_volume(landmarks):
    try:
        y_coordinate = landmarks[4]['y']
        volume_level = (1 - y_coordinate) * -65  # Convert to dB scale
        volume.SetMasterVolumeLevel(volume_level, None)
    except Exception as e:
        st.error(f"Error adjusting volume: {e}")


def control_mouse(landmarks):
    try:
        x = landmarks[8]['x']
        y = landmarks[8]['y']
        screen_width, screen_height = pyautogui.size()
        cursor_x, cursor_y = int(x * screen_width), int(y * screen_height)
        pyautogui.moveTo(cursor_x, cursor_y)
    except Exception as e:
        st.error(f"Error controlling mouse: {e}")


# Streamlit UI
st.set_page_config(page_title="Gesture Controlled Interface", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f4;
        font-family: 'Arial', sans-serif;
    }
    .header {
        text-align: center;
        padding: 20px;
        background-color: #0066b3;
        color: white;
    }
    .section {
        margin: 20px;
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .section h3 {
        color: #333;
    }
    .stButton button {
        width: 100%;
        background-color: #FF5722;
        color: white;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton button:hover {
        background-color: #E64A19;
    }
    .footer {
        text-align: center;
        margin-top: 30px;  /* Reduced margin to move footer up */
        font-size: 14px;
        color: #333;
        background-color: #ffffff;  /* White background */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .footer p {
        margin: 5px 0;
    }
    .footer .names {
        font-size: 16px;
    }
    .footer .tagline {
        font-style: italic;
        color: #333;
        margin-top: 10px;
    }
    .footer .contact {
        color: #FF5722;
        font-size: 14px;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    '<div class="header"><h1>Gesture Pilot: Gesture Controlled Interface for Computer Interaction</h1><p>Control your system seamlessly with hand gestures</p></div>',
    unsafe_allow_html=True,
)

# Sections
col1, col2, col3 = st.columns(3)

# Brightness Section
with col1:
    st.markdown(
        '<div class="section"><h3>Brightness Control</h3><p>Adjust your screen brightness using your left hand gestures.</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("Activate Brightness Control"):
        Thread(target=start_camera, args=("brightness",)).start()

# Volume Section
with col2:
    st.markdown(
        '<div class="section"><h3>Volume Control</h3><p>Manage your system volume with gestures of your right hand.</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("Activate Volume Control"):
        Thread(target=start_camera, args=("volume",)).start()

# Mouse Control Section
with col3:
    st.markdown(
        '<div class="section"><h3>Mouse Tracker</h3><p>Use gestures to move your mouse pointer with precision.</p></div>',
        unsafe_allow_html=True,
    )
    if st.button("Activate Mouse Tracker"):
        Thread(target=start_camera, args=("mouse",)).start()

# # Stop Button
# if st.button("Stop All Controls"):
#     for control in camera_running:
#         camera_running[control] = False

# Footer
st.markdown(
    """
    <div class="footer">
        <p class="names">Created with ❤️ by Aryan Mishra and Abhinav Verma</p>
        <p class="tagline">"Innovating gestures, one motion at a time."</p>
    </div>
    """,
    unsafe_allow_html=True,
)
