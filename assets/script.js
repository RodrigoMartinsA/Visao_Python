function initApp() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    if (!video || !canvas) return;

    const ctx = canvas.getContext('2d');
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    let ws;
    let isWaiting = false;

    const CAPTURE_WIDTH  = 320;
    const CAPTURE_HEIGHT = 240;

    // Configurar URL do servidor
    // Se estiver em localhost, usa localhost. Senão, usa o servidor remoto
    function getServerUrl() {
        if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
            return location.origin; // http://localhost:8000
        }
        // Para GitHub Pages, usar a URL do servidor remoto
        // Substitua com a URL real do seu servidor (Railway, Render, etc)
        return window.API_SERVER || 'https://web-production-f62ea.up.railway.app';
    }

    const SERVER_URL = getServerUrl();

    navigator.mediaDevices.getUserMedia({
        video: {
            width:     { ideal: CAPTURE_WIDTH },
            height:    { ideal: CAPTURE_HEIGHT },
            frameRate: { ideal: 30 }
        }
    }).then(stream => {
        video.srcObject = stream;
        video.onloadedmetadata = () => {
            canvas.width      = video.videoWidth;
            canvas.height     = video.videoHeight;
            tempCanvas.width  = CAPTURE_WIDTH;
            tempCanvas.height = CAPTURE_HEIGHT;
            initWS();
        };
    }).catch(err => {
        console.error('Erro ao acessar a câmera:', err);
        const container = document.getElementById('gesture-container');
        if (container) {
            container.innerHTML = `
                <div class="no-gesture">
                    <span>⚠️</span>
                    Câmera não disponível ou bloqueada
                </div>`;
        }
    });

    function initWS() {
        const protocol = SERVER_URL.startsWith('https') ? 'wss:' : 'ws:';
        const wsUrl = SERVER_URL.replace(/^https?:/, '');
        ws = new WebSocket(`${protocol}${wsUrl}/ws`);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const img = new Image();
            img.onload = () => {
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                img.onload = null;
                img.src = '';

                // FPS
                const fpsCounter = document.getElementById('fps-counter');
                if (fpsCounter && data.fps !== undefined) {
                    fpsCounter.textContent = `FPS: ${data.fps}`;
                }

                // Labels — placeholder quando não detecta gestos
                const labelContainer = document.getElementById('gesture-container');
                if (labelContainer) {
                    if (!data.labels || data.labels.length === 0) {
                        labelContainer.innerHTML = `
                            <div class="no-gesture">
                                <span>🤚</span>
                                Nenhum gesto detectado
                            </div>`;
                    } else {
                        labelContainer.innerHTML = data.labels.map(l =>
                            `<div class="label-item">
                                <span class="name">${l.hand}: ${l.gesture}</span>
                                <span class="prob">${(l.probability * 100).toFixed(1)}%</span>
                             </div>`
                        ).join('');
                    }
                }

                // Imagem do gesto — placeholder quando as mãos não fazem o mesmo gesto
                const gestureImg  = document.getElementById('gesture-image');
                const previewBox  = document.querySelector('.gesture-preview-box');
                if (gestureImg && previewBox) {
                    if (data.gesture_image) {
                        gestureImg.src = `/assets/images/gestures/${data.gesture_image}`;
                        gestureImg.style.display = 'block';
                        gestureImg.classList.add('active-gesture');
                        previewBox.classList.remove('empty');
                    } else {
                        gestureImg.style.display = 'none';
                        gestureImg.classList.remove('active-gesture');
                        previewBox.classList.add('empty');
                    }
                }

                isWaiting = false;
                sendFrame();
            };
            img.src = data.image;
        };

        ws.onopen  = () => { isWaiting = false; sendFrame(); };
        ws.onclose = () => { isWaiting = false; setTimeout(initWS, 1000); };
        ws.onerror = () => { isWaiting = false; };
    }

    const qualitySlider   = document.getElementById('quality-slider');
    const qualityValue    = document.getElementById('quality-value');
    const drawLandmarksCb = document.getElementById('draw-landmarks-cb');
    let currentQuality = 0.4;

    if (qualitySlider && qualityValue) {
        qualitySlider.oninput = function () {
            currentQuality = parseFloat(this.value);
            qualityValue.textContent = Math.round(currentQuality * 100) + '%';
        };
    }

    function sendFrame() {
        if (ws && ws.readyState === WebSocket.OPEN && !isWaiting) {
            isWaiting = true;
            tempCtx.drawImage(video, 0, 0, CAPTURE_WIDTH, CAPTURE_HEIGHT);
            const drawLandmarks = drawLandmarksCb ? drawLandmarksCb.checked : true;
            ws.send(JSON.stringify({
                image: tempCanvas.toDataURL('image/jpeg', currentQuality),
                draw_landmarks: drawLandmarks
            }));
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}