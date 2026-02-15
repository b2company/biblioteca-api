import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routers import auth, users, categories, books, loans

# Criar tabelas no startup
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title="Biblioteca API",
    description="API para sistema de gerenciamento de biblioteca",
    version="1.0.0"
)

# Configurar CORS baseado no ambiente
# Em produção, use a URL do frontend da Vercel
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Produção: permite apenas a origem do frontend
    allowed_origins = [FRONTEND_URL, "https://*.vercel.app"]
else:
    # Desenvolvimento: permite todas as origens
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
