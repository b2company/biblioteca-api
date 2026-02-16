"""
Vercel serverless function handler for FastAPI application.
This file serves as the entry point for the API when deployed on Vercel.
"""
import os
import sys
import traceback

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from mangum import Mangum
    from backend.main import app

    # Create the handler for Vercel serverless functions
    handler = Mangum(app, lifespan="off")

except Exception as e:
    # If there's an error during import, create a simple error handler
    print(f"ERROR LOADING APP: {e}")
    print(traceback.format_exc())

    # Create a simple ASGI app that returns the error
    async def handler(scope, receive, send):
        await send({
            'type': 'http.response.start',
            'status': 500,
            'headers': [[b'content-type', b'text/plain']],
        })
        error_msg = f"Error loading application: {str(e)}\n\n{traceback.format_exc()}"
        await send({
            'type': 'http.response.body',
            'body': error_msg.encode(),
        })
