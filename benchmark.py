"""
Benchmark para identificar onde está o gargalo de FPS.
Execute: uv run benchmark.py
"""
import time
import cv2
import mediapipe as mp
import numpy as np
import joblib
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent
MODEL_PATH = str(BASE_DIR / "models" / "gesture_recognizer.task")
CLF_PATH   = str(BASE_DIR / "models" / "gesture_model.joblib")
ENC_PATH   = str(BASE_DIR / "models" / "label_encoder.joblib")

RUNS = 100
FRAME_W, FRAME_H = 320, 240

print("=" * 55)
print("  BENCHMARK — Identificando gargalo de FPS")
print("=" * 55)

# Frame fake BGR
fake_bgr = np.random.randint(0, 255, (FRAME_H, FRAME_W, 3), dtype=np.uint8)

# ── 1. Encode JPEG ────────────────────────────────────────────
import base64
t0 = time.perf_counter()
for _ in range(RUNS):
    _, buf = cv2.imencode('.jpg', fake_bgr, [cv2.IMWRITE_JPEG_QUALITY, 40])
    base64.b64encode(buf)
t1 = time.perf_counter()
ms_encode = (t1 - t0) / RUNS * 1000
print(f"\n1. Encode JPEG (320x240, q40):  {ms_encode:.1f} ms/frame  →  {1000/ms_encode:.0f} FPS máx")

# ── 2. BGR→RGB ────────────────────────────────────────────────
t0 = time.perf_counter()
for _ in range(RUNS):
    cv2.cvtColor(fake_bgr, cv2.COLOR_BGR2RGB)
t1 = time.perf_counter()
ms_cvt = (t1 - t0) / RUNS * 1000
print(f"2. BGR→RGB:                     {ms_cvt:.1f} ms/frame  →  {1000/ms_cvt:.0f} FPS máx")

# ── 3. MediaPipe (sem mãos) ───────────────────────────────────
options = mp.tasks.vision.GestureRecognizerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
recognizer = mp.tasks.vision.GestureRecognizer.create_from_options(options)
fake_rgb = cv2.cvtColor(fake_bgr, cv2.COLOR_BGR2RGB)
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=fake_rgb)

# warmup
for _ in range(5):
    ts = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
    recognizer.recognize_for_video(mp_image, ts)
    time.sleep(0.01)

t0 = time.perf_counter()
for i in range(RUNS):
    ts = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
    recognizer.recognize_for_video(mp_image, ts)
    time.sleep(0.001)
t1 = time.perf_counter()
ms_mp = (t1 - t0) / RUNS * 1000
print(f"3. MediaPipe (sem mãos):        {ms_mp:.1f} ms/frame  →  {1000/ms_mp:.0f} FPS máx")
recognizer.close()

# ── 4. sklearn predict ────────────────────────────────────────
clf = joblib.load(CLF_PATH)
features = np.random.rand(1, 63).astype(np.float32)
# warmup
clf.predict(features)

t0 = time.perf_counter()
for _ in range(RUNS):
    clf.predict(features)
    clf.predict_proba(features)
t1 = time.perf_counter()
ms_clf = (t1 - t0) / RUNS * 1000
print(f"4. sklearn predict+proba:       {ms_clf:.1f} ms/frame  →  {1000/ms_clf:.0f} FPS máx")

# ── 5. Resize ─────────────────────────────────────────────────
big = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
t0 = time.perf_counter()
for _ in range(RUNS):
    cv2.resize(big, (320, 240), interpolation=cv2.INTER_NEAREST)
t1 = time.perf_counter()
ms_resize = (t1 - t0) / RUNS * 1000
print(f"5. Resize 1280x720→320x240:     {ms_resize:.1f} ms/frame  →  {1000/ms_resize:.0f} FPS máx")

# ── Resumo ────────────────────────────────────────────────────
total = ms_encode + ms_cvt + ms_mp + ms_clf
print(f"\n{'─'*55}")
print(f"  Total estimado (pipeline):    {total:.1f} ms/frame")
print(f"  FPS teórico máximo:           {1000/total:.0f} FPS")
print(f"\n  Maior gargalo: ", end="")
gargalos = {
    "Encode JPEG": ms_encode,
    "BGR→RGB":     ms_cvt,
    "MediaPipe":   ms_mp,
    "sklearn":     ms_clf,
}
maior = max(gargalos, key=gargalos.get)
print(f"{maior}  ({gargalos[maior]:.1f} ms)")
print("=" * 55)