# OpenAI Realtime Base App

## Overview

The OpenAI Realtime Base App is a Python-based application that leverages OpenAI's Realtime API to provide real-time assistance through text and audio interactions. The application includes a basic graphical user interface (GUI) for user interaction and supports functionalities like text input, voice recording, and screenshot analysis. Added image (screenshot) capability using function call to chat completions endpoint. This repo can serve as basis on how to work on OpenAI's realtime API with python as no official documentation from OpenAI for python as of now.

## Features

- **Real-time Text and Audio Interaction**: Communicate with the assistant using text or voice.
- **GUI Interface**: A user-friendly interface built with Tkinter.
- **Screenshot Analysis**: Capture and analyze screenshots to provide detailed solutions based on user queries.
- **WebSocket Communication**: Utilizes WebSocket for real-time data exchange with OpenAI's API.

## Prerequisites

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- An OpenAI API key

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/openai-realtime-api-app.git
   cd openai-realtime-api-app
   ```

2. **Install Dependencies**:
   Ensure you have Poetry installed, then run:
   ```bash
   poetry install
   ```

3. **Environment Setup**:
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. **Run the Application**:
   Start the application using:
   ```bash
   poetry run python -m openai-realtime-base-app.main
   ```

2. **Interacting with the Assistant**:
   - Use the GUI to type messages or hold the "Hold to Record" button to send voice inputs.
   - You can also type the messages in the text input area in GUI
   - The assistant will respond in real-time, and you can view the conversation in the GUI.

3. **Screenshot Analysis**:
   - The assistant can analyze screenshots when prompted by the user. This feature is useful for debugging or providing solutions based on visual content.
   - Used Function Call Functionality where the function calls to normal chat completions endpoint with user query and screenshot

## Project Structure

- `main.py`: Entry point of the application.
- `assistant/`: Contains modules for GUI, real-time assistant logic, and functions.
  - `gui.py`: Manages the graphical user interface.
  - `audio_handler.py`: Manages all logic relating to mic and speaker playback (with buffer to avoid broken voice).
  - `realtime_assistant.py`: Core logic for handling real-time interactions.
  - `functions/analyze_screenshot.py`: Function for taking and analyzing screenshots.
- `utils/`: Utility modules, including WebSocket client management.
- `config.py`: Configuration settings, including API keys and WebSocket URLs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
