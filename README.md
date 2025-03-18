# Jarvis: An Personalized AI Assistant

<!DOCTYPE html>
<html>

<body>

  <h2>Table of Contents</h2>
  <ul>
    <li><a href="#app_manager">app_manager.py</a></li>
    <li><a href="#commands">commands.py</a></li>
    <li><a href="#gemini_client">gemini_client.py</a></li>
    <li><a href="#main">main.py</a></li>
    <li><a href="#process_command">process_command.py</a></li>
    <li><a href="#speech_utils">speech_utils.py</a></li>
    <li><a href="#connections">How the Files Are Connected</a></li>
    <li><a href="#usage">Usage Instructions</a></li>
    <li><a href="#run">How to Run This File</a></li>
  </ul>

  <h2 id="app_manager">app_manager.py</h2>
  <p>This module is responsible for discovering and managing applications on the system. It scans the Windows Start Menu, resolves shortcuts, and uses fuzzy matching to identify the correct application to launch.</p>
  <h3>Key Functions</h3>
  <ul>
    <li><code>resolve_shortcut(shortcut_path)</code>: Resolves a Windows shortcut (.lnk) to its target executable.</li>
    <li><code>discover_apps()</code>: Scans the Start Menu directories for applications and returns a dictionary of app names and their paths.</li>
    <li><code>update_app_cache()</code>: Updates the internal cache with discovered applications.</li>
    <li><code>find_app(app_name)</code>: Locates an application by name using caching and fuzzy matching.</li>
    <li><code>close_app_cache()</code>: Closes the shelve cache file when the application exits.</li>
  </ul>

  <h2 id="commands">commands.py</h2>
  <p>This module handles core voice commands related to system-level actions such as opening apps, playing songs, getting the time and date, shutting down the system, and exiting the assistant.</p>
  <h3>Key Functions</h3>
  <ul>
    <li><code>handle_open_app(command)</code>: Opens an application based on the command provided.</li>
    <li><code>handle_play_song(command)</code>: Plays a specified song on YouTube.</li>
    <li><code>handle_time(command)</code>: Announces the current time.</li>
    <li><code>handle_date(command)</code>: Announces the current date.</li>
    <li><code>handle_shutdown(command)</code>: Initiates a system shutdown sequence.</li>
    <li><code>handle_cancel_shutdown(command)</code>: Cancels a pending system shutdown.</li>
    <li><code>handle_check_status(command)</code>: Reports system status.</li>
    <li><code>handle_exit(command)</code>: Exits the assistant and closes necessary resources.</li>
  </ul>

  <h2 id="gemini_client">gemini_client.py</h2>
  <p>This module integrates with the Gemini AI API. It maintains conversation history and uses the API to generate responses based on user input.</p>
  <h3>Key Functions</h3>
  <ul>
    <li><code>load_conversation_history()</code>: Loads previous conversation history from a file.</li>
    <li><code>save_to_file(entry)</code>: Appends new conversation entries to the history file.</li>
    <li><code>get_gemini_response(command)</code>: Sends a command (or conversation content) to the Gemini API and returns the generated response.</li>
  </ul>

  <h2 id="main">main.py</h2>
  <p>This file serves as the entry point for the assistant. It sets up the system tray icon, greets the user, waits for the wake word ("jarvis"), and starts the main command processing loop.</p>
  <h3>Key Functions</h3>
  <ul>
    <li><code>create_tray_icon()</code>: Creates a system tray icon with a "Quit" menu option.</li>
    <li><code>main()</code>: Initializes the assistant, updates the app cache, and enters the main loop to wait for user commands.</li>
  </ul>

  <h2 id="process_command">process_command.py</h2>
  <p>This module processes and routes user commands to the appropriate handlers. It integrates functionalities from several modules (including <code>commands.py</code>, <code>gemini_client.py</code>, and file management functions) to perform actions ranging from web automation to file operations.</p>
  <h3>Key Functions and Features</h3>
  <ul>
    <li><code>process_command(command)</code>: The main dispatcher that interprets and routes commands to various handlers.</li>
    <li>Web automation functions:
      <ul>
        <li><code>open_web_browser(browser_name)</code>: Opens a browser (Chrome, Firefox, or Edge) using Selenium.</li>
        <li><code>perform_web_search(query)</code>: Performs a search query on Google.</li>
        <li><code>list_all_links_on_page()</code>, <code>select_web_link(index)</code>: Handle extraction and navigation of web page links.</li>
        <li><code>scroll_down()</code> and <code>scroll_up()</code>: Control scrolling in the browser.</li>
        <li><code>move_forward()</code> and <code>move_backward()</code>: Navigate browser history.</li>
        <li><code>close_web_browser()</code>: Closes the web browser instance.</li>
      </ul>
    </li>
    <li>File and folder operations:
      <ul>
        <li><code>handle_create_file(command)</code>: Creates a file in a specified folder and opens it in VS Code.</li>
        <li><code>find_file(file_name)</code> and <code>find_folder(folder_name)</code>: Search for files or folders.</li>
        <li><code>list_folder_structure(folder_path)</code> and <code>get_desktop_path()</code>: Assist in managing file system paths.</li>
      </ul>
    </li>
    <li>Email handling:
      <ul>
        <li><code>send_email(recipient, subject, body)</code>: Sends an email using SMTP.</li>
        <li><code>check_unread_emails()</code> and <code>process_email_command(command)</code>: Manage email notifications and compose emails.</li>
      </ul>
    </li>
    <li>Telegram Automation:
    <ul>
      <li><code>send_message_to_entity(entity, message):</code>
    Sends a message to the specified Telegram entity (user, group, or channel).
  </li>
  <li><code>get_entity(identifier):</code>
    Retrieves a Telegram entity based on a given identifier (username or ID).
  </li>
  <li><code>create_group(group_name, username=None):</code>
    Creates a new Telegram group with the provided name and optional username.
  </li>
  <li><code>create_channel(channel_name, username=None):</code>
    Creates a new Telegram channel with the provided name and optional username.
  </li>
  <li><code>add_user_to_group(group_identifier, user_identifier):</code>
    Adds the specified user to the given Telegram group.
  </li>
  <li><code>add_user_to_channel(channel_identifier, user_identifier):</code>
    Adds the specified user to the given Telegram channel.
  </li>
  <li><code>remove_user_from_group(group_identifier, user_identifier):</code>
    Removes the specified user from the given Telegram group.
  </li>
  <li><code>remove_user_from_channel(channel_identifier, user_identifier):</code>
    Removes the specified user from the given Telegram channel.
  </li>
  <li><code>list_group_members(group_identifier):</code>
    Lists all members of the specified Telegram group.
  </li>
  <li><code>list_channel_members(channel_identifier):</code>
    Lists all members of the specified Telegram channel.
  </li>
  <li><code>list_unread_group_messages(group_identifier):</code>
    Retrieves unread messages from the specified Telegram group.
  </li>
  <li><code>list_unread_channel_messages(channel_identifier):</code>
    Retrieves unread messages from the specified Telegram channel.
  </li>
  <li><code>search_group(group_identifier):</code>
    Searches for a Telegram group by its identifier and displays details such as title, username, and participant count.
  </li>
  <li><code>search_channel(channel_identifier):</code>
    Searches for a Telegram channel by its identifier and displays details such as title, username, and participant count.
  </li>
  <li><code>delete_group(group_identifier):</code>
    Deletes the specified Telegram group.
  </li>
  <li><code>delete_channel(channel_identifier):</code>
    Deletes the specified Telegram channel.
  </li>
  <li><code>logout_telegram():</code>
    Logs out of the current Telegram session.
  </li>
    </ul>
    </li>
    <li>Additional commands for file deletion, clearing file contents, and zipping files/folders.</li>
  </ul>

  <h2 id="speech_utils">speech_utils.py</h2>
  <p>This module handles text-to-speech and user input functions for the assistant. It provides auditory feedback and command input mechanisms.</p>
  <h3>Key Functions</h3>
  <ul>
    <li><code>speak(text)</code>: Converts text into audible speech using pyttsx3.</li>
    <li><code>stop_speech()</code>: Stops any ongoing speech output.</li>
    <li><code>get_command()</code>: Retrieves a command from the user via text input.</li>
    <li><code>greet()</code>: Greets the user based on the current time of day.</li>
    <li><code>wait_for_wake_word()</code>: Waits for the user to type the wake word ("jarvis") to activate the assistant.</li>
  </ul>

  <h2 id="connections">How the Files Are Connected</h2>
  <p>The project is structured into modular components that work together as follows:</p>
  <ul>
    <li><strong>main.py</strong> is the entry point—it initializes the assistant by creating a system tray icon, greeting the user, and waiting for the wake word. Once activated, it continuously listens for user commands.</li>
    <li><strong>process_command.py</strong> receives and interprets the user’s commands. Based on the command content, it routes the request to various modules:</li>
    <ul>
      <li>Commands related to opening or controlling applications are handled via functions in <strong>commands.py</strong> and use utilities from <strong>app_manager.py</strong>.</li>
      <li>Conversational and AI-generated responses are processed by <strong>gemini_client.py</strong>.</li>
      <li>File and web operations are performed within <strong>process_command.py</strong> itself, using helper functions for file system management and Selenium for web automation.</li>
      <li>Text-to-speech and user input are provided by <strong>speech_utils.py</strong>, and are used across all modules to interact with the user.</li>
    </ul>
  </ul>

  <h2 id="usage">Usage Instructions</h2>
  <p>To run the JARVIS Assistant:</p>
  <ol>
    <li>Ensure all dependencies (e.g., <code>pyttsx3</code>, <code>Selenium</code>, <code>pystray</code>, <code>fuzzywuzzy</code>, etc.) are installed.</li>
    <li>Set any required environment variables such as API keys and email credentials.</li>
    <li>Run the application by executing <code>main.py</code> from your command line or preferred IDE.</li>
    <li>Follow the on-screen instructions to activate the assistant by typing "jarvis" and issuing further commands.</li>
  </ol>

  <h2 id="run">How to Run This File</h2>
  <p>To start the JARVIS Assistant, follow these steps:</p>
  <ol>
    <li>Open your terminal or command prompt and navigate to the project directory.</li>
    <li>Ensure that all dependencies are installed (for example, via <code>pip install -r requirements.txt</code> if a requirements file is provided).</li>
    <li>Set the necessary environment variables (such as API keys, email credentials, etc.).</li>
    <li>Run the assistant by executing the following command:
      <pre>python main.py</pre>
    </li>
    <li>The assistant will initialize, display a system tray icon, and wait for you to type "jarvis" to activate it.</li>
  </ol>

  <h2>Conclusion</h2>
  <p>This modular design allows for easy maintenance and expansion of functionalities. Each component is responsible for a distinct set of tasks, ensuring that the JARVIS Assistant remains flexible and responsive to a wide range of commands.</p>

</body>
</html>
