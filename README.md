# Biblioteca API

Sistema completo de gerenciamento de biblioteca com autenticação JWT, controle de empréstimos de livros e interface web.

## Stack Tecnológica

**Backend:**
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- Pydantic 2.5.0
- Python-Jose (JWT)
- Passlib (bcrypt)
- Uvicorn

**Frontend:**
- HTML/CSS/JavaScript (Vanilla)

**Banco de Dados:**
- SQLite (desenvolvimento)

## Como Rodar o Projeto

### 1. Instalar Dependências

```bash
cd biblioteca/backend
pip install -r requirements.txt
```

### 2. Popular Banco de Dados

Execute o script de seed para criar as tabelas e inserir dados iniciais:

```bash
cd biblioteca/backend
python seed.py
```

Este comando irá:
- Criar todas as tabelas do banco
- Inserir usuários de teste
- Inserir categorias de livros
- Inserir livros de exemplo
- Criar empréstimos de exemplo

### 3. Iniciar o Servidor Backend

```bash
cd biblioteca/backend
uvicorn main:app --reload
```

O servidor estará disponível em `http://localhost:8000`

### 4. Iniciar o Frontend

Em outro terminal:

```bash
cd biblioteca/frontend
python -m http.server 8080
```

Acesse a aplicação em `http://localhost:8080`

## Credenciais de Acesso

Após executar o seed, você pode fazer login com:

| Usuário | Senha | Papel |
|---------|-------|-------|
| admin | admin123 | Admin (acesso total) |
| bibliotecario | biblio123 | Bibliotecário (gerenciar livros) |
| joao | joao123 | Membro (emprestar livros) |
| maria | maria123 | Membro (emprestar livros) |

## Testar a API

Execute o script de testes automatizado:

```bash
cd biblioteca
python test_api.py
```

Este script testa todos os endpoints da API e exibe um relatório completo.

## Documentação da API

Acesse a documentação interativa:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Endpoints Disponíveis

### Autenticação (`/auth`)
- `POST /auth/register` - Registrar novo usuário
- `POST /auth/login` - Login e obtenção de token JWT
- `GET /auth/me` - Obter dados do usuário autenticado

### Usuários (`/users`)
- `GET /users` - Listar todos os usuários (Admin)
- `GET /users/{id}` - Obter detalhes de um usuário (Admin)
- `PUT /users/{id}/role` - Alterar role de um usuário (Admin)
- `DELETE /users/{id}` - Deletar um usuário (Admin)
- `GET /users/{id}/stats` - Estatísticas de empréstimos do usuário (Admin/Próprio)

### Categorias (`/categories`)
- `GET /categories` - Listar todas as categorias
- `POST /categories` - Criar nova categoria (Admin)
- `GET /categories/{id}` - Obter detalhes de uma categoria
- `PUT /categories/{id}` - Atualizar categoria (Admin)
- `DELETE /categories/{id}` - Deletar categoria (Admin)
- `GET /categories/{id}/books` - Listar livros de uma categoria

### Livros (`/books`)
- `GET /books` - Listar livros (com filtros: search, category_id, available)
- `POST /books` - Adicionar novo livro (Librarian/Admin)
- `GET /books/{id}` - Obter detalhes de um livro
- `PUT /books/{id}` - Atualizar livro (Librarian/Admin)
- `DELETE /books/{id}` - Deletar livro (Admin)
- `GET /books/{id}/availability` - Verificar disponibilidade de um livro

### Empréstimos (`/loans`)
- `GET /loans` - Listar todos os empréstimos (Librarian/Admin)
- `POST /loans` - Criar empréstimo
- `GET /loans/{id}` - Obter detalhes de um empréstimo
- `PUT /loans/{id}/return` - Devolver livro (Librarian/Admin)
- `GET /loans/my-loans` - Listar meus empréstimos
- `GET /loans/overdue` - Listar empréstimos atrasados (Librarian/Admin)

## Estrutura do Projeto

```
biblioteca/
├── backend/
│   ├── routers/
│   │   ├── auth.py         # Endpoints de autenticação
│   │   ├── users.py        # Endpoints de usuários
│   │   ├── categories.py   # Endpoints de categorias
│   │   ├── books.py        # Endpoints de livros
│   │   └── loans.py        # Endpoints de empréstimos
│   ├── auth.py             # Lógica de JWT e autenticação
│   ├── database.py         # Configuração do banco de dados
│   ├── main.py             # Aplicação FastAPI principal
│   ├── models.py           # Modelos SQLAlchemy
│   ├── schemas.py          # Schemas Pydantic
│   ├── seed.py             # Script de população do banco
│   └── requirements.txt    # Dependências Python
├── frontend/
│   ├── index.html          # Página principal
│   ├── login.html          # Página de login
│   ├── dashboard.html      # Dashboard do usuário
│   ├── books.html          # Listagem de livros
│   ├── loans.html          # Gerenciamento de empréstimos
│   └── admin.html          # Painel administrativo
├── test_api.py             # Script de testes da API
├── .env.example            # Exemplo de variáveis de ambiente
└── README.md               # Este arquivo
```

