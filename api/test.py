"""Simple test endpoint to verify Vercel is working."""

async def handler(scope, receive, send):
    """Simple ASGI handler that just returns OK."""
    if scope['type'] == 'http':
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [[b'content-type', b'application/json']],
        })
        await send({
            'type': 'http.response.body',
            'body': b'{"status": "ok", "message": "Vercel is working!"}',
        })
