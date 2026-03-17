import cv2
import mediapipe as mp
import serial

ser = serial.Serial('COM5', 9600)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hand = mp_hands.Hands()

CLOSED_SERVO_ANGLE = 180
OPEN_SERVO_ANGLE = 0

# Initialize a variable to track the previous hand pose
prev_hand_pose = None

while True:
    success, frame = cap.read()
    if success:
        RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hand.process(frame)

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]  # Assuming only one hand is in the frame

            # Extract key hand landmarks
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            # Calculate distances between fingers
            thumb_index_distance = abs(thumb_tip.y - index_finger_tip.y)
            thumb_middle_distance = abs(thumb_tip.y - middle_finger_tip.y)

            # Detect hand pose based on distances
            if thumb_index_distance < 0.1 and thumb_middle_distance < 0.1:
                hand_pose = "Closed Fist"
                ser.write('C'.encode())
                print("Closing end effector")
            else:
                hand_pose = "Open Palm"
                ser.write('O'.encode())
                print("Opening end effector")

            # Print the detected hand pose
            if hand_pose != prev_hand_pose:
                print(hand_pose)
                prev_hand_pose = hand_pose

            # Extract hand position for controlling the arm
            hand_x, hand_y = int(thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0])

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.circle(frame, (hand_x, hand_y), 10, (0, 255, 0), -1)  # Draw a circle at the hand position

        cv2.imshow("Capture Image", frame)

        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
