## ✅ Checklist de Deploy

### 📁 Arquivos Criados/Modificados
- ✅ `requirements.txt` - Dependências para o servidor Python
- ✅ `Procfile` - Configuração para Railway/Render
- ✅ `.env.example` - Template de variáveis de ambiente
- ✅ `assets/script.js` - Atualizado com URL dinâmica do servidor
- ✅ `app.py` - Adicionado CORS middleware
- ✅ `DEPLOY.md` - Guia completo de deployment
- ✅ `DEPLOY_QUICK.md` - Guia rápido
- ✅ `.gitignore` - Atualizado com mais padrões

### 🚀 Próximas Ações

#### 1️⃣ Preparar GitHub
- [ ] Crie uma conta no GitHub (se não tiver)
- [ ] Crie um novo repositório (pode ser público ou privado)
- [ ] Clone ou inicialize seu repositório local

```bash
git init
git add .
git commit -m "Initial commit - gesture recognition app"
git remote add origin https://github.com/seu-usuario/seu-repo.git
git branch -M main
git push -u origin main
```

#### 2️⃣ Ativar GitHub Pages
- [ ] Vá em **Settings** do repositório
- [ ] Procure por **Pages** (menu lateral esquerdo)
- [ ] Em "Source", selecione **Deploy from a branch**
- [ ] Selecione **main** branch
- [ ] Clique **Save**
- [ ] Aguarde 5-10 minutos
- [ ] Seu site estará em: `https://seu-usuario.github.io/seu-repo/`

#### 3️⃣ Deploy Backend no Railway
- [ ] Crie conta em [railway.app](https://railway.app)
- [ ] Clique **"New Project"**
- [ ] Selecione **"Deploy from GitHub repo"**
- [ ] Conecte sua conta GitHub
- [ ] Selecione seu repositório
- [ ] Railway fará o deploy automaticamente
- [ ] Copie a URL gerada (exemplo: `https://seu-app.railway.app`)

#### 4️⃣ Configurar URL do Backend
- [ ] Abra `assets/script.js`
- [ ] Procure por: `return window.API_SERVER || 'https://seu-app-remotamente.railway.app';`
- [ ] Substitua pela URL real do Railway:
  ```javascript
  return window.API_SERVER || 'https://seu-app.railway.app';
  ```
- [ ] Faça commit e push:
  ```bash
  git add assets/script.js
  git commit -m "Update backend URL to Railway"
  git push
  ```

#### 5️⃣ Testar Tudo
- [ ] Acesse `https://seu-usuario.github.io/seu-repo/`
- [ ] Clique no botão "View Live Demo"
- [ ] Verifique se:
  - [ ] O modal abre
  - [ ] A câmera funciona
  - [ ] Os gestos são detectados
  - [ ] O FPS aparece
  - [ ] As labels aparecem

### 🔧 Variáveis de Ambiente no Railway (Opcional)
Se quiser configurar CORS mais seguro:

1. No Railway, vá para **"Variables"**
2. Adicione:
   ```
   ALLOWED_ORIGINS=https://seu-usuario.github.io
   ```

### 📚 Documentação
- `DEPLOY.md` - Guia detalhado
- `DEPLOY_QUICK.md` - Resumo rápido

### ❓ Dúvidas?
- Verifique a seção "Troubleshooting" em `DEPLOY.md`
- Railway tem ótima documentação em seu painel
- GitHub Pages também tem ajuda integrada

---

**Está tudo pronto! Agora é só seguir o checklist acima.** 🎉
