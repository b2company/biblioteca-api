#!/usr/bin/env python3
"""Adicionar livros ao banco."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from backend.database import SessionLocal
from backend.models import Book, Category

db = SessionLocal()

try:
    # Buscar categorias
    categorias = db.query(Category).all()
    cat_dict = {c.name: c.id for c in categorias}

    print("📖 Adicionando livros...")

    livros = [
        ("9780451524935", "1984", "George Orwell", "Cia Letras", 1949, "Ficção", 3, 3),
        ("9780316769174", "O Apanhador", "J.D. Salinger", "Todavia", 1951, "Ficção", 2, 2),
        ("9780596009205", "Design Patterns", "Eric Freeman", "O'Reilly", 2004, "Técnico", 2, 2),
        ("9788535902778", "Sapiens", "Yuval Harari", "Cia Letras", 2011, "História", 3, 3),
    ]

    for isbn, titulo, autor, editora, ano, cat_nome, qty, avail in livros:
        livro = Book(
            isbn=isbn,
            title=titulo,
            author=autor,
            publisher=editora,
            year=ano,
            category_id=cat_dict.get(cat_nome, 1),
            quantity=qty,
            available=avail
        )
        db.add(livro)
        print(f"   ✅ {titulo}")

    db.commit()
    print("\n✅ Livros adicionados com sucesso!")

except Exception as e:
    print(f"❌ Erro: {e}")
    db.rollback()
finally:
    db.close()
