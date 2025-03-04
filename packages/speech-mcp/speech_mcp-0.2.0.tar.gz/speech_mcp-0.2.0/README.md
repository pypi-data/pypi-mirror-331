# Speech MCP

A Goose MCP extension for voice interaction with audio visualization.

## Overview

Speech MCP provides a voice interface for Goose, allowing users to interact through speech rather than text. It includes:

- Real-time audio processing for speech recognition
- Local speech-to-text using faster-whisper (a faster implementation of OpenAI's Whisper model)
- Text-to-speech capabilities 
- Simple command-line interface for voice interaction

## Features

- **Voice Input**: Capture and transcribe user speech using faster-whisper
- **Voice Output**: Convert agent responses to speech
- **Continuous Conversation**: Automatically listen for user input after agent responses
- **Silence Detection**: Automatically stops recording when the user stops speaking

## Installation

### Option 1: Quick Install (One-Click)

Click the link below if you have Goose installed:

`goose://extension?cmd=uvx&arg=speech-mcp&id=speech_mcp&name=Speech%20Interface&description=Voice%20interaction%20with%20audio%20visualization%20for%20Goose`

### Option 2: Using Goose CLI (recommended)

Start Goose with your extension enabled:

```bash
# If you installed via PyPI
goose session --with-extension "uvx speech-mcp"

# Or if you want to use a local development version
goose session --with-extension "python -m speech_mcp"
```

### Option 3: Manual setup in Goose

1. Run `goose configure`
2. Select "Add Extension" from the menu
3. Choose "Command-line Extension"
4. Enter a name (e.g., "Speech Interface")
5. For the command, enter: `uvx speech-mcp`
6. Follow the prompts to complete the setup

### Option 4: Manual Installation

1. Clone this repository
2. Install dependencies:
   ```
   uv pip install -e .
   ```

## Dependencies

- Python 3.10+
- PyAudio (for audio capture)
- faster-whisper (for speech-to-text)
- NumPy (for audio processing)
- Pydub (for audio processing)
- pyttsx3 (for text-to-speech)

## Usage

To use this MCP with Goose, you can:

1. Start a conversation:
   ```python
   user_input = start_conversation()
   ```

2. Reply to the user and get their response:
   ```python
   user_response = reply("Your response text here")
   ```

## Typical Workflow

```python
# Start the conversation
user_input = start_conversation()

# Process the input and generate a response
# ...

# Reply to the user and get their response
follow_up = reply("Here's my response to your question.")

# Process the follow-up and reply again
reply("I understand your follow-up question. Here's my answer.")
```

## Technical Details

### Speech-to-Text

The MCP uses faster-whisper for speech recognition:
- Uses the "base" model for a good balance of accuracy and speed
- Processes audio locally without sending data to external services
- Automatically detects when the user has finished speaking
- Provides improved performance over the original Whisper implementation

## License

[MIT License](LICENSE)