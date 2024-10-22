import asyncio
import json
import logging
import base64
from ..utils.websocket_client import WebSocketClient
from .audio_handler import AudioHandler
from .gui import GUI
import time
from .functions.analyze_screenshot import take_and_analyze_screenshot

# from docstring_parser.google import (
#     GoogleParser,
#     Section,
#     SectionType,
#     compose,
#     parse,
# )

# parser = GoogleParser()


class RealtimeAssistant:
    def __init__(self, config):
        self.config = config
        self.websocket_client = WebSocketClient(config.WS_URL, config.OPENAI_API_KEY)
        self.audio_handler = AudioHandler(config)
        self.gui = GUI(self.send_text_input, self.start_recording, self.stop_recording)
        self.is_recording = False
        self.stop_event = asyncio.Event()
        self.assistant_transcript_turn = False
        self.assistant_speaking = False
        self.assistant_speaking_start_time = None
        self.assistant_speaking_duration = 0
        # self.tools = [analyze_screenshot]
        # self.tools_info = {tool.__name__: {"description": parser.parse(tool.__doc__).long_description, "parameters": parser.parse(tool.__doc__).params, "required": [param.arg_name for param in parser.parse(tool.__doc__).params if param.arg_name not in ["self", "cls"]], "returns": parser.parse(tool.__doc__).returns} for tool in self.tools}
        # print(self.tools_info)

    async def connect_to_openai(self):

        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "You are a helpful assistant.\n While making a function call do engage with the user. \nWhenever the user query is related to something visible on the screen, you can use take_and_analyze_screenshot function call to help the user.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200,
                },
                "tools": [
                    {
                        "type": "function",
                        "name": "take_and_analyze_screenshot",
                        "description": "Takes a screenshot and analyzes the contents of a screenshot and provide a detailed answer/solution based on the user query. Can be used when the user asks for help for something visible on the screen.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_query": {
                                    "type": "string",
                                    "description": "The query of the user that for which the screenshot is to be analyzed.",
                                }
                            },
                            "required": ["user_query"],
                        },
                    }
                ],
                "tool_choice": "auto",
                "temperature": 0.8,
            },
        }

        await self.websocket_client.connect()
        await self.websocket_client.send(session_config)

    async def send_mic_audio_to_websocket(self):
        try:
            while not self.stop_event.is_set():
                if not self.audio_handler.mic_queue.empty():
                    mic_chunk = await self.audio_handler.mic_queue.get()
                    logging.info(f"🎤 Sending {len(mic_chunk)} bytes of audio data.")
                    encoded_chunk = base64.b64encode(mic_chunk).decode("utf-8")
                    message = {
                        "type": "input_audio_buffer.append",
                        "audio": encoded_chunk,
                    }
                    await self.websocket_client.send(message)
                else:
                    await asyncio.sleep(0.1)
        except Exception as e:
            logging.error(f"Exception in send_mic_audio_to_websocket: {e}")
        finally:
            logging.info("Exiting send_mic_audio_to_websocket.")

    async def receive_audio_from_websocket(self):
        try:
            while not self.stop_event.is_set():
                message = await self.websocket_client.receive()
                message = json.loads(message)
                event_type = message["type"]
                logging.info(f"⚡️ Received WebSocket event: {event_type}")

                if event_type == "response.audio.delta":
                    if not self.assistant_speaking:
                        self.assistant_speaking_start_time = time.time()
                        self.assistant_speaking = True

                    audio_content = base64.b64decode(message["delta"])
                    self.audio_handler.audio_buffer.extend(audio_content)
                elif event_type == "response.audio.done":
                    self.assistant_speaking = False
                    self.assistant_speaking_duration += (
                        time.time() - self.assistant_speaking_start_time
                    )
                    logging.info("🔵 AI finished speaking.")
                elif event_type == "response.audio_transcript.delta":
                    if self.assistant_transcript_turn:
                        self.gui.log(message["delta"], end="")
                    else:
                        self.assistant_transcript_turn = True
                        self.gui.log(f"\nAssistant: {message['delta']}", end="")
                elif event_type == "response.audio_transcript.done":
                    self.assistant_transcript_turn = False
                    self.gui.log("\n<DONE Response>\n")
                elif event_type == "error":
                    logging.error(f'Error from OpenAI: {message["error"]}')
                elif event_type == "input_audio_buffer.speech_started":
                    logging.info("🔵 User Speech started.")
                elif event_type == "input_audio_buffer.speech_stopped":
                    logging.info("🔵 User Speech stopped.")
                elif event_type == "response.function_call_arguments.done":
                    logging.info("🔵 Function call arguments received.")
                    logging.info(f"Message: {message}")
                    logging.info(f"Function call arguments: {message['arguments']}")
                    tool_name = message["name"]
                    tool_args = json.loads(message["arguments"])
                    call_id = message["call_id"]
                    await self.handle_tool(tool_name, tool_args, call_id)
                else:
                    logging.info(f"Unhandled event type: {event_type}")
        except Exception as e:
            logging.error(f"Exception in receive_audio_from_websocket: {e}")
        finally:
            logging.info("Exiting receive_audio_from_websocket.")

    def send_text_input(self, user_input):
        asyncio.create_task(self.send_user_message(user_input))

    def start_recording(self):
        if not self.is_recording:
            self.audio_handler.start_recording()
            self.is_recording = True

    def stop_recording(self):
        if self.is_recording:
            if self.assistant_speaking:
                speaking_time = (
                    time.time()
                    - self.assistant_speaking_start_time
                    + self.assistant_speaking_duration
                )
                asyncio.create_task(self.send_stop_response(speaking_time))
                self.assistant_speaking = False
                self.assistant_speaking_duration = 0
            self.audio_handler.stop_recording()
            self.is_recording = False

    async def send_stop_response(self, speaking_time):
        logging.info(
            f"Sending response.truncate with speaking time: {speaking_time:.2f} seconds"
        )
        cancel_event = {
            "type": "response.cancel",
        }
        await self.websocket_client.send(cancel_event)

    async def send_user_message(self, message):
        logging.info(f"Sending message: {message}")
        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": message}],
            },
        }
        await self.websocket_client.send(event)
        await self.websocket_client.send({"type": "response.create"})

    async def send_stop_response(self):
        await self.websocket_client.send({"type": "response.cancel"})

    async def run(self):
        self.audio_handler.init_audio_streams()
        await self.connect_to_openai()

        websocket_tasks = [
            self.send_mic_audio_to_websocket(),
            self.receive_audio_from_websocket(),
        ]

        try:
            await asyncio.gather(*websocket_tasks, self.gui_loop())
        finally:
            self.audio_handler.close()
            await self.websocket_client.close()
            self.stop_event.set()

    async def gui_loop(self):
        while True:
            self.gui.update()
            await asyncio.sleep(0.1)

    async def handle_tool(self, tool_name, tool_args, call_id):
        logging.info(f"Handling tool: {tool_name}")
        if tool_name == "take_and_analyze_screenshot":
            user_query = tool_args["user_query"]
            response = await take_and_analyze_screenshot(user_query)
            logging.info(f"Response from take_and_analyze_screenshot: {response}")

            function_call_result_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": str(response),
                },
            }

            await self.websocket_client.send(function_call_result_message)
            await self.websocket_client.send({"type": "response.create"})
        else:
            logging.error(f"Unhandled tool: {tool_name}")
