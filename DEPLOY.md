# Guia de Deploy na Vercel

Este guia completo te ajudará a fazer o deploy do projeto Biblioteca na Vercel, incluindo backend (FastAPI) e frontend (HTML/CSS/JS).

## Pré-requisitos

- Conta no GitHub
- Conta na Vercel (pode usar login do GitHub)
- Conta no Vercel Postgres ou outro serviço PostgreSQL (Neon, Supabase, PlanetScale)

## Preparação do Repositório

### 1. Criar Repositório no GitHub

```bash
cd biblioteca
git init
git add .
git commit -m "Initial commit - Biblioteca API"
git branch -M main
git remote add origin https://github.com/seu-usuario/biblioteca.git
git push -u origin main
```

### 2. Verificar Arquivos de Configuração

Certifique-se de que os seguintes arquivos existem:

- `vercel.json` - Configuração de rotas e builds
- `api/index.py` - Handler serverless para FastAPI
- `runtime.txt` - Versão do Python
- `.vercelignore` - Arquivos a ignorar no deploy
- `backend/requirements.txt` - Dependências Python (com mangum)

## Deploy na Vercel

### 1. Importar Projeto

1. Acesse https://vercel.com/
2. Clique em "Add New" > "Project"
3. Selecione seu repositório do GitHub
4. Clique em "Import"

### 2. Configurar Projeto

**Framework Preset:** Other (a Vercel detectará automaticamente)

**Root Directory:** . (raiz do projeto)

**Build Command:** (deixe vazio - não é necessário)

**Output Directory:** (deixe vazio)

### 3. Configurar Variáveis de Ambiente

Antes de fazer o deploy, configure as seguintes variáveis de ambiente:

#### Gerar SECRET_KEY

Execute localmente:

```bash
python scripts/generate_secret.py
```

Copie a SECRET_KEY gerada.

#### Configurar na Vercel

No painel da Vercel, vá em "Settings" > "Environment Variables" e adicione:

**Variáveis Obrigatórias:**

| Nome | Valor | Descrição |
|------|-------|-----------|
| `SECRET_KEY` | (gerada pelo script) | Chave para JWT e criptografia |
| `DATABASE_URL` | postgresql://... | URL do PostgreSQL |
| `ENVIRONMENT` | production | Indica ambiente de produção |

**Variáveis Opcionais:**

| Nome | Valor | Descrição |
|------|-------|-----------|
| `FRONTEND_URL` | https://seu-projeto.vercel.app | URL do frontend para CORS |

### 4. Fazer Deploy

1. Clique em "Deploy"
2. Aguarde o build e deploy (2-5 minutos)
3. Acesse a URL fornecida pela Vercel

## Configuração do Banco de Dados PostgreSQL

### Opção 1: Vercel Postgres (Recomendado)

1. No dashboard do projeto na Vercel, vá em "Storage"
2. Clique em "Create Database" > "Postgres"
3. Siga o wizard de criação
4. A variável `DATABASE_URL` será automaticamente configurada

### Opção 2: Neon (Grátis)

