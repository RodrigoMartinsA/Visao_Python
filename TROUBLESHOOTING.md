# 🆘 SOLUÇÃO DE PROBLEMAS

## ❌ Erro: "CORS policy: Cross-Origin Request Blocked"

**Causa:** Frontend (GitHub Pages) tentando conectar ao backend, mas CORS não permite

**Solução:**
1. Certifique-se que seu GitHub Pages está na lista de `allowed_origins` em `app.py`
2. Exemplo: Se seu site é `https://joao.github.io/gesture-app/`, adicione:
   ```python
   "https://joao.github.io",
   ```
3. Faça commit e push novamente
4. Railway vai fazer redeploy automático

---

## ❌ Erro: "WebSocket connection failed" ou "Failed to connect"

**Causa:** WebSocket tentando conectar a URL errada

**Solução:**
1. Abra DevTools (F12) → Console
2. Verifique a URL que está tentando conectar
3. Deve ser: `wss://seu-app.railway.app/ws` (note o `wss://`)
4. Se está vazio ou errado:
   - Verifique `assets/script.js`
   - Procure por `window.API_SERVER`
   - Deve estar setado com a URL correta do Railway

---

## ❌ Erro 404 no GitHub Pages

**Causa:** GitHub Pages ainda não publicou ou repositório é privado

**Solução:**
1. Verifique se repositório é **público**
2. Vá em **Settings → Pages**
3. Confirme que está usando "Deploy from a branch" → "main"
4. Aguarde 5-10 minutos
5. Tente acessar a URL novamente

---

## ❌ Railway mostra "Application failed to start"

**Causa:** Dependency missing ou erro no código

**Solução:**
1. Clique no Railway → **Logs**
2. Procure por linhas em vermelho/erro
3. Geralmente falta dependency em `requirements.txt`
4. Atualize `requirements.txt` com a dependency faltante
5. Faça commit e push
6. Railway fará redeploy automático

---

## ❌ "Cannot read property 'host' of undefined"

**Causa:** Problema ao detectar localhost

**Solução:**
Já foi corrigido! A versão atual usa:
```javascript
if (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
```

Só pode acontecer se usou versão antiga do script.js.

---

## ❌ Câmera não funciona no modal (GitHub Pages)

**Causa:** GitHub Pages é HTTPS, browser requer HTTPS para acessar câmera

**Solução:**
- Isso é por design (segurança)
- Funciona em localhost (HTTP)
- GitHub Pages sempre usa HTTPS
- Seu usuário precisa permitir câmera no browser
- Mostre uma mensagem clara pedindo permissão

---

## ❌ "ModuleNotFoundError: No module named 'mediapipe'"

**Causa:** Dependency não foi instalada no Railway

**Solução:**
1. Certifique-se que `mediapipe` está em `requirements.txt`
2. Verificar: `pip install -r requirements.txt` localmente funciona?
3. Se não, pode haver incompatibilidade:
   - Use: `mediapipe==0.10.32` (versão específica)
   - Use: `opencv-python==4.13.0.92` (versão específica)
4. Atualize `requirements.txt` e push

---

## ❌ WebSocket funciona local mas não em produção

**Causa:** Firewall, proxy ou configuração do servidor

**Solução:**
1. Railway auto-configura WebSocket corretamente
2. Verifique se está usando `wss://` em HTTPS
3. No `script.js`:
   ```javascript
   const protocol = SERVER_URL.startsWith('https') ? 'wss:' : 'ws:';
   ```
4. Se usar Render/Vercel: pode precisar configuração extra

---

## ❌ "TypeError: Cannot read property of undefined in script.js"

**Causa:** Element HTML não encontrado

**Solução:**
1. Certifique-se que `/app` retorna HTML com os elementos corretos:
   - `<video id="video">`
   - `<canvas id="canvas">`
   - `<div id="gesture-container">`
   - `<div id="fps-counter">`
2. Se falta algum, adicione em `app.py`

---

## ✅ Tudo funciona local mas não online?

**Checklist:**
- [ ] `assets/script.js` tem a URL correta do Railway?
- [ ] GitHub Pages está ativo (Settings → Pages)?
- [ ] Railway deployment mostra "Running" (não "Failed")?
- [ ] URL do Railway está correta (copiar de Railroad dashboard)?
- [ ] Sua URL do GitHub é adicionada em CORS do Railway?

**Teste final:**
1. Abra `https://seu-usuario.github.io/repo/`
2. Clique "View Live Demo"
3. Abra DevTools (F12)
4. Vá para **Network** tab
5. Veja qual é a URL sendo usada
6. Compare com Railway dashboard

---

## 🎯 Se Nada Funcionou:

1. **Limpe cache do browser:**
   - Ctrl+Shift+Delete
   - Limpe tudo
   - Feche e reabra o browser

2. **Tente do zero:**
   ```bash
   git status
   git add .
   git commit -m "fix: update deployment"
   git push
   ```
   Railway fará redeploy automático

3. **Teste local primeiro:**
   ```bash
   python app.py
   ```
   Se funcionar em `localhost:8000`, o problema é produção
   Se não funciona local, problema é no código

4. **Verifique logs:**
   - Railway: Dashboard → Logs
   - GitHub Pages: Settings → Pages (mostra status)
   - Browser: F12 → Console (mostra erros JS)

---

## 📞 Ainda com dúvida?

Mostre-me:
1. A URL completa (GitHub Pages + Railway)
2. Erro exato do console (F12)
3. Saída dos logs do Railway

E consigo ajudar! 🚀
