import asyncio
import logging
from .assistant.realtime_assistant import RealtimeAssistant
from . import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


async def main():
    assistant = RealtimeAssistant(config)
    await assistant.run()


if __name__ == "__main__":
    asyncio.run(main())
