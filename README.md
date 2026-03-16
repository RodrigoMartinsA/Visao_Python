# 🖐️ Rockit Vision — Reconhecimento de Gestos com IA

Reconhecimento de gestos em tempo real usando MediaPipe, OpenCV e FastHTML — suporta duas mãos simultaneamente com um classificador de ML customizado.

---

## ✨ Funcionalidades

- 📷 Captura da webcam em tempo real pelo navegador
- 🖐️ Reconhecimento simultâneo de **duas mãos**
- 🤖 Classificador de ML customizado com `scikit-learn`
- 🦴 Desenho dos pontos das mãos com OpenCV
- ⚡ Comunicação via WebSocket para processamento de baixa latência
- 🎛️ Controle de qualidade de imagem e alternância de landmarks
- 📊 Contador de FPS em tempo real

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Backend | Python, FastHTML |
| Visão Computacional | MediaPipe, OpenCV |
| Classificador ML | scikit-learn, joblib |
| Frontend | HTML, CSS, JavaScript |
| Comunicação | WebSocket |

---

## 📁 Estrutura do Projeto

```
Visao_Python/
├── app.py                  # Servidor principal e rotas
├── core/
│   ├── processor.py        # Processamento de frames e reconhecimento de gestos
│   ├── models.py           # Carregamento dos modelos e configurações do MediaPipe
│   └── utils.py            # Funções auxiliares de encode/decode de imagem
├── models/
│   ├── gesture_recognizer.task   # Modelo base do MediaPipe
│   ├── gesture_model.joblib      # Classificador customizado treinado
│   └── label_encoder.joblib      # Codificador de labels
└── assets/
    ├── style.css
    └── script.js
```

---

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Rode o app

```bash
python app.py
```

Abra o navegador em `http://localhost:5001`

---

## 🌐 Compartilhar com ngrok

Para compartilhar o app publicamente pela internet:

```bash
# Instalar o ngrok
pip install pyngrok

# Autenticar (apenas uma vez)
ngrok config add-authtoken SEU_TOKEN

# Em um segundo terminal, com o app rodando
ngrok http 5001
```

O ngrok vai gerar uma URL pública que você pode enviar para qualquer pessoa.

---

## 🤝 Créditos

Desenvolvido durante o **NLW Operator** da [Rocketseat](https://rocketseat.com.br).