1. Acesse https://neon.tech
2. Crie uma conta e um novo projeto
3. Copie a connection string (postgres://...)
4. Adicione como variável `DATABASE_URL` na Vercel

### Opção 3: Supabase (Grátis)

1. Acesse https://supabase.com
2. Crie um projeto
3. Vá em Settings > Database
4. Copie a "Connection string" (mode: Session)
5. Adicione como variável `DATABASE_URL` na Vercel

### Opção 4: Railway (Grátis/Pago)

1. Acesse https://railway.app
2. Crie um novo projeto PostgreSQL
3. Copie a connection string
4. Adicione como variável `DATABASE_URL` na Vercel

## Seed do Banco de Dados em Produção

### Opção 1: Usar Railway/Heroku CLI (Recomendado)

Se você estiver usando Railway ou Heroku para o banco:

```bash
# Railway
railway run python scripts/prod_seed.py

# Heroku
heroku run python scripts/prod_seed.py
```

### Opção 2: Executar Localmente Contra Produção

```bash
# Configure DATABASE_URL temporariamente
export DATABASE_URL="sua-url-postgresql-producao"
export SECRET_KEY="sua-secret-key-producao"

# Execute o seed
python scripts/prod_seed.py
```

**IMPORTANTE:** Nunca faça commit do DATABASE_URL de produção!

### Opção 3: Usar Vercel CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Link ao projeto
vercel link

# Executar comando em produção
vercel env pull .env.production
source .env.production
python scripts/prod_seed.py
```

## Estrutura de URLs em Produção

Após o deploy, sua aplicação estará disponível em:

- **Frontend:** https://seu-projeto.vercel.app
- **API:** https://seu-projeto.vercel.app/api
- **Docs:** https://seu-projeto.vercel.app/api/docs
- **Root endpoint:** https://seu-projeto.vercel.app/api/

**Exemplo de rotas:**

- `GET /api/` - Status da API
- `POST /api/auth/login` - Login
- `GET /api/books` - Listar livros
- `GET /api/docs` - Documentação Swagger

## Atualizar Frontend para Produção

Os arquivos HTML do frontend precisam apontar para a URL correta da API em produção.

### 1. Criar arquivo de configuração

Crie `frontend/config.js`:

```javascript
// Detecta automaticamente o ambiente
const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : window.location.origin + '/api';

console.log('API URL:', API_BASE_URL);
```

### 2. Importar em todos os HTMLs

Adicione no `<head>` de cada arquivo HTML:

```html
<script src="config.js"></script>
```

### 3. Usar a variável nas chamadas

Em vez de:

```javascript
fetch('http://localhost:8000/auth/login', ...)
```

Use:

```javascript
fetch(`${API_BASE_URL}/auth/login`, ...)
```

## Troubleshooting

### Erro 404 nas rotas da API

**Problema:** Rotas da API retornam 404

**Solução:** Verifique se `vercel.json` está correto e se as rotas começam com `/api`

### Erro de CORS

**Problema:** Frontend não consegue acessar API (CORS error)

**Solução:**
1. Verifique se `ENVIRONMENT=production` está configurado
2. Configure `FRONTEND_URL` com a URL do seu projeto
3. Verifique o código CORS em `backend/main.py`

### Erro de Conexão com Banco

**Problema:** Erros de conexão com PostgreSQL

**Solução:**
1. Verifique se `DATABASE_URL` está correta
2. Certifique-se de que a URL começa com `postgresql://` (não `postgres://`)
3. Verifique se o IP da Vercel está permitido no firewall do banco

### Imports Falhando

**Problema:** Erros de import do tipo `ModuleNotFoundError`

**Solução:**
1. Verifique se `backend/requirements.txt` tem todas as dependências
2. Certifique-se de que `mangum` está nas requirements
3. Verifique o path no `api/index.py`

### Tabelas Não Criadas

**Problema:** Banco vazio, sem tabelas

**Solução:**
1. Execute o seed de produção (veja seção acima)
2. Verifique logs da Vercel para erros de criação de tabelas
3. Certifique-se de que `Base.metadata.create_all()` está sendo executado

### Build Timeout

**Problema:** Build demora muito e dá timeout

**Solução:**
1. Adicione arquivo `.vercelignore` para ignorar arquivos grandes
2. Remova dependências desnecessárias do `requirements.txt`
3. Use versões específicas das dependências (sem `>=`)

### Secret Key Não Configurada

**Problema:** Erros relacionados a SECRET_KEY

**Solução:**
1. Gere uma nova chave: `python scripts/generate_secret.py`
2. Configure nas variáveis de ambiente da Vercel
3. Redeploy o projeto

## Logs e Monitoramento

### Ver Logs em Tempo Real

1. Acesse o dashboard do projeto na Vercel
2. Vá em "Deployments"
3. Clique no deployment mais recente
4. Clique em "View Function Logs"

### Monitorar Performance

1. Vá em "Analytics" no dashboard
2. Monitore tempo de resposta, erros, uso de recursos

### Alertas

Configure alertas em "Settings" > "Notifications" para ser notificado sobre:
- Builds falhados
- Erros em produção
- Uso excessivo de recursos

## Domínio Customizado

### Adicionar Domínio Próprio

1. Vá em "Settings" > "Domains"
2. Clique em "Add"
3. Digite seu domínio (ex: biblioteca.com.br)
4. Siga as instruções para configurar DNS

### Configurar SSL

A Vercel automaticamente configura SSL/HTTPS para todos os domínios.

## Backups

### Backup do Banco de Dados

Configure backups automáticos no seu provedor PostgreSQL:

- **Vercel Postgres:** Backups automáticos diários
- **Neon:** Configurar em Settings > Backups
- **Supabase:** Backups automáticos
- **Railway:** Configure via CLI ou dashboard

### Backup Manual

```bash
# Exportar schema e dados
pg_dump $DATABASE_URL > backup.sql

# Restaurar
psql $DATABASE_URL < backup.sql
```

## CI/CD

### Deploy Automático

A Vercel já configura CI/CD automaticamente:

- **Production:** Deploys automáticos do branch `main`
- **Preview:** Deploys de preview para PRs e outros branches

### Configurar Ambientes

1. Crie branches: `development`, `staging`, `main`
2. Configure variáveis de ambiente por branch
3. Deploys automáticos para cada ambiente

## Segurança

### Boas Práticas

1. **SECRET_KEY única** para cada ambiente
2. **Nunca commite** credenciais ou .env
3. **Ative 2FA** na Vercel e GitHub
4. **Limite permissões** do usuário do banco
5. **Configure rate limiting** (Vercel tem limites padrão)
6. **Monitore logs** regularmente

### Variáveis Sensíveis

Sempre use variáveis de ambiente para:
- SECRET_KEY
- DATABASE_URL
- Chaves de API externas
- Credenciais de serviços

## Rollback

### Reverter Deploy

1. Vá em "Deployments"
2. Encontre um deployment anterior que funcionava
3. Clique nos 3 pontinhos > "Promote to Production"

### Rollback via CLI

```bash
vercel rollback [deployment-url]
```

## Custos

### Vercel

- **Hobby (Grátis):**
  - 100 GB-hours serverless function execution
  - 100 GB bandwidth
  - Ideal para desenvolvimento e projetos pequenos

- **Pro ($20/mês):**
  - 1000 GB-hours execution
  - 1 TB bandwidth
  - Analytics avançado

### PostgreSQL

- **Vercel Postgres:** $0.12/GB-hora
- **Neon:** 10GB grátis, depois pago
- **Supabase:** 500MB grátis, depois pago
- **Railway:** $5/mês após trial

## Suporte

### Recursos

- Documentação Vercel: https://vercel.com/docs
- Discord Vercel: https://vercel.com/discord
- Stack Overflow: tag `vercel`

### Contato

- Support Vercel: support@vercel.com (Pro plan)
- Community: https://github.com/vercel/community

## Checklist de Deploy

- [ ] Repositório GitHub criado e código pushed
- [ ] Projeto importado na Vercel
- [ ] SECRET_KEY gerada e configurada
- [ ] DATABASE_URL configurada (PostgreSQL)
- [ ] ENVIRONMENT=production configurada
- [ ] Deploy realizado com sucesso
- [ ] Seed de produção executado
- [ ] Usuário admin criado
- [ ] Frontend acessível
- [ ] API respondendo em /api
- [ ] Docs acessível em /api/docs
- [ ] Login funcionando
- [ ] CORS configurado corretamente
- [ ] Logs verificados (sem erros)
- [ ] Domínio customizado configurado (opcional)
- [ ] Backups configurados
- [ ] Monitoramento ativo

## Conclusão

Após seguir este guia, sua aplicação Biblioteca estará rodando em produção na Vercel com:

- Backend FastAPI serverless
- Frontend estático otimizado
- Banco de dados PostgreSQL
- SSL/HTTPS automático
- CI/CD configurado
- Monitoramento ativo

Para atualizações, basta fazer push no GitHub que a Vercel automaticamente fará o deploy!
