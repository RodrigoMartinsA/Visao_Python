# 🚀 Deploy Rápido

## Resumo
1. **Frontend** → GitHub Pages (estático)
2. **Backend** → Railway/Render (Python)

## Passos Rápidos

### 1. GitHub Pages
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

Depois vá em **Settings → Pages** e ative o deploy da branch `main`.

### 2. Railway.app (Recomendado)
- Crie conta em [railway.app](https://railway.app)
- Crie novo projeto e selecione seu repo no GitHub
- Railway faz todo o resto automaticamente!
- Copie a URL gerada

### 3. Conectar Frontend ao Backend
No arquivo `assets/script.js`, encontre:
```javascript
return window.API_SERVER || 'https://seu-app-remotamente.railway.app';
```

E substitua pela URL do Railway que você copiou.

### 4. Fazer commit final
```bash
git add assets/script.js
git commit -m "Update backend URL"
git push
```

Pronto! Seu site estará em:
- **Frontend:** `https://seu-usuario.github.io/seu-repo/`
- **Backend:** `https://seu-app.railway.app`

---

Para mais detalhes, veja `DEPLOY.md` 📖
