"""
Script para popular o banco de dados com dados iniciais.
Limpa o banco existente e cria dados de exemplo.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Imports relativos quando executado diretamente
try:
    from backend.database import SessionLocal, engine, Base
    from backend.models import User, Category, Book, Loan, UserRole, LoanStatus
    from backend.auth import hash_password
except ModuleNotFoundError:
    from database import SessionLocal, engine, Base
    from models import User, Category, Book, Loan, UserRole, LoanStatus
    from auth import hash_password


def drop_all_tables():
    """Remove todas as tabelas do banco de dados."""
    print("🗑️  Removendo tabelas existentes...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tabelas removidas!")


def create_all_tables():
    """Cria todas as tabelas no banco de dados."""
    print("🔨 Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas!")


def seed_users(db: Session):
    """Cria usuários iniciais."""
    print("👥 Criando usuários...")

    users = [
        User(
            username="admin",
            email="admin@biblioteca.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN
        ),
        User(
            username="bibliotecario",
            email="biblio@biblioteca.com",
            password_hash=hash_password("biblio123"),
            role=UserRole.LIBRARIAN
        ),
        User(
            username="joao",
            email="joao@email.com",
            password_hash=hash_password("joao123"),
            role=UserRole.MEMBER
        ),
        User(
            username="maria",
            email="maria@email.com",
            password_hash=hash_password("maria123"),
            role=UserRole.MEMBER
        ),
    ]

    db.add_all(users)
    db.commit()
    print(f"✅ {len(users)} usuários criados!")
    return users


def seed_categories(db: Session):
    """Cria categorias iniciais."""
    print("📚 Criando categorias...")

    categories = [
        Category(
            name="Ficção Científica",
            description="Livros de ficção científica, cyberpunk, space opera"
        ),
        Category(
            name="Romance",
            description="Literatura romântica e relacionamentos"
        ),
        Category(
            name="Técnico/Programação",
            description="Livros técnicos sobre programação e tecnologia"
        ),
        Category(
            name="História",
            description="Livros históricos e biografias históricas"
        ),
        Category(
            name="Biografia",
            description="Biografias e autobiografias"
        ),
    ]

    db.add_all(categories)
    db.commit()
    print(f"✅ {len(categories)} categorias criadas!")
    return categories


def seed_books(db: Session, categories: list):
    """Cria livros iniciais."""
    print("📖 Criando livros...")

    # Mapear categorias por nome para facilitar
    cat_map = {cat.name: cat.id for cat in categories}

    books = [
        # Ficção Científica
        Book(
            isbn="9780441013593",
            title="Neuromancer",
            author="William Gibson",
            publisher="Ace Books",
            year=1984,
            category_id=cat_map["Ficção Científica"],
            quantity=2,
            available=2
        ),
        Book(
            isbn="9780441569595",
            title="Dune",
            author="Frank Herbert",
            publisher="Chilton Books",
            year=1965,
            category_id=cat_map["Ficção Científica"],
            quantity=3,
            available=2
        ),
        Book(
            isbn="9780553293357",
            title="Fundação",
            author="Isaac Asimov",
            publisher="Aleph",
            year=1951,
            category_id=cat_map["Ficção Científica"],
            quantity=2,
            available=1
        ),

        # Romance
        Book(
            isbn="9788580416923",
            title="Orgulho e Preconceito",
            author="Jane Austen",
            publisher="Martin Claret",
            year=1813,
            category_id=cat_map["Romance"],
            quantity=2,
            available=2
        ),
        Book(
            isbn="9788544001981",
            title="A Culpa é das Estrelas",
            author="John Green",
            publisher="Intrínseca",
            year=2012,
            category_id=cat_map["Romance"],
            quantity=3,
            available=3
        ),

        # Técnico/Programação
        Book(
            isbn="9780132350884",
            title="Clean Code",
            author="Robert C. Martin",
            publisher="Prentice Hall",
            year=2008,
            category_id=cat_map["Técnico/Programação"],
            quantity=2,
            available=2
        ),
        Book(
            isbn="9780596517748",
            title="JavaScript: The Good Parts",
            author="Douglas Crockford",
            publisher="O'Reilly",
            year=2008,
            category_id=cat_map["Técnico/Programação"],
            quantity=1,
            available=0
        ),
        Book(
            isbn="9780134685991",
            title="Effective Java",
            author="Joshua Bloch",
            publisher="Addison-Wesley",
            year=2017,
            category_id=cat_map["Técnico/Programação"],
            quantity=2,
            available=2
        ),
        Book(
            isbn="9781617294945",
            title="Python Crash Course",
            author="Eric Matthes",
            publisher="No Starch Press",
            year=2019,
            category_id=cat_map["Técnico/Programação"],
            quantity=3,
            available=3
        ),

        # História
        Book(
            isbn="9788535902773",
            title="Sapiens",
            author="Yuval Noah Harari",
            publisher="L&PM",
            year=2011,
            category_id=cat_map["História"],
            quantity=4,
            available=4
        ),
        Book(
            isbn="9788580578973",
            title="1808",
            author="Laurentino Gomes",
            publisher="Planeta",
            year=2007,
            category_id=cat_map["História"],
            quantity=2,
            available=2
        ),
        Book(
            isbn="9788535922844",
            title="Homo Deus",
            author="Yuval Noah Harari",
            publisher="Companhia das Letras",
            year=2015,
            category_id=cat_map["História"],
            quantity=2,
            available=2
        ),

        # Biografia
        Book(
            isbn="9788580576467",
            title="Steve Jobs",
            author="Walter Isaacson",
            publisher="Companhia das Letras",
            year=2011,
            category_id=cat_map["Biografia"],
            quantity=2,
            available=2
        ),
        Book(
            isbn="9788535931495",
            title="Einstein: Sua Vida, Seu Universo",
            author="Walter Isaacson",
            publisher="Companhia das Letras",
            year=2007,
            category_id=cat_map["Biografia"],
            quantity=1,
            available=1
        ),
        Book(
            isbn="9788535928242",
            title="Leonardo da Vinci",
            author="Walter Isaacson",
            publisher="Intrínseca",
            year=2017,
            category_id=cat_map["Biografia"],
            quantity=2,
            available=2
        ),
    ]

    db.add_all(books)
    db.commit()
    print(f"✅ {len(books)} livros criados!")
    return books


def seed_loans(db: Session, users: list, books: list):
    """Cria empréstimos iniciais."""
    print("📋 Criando empréstimos...")

    # Encontrar usuários específicos
    joao = next(u for u in users if u.username == "joao")
    maria = next(u for u in users if u.username == "maria")

    # Encontrar livros específicos
    dune = next(b for b in books if b.title == "Dune")
    fundacao = next(b for b in books if b.title == "Fundação")
    javascript = next(b for b in books if b.title == "JavaScript: The Good Parts")

    now = datetime.utcnow()

    loans = [
        # João - empréstimo no prazo (vence em 7 dias)
        Loan(
            book_id=dune.id,
            user_id=joao.id,
            loan_date=now - timedelta(days=7),
            due_date=now + timedelta(days=7),
            status=LoanStatus.ACTIVE
        ),
        # João - empréstimo atrasado (venceu há 5 dias)
        Loan(
            book_id=fundacao.id,
            user_id=joao.id,
            loan_date=now - timedelta(days=19),
            due_date=now - timedelta(days=5),
            status=LoanStatus.OVERDUE
        ),
        # Maria - empréstimo devolvido
        Loan(
            book_id=javascript.id,
            user_id=maria.id,
            loan_date=now - timedelta(days=30),
            due_date=now - timedelta(days=16),
            return_date=now - timedelta(days=20),
            status=LoanStatus.RETURNED
        ),
    ]

    db.add_all(loans)
    db.commit()
    print(f"✅ {len(loans)} empréstimos criados!")
    return loans


def main():
    """Função principal para executar o seed."""
    print("\n" + "="*60)
    print("🌱 SEED DO BANCO DE DADOS - BIBLIOTECA")
    print("="*60 + "\n")

    # Remover e recriar tabelas
    drop_all_tables()
    create_all_tables()

    # Criar sessão do banco
    db = SessionLocal()

    try:
        # Popular dados
        users = seed_users(db)
        categories = seed_categories(db)
        books = seed_books(db, categories)
        loans = seed_loans(db, users, books)

        # Resumo
        print("\n" + "="*60)
        print("✨ SEED CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print(f"\n📊 Resumo:")
        print(f"   • {len(users)} usuários")
        print(f"   • {len(categories)} categorias")
        print(f"   • {len(books)} livros")
        print(f"   • {len(loans)} empréstimos")

        print(f"\n🔑 Credenciais de acesso:")
        print(f"   • Admin: admin / admin123")
        print(f"   • Bibliotecário: bibliotecario / biblio123")
        print(f"   • Usuário 1: joao / joao123")
        print(f"   • Usuário 2: maria / maria123")

        print("\n" + "="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Erro ao popular banco de dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
