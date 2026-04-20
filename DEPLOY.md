# 🚀 Guia de Deploy - GitHub Pages + Servidor Python Separado

## 📋 Visão Geral
- **Frontend:** Hospedado no GitHub Pages (estático)
- **Backend:** Hospedado em Railway, Render ou Vercel (Python)

---

## 1️⃣ DEPLOY DO FRONTEND (GitHub Pages)

### Passo 1: Preparar arquivos para GitHub Pages
Você precisa apenas desses arquivos no GitHub Pages:
- `index.html`
- `assets/` (style.css, script.js, images/)

### Passo 2: Criar repositório no GitHub

```bash
# Se ainda não tem repositório local
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/seu-repo.git
git branch -M main
git push -u origin main
```

### Passo 3: Ativar GitHub Pages

1. Vá para **Settings** do repositório
2. Procure por **Pages** (lado esquerdo)
3. Em "Source", selecione **main branch** e clique **Save**
4. Aguarde alguns segundos
5. Seu site estará em: `https://seu-usuario.github.io/seu-repo/`

---

## 2️⃣ DEPLOY DO BACKEND

### Opção A: Railway (Recomendado ⭐)

#### Pré-requisitos:
- Conta no [Railway.app](https://railway.app)
- Git instalado
- Seu código no GitHub

#### Passos:

1. **Criar novo projeto no Railway**
   - Vá para railway.app
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Conecte sua conta GitHub
   - Selecione seu repositório

2. **Railway detectará automaticamente**
   - Vai usar `requirements.txt`
   - Vai usar `Procfile`
   - Vai rodar: `python app.py`

3. **Configurar variáveis de ambiente**
   - No Railway, vá para "Variables"
   - Adicione: `PORT=8000`

4. **Obter URL do seu app**
   - Railway vai gerar uma URL como: `https://seu-app.railway.app`

#### Para conectar Frontend ao Backend:

5. **No GitHub, editar `assets/script.js`**
   
   Procure por essa linha:
   ```javascript
   return window.API_SERVER || 'https://seu-app-remotamente.railway.app';
   ```

   E substitua por sua URL do Railway:
   ```javascript
   return window.API_SERVER || 'https://seu-app.railway.app';
   ```

6. **Fazer commit e push**
   ```bash
   git add assets/script.js
   git commit -m "Update backend URL to Railway"
   git push
   ```

7. **GitHub Pages se atualizará automaticamente**

---

### Opção B: Render

1. Vá para [render.com](https://render.com)
2. Clique "New Web Service"
3. Conecte seu GitHub
4. Selecione o repositório
5. Configure:
   - **Name:** seu-app
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
6. Clique "Create Web Service"
7. Aguarde o deploy (pode levar alguns minutos)
8. Copie a URL gerada

---

## 3️⃣ CONFIGURAR CORS (Importante!)

Seu `app.py` precisa permitir requisições do GitHub Pages. Adicione isto ao topo do `app.py`:

```python
from fasthtml.common import *
from starlette.middleware.cors import CORSMiddleware

app, rt = fast_app(...)

# Permitir requisições do GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000",
        "https://seu-usuario.github.io",  # Seu GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Depois, faça commit e push:
```bash
git add app.py
git commit -m "Add CORS configuration"
git push
```

Railway/Render fará o redeploy automaticamente.

---

## 4️⃣ TESTAR TUDO

### Local:
1. Rodando `python app.py` na porta 8000
2. Abra `http://localhost:8000`
3. Clique "View Live Demo"
4. Deve funcionar perfeitamente

### Online:
1. Vá para `https://seu-usuario.github.io/seu-repo/`
2. Clique "View Live Demo"
3. O modal abre e faz requisições para seu servidor Railway/Render
4. Tudo deve funcionar igual ao local!

---

## 5️⃣ PRÓXIMOS PASSOS

- [ ] Criar repositório no GitHub
- [ ] Fazer push do código
- [ ] Ativar GitHub Pages
- [ ] Criar conta em Railway/Render
- [ ] Fazer deploy do backend
- [ ] Copiar URL do backend
- [ ] Atualizar URL no `script.js`
- [ ] Fazer commit e push novamente
- [ ] Testar no GitHub Pages

---

## 🔧 Troubleshooting

**"Cannot GET /app" no modal?**
- Certifique-se que a URL do servidor está correta em `script.js`
- Verifique se Railway/Render está rodando (status: Running)

**WebSocket connection failed?**
- Protocolo deve ser `wss://` (seguro) para HTTPS
- Verifique CORS no `app.py`

**404 no GitHub Pages?**
- Verifique se o repositório é público
- GitHub Pages deve estar habilitado
- Pode levar 5-10 minutos para publicar

---

## 📞 Dúvidas?

Qualquer problema, me avisa! 🚀
