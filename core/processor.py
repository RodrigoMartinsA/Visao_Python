import cv2
import mediapipe as mp
import numpy as np
from .models import get_mediapipe_options, load_custom_models

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),
    (0,17),
]

def draw_hand_landmarks(frame, hand_landmarks):
    h, w = frame.shape[:2]
    points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
    for s, e in HAND_CONNECTIONS:
        cv2.line(frame, points[s], points[e], (0, 200, 255), 1)
    for i, pt in enumerate(points):
        color = (0, 255, 100) if i in (4, 8, 12, 16, 20) else (220, 220, 220)
        cv2.circle(frame, pt, 3, color, -1)

class GestureProcessor:
    def __init__(self):
        self.clf, self.label_encoder = load_custom_models()
        self.options = get_mediapipe_options()
        self.recognizer = mp.tasks.vision.GestureRecognizer.create_from_options(self.options)
        self._features_buf = np.zeros((1, 63), dtype=np.float32)

    def process_frame(self, frame, draw_landmarks=True):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
        result = self.recognizer.recognize_for_video(mp_image, timestamp_ms)

        labels = []
        if result.hand_landmarks:
            for i, hand_landmarks in enumerate(result.hand_landmarks):
                if draw_landmarks:
                    draw_hand_landmarks(frame, hand_landmarks)
                idx = 0
                for lm in hand_landmarks:
                    self._features_buf[0, idx]     = lm.x
                    self._features_buf[0, idx + 1] = lm.y
                    self._features_buf[0, idx + 2] = lm.z
                    idx += 3
                hand_label     = result.handedness[i][0].category_name
                pred_idx       = self.clf.predict(self._features_buf)[0]
                pred_prob      = float(np.max(self.clf.predict_proba(self._features_buf)))
                gesture_name   = self.label_encoder.inverse_transform([pred_idx])[0]
                labels.append({"hand": hand_label, "gesture": gesture_name,
                                "probability": pred_prob})

        gesture_image = None
        if len(labels) == 2 and labels[0]['gesture'] == labels[1]['gesture']:
            gesture_image = f"{labels[0]['gesture']}.png"

        return frame, labels, gesture_image

    def close(self):
        if self.recognizer:
            self.recognizer.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()