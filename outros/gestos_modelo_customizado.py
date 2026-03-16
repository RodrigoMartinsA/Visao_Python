"""
Reconhecimento de Gestos — Modelo Customizado
Bibliotecas: OpenCV + MediaPipe + scikit-learn

A cada execução verifica automaticamente se o CSV possui gestos novos.
Se sim, re-treina o modelo antes de abrir a câmera.

Uso:
    python gestos_modelo_customizado.py
"""

import os
import warnings
import urllib.request

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import joblib

from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore")

# ── Configurações ─────────────────────────────────────────────────────────────
CSV_PATH        = "dataset_gestos.csv"
MODEL_PKL       = "modelo_gestos.pkl"
ENCODER_PKL     = "label_encoder.pkl"
CLASSES_PKL     = "classes_conhecidas.pkl"
MP_MODEL_PATH   = "gesture_recognizer.task"
MP_MODEL_URL    = "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"

CAMERA_INDEX    = 0
SCORE_THRESHOLD = 0.5   # confiança mínima do MediaPipe para detectar a mão
CONFIANCA_MIN   = 0.6   # confiança mínima do seu modelo para exibir o gesto
MAX_HANDS       = 2
TECLA_SAIR      = "q"

CORES_MAO = [
    (0, 255, 120),   # verde  — mão 1
    (255, 180, 0),   # laranja — mão 2
]

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17),
]


# ── Treinamento ───────────────────────────────────────────────────────────────
def treinar_e_salvar(csv_path):
    """Treina os 3 modelos, salva o melhor e retorna (pipeline, label_encoder)."""
    df = pd.read_csv(csv_path)
    X  = df.drop(columns=["label"]).values
    y  = df["label"].values

    le = LabelEncoder()
    y  = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    candidatos = {
        "Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=200, random_state=42)),
        ]),
        "SVM": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="rbf", C=10, gamma="scale", random_state=42, probability=True)),
        ]),
        "MLP": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=500, random_state=42)),
        ]),
    }

    melhor_nome, melhor_pipeline, melhor_acc = None, None, -1
    for nome, pipeline in candidatos.items():
        pipeline.fit(X_train, y_train)
        acc = pipeline.score(X_test, y_test)
        print(f"  {nome:20s} → {acc:.1%}")
        if acc > melhor_acc:
            melhor_acc, melhor_nome, melhor_pipeline = acc, nome, pipeline

    joblib.dump(melhor_pipeline, MODEL_PKL)
    joblib.dump(le, ENCODER_PKL)
    joblib.dump(set(le.classes_), CLASSES_PKL)

    print(f"\n🏆 Melhor: {melhor_nome} ({melhor_acc:.1%})")
    return melhor_pipeline, le


def carregar_ou_treinar():
    """Verifica CSV por gestos novos e re-treina se necessário."""
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV não encontrado: {CSV_PATH}")
        print("   Execute o coletor_dataset_gestos.ipynb primeiro.")
        raise SystemExit(1)

    classes_csv    = set(pd.read_csv(CSV_PATH)["label"].unique())
    modelo_existe  = os.path.exists(MODEL_PKL) and os.path.exists(ENCODER_PKL)
    classes_salvas = joblib.load(CLASSES_PKL) if os.path.exists(CLASSES_PKL) else set()
    gestos_novos   = classes_csv - classes_salvas

    if not modelo_existe:
        print("⚠️  Modelo não encontrado. Treinando do zero...\n")
        return treinar_e_salvar(CSV_PATH)
    elif gestos_novos:
        print(f"🆕 Novos gestos detectados: {gestos_novos}")
        print("   Re-treinando o modelo...\n")
        return treinar_e_salvar(CSV_PATH)
    else:
        print("✅ Nenhum gesto novo. Carregando modelo existente...")
        return joblib.load(MODEL_PKL), joblib.load(ENCODER_PKL)


# ── Funções auxiliares ────────────────────────────────────────────────────────
def baixar_modelo_mp():
    if not os.path.exists(MP_MODEL_PATH):
        print("Baixando modelo MediaPipe...")
        urllib.request.urlretrieve(MP_MODEL_URL, MP_MODEL_PATH)
        print(f"✅ Salvo em: {MP_MODEL_PATH}")
    else:
        print(f"✅ Modelo MediaPipe já existe: {MP_MODEL_PATH}")


