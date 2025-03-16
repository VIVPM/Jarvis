import os
from google import genai

# Initialize the Gemini API client with your API key
client = genai.Client(api_key="AIzaSyAE-_hEtucBKHS-R3SUY0NDrpTjdlMhjz0")

# Get the Desktop path
desktop_path = os.path.join(os.path.expanduser("~"), "C:\\Users\\Vivek\\Desktop")
history_file = os.path.join(desktop_path, "chat_history.txt")

# Function to read conversation history from file
def load_conversation_history():
    # Check if the file exists, if not, create an empty one
    if not os.path.exists(history_file):
        with open(history_file, "w", encoding="utf-8") as file:
            pass  # Just creates an empty file

    # Read and return the history
    with open(history_file, "r", encoding="utf-8") as file:
        return file.readlines()


# Function to save conversation history to file
def save_to_file(entry):
    with open(history_file, "a", encoding="utf-8") as file:
        file.write(entry + "\n")

def get_gemini_response(command):
    try:
        # Load previous conversation history
        conversation_history = load_conversation_history()
        
        # Add the user's command to the history
        save_to_file(f"user: {command}")
        
        # Call the Gemini API with the history
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=conversation_history + [command],
        )
        
        # Extract the assistant's response
        assistant_response = response.text
        save_to_file(f"assistant: {assistant_response}")
        
        return assistant_response
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        error_msg = "I'm having trouble processing your request, sir."
        save_to_file(f"assistant: {error_msg}")
        return error_msg
