import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Load the sunglasses image
sunglasses = cv2.imread('sunglasses.png', -1)

def add_sunglasses(image, landmarks):
    # Get the left and right eye coordinates
    left_eye = landmarks[33]  # Left eye
    right_eye = landmarks[263]  # Right eye

    # Calculate the center and size of the sunglasses
    left_eye_center = np.array([left_eye.x * image.shape[1], left_eye.y * image.shape[0]]).astype("int")
    right_eye_center = np.array([right_eye.x * image.shape[1], right_eye.y * image.shape[0]]).astype("int")

    eye_center = ((left_eye_center + right_eye_center) // 2).astype("int")
    eye_width = np.linalg.norm(right_eye_center - left_eye_center)

    # Resize the sunglasses to fit the width of the eyes
    scale = eye_width / sunglasses.shape[1]
    new_sunglasses_size = (int(sunglasses.shape[1] * scale), int(sunglasses.shape[0] * scale))
    resized_sunglasses = cv2.resize(sunglasses, new_sunglasses_size, interpolation=cv2.INTER_AREA)

    # Calculate the position to overlay the sunglasses
    top_left = (eye_center[0] - new_sunglasses_size[0] // 2, eye_center[1] - new_sunglasses_size[1] // 2)

    # Overlay the sunglasses
    for i in range(new_sunglasses_size[1]):
        for j in range(new_sunglasses_size[0]):
            if resized_sunglasses[i, j, 3] > 0:  # Check the alpha channel
                image[top_left[1] + i, top_left[0] + j] = resized_sunglasses[i, j, :3]

    return image

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect face landmarks
    results = face_mesh.process(rgb_frame)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark

            # Add sunglasses to the detected face
            frame = add_sunglasses(frame, landmarks)

    # Display the result
    cv2.imshow('Face Filter', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
