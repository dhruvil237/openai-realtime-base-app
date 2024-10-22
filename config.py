import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

CHUNK_SIZE = 1024
FORMAT = "Int16"
CHANNELS = 1
RATE = 24000
REENGAGE_DELAY_MS = 500
