"""
Script de teste manual para todos os endpoints da API.
Testa o fluxo completo do sistema.
"""
import requests
from datetime import datetime, timedelta
import json


BASE_URL = "http://localhost:8000"


class Colors:
    """Cores para output no terminal."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_test(name: str, success: bool, details: str = ""):
    """Imprime resultado do teste formatado."""
    status = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
    print(f"{status} {name}")
    if details:
        print(f"  {Colors.YELLOW}{details}{Colors.END}")
    if not success:
        print()


def print_section(title: str):
    """Imprime cabeçalho de seção."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


# Variáveis globais para armazenar tokens e IDs
tokens = {}
created_ids = {}


def test_register():
    """Teste 1: POST /auth/register - Criar novo usuário."""
    print_section("1. AUTENTICAÇÃO - REGISTRO")

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "username": "teste_user",
            "email": "teste@email.com",
            "password": "teste123"
        })

        success = response.status_code in [200, 201]
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            details += f" | User ID: {data.get('id')}"

        print_test("Registrar novo usuário", success, details)
        return success

    except Exception as e:
        print_test("Registrar novo usuário", False, f"Erro: {str(e)}")
        return False


def test_login(username: str, password: str, role: str):
    """Teste 2: POST /auth/login - Login e obter token."""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": username,
            "password": password
        })

        success = response.status_code == 200
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            token = data.get("access_token")
            tokens[role] = token
            details += f" | Token obtido para {username}"

        print_test(f"Login como {username} ({role})", success, details)
        return success

    except Exception as e:
        print_test(f"Login como {username}", False, f"Erro: {str(e)}")
        return False