def frame_para_mp(frame_bgr):
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    return mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)


def extrair_e_normalizar(hand_landmarks):
    """Extrai e normaliza os 21 landmarks → vetor de 63 features."""
    valores = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks])
    valores = valores - valores[0]
    escala  = np.max(np.abs(valores)) or 1.0
    return (valores / escala).flatten()


def classificar_gesto(hand_landmarks, clf, le):
    """Usa o modelo treinado para classificar o gesto. Retorna (label, confiança)."""
    features  = extrair_e_normalizar(hand_landmarks).reshape(1, -1)
    label_idx = clf.predict(features)[0]
    label     = le.inverse_transform([label_idx])[0]
    try:
        confianca = clf.predict_proba(features)[0][label_idx]
    except AttributeError:
        confianca = 1.0
    return label, confianca


def desenhar_landmarks(frame, hand_landmarks_list, cor):
    h, w = frame.shape[:2]
    for hand_landmarks in hand_landmarks_list:
        pontos = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
        for ini, fim in HAND_CONNECTIONS:
            cv2.line(frame, pontos[ini], pontos[fim], cor, 2)
        for p in pontos:
            cv2.circle(frame, p, 5, cor, -1)
            cv2.circle(frame, p, 5, (255, 255, 255), 1)
    return frame


def desenhar_hud(frame, label, confianca, cor, offset_y=0):
    """Exibe label e confiança no canto superior, empilhada por mão."""
    overlay = frame.copy()
    y1 = 8  + offset_y
    y2 = 72 + offset_y
    cv2.rectangle(overlay, (8, y1), (340, y2), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.putText(frame, "Modelo customizado",
                (14, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1, cv2.LINE_AA)
    cv2.putText(frame, f"{label}  {confianca:.0%}",
                (14, y1 + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.9, cor, 2, cv2.LINE_AA)
    return frame


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # 1. Verifica/treina modelo
    clf, le = carregar_ou_treinar()
    print(f"✅ Classes ativas: {list(le.classes_)}\n")

    # 2. Baixa modelo MediaPipe se necessário
    baixar_modelo_mp()

    # 3. Inicializa MediaPipe
    base_options = mp_python.BaseOptions(model_asset_path=MP_MODEL_PATH)
    options      = mp_vision.GestureRecognizerOptions(
        base_options=base_options,
        running_mode=mp_vision.RunningMode.IMAGE,
        num_hands=MAX_HANDS,
        min_hand_detection_confidence=SCORE_THRESHOLD,
        min_hand_presence_confidence=SCORE_THRESHOLD,
        min_tracking_confidence=SCORE_THRESHOLD,
    )
    recognizer = mp_vision.GestureRecognizer.create_from_options(options)
    print("✅ MediaPipe pronto!")

    # 4. Loop principal
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"❌ Não foi possível abrir a câmera (índice {CAMERA_INDEX}).")
        return

    print("✅ Câmera aberta. Pressione 'q' para encerrar.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️  Falha ao capturar frame.")
            break

        frame     = cv2.flip(frame, 1)
        mp_image  = frame_para_mp(frame)
        resultado = recognizer.recognize(mp_image)

        if resultado.hand_landmarks:
            for idx, hand_landmarks in enumerate(resultado.hand_landmarks):
                cor   = CORES_MAO[idx % len(CORES_MAO)]
                frame = desenhar_landmarks(frame, [hand_landmarks], cor)

                label, confianca = classificar_gesto(hand_landmarks, clf, le)

                offset_y = idx * 80
                if confianca >= CONFIANCA_MIN:
                    frame = desenhar_hud(frame, label, confianca, cor, offset_y)
                else:
                    frame = desenhar_hud(frame, f"{label} (?)", confianca, (80, 80, 80), offset_y)
        else:
            cv2.putText(frame, "Nenhuma mao detectada", (10, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2, cv2.LINE_AA)

        cv2.imshow("Gestos — Modelo Customizado  |  Q para sair", frame)

        if cv2.waitKey(1) & 0xFF == ord(TECLA_SAIR):
            print("Encerrando...")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Câmera liberada.")


if __name__ == "__main__":
    main()