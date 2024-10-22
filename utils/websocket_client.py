import asyncio
import json
import logging
import websockets


class WebSocketClient:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.websocket = None

    async def connect(self):
        headers = [
            ("Authorization", f"Bearer {self.api_key}"),
            ("OpenAI-Beta", "realtime=v1"),
        ]
        self.websocket = await websockets.connect(self.url, extra_headers=headers)
        logging.info("Connected to OpenAI WebSocket.")

    async def send(self, message):
        if not self.websocket:
            raise Exception("WebSocket not connected")
        await self.websocket.send(json.dumps(message))

    async def receive(self):
        if not self.websocket:
            raise Exception("WebSocket not connected")
        return await self.websocket.recv()

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            logging.info("WebSocket connection closed.")