## Funcionalidades

### Gerenciamento de Usuários
- Registro e autenticação com JWT
- Três níveis de acesso: Admin, Librarian, Member
- Perfil do usuário com estatísticas de empréstimos

### Gerenciamento de Livros
- CRUD completo de livros
- Categorização de livros
- Busca por título, autor ou ISBN
- Controle de quantidade e disponibilidade

### Gerenciamento de Empréstimos
- Emprestar livros com prazo de devolução
- Devolução de livros
- Controle de status (ativo, devolvido, atrasado)
- Histórico de empréstimos
- Listagem de empréstimos atrasados

### Interface Web
- Login e autenticação
- Dashboard com resumo de atividades
- Listagem e busca de livros
- Sistema de empréstimos
- Painel administrativo

## Regras de Negócio

1. **Empréstimos:**
   - Usuário só pode emprestar livro disponível (available > 0)
   - Prazo padrão: 14 dias
   - Usuário pode ter múltiplos empréstimos ativos
   - Livro atrasado tem status "overdue" automaticamente

2. **Permissões:**
   - Member: pode emprestar e devolver livros, ver seus empréstimos
   - Librarian: pode gerenciar livros e empréstimos
   - Admin: acesso total ao sistema

3. **Livros:**
   - ISBN deve ser único
   - Categoria é obrigatória
   - Quantidade disponível nunca pode ser negativa

## Desenvolvimento

### Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste as configurações:

```bash
cp .env.example .env
```

### Adicionar Dados ao Banco

Para resetar e repopular o banco:

```bash
cd biblioteca/backend
python seed.py
```

### Testar Endpoints

Use o Swagger UI em `http://localhost:8000/docs` ou execute:

```bash
python test_api.py
```

## Deploy na Vercel

Este projeto está pronto para deploy na Vercel com backend FastAPI e frontend estático.

### Passo a Passo Rápido

1. **Fazer push do código para GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/seu-usuario/biblioteca.git
   git push -u origin main
   ```

2. **Importar projeto na Vercel:**
   - Acesse https://vercel.com/
   - Clique em "Add New" > "Project"
   - Selecione seu repositório
   - Clique em "Import"

3. **Configurar variáveis de ambiente:**

   Gere a SECRET_KEY:
   ```bash
   python scripts/generate_secret.py
   ```

   Configure na Vercel (Settings > Environment Variables):
   - `SECRET_KEY` - Chave gerada pelo script
   - `DATABASE_URL` - URL do PostgreSQL (Vercel Postgres, Neon, Supabase)
   - `ENVIRONMENT` - production

4. **Deploy automático:**
   - Clique em "Deploy"
   - Aguarde 2-5 minutos
   - Acesse a URL fornecida

5. **Popular banco de dados:**
   ```bash
   # Configure DATABASE_URL localmente
   export DATABASE_URL="sua-url-postgresql"
   export SECRET_KEY="sua-secret-key"

   # Execute o seed de produção
   python scripts/prod_seed.py
   ```

### Variáveis de Ambiente Necessárias

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| SECRET_KEY | Chave para JWT (gerar com script) | Sim |
| DATABASE_URL | URL PostgreSQL | Sim |
| ENVIRONMENT | production ou development | Sim |
| FRONTEND_URL | URL do frontend para CORS | Não |

### Documentação Completa

Para guia completo de deploy, troubleshooting e configurações avançadas, consulte:
**[DEPLOY.md](./DEPLOY.md)**

### Arquivos de Deploy

O projeto inclui:
- `vercel.json` - Configuração de rotas e builds
- `api/index.py` - Handler serverless para FastAPI
- `runtime.txt` - Versão do Python (3.11)
- `.vercelignore` - Arquivos a ignorar
- `scripts/generate_secret.py` - Gera SECRET_KEY segura
- `scripts/prod_seed.py` - Seed para produção

### URLs em Produção

- **Frontend:** https://seu-projeto.vercel.app
- **API:** https://seu-projeto.vercel.app/api
- **Docs:** https://seu-projeto.vercel.app/api/docs

### Banco de Dados

Para produção, use PostgreSQL em vez de SQLite. Opções gratuitas:
- **Vercel Postgres** (integrado)
- **Neon** (https://neon.tech)
- **Supabase** (https://supabase.com)
- **Railway** (https://railway.app)

O código já está preparado para funcionar com PostgreSQL ou SQLite (desenvolvimento).

## Próximos Passos

- [x] Deploy na Vercel/Railway
- [ ] Adicionar paginação em todos os endpoints
- [ ] Implementar sistema de multas
- [ ] Adicionar renovação de empréstimos
- [ ] Sistema de reserva de livros
- [ ] Notificações por email
- [ ] Upload de capa de livros

## Licença

Este projeto foi desenvolvido como exemplo educacional.
