"""
Vercel serverless function handler for FastAPI application.
This file serves as the entry point for the API when deployed on Vercel.
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mangum import Mangum
from backend.main import app

# Create the handler for Vercel serverless functions
handler = Mangum(app, lifespan="off")
