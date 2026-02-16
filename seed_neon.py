#!/usr/bin/env python3
"""Script simples para popular banco Neon com dados iniciais."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from backend.database import SessionLocal, Base, engine
from backend.models import User, Category, Book, UserRole
from backend.auth import hash_password

def seed_database():
    """Popular banco com dados iniciais."""
    print("=" * 60)
    print("POPULANDO BANCO DE DADOS NEON")
    print("=" * 60)

    # Criar tabelas
    print("\n🔨 Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas!")

    db = SessionLocal()

    try:
        # Criar admin
        print("\n👤 Criando usuário admin...")
        admin = User(
            username="admin",
            email="admin@biblioteca.com",
            password_hash=hash_password("Admin@2026"),
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
        print("✅ Admin criado!")

        # Criar categorias
        print("\n📚 Criando categorias...")
        categorias = [
            ("Ficção", "Ficção geral e literatura"),
            ("Técnico", "Livros técnicos e programação"),
            ("Autoajuda", "Desenvolvimento pessoal"),
            ("História", "História e biografias"),
            ("Ciência", "Livros de ciência")
        ]

        cats = []
        for nome, desc in categorias:
            cat = Category(name=nome, description=desc)
            cats.append(cat)
            db.add(cat)
        db.commit()
        print(f"✅ {len(categorias)} categorias criadas!")

        # Criar alguns livros (ISBNs sem hífen para caber em 13 caracteres)
        print("\n📖 Criando livros...")
        livros = [
            ("9780451524935", "1984", "George Orwell", "Cia Letras", 1949, 0, 3, 3),
            ("9780316769174", "O Apanhador", "J.D. Salinger", "Todavia", 1951, 0, 2, 2),
            ("9780596009205", "Design Patterns", "Eric Freeman", "O'Reilly", 2004, 1, 2, 2),
            ("9788535902778", "Sapiens", "Yuval Harari", "Cia Letras", 2011, 3, 3, 3),
        ]

        for isbn, titulo, autor, editora, ano, cat_idx, qty, avail in livros:
            livro = Book(
                isbn=isbn,
                title=titulo,
                author=autor,
                publisher=editora,
                year=ano,
                category_id=cats[cat_idx].id,
                quantity=qty,
                available=avail
            )
            db.add(livro)
        db.commit()
        print(f"✅ {len(livros)} livros criados!")

        print("\n" + "=" * 60)
        print("✅ BANCO POPULADO COM SUCESSO!")
        print("=" * 60)
        print("\n🔑 Credenciais de Acesso:")
        print("   Username: admin")
        print("   Password: Admin@2026")
        print("\n🌐 Acesse sua aplicação na Vercel e faça login!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Erro: Configure DATABASE_URL")
        sys.exit(1)

    print(f"\n🗄️  Conectando ao banco: {db_url[:40]}...")
    seed_database()
