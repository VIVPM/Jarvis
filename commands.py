import subprocess
import os
import pywhatkit
from speech_utils import speak
from app_manager import find_app, close_app_cache

def handle_open_app(command):
    app_name = command.replace("open", "").strip()
    if not app_name:
        speak("Please specify an application to open.")
        return
    app_path = find_app(app_name)
    if app_path:
        try:
            subprocess.Popen(app_path)
            speak(f"Opening {app_name}")
        except Exception as e:
            speak(f"Sorry, I couldn't open {app_name} due to an error.")
    else:
        speak(f"Sorry, I couldn't find {app_name} on your system.")

# def handle_search(command):
#     search_query = command.replace("search for", "").strip()
#     speak(f"Searching for {search_query}")
#     pywhatkit.search(search_query)

def handle_play_song(command):
    song = command.replace("play", "").replace("song", "").strip()
    speak(f"Playing {song} song on YouTube")
    pywhatkit.playonyt(song)

def handle_time(command):
    from datetime import datetime
    current_time = datetime.now().strftime("%H:%M")
    speak(f"The time is {current_time}")

def handle_date(command):
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    speak(f"Today's date is {current_date}")

def handle_shutdown(command):
    speak("Initiating system shutdown in 30 seconds. Say 'cancel shutdown' to stop.")
    os.system("shutdown /s /t 30")

def handle_cancel_shutdown(command):
    speak("System shutdown cancelled.")
    os.system("shutdown /a")

def handle_check_status(command):
    speak("Checking system status. All systems are operational, sir.")

def handle_exit(command):
    speak("Goodbye, sir!")
    close_app_cache()
    import sys
    sys.exit(0)