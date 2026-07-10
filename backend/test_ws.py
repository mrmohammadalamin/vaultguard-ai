import asyncio
import websockets

async def test():
    try:
        async with websockets.connect('ws://127.0.0.1:8000/ws') as ws:
            print('Connected to 127.0.0.1!')
    except Exception as e:
        print(f"Failed 127.0.0.1: {e}")
        
    try:
        async with websockets.connect('ws://localhost:8000/ws') as ws:
            print('Connected to localhost!')
    except Exception as e:
        print(f"Failed localhost: {e}")

asyncio.run(test())
