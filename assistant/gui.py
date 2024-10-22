import tkinter as tk
from tkinter import scrolledtext
import time


class GUI:
    def __init__(
        self, send_text_callback, start_recording_callback, stop_recording_callback
    ):
        self.root = tk.Tk()
        self.send_text_callback = send_text_callback
        self.start_recording_callback = start_recording_callback
        self.stop_recording_callback = stop_recording_callback
        self.setup_gui()
        self.bind_events()

    def setup_gui(self):
        self.root.title("Realtime Assistant")
        self.root.geometry("500x400")

        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=70, height=20
        )
        self.text_area.pack(padx=5, pady=5)

        self.input_entry = tk.Entry(self.root, width=30)
        self.input_entry.pack(side=tk.LEFT, padx=10)

        self.send_button = tk.Button(
            self.root, text="Send", command=self.send_text_input
        )
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Push-to-hold recording button (records while pressed)
        self.voice_button = tk.Button(self.root, text="Hold to Record")
        self.voice_button.pack(side=tk.LEFT, padx=5)

        # Bind button press and release events
        self.voice_button.bind("<ButtonPress>", self.start_recording)
        self.voice_button.bind("<ButtonRelease>", self.stop_recording)
    def bind_events(self):
        # Bind space+m key combination to behave like the voice button (press to start, release to stop)
        self.root.bind('<space><m>', lambda event: self.start_recording(event))
        self.root.bind('<KeyRelease-space><KeyRelease-m>', lambda event: self.stop_recording(event))
        self.root.bind('<KeyRelease-m><KeyRelease-space>', lambda event: self.stop_recording(event))


    def send_text_input(self):
        user_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self.log(f"You: {user_input}")
        self.send_text_callback(user_input)

    def start_recording(self, event=None):
        self.start_recording_callback()

    def stop_recording(self, event=None):
        # wait for 1 second before stopping recording to trigger the User speaking stop event
        time.sleep(1)
        self.stop_recording_callback()

    def log(self, message, end="\n"):
        self.text_area.insert(tk.END, message + end)
        self.text_area.see(tk.END)

    def update(self):
        self.root.update()
