# import speech_recognition as sr
# import pyttsx3
# import datetime
# import pythoncom

# # Initialize COM for speech-related tasks
# pythoncom.CoInitialize()

# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[0].id)
# engine.setProperty('rate', 180)

# def speak(text):
#     try:
#         print(f"Speaking: {text}")
#         engine.say(text)
#         engine.runAndWait()
#     except Exception as e:
#         print(f"Error in speech: {e}")

# def take_command(timeout=15, phrase_time_limit=15):
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Listening...")
#         recognizer.pause_threshold = 1
#         recognizer.adjust_for_ambient_noise(source, duration=2)
#         try:
#             audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
#         except sr.WaitTimeoutError:
#             print("Listening timed out. No audio detected.")
#             return "none"
#         except Exception as e:
#             print(f"Microphone error: {e}")
#             return "none"
#     try:
#         print("Recognizing...")
#         command = recognizer.recognize_google(audio, language='en-in')
#         print(f"You said: {command}")
#     except sr.UnknownValueError:
#         print("Sorry, I didn't catch that.")
#         return "none"
#     except sr.RequestError:
#         print("Sorry, my speech service is down.")
#         return "none"
#     except Exception as e:
#         print(f"Recognition error: {e}")
#         return "none"
#     return command.lower()

# def greet():
#     hour = int(datetime.datetime.now().hour)
#     if 0 <= hour < 12:
#         speak("Good morning, sir!")
#     elif 12 <= hour < 18:
#         speak("Good afternoon, sir!")
#     else:
#         speak("Good evening, sir!")
#     speak("I am JARVIS, your personal assistant. Awaiting your command.")

# def listen_for_wake_word():
#     while True:
#         command = take_command(timeout=20, phrase_time_limit=5)
#         if command == "none":
#             continue
#         if "jarvis" in command:
#             speak("Yes, sir?")
#             return True


import pyttsx3
import datetime
import pythoncom

# Initialize COM for speech-related tasks
pythoncom.CoInitialize()

# Set up the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Use the first available voice
engine.setProperty('rate', 180)  # Set speech rate to 180 words per minute

def stop_speech():
    try:
        engine.stop()
        print("Speech stopped by user command.")
    except Exception as e:
        print(f"Error stopping speech: {e}")

# Function to handle text-to-speech output
def speak(text):
    try:
        print(f"Speaking: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speech: {e}")

# Function to get typed input from the user
def get_command():
    command = input("Type your command: ")
    return command.lower()

# Function to greet the user based on the current time
def greet():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning, sir!")
    elif 12 <= hour < 18:
        speak("Good afternoon, sir!")
    else:
        speak("Good evening, sir!")
    speak("I am JARVIS, your personal assistant. Awaiting your command.")

# Function to wait for the wake word "jarvis"
def wait_for_wake_word():
    while True:
        user_input = input("Type 'jarvis' to activate: ").lower()
        if "jarvis" in user_input:
            speak("Yes, sir?")
            return True