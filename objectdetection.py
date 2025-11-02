import os
import time
import io
import tempfile
import cv2
import PIL.Image
import numpy as np
import speech_recognition as sr
import google.generativeai as genai
import google.api_core.exceptions
from dotenv import load_dotenv
from gtts import gTTS
import pygame

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = input("Enter your Google API key: ").strip()
    with open(".env", "w") as f:
        f.write(f"GOOGLE_API_KEY={GOOGLE_API_KEY}")
genai.configure(api_key=GOOGLE_API_KEY)

pygame.mixer.init()
recognizer = sr.Recognizer()

LANG_MAP = {
    "1": {"name": "English", "sr": "en-US", "tts": "en", "gemini": "English"},
    "2": {"name": "Hindi", "sr": "hi-IN", "tts": "hi", "gemini": "Hindi"},
    "3": {"name": "Telugu", "sr": "te-IN", "tts": "te", "gemini": "Telugu"},
    "4": {"name": "Tamil", "sr": "ta-IN", "tts": "ta", "gemini": "Tamil"}
}

def play_tts(text, lang_tts):
    try:
        t = gTTS(text=text, lang=lang_tts)
    except Exception:
        return
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    t.save(path)
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception:
        pass
    try:
        os.remove(path)
    except Exception:
        pass

def ask_gemini(prompt, image_bytes=None, instruct_language=None):
    models_to_try = ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.0-pro-exp"]
    if instruct_language:
        prompt = f"Answer in {instruct_language}. {prompt}"
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name=model_name)
            parts = [prompt]
            if image_bytes:
                parts.append({"mime_type": "image/jpeg", "data": image_bytes})
            response = model.generate_content(parts)
            if hasattr(response, "text") and response.text:
                return response.text
        except google.api_core.exceptions.NotFound:
            continue
        except google.api_core.exceptions.ResourceExhausted:
            continue
        except Exception:
            continue
    return None

def capture_image_from_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None
    print("Press Space to capture image or Esc to cancel.")
    captured = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Webcam - Press Space", frame)
        key = cv2.waitKey(1)
        if key == 32:
            captured = frame
            break
        elif key == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    return captured

def listen(language_sr, prompt_text=None, timeout=5):
    if prompt_text:
        print(prompt_text)
        play_tts(prompt_text, language_sr.split("-")[0])
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout)
            text = recognizer.recognize_google(audio, language=language_sr)
            return text
        except sr.UnknownValueError:
            return None
        except Exception:
            return None

def ask_question_about_image(image, lang):
    pil_image = PIL.Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    img_buffer = io.BytesIO()
    pil_image.save(img_buffer, format="JPEG")
    image_bytes = img_buffer.getvalue()
    question = listen(lang["sr"], "Please ask your question now", timeout=6)
    if not question:
        print("No voice input detected. Type your question:")
        question = input("> ").strip()
        if not question:
            print("No question provided.")
            return
    response = ask_gemini(question, image_bytes=image_bytes, instruct_language=lang["gemini"])
    if not response:
        print("No response from Gemini.")
        return
    print(response)
    play_tts(response, lang["tts"])

def live_video_explain(interval, lang):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    print("Live feed started. Say 'quit' or press q to stop.")
    last_time = time.time()
    last_response = ""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if time.time() - last_time > interval:
            _, buffer = cv2.imencode(".jpg", frame)
            image_bytes = buffer.tobytes()
            prompt = "Describe what you see in this frame briefly."
            response = ask_gemini(prompt, image_bytes=image_bytes, instruct_language=lang["gemini"])
            if response:
                last_response = response
                print(response)
                play_tts(response, lang["tts"])
            last_time = time.time()
        y0, dy = 30, 30
        for i, line in enumerate(last_response.splitlines()):
            y = y0 + i * dy
            cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = recognizer.listen(source, timeout=0.5)
                cmd = recognizer.recognize_google(audio, language=lang["sr"]).lower()
                if "quit" in cmd or "stop" in cmd or {"అమ్మ","నిలుపు"} & set(cmd.split()):
                    break
        except Exception:
            pass
    cap.release()
    cv2.destroyAllWindows()

def voice_menu(lang):
    print("Say 'capture photo' or 'start live mode' or 'quit'.")
    play_tts("Say capture photo or start live mode or quit", lang["tts"])
    cmd = listen(lang["sr"], timeout=6)
    if not cmd:
        return None
    return cmd.lower()

def choose_language():
    print("Select language:")
    for k, v in LANG_MAP.items():
        print(f"{k} - {v['name']}")
    choice = input("Enter choice: ").strip()
    return LANG_MAP.get(choice, LANG_MAP["1"])

def main():
    lang = choose_language()
    while True:
        print("1 Capture image")
        print("2 Live feed")
        print("3 Voice control")
        print("4 Exit")
        choice = input("Enter choice (1/2/3/4): ").strip()
        if choice == "1":
            img = capture_image_from_webcam()
            if img is not None:
                ask_question_about_image(img, lang)
        elif choice == "2":
            live_video_explain(interval=5, lang=lang)
        elif choice == "3":
            cmd = voice_menu(lang)
            if not cmd:
                print("No voice command detected.")
                continue
            if "capture" in cmd or "photo" in cmd:
                img = capture_image_from_webcam()
                if img is not None:
                    ask_question_about_image(img, lang)
            elif "live" in cmd or "start" in cmd:
                live_video_explain(interval=5, lang=lang)
            elif "quit" in cmd or "stop" in cmd:
                break
            else:
                print("Command not recognized.")
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
    print("Goodbye.")

if __name__ == "__main__":
    main()
