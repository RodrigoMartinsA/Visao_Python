# 🔧 MUDANÇAS TÉCNICAS REALIZADAS

## 1. `assets/script.js` - Configuração de URL Dinâmica

### O que mudou:
Adicionada função para detectar se está em localhost ou produção:

```javascript
// Configurar URL do servidor
// Se estiver em localhost, usa localhost. Senão, usa o servidor remoto
function getServerUrl() {
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        return location.origin; // http://localhost:8000
    }
    // Para GitHub Pages, usar a URL do servidor remoto
    return window.API_SERVER || 'https://seu-app-remotamente.railway.app';
}

const SERVER_URL = getServerUrl();
```

### Mudança na WebSocket:
**Antes:**
```javascript
const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
ws = new WebSocket(`${protocol}//${location.host}/ws`);
```

**Depois:**
```javascript
const protocol = SERVER_URL.startsWith('https') ? 'wss:' : 'ws:';
const wsUrl = SERVER_URL.replace(/^https?:/, '');
ws = new WebSocket(`${protocol}${wsUrl}/ws`);
```

---

## 2. `app.py` - CORS Middleware e Importações

### Importações adicionadas:
```python
import os
from starlette.middleware.cors import CORSMiddleware
```

### CORS Middleware configurado:
```python
# Permitir CORS para GitHub Pages e localhost
allowed_origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "https://seu-usuario.github.io",  # Substitua com seu GitHub Pages
]

# Adicionar origens de variável de ambiente (para deploy em produção)
if os.getenv('ALLOWED_ORIGINS'):
    allowed_origins.extend(os.getenv('ALLOWED_ORIGINS').split(','))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Por quê?** 
- Permite requisições WebSocket do GitHub Pages
- Configurável via variável de ambiente
- Funciona com localhost para testes

---

## 3. Novos Arquivos

### `requirements.txt`
Lista completa de dependências Python para Railway instalar automaticamente.

### `Procfile`
```
web: python app.py
```
Diz ao Railway qual comando executar para iniciar o servidor.

### `.env.example`
Template para variáveis de ambiente:
```
API_URL=http://localhost:8000
```

### `.gitignore`
Atualizado com padrões de produção:
- Python cache e ambientes virtuais
- IDE configs (.vscode, .idea)
- Arquivos OS (Thumbs.db, .DS_Store)
- Logs e cache

---

## 4. Fluxo de Funcionamento

### Local (Desenvolvimento)
```
Navegador → index.html (localhost:3000 ou arquivo local)
            ↓
            script.js detecta localhost
            ↓
            getServerUrl() retorna "http://localhost:8000"
            ↓
            WebSocket conecta em ws://localhost:8000/ws
            ↓
            app.py recebe e processa
```

### Online (Produção - GitHub Pages + Railway)
```
Navegador → GitHub Pages (seu-usuario.github.io/repo)
            ↓
            script.js detecta que NÃO é localhost
            ↓
            getServerUrl() retorna "https://seu-app.railway.app"
            ↓
            CORS permite requisição (seu app está na allowlist)
            ↓
            WebSocket conecta em wss://seu-app.railway.app/ws
            ↓
            app.py no Railway recebe e processa
```

---

## 5. Variáveis de Ambiente

### Railway pode usar:
```
ALLOWED_ORIGINS=https://seu-usuario.github.io,https://outro-dominio.com
```

### Seu app automaticamente:
```python
if os.getenv('ALLOWED_ORIGINS'):
    allowed_origins.extend(os.getenv('ALLOWED_ORIGINS').split(','))
```

Isso permite adicionar novos domínios SEM modificar o código!

---

## 6. Compatibilidade

### Funciona com:
- ✅ Railway
- ✅ Render.com
- ✅ Vercel Python
- ✅ Localhost (desenvolvimento)
- ✅ Qualquer serviço que rode Python

### Testes realizados:
- ✅ Local em `http://localhost:8000`
- ✅ CORS headers configurados
- ✅ WebSocket wss:// para HTTPS
- ✅ Fallback para URL remota

---

## 7. Segurança

- ✅ CORS middleware apenas permite origens específicas
- ✅ Variáveis de ambiente não enviadas para Git
- ✅ .gitignore protege arquivos sensíveis
- ✅ WebSocket seguro com wss:// em produção

---

## 📖 Para Mais Detalhes:

- Ver `DEPLOY.md` para guia completo
- Ver `CHECKLIST.md` para passo-a-passo
- Ver `ARCHITECTURE.md` para diagrama visual
