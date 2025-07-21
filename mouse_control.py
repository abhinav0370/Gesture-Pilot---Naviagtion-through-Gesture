import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Initialize Mediapipe and PyAutoGUI
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
screen_width, screen_height = pyautogui.size()

# Smoothing parameters
smoothening = 5
prev_x, prev_y = 0, 0

# Open Webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Mirror image for natural control
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Extract index finger tip coordinates
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_finger_tip.x * screen_width), int(index_finger_tip.y * screen_height)

            # Smooth movement
            x = int(prev_x + (x - prev_x) / smoothening)
            y = int(prev_y + (y - prev_y) / smoothening)

            # Move mouse
            pyautogui.moveTo(x, y)
            prev_x, prev_y = x, y

            # Check for click gesture (index & middle finger tips close)
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            middle_x, middle_y = int(middle_finger_tip.x * screen_width), int(middle_finger_tip.y * screen_height)
            if abs(middle_x - x) < 30 and abs(middle_y - y) < 30:
                pyautogui.click()

            # Draw landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the frame
    cv2.imshow("AI Mouse Controller", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Press 'ESC' to exit
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
