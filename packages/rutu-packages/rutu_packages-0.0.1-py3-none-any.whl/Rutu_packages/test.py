import cv2  # Keep cv2 inside this file
import mediapipe as mp
import math

from flatbuffers.compat import import_numpy

import_numpy()


class Webcam:
    def __init__(self):
        """Initialize webcam settings."""
        self.cap = cv2.VideoCapture(0)  # Open the default webcam
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

        if not self.cap.isOpened():
            print("Error: Could not open the webcam.")
            exit()  # Exit if webcam fails

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hand_detector = self.mp_hands.Hands(max_num_hands=1)

        self.hand_detected = False  # Track discrete hand detection
        self.x1 = None
        self.y1 = None

    def capture_frame(self):
        """Capture a single frame."""
        success, frame = self.cap.read()
        return frame if success else None

    def show_frame(self, frame):
        """Display the frame."""
        cv2.imshow("Live Video", frame)

    def wait_key(self):
        """Handle key press event."""
        return cv2.waitKey(1) & 0xFF

    def release_cam(self):
        """Release the webcam properly."""
        self.cap.release()
        cv2.destroyAllWindows()

    def detect_hand(self, frame, point):
        """Detect and return a single specified hand landmark point."""
        RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hand_detector.process(RGB_frame)

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]  # Only consider the first detected hand
            self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            x, y = int(hand_landmarks.landmark[point].x * w), int(hand_landmarks.landmark[point].y * h)
            return x, y
        return None

    def discrete_hand(self, frame, point):
        """Detect hand only once and return its position."""
        if not self.hand_detected:
            hand_point = self.detect_hand(frame, point)
            if hand_point:
                print("Hand detected at:", hand_point)
                self.hand_detected = True  # Set flag to prevent multiple prints
                self.x1, self.y1 = hand_point
                print('x1', self.x1)
                print('y1', self.y1)
                return hand_point
        return None

    def conti_hand(self, point):
        """Continuously detect and print a single hand landmark position."""
        print("Continuous hand detection started... Press 'q' to stop.")
        self.hand_detected = False  # Reset flag to allow continuous detection

        while True:
            frame = self.capture_frame()
            if frame is None:
                break

            self.show_frame(frame)
            hand_point = self.detect_hand(frame, point)
            if hand_point:
                print("Hand detected:", hand_point)

            if self.wait_key() == ord('q'):
                print("Exiting continuous hand detection...")
                break

        self.release_cam()


    def detect_hand_and_calculate_distance(self, point1, point2):
        """Detect hand landmarks and calculate distance between two points."""
        while True:
            frame = self.capture_frame()
            if frame is None:
                continue

            RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.hand_detector.process(RGB_frame)

            distance = None  # Default to None if no hands detected
            if result.multi_hand_landmarks:
                hand_landmarks = result.multi_hand_landmarks[0]
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # Extract specified landmark points
                point1_coords = hand_landmarks.landmark[point1]
                point2_coords = hand_landmarks.landmark[point2]

                # Calculate Euclidean distance
                distance = math.sqrt((point2_coords.x - point1_coords.x) ** 2 +
                                     (point2_coords.y - point1_coords.y) ** 2)

                # Overlay distance on the video feed
                cv2.putText(frame, f"Distance: {distance:.4f}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                print(f"Distance: {distance:.4f}")  # Print distance in terminal

            self.show_frame(frame)

            if self.wait_key() == ord('q'):
                break

        self.release_cam()
