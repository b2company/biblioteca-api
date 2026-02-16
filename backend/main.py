import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routers import auth, users, categories, books, loans

# Criar tabelas no startup - DESABILITADO EM PRODUÇÃO
# As tabelas devem ser criadas via script de seed em produção
# Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title="Biblioteca API",
    description="API para sistema de gerenciamento de biblioteca",
    version="1.0.0"
)

# Configurar CORS
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Produção: permite Vercel
    allowed_origins = [
        "https://biblioteca-api-theta.vercel.app",
        "https://*.vercel.app"
    ]
    allow_origin_regex = "https://.*\.vercel\.app"
else:
    # Desenvolvimento: permite todas as origens
    allowed_origins = ["*"]
    allow_origin_regex = None

cors_config = {
    "allow_origins": allowed_origins,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

if allow_origin_regex:
    cors_config["allow_origin_regex"] = allow_origin_regex

app.add_middleware(CORSMiddleware, **cors_config)

# Incluir routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(books.router)
app.include_router(loans.router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Biblioteca API",
        "version": "1.0.0",
        "status": "operational"
    }
