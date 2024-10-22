import pyaudio
import asyncio
import time
import logging
import base64


class AudioHandler:
    def __init__(self, config):
        self.config = config
        self.p = pyaudio.PyAudio()
        self.mic_stream = None
        self.spkr_stream = None
        self.audio_buffer = bytearray()
        self.mic_queue = asyncio.Queue()
        self.mic_active = None
        self.mic_on_at = 0
        self.assistant_speaking_actual = False
        self.assistant_speaking_actual_start_time = None
        self.assistant_speaking_actual_duration = 0
        self.assistant_speaking_stop_signal = False

    def init_audio_streams(self):
        self.spkr_stream = self.p.open(
            format=getattr(pyaudio, f"pa{self.config.FORMAT}"),
            channels=self.config.CHANNELS,
            rate=self.config.RATE,
            output=True,
            stream_callback=self.spkr_callback,
            frames_per_buffer=self.config.CHUNK_SIZE,
        )
        self.spkr_stream.start_stream()
        logging.info("Speaker stream initialized and started.")

    def mic_callback(self, in_data, frame_count, time_info, status):
        if self.mic_active != True:
            logging.info("🎙️🟢 Mic active")
            self.mic_active = True
        self.mic_queue.put_nowait(in_data)
        return (None, pyaudio.paContinue)

    def spkr_callback(self, in_data, frame_count, time_info, status):
        bytes_needed = frame_count * 2
        current_buffer_size = len(self.audio_buffer)
        if not self.assistant_speaking_stop_signal:
            if not self.assistant_speaking_actual:
                self.assistant_speaking_actual = True
                self.assistant_speaking_actual_start_time = time.time()
            if current_buffer_size >= bytes_needed:
                audio_chunk = bytes(self.audio_buffer[:bytes_needed])
                self.audio_buffer = self.audio_buffer[bytes_needed:]
            else:
                audio_chunk = bytes(self.audio_buffer) + b"\x00" * (
                    bytes_needed - current_buffer_size
                )
                self.audio_buffer.clear()
        else:
            audio_chunk = bytes(self.audio_buffer) + b"\x00" * (
                bytes_needed - current_buffer_size
            )
            self.audio_buffer.clear()
            self.assistant_speaking_stop_signal = False
            self.assistant_speaking_actual = False
            self.assistant_speaking_actual_start_time = None
            if self.assistant_speaking_actual_start_time:
                self.assistant_speaking_actual_duration = (
                    time.time() - self.assistant_speaking_actual_start_time
                )

        return (audio_chunk, pyaudio.paContinue)

    def start_recording(self):
        self.mic_stream = self.p.open(
            format=getattr(pyaudio, f"pa{self.config.FORMAT}"),
            channels=self.config.CHANNELS,
            rate=self.config.RATE,
            input=True,
            stream_callback=self.mic_callback,
            frames_per_buffer=self.config.CHUNK_SIZE,
        )
        logging.info("Starting microphone recording...")
        self.assistant_speaking_stop_signal = True
        self.mic_stream.start_stream()

    def stop_recording(self):
        logging.info("Stopping microphone recording...")
        if self.mic_stream:
            self.mic_stream.stop_stream()
            self.mic_stream.close()
            self.mic_stream = None

    def close(self):
        self.stop_recording()
        if self.spkr_stream:
            self.spkr_stream.stop_stream()
            self.spkr_stream.close()
        if self.p:
            self.p.terminate()
