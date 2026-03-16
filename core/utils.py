import cv2
import numpy as np
import base64

# Resolução mínima — MediaPipe aguenta bem em 320x240
PROCESS_WIDTH  = 320
PROCESS_HEIGHT = 240

def decode_image(data_url):
    try:
        _, encoded = data_url.split(",", 1)
        data = base64.b64decode(encoded)
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        if img.shape[1] != PROCESS_WIDTH or img.shape[0] != PROCESS_HEIGHT:
            img = cv2.resize(img, (PROCESS_WIDTH, PROCESS_HEIGHT),
                             interpolation=cv2.INTER_NEAREST)  # NEAREST é o mais rápido
        return img
    except Exception as e:
        print(f"Erro ao decodificar imagem: {e}")
        return None

def encode_image(img):
    # Qualidade 40 — aceitável para visualização em tempo real
    _, buffer = cv2.imencode('.jpg', img,
                             [cv2.IMWRITE_JPEG_QUALITY, 40,
                              cv2.IMWRITE_JPEG_OPTIMIZE, 1])
    return "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')