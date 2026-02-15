# Configuração do Frontend para Produção

Este documento explica como configurar o frontend para funcionar tanto em desenvolvimento quanto em produção.

## Arquivo de Configuração

O arquivo `frontend/config.js` detecta automaticamente o ambiente e configura a URL da API:

```javascript
// Desenvolvimento: http://localhost:8000
// Produção: https://seu-projeto.vercel.app/api
const API_BASE_URL = window.API_BASE_URL;
```

## Como Usar nos Arquivos HTML

### 1. Importar o config.js

Adicione no `<head>` de cada arquivo HTML **antes** dos outros scripts:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biblioteca</title>
    <link rel="stylesheet" href="assets/styles.css">

    <!-- IMPORTANTE: Importar config.js PRIMEIRO -->
    <script src="config.js"></script>
</head>
```

### 2. Usar API_BASE_URL nas Chamadas

Em vez de URLs hardcoded, use a variável global `API_BASE_URL`:

#### Antes (hardcoded):

```javascript
fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
})
```

#### Depois (dinâmico):

```javascript
fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
})
```

## Exemplos de Atualização

### Login (dashboard.html, users.html, etc)

```javascript
// Login
async function login(username, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    return await response.json();
}

// Get user info
async function getUserInfo() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return await response.json();
}
```

### Listar Livros (books.html)

```javascript
async function loadBooks() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/books`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const books = await response.json();
    displayBooks(books);
}
```

### Criar Empréstimo (loans.html)

```javascript
async function createLoan(bookId) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/loans`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ book_id: bookId })
    });
    return await response.json();
}
```

### Listar Usuários (users.html)

```javascript
async function loadUsers() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const users = await response.json();
    displayUsers(users);
}
```

## Verificação

Para verificar se a configuração está funcionando:

1. Abra o console do navegador (F12)
2. Verifique as mensagens de log:
   ```
   Ambiente: Development
   API Base URL: http://localhost:8000
   ```
   ou
   ```
   Ambiente: Production
   API Base URL: https://seu-projeto.vercel.app/api
   ```

3. Verifique as chamadas na aba Network
4. As URLs devem estar corretas para o ambiente

## Buscar e Substituir

Para atualizar todos os arquivos HTML de uma vez, use buscar e substituir:

### Buscar:
```
'http://localhost:8000
```

### Substituir por:
```
`${API_BASE_URL}
```

**IMPORTANTE:** Não esqueça de trocar aspas simples `'` por template literals `` ` ``

### Regex para busca avançada (VSCode):

**Buscar:**
```regex
['"]http://localhost:8000(/[^'"]*?)['"]
```

**Substituir por:**
```
\`\${API_BASE_URL}$1\`
```

## Checklist de Atualização

Para cada arquivo HTML:

- [ ] Importar `config.js` no `<head>`
- [ ] Substituir URLs hardcoded por `${API_BASE_URL}`
- [ ] Usar template literals (backticks) em vez de aspas
- [ ] Testar em desenvolvimento (localhost)
- [ ] Testar em produção (Vercel)

## Arquivos a Atualizar

- [ ] `index.html`
- [ ] `dashboard.html`
- [ ] `books.html`
- [ ] `loans.html`
- [ ] `users.html`

## Fallback para JavaScript Inline

Se você tiver JavaScript inline nos HTMLs (dentro de tags `<script>`), também atualize:

```html
<script>
    // Antes
    fetch('http://localhost:8000/books')

    // Depois
    fetch(`${API_BASE_URL}/books`)
</script>
```

## Testes

### Desenvolvimento (localhost)

1. Inicie o backend: `uvicorn backend.main:app --reload`
2. Inicie o frontend: `python -m http.server 8080`
3. Acesse: http://localhost:8080
4. Verifique console: deve usar http://localhost:8000

### Produção (Vercel)

1. Faça deploy na Vercel
2. Acesse: https://seu-projeto.vercel.app
3. Verifique console: deve usar https://seu-projeto.vercel.app/api
4. Teste login, listagem, etc

## Troubleshooting

### Erro: API_BASE_URL is not defined

**Causa:** config.js não foi importado ou foi importado depois do script que usa

**Solução:** Importe config.js ANTES de qualquer outro script

### URLs ainda apontam para localhost em produção

**Causa:** Esqueceu de atualizar alguma URL ou não usou template literals

**Solução:** Busque por `localhost:8000` no código e substitua

### CORS error em produção

**Causa:** Backend não está configurado para aceitar origem da Vercel

**Solução:** Verifique `backend/main.py` e configure CORS corretamente

### Network error: Failed to fetch

**Causa:** API não está respondendo ou URL incorreta

**Solução:**
1. Verifique se API está online: acesse /api/ diretamente
2. Verifique console para ver URL sendo chamada
3. Verifique variáveis de ambiente na Vercel

## Conclusão

Após seguir este guia, seu frontend funcionará automaticamente tanto em desenvolvimento quanto em produção, sem precisar alterar código entre ambientes.
