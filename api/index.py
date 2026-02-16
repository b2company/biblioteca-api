"""Simple FastAPI test without backend dependencies."""
from fastapi import FastAPI
from mangum import Mangum

# Create a simple FastAPI app
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "API is working!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Handler for Vercel
handler = Mangum(app, lifespan="off")
