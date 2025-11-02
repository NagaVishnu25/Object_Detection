🌍 Multilingual Gemini Vision Assistant

An AI-powered vision assistant that uses Google Gemini and speech recognition to describe images, analyze live webcam video, and answer your questions — all in multiple languages (English, Hindi, Telugu, and Tamil).

🧠 Features

✅ Capture a photo and ask questions about it (voice or text).
✅ Real-time video description mode (AI narrates what’s happening).
✅ Voice-controlled menu navigation.
✅ Multilingual support:

🇬🇧 English

🇮🇳 Hindi

🇮🇳 Telugu

🇮🇳 Tamil
✅ Uses Gemini for vision + text understanding.
✅ Uses Google TTS for realistic audio replies.

⚙️ Requirements

Make sure you have Python 3.9+ installed.

🧩 Install dependencies
pip install google-generativeai SpeechRecognition gtts pygame python-dotenv pillow opencv-python

🔑 Setup

Get your Google Gemini API key from:
👉 https://aistudio.google.com/app/apikey

Create a .env file in the same directory as the script:

GOOGLE_API_KEY=your_api_key_here


Alternatively, the script will ask for your API key on first run and automatically save it.

🚀 How to Run

Run the Python file:

python gemini_multilang_assistant.py


You’ll see:

Select language:
1 - English
2 - Hindi
3 - Telugu
4 - Tamil


Then choose a mode:

1 Capture image
2 Live feed
3 Voice control
4 Exit

🗣️ Modes
🎤 1. Capture Image & Ask

Press Space to capture an image.

Speak your question (or type it if voice not detected).

AI answers in your chosen language (spoken + text).

📹 2. Live Feed

The AI continuously analyzes video from your webcam every few seconds.

You can say "quit" or press Q to exit.

🤖 3. Voice Control

Just speak commands like:

“Capture photo”

“Start live mode”

“Quit”

🧩 File Structure
📁 GeminiVisionAssistant/
│
├── gemini_multilang_assistant.py     # Main Python script
├── .env                              # Stores your API key
├── README.md                         # This documentation

🧠 How It Works
Component	Purpose
SpeechRecognition	Captures and recognizes your voice
gTTS	Converts AI text responses to speech
pygame	Plays the speech audio
OpenCV	Captures images/video from webcam
Google Gemini	Analyzes images and answers intelligently
.env	Stores your API key securely
🌐 Language Expansion

To add more languages, edit LANG_MAP:

"5": {"name": "Spanish", "sr": "es-ES", "tts": "es", "gemini": "Spanish"}

🧩 Example Interaction

User: (Takes photo)
“Tell me what is in this picture.”
AI:
“This is a person sitting in front of a laptop.” (spoken and printed in chosen language)

🛠️ Troubleshooting

If the webcam doesn’t open → check your camera permissions.

If no voice detected → try reducing background noise.

If text-to-speech fails → check internet connection (gTTS requires it).

If Gemini returns no response → check your API key and quota.

🧑‍💻 Author

Created with ❤️ by Naga Vishnu and Gemini AI.
