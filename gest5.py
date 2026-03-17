import cv2
import mediapipe as mp
from pyfirmata import Arduino, SERVO
from time import sleep
from math import sqrt

port = "com5"  # Adjust the port name if needed
pins = [3, 5, 6, 8, 10, 11]  # Adjust pin numbers if needed
board = Arduino(port)

# Set the mode to SERVO for each pin
for pin in pins:
    board.digital[pin].mode = SERVO


def rotateServo(pins, servo_angles):
    for i in range(len(pins)):
        board.digital[pins[i]].write(servo_angles[i])
        sleep(0.01)


# config
write_video = False  # Set to True if you want to record video

y_min = 0.3  # Adjust threshold for upward movement (Y-axis)
y_max = 0.9  # Adjust threshold for downward movement (Y-axis)

palm_size_min = 0.1  # Adjust threshold for hand closer to camera (Z-axis)
palm_size_max = 0.3  # Adjust threshold for hand farther from camera (Z-axis)

claw_open_angle = 0
claw_close_angle = 180

servo_angle = [180, 180, 60, -20, 85, 85]  # [0, 1, 2, 3, 4, 5]
prev_servo_angle = servo_angle
fist_threshold = 5

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

# video writer
if write_video:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 60.0, (640, 480))

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
map_range = lambda x, in_min, in_max, out_min, out_max: abs(
    (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min)


# Check if the hand is a fist
def is_fist(hand_landmarks):
    # Calculate distances between fingertips and palm center
    distances = []
    for i in [8, 12, 16, 20]:
        distances.append(abs(sqrt((hand_landmarks.landmark[i].x - hand_landmarks.landmark[0].x)**2 +
                                  (hand_landmarks.landmark[i].y - hand_landmarks.landmark[0].y)**2)))

    # Check if all distances are below a threshold
    if all(distance <= fist_threshold for distance in distances):
        return True
    else:
        return False


def landmark_to_servo_angle(hand_landmarks):
    servo_angle = [180, 180, 60, -20, 85, 85]  # [0, 1, 2, 3, 4, 5]
    WRIST = hand_landmarks.landmark[0]
    INDEX_FINGER_MCP = hand_landmarks.landmark[5]

    # Calculate palm size
    x_sum = sum(landmark.x for landmark in hand_landmarks.landmark)
    y_sum = sum(landmark.y for landmark in hand_landmarks.landmark)
    center_x = x_sum / len(hand_landmarks.landmark)
    center_y = y_sum / len(hand_landmarks.landmark)

    # Calculate the Euclidean distance between the wrist and index finger MCP
    palm_size = ((WRIST.x - INDEX_FINGER_MCP.x) ** 2 + (WRIST.y - INDEX_FINGER_MCP.y) ** 2) ** 0.5

    if is_fist(hand_landmarks):
        servo_angle[0] = claw_close_angle
    else:
        servo_angle[0] = claw_open_angle

    # calculate x angle
    distance = palm_size
    angle = (WRIST.x - INDEX_FINGER_MCP.x) / distance  # calculate the radian between the wrist and the index finger
    angle = int(angle * 180 / 3.1415926)  # convert radian to degree
    angle = clamp(angle, palm_angle_min, palm_angle_mid)
    servo_angle[1] = map_range(angle, palm_angle_min, palm_angle_mid, x_max, x_min)

    # calculate y angle
    wrist_y = clamp(WRIST.y, wrist_y_min, wrist_y_max)
    servo_angle[2] = map_range(wrist_y, wrist_y_min, wrist_y_max, y_max, y_min)

    # calculate z angle
    palm_size = clamp(palm_size, palm_size_min, palm_size_max)
    servo_angle[3] = map_range(palm_size, palm_size_min, palm_size_max, z_max, z_min)

    # float to int
    servo_angle = [int(i) for i in servo_angle]

    return servo_angle

