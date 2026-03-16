"""
Treina o modelo de gestos a partir do CSV coletado.
Usa MLP (rede neural leve) — muito mais rápido que Random Forest em inferência.
Execute: uv run train_model.py
"""

import pandas as pd
import numpy as np
import joblib
import time
from pathlib import Path
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR    = Path(__file__).resolve().parent
CSV_PATH    = BASE_DIR / "data" / "gesture_data.csv"
MODEL_OUT   = BASE_DIR / "models" / "gesture_model.joblib"
ENCODER_OUT = BASE_DIR / "models" / "label_encoder.joblib"

# ── Carrega CSV ───────────────────────────────────────────────────────────────
if not CSV_PATH.exists():
    print(f"❌ CSV não encontrado em: {CSV_PATH}")
    print("   Rode primeiro: uv run collect_data.py")
    exit(1)

print("📂 Carregando dados do CSV...")
df = pd.read_csv(CSV_PATH)
print(f"   {len(df)} amostras totais")
print(f"   Gestos: {sorted(df['gesture'].unique().tolist())}\n")

print("Amostras por gesto:")
for gesture, count in df['gesture'].value_counts().items():
    bar = "█" * int(count / df['gesture'].value_counts().max() * 30)
    print(f"  {gesture:<14} {count:>4}  {bar}")
print()

# ── Prepara dados ─────────────────────────────────────────────────────────────
X = df.drop("gesture", axis=1).values.astype(np.float32)
y = df["gesture"].values

le = LabelEncoder()
y_enc = le.fit_transform(y)
print(f"Classes: {list(le.classes_)}\n")

X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)
print(f"Treino: {len(X_train)}  |  Teste: {len(X_test)}\n")

# ── Treina MLP ────────────────────────────────────────────────────────────────
# MLP com 2 camadas ocultas pequenas — acurácia alta + inferência ~1ms
print("🤖 Treinando MLP (rede neural leve)...")
clf = Pipeline([
    ("scaler", StandardScaler()),
    ("mlp", MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        solver='adam',
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=15,
        verbose=False,
    ))
])

t0 = time.perf_counter()
clf.fit(X_train, y_train)
t1 = time.perf_counter()
print(f"   Treinado em {t1-t0:.1f}s\n")

# ── Avaliação ─────────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Acurácia: {acc * 100:.1f}%\n")
print("Relatório por gesto:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# ── Benchmark de velocidade ───────────────────────────────────────────────────
sample = X_test[:1]
# warmup
for _ in range(10):
    clf.predict(sample)

t0 = time.perf_counter()
for _ in range(500):
    clf.predict(sample)
    clf.predict_proba(sample)
t1 = time.perf_counter()
ms = (t1 - t0) / 500 * 1000
print(f"⚡ Velocidade de inferência: {ms:.2f} ms/frame  →  {1000/ms:.0f} FPS teórico\n")

# ── Salva ─────────────────────────────────────────────────────────────────────
joblib.dump(clf, MODEL_OUT)
joblib.dump(le, ENCODER_OUT)
print(f"💾 Modelo salvo em:  {MODEL_OUT}")
print(f"💾 Encoder salvo em: {ENCODER_OUT}")
print("\n🚀 Pronto! Rode: uv run app.py")