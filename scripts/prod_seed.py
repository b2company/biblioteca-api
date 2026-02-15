#!/usr/bin/env python3
"""
Script de seed para produção.

Este script popula o banco de dados PostgreSQL em produção com dados iniciais.
Apenas cria o usuário admin e categorias básicas - não cria dados de exemplo.

Uso:
    python scripts/prod_seed.py

Variáveis de ambiente necessárias:
    DATABASE_URL: URL de conexão com PostgreSQL
    SECRET_KEY: Chave secreta para JWT
"""
import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.database import engine, Base, SessionLocal
from backend.models import User, Category
from backend.auth import get_password_hash

def create_tables():
    """Cria todas as tabelas no banco."""
    print("Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

def seed_admin_user(db):
    """Cria o usuário admin."""
    print("\nCriando usuário admin...")

    # Verificar se admin já existe
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("Usuário admin já existe. Pulando...")
        return

    admin = User(
        username="admin",
        email="admin@biblioteca.com",
        full_name="Administrador",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("Usuário admin criado com sucesso!")
    print("Username: admin")
    print("Password: admin123")
    print("\nIMPORTANTE: Altere a senha do admin após o primeiro login!")

def seed_categories(db):
    """Cria categorias básicas."""
    print("\nCriando categorias...")

    categories = [
        {"name": "Ficção", "description": "Livros de ficção e literatura"},
        {"name": "Não-Ficção", "description": "Livros de não-ficção"},
        {"name": "Ciência", "description": "Livros científicos e técnicos"},
        {"name": "História", "description": "Livros de história"},
        {"name": "Biografia", "description": "Biografias e autobiografias"},
        {"name": "Infantil", "description": "Livros infantis"},
        {"name": "Juvenil", "description": "Livros para jovens"},
        {"name": "Tecnologia", "description": "Livros sobre tecnologia e computação"},
    ]

    for cat_data in categories:
        # Verificar se categoria já existe
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if existing:
            print(f"Categoria '{cat_data['name']}' já existe. Pulando...")
            continue

        category = Category(**cat_data)
        db.add(category)
        print(f"Categoria '{cat_data['name']}' criada.")

    db.commit()
    print("Categorias criadas com sucesso!")

def main():
    """Função principal."""
    print("=== Seed de Produção ===\n")

    # Verificar variáveis de ambiente
    if not os.getenv("DATABASE_URL"):
        print("ERRO: DATABASE_URL não configurada!")
        print("Configure a variável de ambiente DATABASE_URL antes de executar o seed.")
        sys.exit(1)

    if not os.getenv("SECRET_KEY"):
        print("AVISO: SECRET_KEY não configurada!")
        print("É altamente recomendado configurar SECRET_KEY em produção.")

    try:
        # Criar tabelas
        create_tables()

        # Criar sessão do banco
        db = SessionLocal()

        try:
            # Seed de dados
            seed_admin_user(db)
            seed_categories(db)

            print("\n=== Seed concluído com sucesso! ===")
            print("\nPróximos passos:")
            print("1. Faça login com o usuário admin")
            print("2. Altere a senha do admin")
            print("3. Crie os usuários bibliotecários e membros necessários")
            print("4. Adicione livros ao sistema")

        finally:
            db.close()

    except Exception as e:
        print(f"\nERRO durante o seed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
