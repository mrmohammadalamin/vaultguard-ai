import asyncio
import websockets
import json
import traceback

async def test():
    uri = 'ws://127.0.0.1:8001/ws'
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as ws:
            print("Connected successfully!")
            
            # Send start_goal
            print("Sending start_goal...")
            await ws.send(json.dumps({"action": "start_goal"}))
            
            # Listen to response
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                print(f"Received: {msg}")
    except Exception as e:
        print(f"Error occurred: {repr(e)}")
        traceback.print_exc()

asyncio.run(test())
