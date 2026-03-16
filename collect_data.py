"""
Coletor automático de gestos — com suporte a sessões parciais.
- Detecta quais gestos já têm dados no CSV
- Pergunta o que fazer com cada gesto existente (pular ou recriar)
- Grava automaticamente quando detecta mãos
- [N] próximo gesto  |  [Q] sair e salvar
"""

import cv2
import mediapipe as mp
import csv
import os
import pandas as pd
from pathlib import Path

# ── Configurações ──────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
MODEL_PATH = str(BASE_DIR / "models" / "gesture_recognizer.task")
OUTPUT_CSV = str(BASE_DIR / "data" / "gesture_data.csv")
SAMPLES_PER_GESTURE = 500
GESTURES = ["rock", "hang_loose", "peace", "thumbs_up", "coracao", "ola", "spock", "fuck", "none"]
# ──────────────────────────────────────────────────────────────────────────────

os.makedirs(BASE_DIR / "data", exist_ok=True)

# ── Verifica CSV existente e pergunta o que fazer ─────────────────────────────
existing_counts = {}
gestures_to_collect = []
gestures_to_keep = {}   # {gesto: [linhas do CSV a manter]}

if os.path.exists(OUTPUT_CSV):
    df_existing = pd.read_csv(OUTPUT_CSV)
    existing_counts = df_existing['gesture'].value_counts().to_dict()

    print("\n📊 Dados existentes no CSV:")
    print(f"{'Gesto':<14} {'Amostras':>8}  {'Status'}")
    print("─" * 40)
    for g in GESTURES:
        c = existing_counts.get(g, 0)
        pct = min(int(c / SAMPLES_PER_GESTURE * 100), 100)
        status = "✅ completo" if pct >= 100 else f"⚠️  {pct}%"
        print(f"  {g:<12} {c:>8}  {status}")

    print("\n📝 Para cada gesto existente, o que deseja fazer?")
    print("   [S] Pular (manter dados)  |  [R] Recriar (apagar e coletar novamente)  |  [A] Adicionar mais amostras\n")

    for g in GESTURES:
        c = existing_counts.get(g, 0)
        if c == 0:
            gestures_to_collect.append(g)
            print(f"  {g:<12} → sem dados, será coletado automaticamente")
        else:
            pct = min(int(c / SAMPLES_PER_GESTURE * 100), 100)
            while True:
                resp = input(f"  {g:<12} ({c} amostras, {pct}%) [S/R/A]: ").strip().lower()
                if resp in ('s', ''):
                    # Mantém os dados existentes
                    gestures_to_keep[g] = df_existing[df_existing['gesture'] == g]
                    print(f"    ↳ mantendo {c} amostras existentes")
                    break
                elif resp == 'r':
                    # Recria — não mantém nada
                    gestures_to_collect.append(g)
                    print(f"    ↳ será recriado do zero")
                    break
                elif resp == 'a':
                    # Mantém e adiciona mais
                    gestures_to_keep[g] = df_existing[df_existing['gesture'] == g]
                    gestures_to_collect.append(g)
                    print(f"    ↳ mantendo {c} e adicionando mais amostras")
                    break
                else:
                    print("    ⚠️  Digite S, R ou A")

    # Gestos que não estavam no CSV mas estão na lista
    for g in GESTURES:
        if g not in existing_counts and g not in gestures_to_collect:
            gestures_to_collect.append(g)
else:
    print("\n📂 Nenhum CSV encontrado — coletando todos os gestos.")
    gestures_to_collect = GESTURES[:]

if not gestures_to_collect:
    print("\n✅ Nenhum gesto para coletar. Todos os dados estão mantidos!")
    exit(0)

print(f"\n🎯 Gestos a coletar: {gestures_to_collect}")
print("   Aponte as mãos para a câmera — gravação automática!")
print("   [N] próximo gesto  |  [Q] sair e salvar\n")

# ── Inicializa MediaPipe ──────────────────────────────────────────────────────
options = mp.tasks.vision.GestureRecognizerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
recognizer = mp.tasks.vision.GestureRecognizer.create_from_options(options)

CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),(0,17)
]

def draw_landmarks(frame, result):
    h, w = frame.shape[:2]
    for hand_lms in result.hand_landmarks:
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_lms]
        for s, e in CONNECTIONS:
            cv2.line(frame, pts[s], pts[e], (0, 200, 255), 1)
        for i, pt in enumerate(pts):
            color = (0, 255, 100) if i in (4,8,12,16,20) else (255,255,255)
            cv2.circle(frame, pt, 4, color, -1)

