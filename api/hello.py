"""Simplest possible Python function for Vercel."""

def handler(event, context):
    """Simple handler that returns OK."""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"status": "ok", "message": "Python is working!"}'
    }
