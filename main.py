import sys
import threading
import pystray
from PIL import Image
from speech_utils import greet, get_command, wait_for_wake_word, speak
from process_command import process_command
from app_manager import update_app_cache, close_app_cache

def create_tray_icon():
    def on_quit(icon, item):
        icon.stop()
        speak("Shutting down.")
        close_app_cache()
        sys.exit(0)
    image = Image.new('RGB', (64, 64), color='blue')
    icon = pystray.Icon("JARVIS", image, "JARVIS Assistant")
    icon.menu = pystray.Menu(pystray.MenuItem("Quit", on_quit))
    icon.run()

def main():
    # Start tray icon in a separate thread
    threading.Thread(target=create_tray_icon, daemon=True).start()
    greet()
    update_app_cache()
    speak("Type 'Jarvis' to activate me.")
    
    # Wait for the wake word
    while True:
        if wait_for_wake_word():
            speak("I'm now active, sir. How can I assist you?")
            break

    # Main loop to process commands and chat
    while True:
        command = get_command()
        if command.strip() == "":
            continue  # Ignore empty commands
        process_command(command)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Shutting down.")
        close_app_cache()
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        speak("An error occurred. Shutting down.")
        close_app_cache()
        sys.exit(1)