def draw_progress_bar(frame, count, total, y=95):
    W = frame.shape[1]
    pct = min(count / total, 1.0)
    bar_w = W - 40
    filled = int(bar_w * pct)
    if pct < 0.5:
        color = (0, int(255 * pct * 2), 255)
    else:
        color = (0, 255, int(255 * (1 - pct) * 2))
    cv2.rectangle(frame, (20, y), (20 + bar_w, y + 22), (50, 50, 50), -1)
    cv2.rectangle(frame, (20, y), (20 + filled, y + 22), color, -1)
    cv2.rectangle(frame, (20, y), (20 + bar_w, y + 22), (150,150,150), 1)
    pct_text = f"{int(pct * 100)}%  ({count}/{total})"
    cv2.putText(frame, pct_text, (25, y + 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

# ── Coleta ────────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

new_rows = []
new_counts = {g: 0 for g in gestures_to_collect}
gesture_idx = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    ts = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
    result = recognizer.recognize_for_video(mp_image, ts)

    gesture_name = gestures_to_collect[gesture_idx]
    count = new_counts[gesture_name]

    # Gravação automática
    if result.hand_landmarks and count < SAMPLES_PER_GESTURE:
        for hand_lms in result.hand_landmarks:
            landmarks_array = []
            for lm in hand_lms:
                landmarks_array.extend([lm.x, lm.y, lm.z])
            if len(landmarks_array) == 63:
                new_rows.append([gesture_name] + landmarks_array)
                new_counts[gesture_name] += 1

    if result.hand_landmarks:
        draw_landmarks(frame, result)

    # Painel superior
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (640, 125), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    recording = result.hand_landmarks and count < SAMPLES_PER_GESTURE
    status = "● GRAVANDO" if recording else ("✅ COMPLETO" if count >= SAMPLES_PER_GESTURE else "⏸ Aguardando maos...")
    color_status = (0, 80, 255) if recording else ((0, 255, 100) if count >= SAMPLES_PER_GESTURE else (180,180,0))

    cv2.putText(frame, f"Gesto: {gesture_name.upper()}", (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 150), 2)
    cv2.putText(frame, status, (400, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_status, 2)
    cv2.putText(frame, "[N] proximo   [Q] sair e salvar", (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

    draw_progress_bar(frame, new_counts[gesture_name], SAMPLES_PER_GESTURE, y=70)

    # Painel inferior — todos os gestos a coletar
    panel_y = frame.shape[0] - (len(gestures_to_collect) * 18 + 10)
    overlay2 = frame.copy()
    cv2.rectangle(overlay2, (0, panel_y - 5), (640, frame.shape[0]), (0,0,0), -1)
    cv2.addWeighted(overlay2, 0.5, frame, 0.5, 0, frame)

    for j, g in enumerate(gestures_to_collect):
        c = new_counts[g]
        pct = min(c / SAMPLES_PER_GESTURE, 1.0)
        bar_filled = int(150 * pct)
        bar_color = (0, 200, 80) if pct >= 1.0 else (0, 160, 255)
        prefix = "▶ " if j == gesture_idx else "  "
        y_pos = panel_y + j * 18 + 14
        cv2.putText(frame, f"{prefix}{g:<12} {int(pct*100):3}%",
                    (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                    (0,255,100) if j == gesture_idx else (180,180,180), 1)
        cv2.rectangle(frame, (160, y_pos-10), (310, y_pos-2), (50,50,50), -1)
        cv2.rectangle(frame, (160, y_pos-10), (160+bar_filled, y_pos-2), bar_color, -1)

    cv2.imshow("Coletor de Gestos — NLW Operator", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('n'):
        gesture_idx = (gesture_idx + 1) % len(gestures_to_collect)
        print(f"🎯 Gesto atual: {gestures_to_collect[gesture_idx].upper()}")

cap.release()
cv2.destroyAllWindows()
recognizer.close()

# ── Monta CSV final: dados mantidos + novos ───────────────────────────────────
if new_rows:
    header = ["gesture"] + [f"{a}{i}" for i in range(21) for a in ["x","y","z"]]

    # Junta DataFrames: mantidos + novos
    frames = []
    for g, df_kept in gestures_to_keep.items():
        frames.append(df_kept)

    if frames:
        df_kept_all = pd.concat(frames, ignore_index=True)
        kept_rows = df_kept_all.values.tolist()
    else:
        kept_rows = []

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(kept_rows)
        writer.writerows(new_rows)

    print(f"\n💾 CSV salvo em: {OUTPUT_CSV}")
    print(f"\nResumo final:")
    # Relê pra mostrar contagem real
    df_final = pd.read_csv(OUTPUT_CSV)
    for g in GESTURES:
        c = df_final['gesture'].value_counts().get(g, 0)
        bar = "█" * int(min(c / SAMPLES_PER_GESTURE, 1.0) * 20)
        print(f"  {g:<14} {c:>4} amostras  [{bar:<20}] {min(int(c/SAMPLES_PER_GESTURE*100),100)}%")
    print(f"\n▶ Agora rode: uv run train_model.py")
else:
    print("\n⚠️  Nenhum dado novo coletado.")