#!/usr/bin/env python3
"""
Script para gerar uma SECRET_KEY segura para uso em produção.

Uso:
    python scripts/generate_secret.py

O script irá gerar uma chave aleatória de 64 caracteres usando
caracteres seguros para uso em URLs e tokens JWT.
"""
import secrets
import string

def generate_secret_key(length=64):
    """
    Gera uma chave secreta segura.

    Args:
        length: Tamanho da chave em caracteres (padrão: 64)

    Returns:
        String aleatória segura
    """
    # Caracteres seguros: letras, números, alguns símbolos
    alphabet = string.ascii_letters + string.digits + "-_"
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret_key

if __name__ == "__main__":
    print("Gerando SECRET_KEY segura...\n")
    secret_key = generate_secret_key()
    print(f"SECRET_KEY={secret_key}\n")
    print("IMPORTANTE:")
    print("1. Copie a chave acima")
    print("2. Configure como variável de ambiente na Vercel")
    print("3. NUNCA commite esta chave no GitHub")
    print("4. Use uma chave diferente para cada ambiente (dev, staging, prod)")