def test_me(role: str):
    """Teste 3: GET /auth/me - Verificar usuário logado."""
    try:
        headers = {"Authorization": f"Bearer {tokens[role]}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

        success = response.status_code == 200
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            details += f" | User: {data.get('username')} | Role: {data.get('role')}"

        print_test(f"Verificar usuário logado ({role})", success, details)
        return success

    except Exception as e:
        print_test("Verificar usuário logado", False, f"Erro: {str(e)}")
        return False


def test_list_categories():
    """Teste 4: GET /categories - Listar categorias."""
    try:
        response = requests.get(f"{BASE_URL}/categories")

        success = response.status_code == 200
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            details += f" | {len(data)} categorias encontradas"
            if data:
                created_ids['category'] = data[0]['id']

        print_test("Listar categorias", success, details)
        return success

    except Exception as e:
        print_test("Listar categorias", False, f"Erro: {str(e)}")
        return False


def test_create_category():
    """Teste 5: POST /categories - Criar nova categoria (como admin)."""
    try:
        headers = {"Authorization": f"Bearer {tokens['admin']}"}
        response = requests.post(f"{BASE_URL}/categories", headers=headers, json={
            "name": "Filosofia",
            "description": "Livros de filosofia e pensamento crítico"
        })

        success = response.status_code in [200, 201]
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            details += f" | Categoria ID: {data.get('id')}"

        print_test("Criar nova categoria (admin)", success, details)
        return success

    except Exception as e:
        print_test("Criar nova categoria", False, f"Erro: {str(e)}")
        return False


def test_list_books():
    """Teste 6: GET /books - Listar livros com filtros."""
    try:
        # Sem filtros
        response = requests.get(f"{BASE_URL}/books")
        success1 = response.status_code == 200
        if success1:
            data = response.json()
            books_count = data.get('total', 0)
            books_list = data.get('books', [])
            if books_list:
                created_ids['book'] = books_list[0]['id']
        else:
            books_count = 0

        # Com filtro de categoria
        response2 = requests.get(f"{BASE_URL}/books?category_id=1")
        success2 = response2.status_code == 200

        # Com busca por título
        response3 = requests.get(f"{BASE_URL}/books?search=clean")
        success3 = response3.status_code == 200

        success = success1 and success2 and success3

        print_test("Listar livros (sem filtro)", success1, f"{books_count} livros")
        print_test("Listar livros (filtro categoria)", success2)
        print_test("Listar livros (busca por título)", success3)

        return success

    except Exception as e:
        print_test("Listar livros", False, f"Erro: {str(e)}")
        return False


def test_create_book():
    """Teste 7: POST /books - Adicionar livro (como librarian)."""
    try:
        headers = {"Authorization": f"Bearer {tokens['librarian']}"}
        response = requests.post(f"{BASE_URL}/books", headers=headers, json={
            "isbn": "9781234567890",
            "title": "Livro de Teste API",
            "author": "Autor Teste",
            "publisher": "Editora Teste",
            "year": 2024,
            "category_id": created_ids.get('category', 1),
            "quantity": 5,
            "available": 5
        })

        success = response.status_code in [200, 201]
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            created_ids['new_book'] = data.get('id')
            details += f" | Livro ID: {data.get('id')}"

        print_test("Adicionar livro (librarian)", success, details)
        return success

    except Exception as e:
        print_test("Adicionar livro", False, f"Erro: {str(e)}")
        return False


def test_get_book():
    """Teste 8: GET /books/{id} - Detalhes do livro."""
    try:
        book_id = created_ids.get('book', 1)
        response = requests.get(f"{BASE_URL}/books/{book_id}")

        success = response.status_code == 200
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            details += f" | {data.get('title')} por {data.get('author')}"

        print_test(f"Obter detalhes do livro #{book_id}", success, details)
        return success

    except Exception as e:
        print_test("Obter detalhes do livro", False, f"Erro: {str(e)}")
        return False


def test_create_loan():
    """Teste 9: POST /loans - Emprestar livro."""
    try:
        headers = {"Authorization": f"Bearer {tokens['member']}"}

        # Pegar ID do usuário member
        me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        user_id = me_response.json().get('id')

        # Usar livro recém-criado
        book_id = created_ids.get('new_book', 1)

        due_date = (datetime.now() + timedelta(days=14)).isoformat()

        response = requests.post(f"{BASE_URL}/loans", headers=headers, json={
            "book_id": book_id
        })

        success = response.status_code in [200, 201]
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            created_ids['loan'] = data.get('id')
            details += f" | Empréstimo ID: {data.get('id')}"

        print_test("Emprestar livro", success, details)
        return success

    except Exception as e:
        print_test("Emprestar livro", False, f"Erro: {str(e)}")
        return False


def test_my_loans():
    """Teste 10: GET /loans/my-loans - Ver meus empréstimos."""
    try:
        headers = {"Authorization": f"Bearer {tokens['member']}"}
        response = requests.get(f"{BASE_URL}/loans/my-loans", headers=headers)

        success = response.status_code == 200
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            details += f" | {len(data)} empréstimos ativos"

        print_test("Listar meus empréstimos", success, details)
        return success

    except Exception as e:
        print_test("Listar meus empréstimos", False, f"Erro: {str(e)}")
        return False


def test_return_loan():
    """Teste 11: PUT /loans/{id}/return - Devolver livro."""
    try:
        headers = {"Authorization": f"Bearer {tokens['librarian']}"}
        loan_id = created_ids.get('loan', 1)

        response = requests.put(f"{BASE_URL}/loans/{loan_id}/return", headers=headers)

        success = response.status_code == 200
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            details += f" | Status: {data.get('status')}"

        print_test(f"Devolver livro (empréstimo #{loan_id})", success, details)
        return success

    except Exception as e:
        print_test("Devolver livro", False, f"Erro: {str(e)}")
        return False


def test_list_users():
    """Teste 12: GET /users - Listar usuários (como admin)."""
    try:
        headers = {"Authorization": f"Bearer {tokens['admin']}"}
        response = requests.get(f"{BASE_URL}/users", headers=headers)

        success = response.status_code == 200
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            user_count = data.get('total', len(data.get('users', [])))
            details += f" | {user_count} usuários cadastrados"

        print_test("Listar todos os usuários (admin)", success, details)
        return success

    except Exception as e:
        print_test("Listar usuários", False, f"Erro: {str(e)}")
        return False


def test_update_user_role():
    """Teste 13: PUT /users/{id}/role - Alterar role (como admin)."""
    try:
        headers = {"Authorization": f"Bearer {tokens['admin']}"}

        # Buscar ID do usuário teste
        users_response = requests.get(f"{BASE_URL}/users", headers=headers)
        users_data = users_response.json()
        users = users_data.get('users', [])
        teste_user = next((u for u in users if u['username'] == 'teste_user'), None)

        if not teste_user:
            print_test("Alterar role do usuário", False, "Usuário teste não encontrado")
            return False

        user_id = teste_user['id']

        response = requests.put(
            f"{BASE_URL}/users/{user_id}/role",
            headers=headers,
            json={"role": "librarian"}
        )

        success = response.status_code == 200
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            details += f" | Novo role: {data.get('role')}"

        print_test(f"Alterar role do usuário #{user_id}", success, details)
        return success

    except Exception as e:
        print_test("Alterar role do usuário", False, f"Erro: {str(e)}")
        return False


def test_user_stats():
    """Teste 14: GET /users/{id}/stats - Ver estatísticas."""
    try:
        headers = {"Authorization": f"Bearer {tokens['admin']}"}

        # Buscar ID do usuário joao (tem empréstimos)
        users_response = requests.get(f"{BASE_URL}/users", headers=headers)
        users_data = users_response.json()
        users = users_data.get('users', [])
        joao = next((u for u in users if u['username'] == 'joao'), None)

        if not joao:
            print_test("Ver estatísticas do usuário", False, "Usuário joao não encontrado")
            return False

        user_id = joao['id']

        response = requests.get(f"{BASE_URL}/users/{user_id}/stats", headers=headers)

        success = response.status_code == 200
        details = f"Status: {response.status_code}"

        if success:
            data = response.json()
            details += f" | Total: {data.get('total_loans')} | Ativos: {data.get('active_loans')}"

        print_test(f"Ver estatísticas do usuário #{user_id}", success, details)
        return success

    except Exception as e:
        print_test("Ver estatísticas do usuário", False, f"Erro: {str(e)}")
        return False


def main():
    """Função principal para executar todos os testes."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}🧪 TESTES DA API - BIBLIOTECA{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"\n{Colors.YELLOW}Base URL: {BASE_URL}{Colors.END}\n")

    results = []

    # Testes de autenticação
    print_section("1-3. AUTENTICAÇÃO")
    results.append(test_register())
    results.append(test_login("admin", "admin123", "admin"))
    results.append(test_login("bibliotecario", "biblio123", "librarian"))
    results.append(test_login("joao", "joao123", "member"))

    if "admin" in tokens:
        results.append(test_me("admin"))

    # Testes de categorias
    print_section("4-5. CATEGORIAS")
    results.append(test_list_categories())
    if "admin" in tokens:
        results.append(test_create_category())

    # Testes de livros
    print_section("6-8. LIVROS")
    results.append(test_list_books())
    if "librarian" in tokens:
        results.append(test_create_book())
    results.append(test_get_book())

    # Testes de empréstimos
    print_section("9-11. EMPRÉSTIMOS")
    if "member" in tokens:
        results.append(test_create_loan())
        results.append(test_my_loans())
    if "librarian" in tokens:
        results.append(test_return_loan())

    # Testes de usuários
    print_section("12-14. USUÁRIOS")
    if "admin" in tokens:
        results.append(test_list_users())
        results.append(test_update_user_role())
        results.append(test_user_stats())

    # Resumo
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📊 RESUMO DOS TESTES{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Total de testes: {total}")
    print(f"{Colors.GREEN}✓ Passou: {passed}{Colors.END}")
    print(f"{Colors.RED}✗ Falhou: {failed}{Colors.END}")

    percentage = (passed / total * 100) if total > 0 else 0
    print(f"\nTaxa de sucesso: {percentage:.1f}%")

    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}\n")

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Testes interrompidos pelo usuário.{Colors.END}\n")
        exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Erro fatal: {str(e)}{Colors.END}\n")
        exit(1)
