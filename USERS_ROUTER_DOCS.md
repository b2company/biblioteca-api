# Router de Usuários - Documentação

## Arquivo Criado

`/Users/odavi.feitosa/biblioteca/backend/routers/users.py`

## Endpoints Implementados

### 1. GET /users
**Descrição**: Listar usuários com paginação e filtro opcional por role

**Autenticação**: Requerida (Admin only)

**Query Parameters**:
- `role` (opcional): Filtrar por role (admin, librarian, member)
- `page` (obrigatório, default=1): Número da página
- `limit` (obrigatório, default=10, max=100): Itens por página

**Response**:
```json
{
  "total": 25,
  "page": 1,
  "limit": 10,
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@biblioteca.com",
      "role": "admin",
      "created_at": "2026-01-01T00:00:00"
    }
  ]
}
```

**Autorização**: Apenas administradores

---

### 2. GET /users/{user_id}
**Descrição**: Obter detalhes de um usuário específico

**Autenticação**: Requerida

**Path Parameters**:
- `user_id` (int): ID do usuário

**Response**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@biblioteca.com",
  "role": "admin",
  "created_at": "2026-01-01T00:00:00"
}
```

**Autorização**:
- Administradores: podem ver qualquer usuário
- Outros usuários: só podem ver o próprio perfil

**Erros**:
- 403: Usuário tentando ver perfil de outro usuário
- 404: Usuário não encontrado

---

### 3. PUT /users/{user_id}/role
**Descrição**: Alterar a role de um usuário

**Autenticação**: Requerida (Admin only)

**Path Parameters**:
- `user_id` (int): ID do usuário

**Request Body**:
```json
{
  "role": "librarian"
}
```

**Response**:
```json
{
  "id": 1,
  "username": "usuario",
  "email": "usuario@biblioteca.com",
  "role": "librarian",
  "created_at": "2026-01-01T00:00:00"
}
```

**Autorização**: Apenas administradores

**Validações**:
- Role deve ser um dos valores válidos: admin, librarian, member

**Erros**:
- 403: Usuário não é administrador
- 404: Usuário não encontrado

---

### 4. GET /users/{user_id}/stats
**Descrição**: Obter estatísticas de empréstimos do usuário

**Autenticação**: Requerida

**Path Parameters**:
- `user_id` (int): ID do usuário

**Response**:
```json
{
  "active_loans": 2,
  "total_loans": 15,
  "overdue_loans": 0,
  "can_borrow": true
}
```

**Campos da Resposta**:
- `active_loans`: Quantidade de empréstimos ativos
- `total_loans`: Total de empréstimos (histórico completo)
- `overdue_loans`: Empréstimos atrasados (due_date < now)
- `can_borrow`: Se o usuário pode fazer novos empréstimos

**Regras de Negócio**:
- `can_borrow = true` se:
  - `overdue_loans == 0` E
  - `active_loans < 3`

**Autorização**:
- Administradores e bibliotecários: podem ver estatísticas de qualquer usuário
- Membros: só podem ver próprias estatísticas

**Erros**:
- 403: Membro tentando ver estatísticas de outro usuário
- 404: Usuário não encontrado

---

## Funções Helper de Autorização

### `require_admin(current_user)`
Dependency que garante que o usuário atual é administrador.

**Retorna**: User object se admin
**Exceção**: HTTPException 403 se não for admin

### `require_admin_or_librarian(current_user)`
Dependency que garante que o usuário atual é admin ou librarian.

**Retorna**: User object se admin ou librarian
**Exceção**: HTTPException 403 se for apenas member

---

## Schemas Adicionais Criados

### `RoleUpdate`
```python
{
  "role": UserRole  # admin | librarian | member
}
```

### `UserListResponse`
```python
{
  "total": int,
  "page": int,
  "limit": int,
  "users": list[UserResponse]
}
```

### `UserStatsResponse`
```python
{
  "active_loans": int,
  "total_loans": int,
  "overdue_loans": int,
  "can_borrow": bool
}
```

---

## Integração com main.py

O arquivo `/Users/odavi.feitosa/biblioteca/backend/main.py` foi atualizado para incluir:

```python
from backend.routers import auth, users, categories

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(categories.router, tags=["categories"])
```

Os routers de books e loans estão comentados aguardando implementação pelos Agents 1 e 2.

---

## Segurança Implementada

1. **Autenticação JWT**: Todos os endpoints requerem token válido
2. **Autorização por Role**:
   - Admin: acesso total
   - Librarian: acesso a estatísticas
   - Member: acesso apenas aos próprios dados
3. **Validação de Dados**: Pydantic valida todos os inputs
4. **Password Hash**: Não é exposto em nenhum endpoint (UserResponse não inclui)

---

## Dependências Utilizadas

- `fastapi`: Framework web
- `sqlalchemy`: ORM para database
- `pydantic`: Validação de dados
- `jose`: JWT tokens (via auth.py)
- `passlib`: Password hashing (via auth.py)

---

## Status do Projeto

✅ Router de Usuários completo e funcional
✅ Main.py atualizado com routers existentes
⏳ Aguardando routers de Books (Agent 1) e Loans (Agent 2)

---

## Próximos Passos

1. Agent 1 deve criar `/backend/routers/books.py`
2. Agent 2 deve criar `/backend/routers/loans.py`
3. Descomentar imports no main.py quando todos estiverem prontos
4. Testar integração completa
