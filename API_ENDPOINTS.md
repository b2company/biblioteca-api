# API Endpoints - Sistema Biblioteca

## Autenticação (Auth Router)
| Método | Endpoint | Descrição | Auth | Role |
|--------|----------|-----------|------|------|
| POST | `/auth/register` | Criar novo usuário | ❌ | - |
| POST | `/auth/login` | Login (retorna JWT token) | ❌ | - |
| GET | `/auth/me` | Obter dados do usuário logado | ✅ | Qualquer |

---

## Usuários (Users Router) ✅
| Método | Endpoint | Descrição | Auth | Role |
|--------|----------|-----------|------|------|
| GET | `/users` | Listar usuários (paginado, filtros) | ✅ | Admin |
| GET | `/users/{id}` | Detalhes de usuário | ✅ | Admin ou próprio |
| PUT | `/users/{id}/role` | Alterar role do usuário | ✅ | Admin |
| GET | `/users/{id}/stats` | Estatísticas de empréstimos | ✅ | Admin/Librarian ou próprio |

---

## Categorias (Categories Router) ✅
| Método | Endpoint | Descrição | Auth | Role |
|--------|----------|-----------|------|------|
| GET | `/categories` | Listar categorias | ❌ | - |
| POST | `/categories` | Criar categoria | ✅ | Admin/Librarian |
| GET | `/categories/{id}` | Detalhes de categoria | ❌ | - |
| PUT | `/categories/{id}` | Atualizar categoria | ✅ | Admin/Librarian |
| DELETE | `/categories/{id}` | Deletar categoria | ✅ | Admin |

---

## Livros (Books Router) ⏳
| Método | Endpoint | Descrição | Auth | Role |
|--------|----------|-----------|------|------|
| GET | `/books` | Listar livros | ❌ | - |
| POST | `/books` | Criar livro | ✅ | Admin/Librarian |
| GET | `/books/{id}` | Detalhes de livro | ❌ | - |
| PUT | `/books/{id}` | Atualizar livro | ✅ | Admin/Librarian |
| DELETE | `/books/{id}` | Deletar livro | ✅ | Admin |
| GET | `/books/search` | Buscar livros | ❌ | - |

---

## Empréstimos (Loans Router) ⏳
| Método | Endpoint | Descrição | Auth | Role |
|--------|----------|-----------|------|------|
| POST | `/loans` | Criar empréstimo | ✅ | Admin/Librarian |
| GET | `/loans` | Listar empréstimos | ✅ | Admin/Librarian |
| GET | `/loans/{id}` | Detalhes de empréstimo | ✅ | Admin/Librarian ou dono |
| PUT | `/loans/{id}/return` | Devolver livro | ✅ | Admin/Librarian |
| GET | `/loans/overdue` | Listar empréstimos atrasados | ✅ | Admin/Librarian |

---

## Legenda
- ✅ = Implementado
- ⏳ = Aguardando implementação
- ❌ = Não requer autenticação
- ✅ = Requer autenticação

---

## Regras de Autorização

### Roles
1. **Admin**: Acesso total a todos os endpoints
2. **Librarian**: Gerenciar livros, categorias e empréstimos
3. **Member**: Ver livros, categorias e próprios empréstimos

### Regras Específicas
- **Ver próprio perfil**: Qualquer usuário autenticado
- **Ver stats de outro usuário**: Admin ou Librarian
- **Alterar role**: Apenas Admin
- **Gerenciar livros/categorias**: Admin ou Librarian
- **Fazer empréstimo**: Admin ou Librarian (para qualquer usuário)
- **Ver empréstimos**: Admin/Librarian (todos) ou Member (próprios)

---

## Paginação

Endpoints que suportam paginação:
- `/users` - Query params: `page`, `limit`, `role`
- `/books` - Query params: `page`, `limit`, `category_id`, `available`
- `/loans` - Query params: `page`, `limit`, `status`, `user_id`

Formato de resposta paginada:
```json
{
  "total": 100,
  "page": 1,
  "limit": 10,
  "items": [...]
}
```

---

## Filtros

### Users
- `role`: admin | librarian | member

### Books
- `category_id`: int
- `available`: bool (apenas disponíveis)

### Loans
- `status`: active | returned | overdue
- `user_id`: int

---

## Status Codes

| Code | Descrição |
|------|-----------|
| 200 | Sucesso |
| 201 | Criado |
| 400 | Erro de validação |
| 401 | Não autenticado |
| 403 | Sem permissão |
| 404 | Não encontrado |
| 409 | Conflito (ex: ISBN duplicado) |
| 422 | Entidade não processável |
| 500 | Erro interno |

