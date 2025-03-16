import os
import re
import subprocess
import shutil
import sys
import string
import zipfile
import imaplib
import email
from email.header import decode_header
from pywinauto import Application,keyboard
import smtplib
import time
from email.message import EmailMessage
import asyncio
import re
from telethon import TelegramClient
from telethon import functions, types
from telethon.tl.types import InputChannel, InputUser, ChatBannedRights,InputPeerChannel,InputPeerUser
from speech_utils import get_command
from dotenv import load_dotenv
load_dotenv()
from commands import (
    handle_open_app, handle_play_song, handle_time,
    handle_date, handle_shutdown, handle_cancel_shutdown, handle_check_status, handle_exit
)
from gemini_client import get_gemini_response
from speech_utils import speak, stop_speech

from pywinauto import Application, keyboard
import time

# --- Web Automation Imports ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Global variables for web automation
global_driver = None
global_links = []

# Global Telegram client
telegram_client = None

api_id = os.environ.get("api_id")
api_hash = os.environ.get("api_hash")

async def send_message_to_entity(entity, message):
    if telegram_client is None:
        speak("Please start the Telegram session first.")
        return
    try:
        await telegram_client.send_message(entity, message)
        speak(f"Message sent to {entity}")
    except Exception as e:
        speak(f"Error: {e}")

        
async def create_group(group_name):
    try:
        me = await telegram_client.get_me()
        input_me = InputPeerUser(me.id, me.access_hash)
        result = await telegram_client(functions.messages.CreateChatRequest(
            users=[input_me],
            title=group_name
        ))
        # chat = result.chats[0]  # The Chat object
        speak(f"Group '{group_name}' created successfully.")
        # return chat  # Return the entity
    except Exception as e:
        speak(f"Failed to create group: {e}")
        return None

async def create_channel(channel_name):
    try:
        result = await telegram_client(functions.channels.CreateChannelRequest(
            title=channel_name,
            about="Created by assistant",
            megagroup=False
        ))
        channel = result.chats[0]  # The Channel object
        speak(f"Channel '{channel_name}' created successfully. ID '{channel.id}'")
        return channel  # Return the entity
    except Exception as e:
        speak(f"Failed to create channel: {e}")
        return None
        
def prompt_save_summary(summary):
    """
    Asks the user if they want to save the summary.
    If yes, it prompts for a file name, searches for that file on the C: drive,
    and if found, saves the summary there; otherwise, it saves the file on the Desktop.
    """
    speak("Would you like to save the summary to a file? Please answer yes or no.")
    response = get_command()  # This function retrieves user input
    if "yes" in response.lower():
        speak("Please provide the file name with extension, for example summary.txt")
        file_name = get_command().strip()
        # Search the entire C drive for the file.
        file_path = find_file(file_name, search_path="C:\\Users\\Vivek\\Desktop")
        if file_path:
            # If file exists on C drive, save there.
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(summary)
                speak(f"Summary has been saved to {file_path}.")
            except Exception as e:
                speak(f"Sorry, I couldn't save the file due to: {e}")
        else:
            # If file does not exist, save it on the Desktop.
            desktop = get_desktop_path()
            file_path = os.path.join(desktop, file_name)
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(summary)
                speak(f"Summary has been saved to {file_path} on your Desktop.")
            except Exception as e:
                speak(f"Sorry, I couldn't save the file due to: {e}")
    else:
        speak("Alright, not saving the summary.")

def open_web_browser(browser_name):
    """
    Opens the specified browser (Chrome, Firefox, or Edge) using Selenium,
    navigates to Google immediately, and returns the driver.
    """
    global global_driver
    browser_name = browser_name.lower()
    try:
        if browser_name == "chrome":
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--ignore-certificate-errors")
            global_driver = webdriver.Chrome(options=options)
        elif browser_name == "firefox":
            from selenium.webdriver.firefox.options import Options as FFOptions
            options = FFOptions()
            options.accept_insecure_certs = True
            global_driver = webdriver.Firefox(options=options)
        elif browser_name == "edge":
            from selenium.webdriver.edge.options import Options as EdgeOptions
            options = EdgeOptions()
            options.use_chromium = True
            options.add_argument("--ignore-certificate-errors")
            global_driver = webdriver.Edge(options=options)
        else:
            speak("Unsupported browser. Please choose Chrome, Firefox, or Edge.")
            return None
        
        # Immediately navigate to Google
        global_driver.get("https://www.google.com")
        speak(f"{browser_name.capitalize()} browser opened and navigated to Google.")
        return global_driver
    except Exception as e:
        speak(f"Sorry, I couldn't open the browser due to: {e}")
        return None

def list_all_links_on_page():
    """
    Scrapes the current page for all anchor (<a>) elements with visible text and an href,
    updates the global_links variable, and speaks out a summary.
    """
    global global_driver, global_links
    if global_driver is None:
        speak("No browser is open.")
        return
    try:
        # Find all anchor elements on the current page
        link_elements = global_driver.find_elements(By.TAG_NAME, "a")
        new_links = []
        for elem in link_elements:
            href = elem.get_attribute("href")
            text = elem.text.strip()
            if href and text:
                new_links.append((text, href))
        
        # Update global_links with fresh data
        global_links = new_links
        
        if new_links:
            speak(f"I found {len(new_links)} links on this page. select link number [n]")
            # for idx, (text, href) in enumerate(new_links[:5], 1):
            #     speak(f"Link {idx}: {text}")
            #     print(f"{idx}. {text} - {href}")
            # print()
            # Optionally, print all the links to the terminal for further inspection:
            for idx, (text, href) in enumerate(new_links, 1):
                print(f"{idx}. {text} - {href}")
        else:
            speak("I couldn't find any links on this page.")
    except Exception as e:
        speak(f"Sorry, I encountered an error while retrieving links: {e}")
def perform_web_search(query):
    """
    Types the query in the search field of the current page (assumed to be Google)
    and collects a list of search result links.
    """
    global global_driver, global_links
    if global_driver is None:
        speak("Please open a browser first using 'open browser [browser_name]'.")
        return
    try:
        # Assume the browser is already on Google, so no need to call get("https://www.google.com")
        time.sleep(2)
        search_box = global_driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for results to load
        
        # Extract search result links (assuming h3 elements for titles)
        result_elements = global_driver.find_elements(By.CSS_SELECTOR, "a > h3")
        global_links = []
        for element in result_elements:
            try:
                parent = element.find_element(By.XPATH, "./ancestor::a")
                href = parent.get_attribute("href")
                title = element.text.strip()
                if title and href:
                    global_links.append((title, href))
            except Exception:
                continue
        
        if global_links:
            speak(f"I found {len(global_links)} links. Please say, 'select link number [n]'.")
            # Optionally, print out the links in terminal for reference:
            # for idx, (title, url) in enumerate(global_links[:5], 1):
            #     print(f"{idx}. {title} - {url}")
            # print()
            for idx, (title, url) in enumerate(global_links, 1):
                print(f"{idx}. {title} - {url}")
        else:
            speak("No links were found for that query.")
    except Exception as e:
        speak(f"Sorry, I encountered an error while searching: {e}")
def select_web_link(index):
    """
    Navigates the browser to the URL of the search result at the given index.
    """
    global global_driver, global_links
    if global_driver is None:
        speak("Please open a browser and perform a search first.")
        return
    if index < 0 or index >= len(global_links):
        speak("Invalid link number. Please choose a valid link number.")
        return
    try:
        url = global_links[index][1]
        global_driver.get(url)
        speak(f"Navigated to link number {index + 1}.")
    except Exception as e:
        speak(f"Sorry, I couldn't navigate to the link due to: {e}")
        
def read_page_content():
    """
    Extracts and returns the visible text content of the current web page.
    """
    global global_driver
    if global_driver is None:
        speak("No browser is open.")
        return None
    try:
        # Find the body element and get its visible text
        body_element = global_driver.find_element(By.TAG_NAME, "body")
        page_text = body_element.text.strip()
        return page_text
    except Exception as e:
        speak(f"Sorry, I couldn't read the page content due to: {e}")
        return None

def summarize_page_content():
    """
    Reads the current page's content, sends it to Gemini for summarization, and speaks the summary.
    """
    content = read_page_content()
    if content:
        summary = get_gemini_response(content)
        speak("Here is the summary of the page:")
        speak(summary)
        prompt_save_summary(summary)
    else:
        speak("No content could be extracted from this page.")

        
def scroll_down():
    global global_driver
    if global_driver is None:
        speak("Please open a browser first.")
        return
    try:
        total_height = global_driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        step = 100  # Smaller step for slower scrolling
        while current_position < total_height:
            global_driver.execute_script("window.scrollBy(0, arguments[0]);", step)
            current_position += step
            time.sleep(1)  # Increase delay for slower scroll
        speak("Scrolled down.")
    except Exception as e:
        speak(f"Sorry, I couldn't scroll down due to: {e}")

def scroll_up():
    global global_driver
    if global_driver is None:
        speak("Please open a browser first.")
        return
    try:
        current_position = global_driver.execute_script("return window.pageYOffset;")
        step = 100  # Smaller step for slower scrolling
        while current_position > 0:
            global_driver.execute_script("window.scrollBy(0, -arguments[0]);", step)
            time.sleep(1)  # Increase delay for slower scroll
            current_position = global_driver.execute_script("return window.pageYOffset;")
        speak("Scrolled up.")
    except Exception as e:
        speak(f"Sorry, I couldn't scroll up due to: {e}")
        
def move_forward():
    global global_driver
    if global_driver is None:
        speak("No browser is open.")
    else:
        try:
            global_driver.forward()
            speak("Moved forward in the browser history.")
        except Exception as e:
            speak(f"Sorry, I couldn't move forward due to: {e}")

def move_backward():
    global global_driver
    if global_driver is None:
        speak("No browser is open.")
    else:
        try:
            global_driver.back()
            speak("Moved backward in the browser history.")
        except Exception as e:
            speak(f"Sorry, I couldn't move backward due to: {e}")

def close_web_browser():
    """
    Closes the Selenium web browser and resets the global driver.
    """
    global global_driver
    if global_driver is None:
        speak("No browser is open.")
        return
    try:
        global_driver.quit()
        global_driver = None
        speak("Browser closed successfully.")
    except Exception as e:
        speak(f"Sorry, I couldn't close the browser due to: {e}")
        
def send_email(recipient, subject, body):
    # Get credentials (make sure to set these in your environment for security)
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    
    if not sender or not password:
        speak("Email credentials are not set.")
        return

    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        # For Gmail, use smtp.gmail.com and TLS on port 587
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(sender, password)
            smtp.send_message(msg)
        speak("Email sent successfully.")
    except Exception as e:
        speak(f"Sorry, I couldn't send the email due to: {e}")

def handle_create_file(command):
    # Extract file_name and folder_name from the command using a regular expression
    match = re.search(r"create file (.+) in (.+)", command)
    if match:
        file_name = match.group(1).strip()   # e.g., "main.py"
        folder_name = match.group(2).strip()   # e.g., "my_project" or "Desktop"
        try:
            # Determine the parent folder path based on user's specification
            if folder_name.lower() == "desktop":
                folder_path = get_desktop_path()
            elif os.path.isabs(folder_name):
                folder_path = folder_name
            else:
                # Try to find the folder on Desktop (or you can choose another default search path)
                folder_path = find_folder(folder_name, search_path=get_desktop_path())
                if folder_path is None:
                    # If not found, create the folder in the current working directory
                    os.makedirs(folder_name, exist_ok=True)
                    folder_path = os.path.abspath(folder_name)
            
            # Build the full path to the file inside the determined folder
            full_path = os.path.join(folder_path, file_name)
            # Create an empty file
            open(full_path, "w").close()
            # Open the file in VS Code using your specified command path
            subprocess.run([r"C:\Users\Vivek\AppData\Local\Programs\cursor\resources\app\bin\code.cmd", full_path])
            speak(f"File {file_name} created in folder {folder_path}.")
        except Exception as e:
            speak(f"Sorry, I couldn’t create the file due to an error: {e}")
    else:
        speak("I didn’t understand the create file command. Please say 'create file [file_name] in [folder_name]'.")


def find_file(file_name, search_path="C:\\Users\\Vivek\\Desktop"):
    """
    Recursively search for a file with the given file_name starting from the C: drive.
    Returns the full path if found, otherwise returns None.
    """
    for root, dirs, files in os.walk(search_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def find_folder(folder_name, search_path="C:\\Users\\Vivek\\Desktop"):
    """
    Recursively search for a folder with the given folder_name starting from the C: drive.
    Returns the full path if found, otherwise returns None.
    """
    for root, dirs, files in os.walk(search_path):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return None

def list_folder_structure(folder_path):
    """Returns a list of file and folder names in the given folder_path."""
    try:
        return os.listdir(folder_path)
    except Exception as e:
        speak(f"Sorry, I couldn't list the contents due to: {e}")
        return []
    
def get_desktop_path():
    """
    Returns the Desktop folder path for the current user.
    """
    return os.path.join(os.path.expanduser("~"), "Desktop")

# Example usage:
# check_unread_emails()

def check_unread_emails():
    # Get credentials from environment variables
    user = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    
    if not user or not password:
        speak("Email credentials are not set.")
        return

    try:
        # Connect to the Gmail IMAP server
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(user, password)
        imap.select("inbox")

        # Search for unseen emails
        status, messages = imap.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        if not email_ids:
            speak("You have no new emails.")
        else:
            speak(f"You have {len(email_ids)} new email(s).")
            for num in email_ids:
                # Fetch the email by ID
                status, msg_data = imap.fetch(num, "(RFC822)")
                if status != "OK":
                    continue
                for response in msg_data:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        # Decode email subject
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        from_ = msg.get("From")
                        speak(f"Email from {from_} with subject: {subject}.")
        imap.logout()
    except Exception as e:
        speak(f"Sorry, I couldn't check emails due to: {e}")

# def process_email_command(command):
#     # Example command: "compose email to recipient@example.com subject Test Email body Hello, this is a test."
#     try:
#         recipient = re.search(r"to (.+?) subject", command, re.IGNORECASE).group(1).strip()
#         subject = re.search(r"subject (.+?) body", command, re.IGNORECASE).group(1).strip()
#         body = re.search(r"body (.+)", command, re.IGNORECASE).group(1).strip()
#         send_email(recipient, subject, body)
#     except Exception as e:
#         speak("I didn't understand your email command. Please say something like, compose email to [recipient] subject [subject] body [message].")


def process_email_command(command):
    #compose email to abc@gmail.com subject report body from name.txt
    try:
        recipient = re.search(r"to (.+?) subject", command, re.IGNORECASE).group(1).strip()
        subject = re.search(r"subject (.+?) body", command, re.IGNORECASE).group(1).strip()
        body_match = re.search(r"body (.+)", command, re.IGNORECASE)

        if body_match:
            body_content = body_match.group(1).strip()
            # Check if the body is referring to a file (e.g., "body from file.txt")
            file_match = re.search(r"from (.+\.txt)", body_content, re.IGNORECASE)
            if file_match:
                file_name = file_match.group(1).strip()
                full_path = find_file(file_name)
                if full_path:
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            body_content = f.read()
                    except Exception as e:
                        speak(f"Sorry, I couldn't read the file {file_name} due to: {e}")
                        return
                else:
                    speak(f"I couldn't find the file {file_name}.")
                    return

        send_email(recipient, subject, body_content)
    
    except Exception as e:
        speak("I didn't understand your email command. Please say something like, 'compose email to [recipient] subject [subject] body [message]' or 'body from [file_name.txt]'.")

async def logout_telegram():
    try:
        await telegram_client.log_out()
        await telegram_client.disconnect()
        speak("Logged out of Telegram successfully.")
    except Exception as e:
        speak(f"Error logging out of Telegram: {e}")

def process_command(command):
    # Check if the user wants to stop any ongoing speech
    if command.strip() == "stop":
        stop_speech()
        speak("Okay, I've stopped speaking. How can I assist you next?")
        return
    
    global telegram_client
    
    if command == "start telegram":
        if telegram_client is None:
            phone = input("Please enter your phone number: ")
            telegram_client = TelegramClient('telegram_session', api_id, api_hash)
            try:
                telegram_client.start(phone=phone)
                speak("Telegram session started successfully.")
            except Exception as e:
                speak(f"Failed to start Telegram session: {e}")
        else:
            speak("Telegram session is already started.")
    
    elif "create group" in command:
        match = re.search(r"create group (.+)", command)
        if match:
            group_name = match.group(1).strip()
            asyncio.get_event_loop().run_until_complete(create_group(group_name))
        else:
            speak("Please specify the group name.")
            
    elif "create channel" in command:
        match = re.search(r"create channel (.+)", command)
        if match:
            channel_name = match.group(1).strip()
            asyncio.get_event_loop().run_until_complete(create_channel(channel_name))
        else:
            speak("Please specify the channel name.")
    
    # Example condition for adding a user to a group:
            
    # And for sending a message:
    elif "send message to" in command:
        match = re.search(r"send message to (.+?) (.*)", command)
        if match:
            entity = match.group(1).strip()
            message = match.group(2).strip()
            asyncio.get_event_loop().run_until_complete(send_message_to_entity(entity, message))
        else:
            speak("I didn't understand the send message command. Please say 'send message to [recipient] [message]'.")

            
    elif "logout telegram" in command:
        asyncio.get_event_loop().run_until_complete(logout_telegram())
    
    # Web automation
    elif "open browser" in command:
        browser_name = command.replace("open browser", "").strip()
        open_web_browser(browser_name)
    elif "type query" in command:
        query = command.replace("type query", "").strip()
        perform_web_search(query)
        
        
    elif "summarize page" in command or "read page" in command:
        summarize_page_content()

    elif "select link number" in command:
        match = re.search(r"select link number (\d+)", command, re.IGNORECASE)
        if match:
            index = int(match.group(1)) - 1
            select_web_link(index)
        else:
            speak("I didn't understand which link to select.")
            
    elif "list links" in command:
        list_all_links_on_page()

            
    elif "scroll down" in command:
        scroll_down()

    elif "scroll up" in command:
        scroll_up()
        
    elif "move forward" in command:
        move_forward()
    
    elif "move backward" in command:
        move_backward()


    elif "close browser" in command:
        close_web_browser()
    
    # Existing commands
    elif "open" in command and "file" not in command:  # "open" as a generic command
        handle_open_app(command)

    # New VS Code automation commands
    
    elif "create folder" in command and " in " in command:
    # Expected format: "create folder [child_folder] in [parent_folder]"
        match = re.search(r"create folder (.+) in (.+)", command)
        if match:
            child_folder = match.group(1).strip()
            parent_folder_str = match.group(2).strip()
            
            # Determine the parent's folder path based on the user's input
            if parent_folder_str.lower() == "desktop":
                parent_folder_path = get_desktop_path()
            else:
                if os.path.isabs(parent_folder_str):
                    parent_folder_path = parent_folder_str
                else:
                    # Attempt to find the folder on the system using your find_folder function
                    parent_folder_path = find_folder(parent_folder_str)
                    if parent_folder_path is None:
                        # If not found, create it relative to the current working directory
                        os.makedirs(parent_folder_str, exist_ok=True)
                        parent_folder_path = os.path.abspath(parent_folder_str)
            
            # Now build the full path for the child folder inside the determined parent folder
            child_folder_path = os.path.join(parent_folder_path, child_folder)
            if not os.path.exists(child_folder_path):
                os.makedirs(child_folder_path, exist_ok=True)
                speak(f"Folder '{child_folder}' created in '{parent_folder_path}'.")
            else:
                speak(f"Folder '{child_folder}' already exists in '{parent_folder_path}'.")
        else:
            speak("I didn’t understand the create folder command. Please say 'create folder [folder_name] in [parent_folder]'.")

    
    elif "create file" in command and " in " in command:
        handle_create_file(command)
    
    elif ("write" in command or "update" in command):
    # Look for a candidate file name in the command: e.g., something like main.py, script.cpp, etc.
        file_candidates = re.findall(r"(\S+\.\w+)", command)
        if file_candidates:
            file_name = file_candidates[0]  # Pick the first candidate as the file name
            # Remove file name and keywords ("write", "update", "in") from the command to extract the prompt
            prompt = command.replace(file_name, "")
            prompt = prompt.replace("write", "").replace("update", "").replace("in", "").strip()
            full_path = find_file(file_name)
            if full_path:
                code = get_gemini_response(f"Write {prompt}")
                try:
                    with open(full_path, "w") as f:
                        f.write(code)
                    speak(f"Text written to {file_name} at {full_path}.")
                except Exception as e:
                    speak(f"Sorry, I couldn't write to the file due to: {e}")
            else:
                speak(f"I couldn't find a file named {file_name} in the folder structure.")
        else:
            speak("I couldn't detect a file name in your command. Please include a valid file name with an extension.")

    
    elif "open file" in command:
        # New command: "open file [file_name]"
        file_name = command.replace("open file", "").strip()
        full_path = find_file(file_name)
        if full_path:
            try:
                os.startfile(full_path)
                speak(f"Opening file {file_name}.")
            except Exception as e:
                speak(f"Sorry, I couldn't open the file due to: {e}")
        else:
            speak(f"I couldn't find a file named {file_name} in the folder structure.")
    
    elif "list folder structure" in command:
        # New command: "list folder structure [folder_name]"
        match = re.search(r"list folder structure (.+)", command)
        if match:
            folder_name = match.group(1).strip()
            folder_path = find_folder(folder_name)
            if folder_path:
                contents = list_folder_structure(folder_path)
                if contents:
                    speak(f"The contents of folder {folder_name} are:")
                    for item in contents:
                        speak(item)
                else:
                    speak(f"Folder {folder_name} is empty.")
            else:
                speak(f"I couldn't find a folder named {folder_name} in the folder structure.")
        else:
            speak("I didn't understand the list folder structure command. Please say 'list folder structure [folder_name]'.")
            
    elif "read file" in command:
    # Expected format: "read file [file_name]"
        file_name = command.replace("read file", "").strip()
        full_path = find_file(file_name)
        if full_path:
            try:
                with open(full_path, "r") as f:
                    file_content = f.read()
                # Pass the file content to Gemini as a prompt
                response = get_gemini_response(file_content)
                speak(response)
            except Exception as e:
                speak(f"Sorry, I couldn't read the file due to: {e}")
        else:
            speak(f"I couldn't find a file named {file_name} in the folder structure.")

    
    # Run command: "run [file_name]"
    elif "run" in command:
        file_name = command.replace("run", "").strip()
        full_path = find_file(file_name)
        if full_path:
            ext = os.path.splitext(full_path)[1].lower()
            try:
                if ext == ".py":
                    subprocess.Popen(f'start cmd /k python "{full_path}"', shell=True)
                elif ext == ".cpp":
                    exe_path = os.path.splitext(full_path)[0] + ".exe"
                    compile_cmd = f'g++ "{full_path}" -o "{exe_path}"'
                    compile_result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
                    if compile_result.returncode != 0:
                        speak(f"Compilation error: {compile_result.stderr}")
                        return
                    subprocess.Popen(f'start cmd /k "{exe_path}"', shell=True)
                elif ext == ".js":
                    subprocess.Popen(f'start cmd /k node "{full_path}"', shell=True)
                elif ext == ".bat":
                    subprocess.Popen(f'start cmd /k "{full_path}"', shell=True)
                else:
                    os.startfile(full_path)
                speak(f"Running {file_name} in a new terminal.")
            except Exception as e:
                speak(f"Sorry, I couldn't run the file due to: {e}")
        else:
            speak(f"I couldn't find a file named {file_name} in the folder structure.")
    
    # New command for file deletion: "delete file [file_name]"
    elif "delete file" in command:
        match = re.search(r"delete file (.+)", command)
        if match:
            file_name = match.group(1).strip()
            full_path = find_file(file_name)
            if full_path:
                try:
                    os.remove(full_path)
                    speak(f"File {file_name} has been deleted.")
                except Exception as e:
                    speak(f"Sorry, I couldn't delete the file due to: {e}")
            else:
                speak(f"I couldn't find a file named {file_name} in the folder structure.")
        else:
            speak("I didn't understand the delete file command. Please say 'delete file [file_name]'.")
    
    # New command for clearing file content: "clear file [file_name]"
    elif "clear file" in command:
        match = re.search(r"clear file (.+)", command)
        if match:
            file_name = match.group(1).strip()
            full_path = find_file(file_name)
            if full_path:
                try:
                    with open(full_path, "w") as f:
                        f.write("")
                    speak(f"Contents of file {file_name} have been cleared.")
                except Exception as e:
                    speak(f"Sorry, I couldn't clear the file due to: {e}")
            else:
                speak(f"I couldn't find a file named {file_name} in the folder structure.")
        else:
            speak("I didn't understand the clear file command. Please say 'clear file [file_name]'.")
    
    # New command for deleting a folder: "delete folder [folder_name]"
    elif "delete folder" in command:
        match = re.search(r"delete folder (.+)", command)
        if match:
            folder_name = match.group(1).strip()
            full_folder_path = find_folder(folder_name)
            if full_folder_path:
                try:
                    shutil.rmtree(full_folder_path)
                    speak(f"Folder {folder_name} has been deleted.")
                except Exception as e:
                    speak(f"Sorry, I couldn't delete the folder due to: {e}")
            else:
                speak(f"I couldn't find a folder named {folder_name} in the folder structure.")
        else:
            speak("I didn't understand the delete folder command. Please say 'delete folder [folder_name]'.")
            
    # New command for zipping a file: "zip file [file_name] in [folder_name]"
    elif "zip file" in command and " in " in command:
        match = re.search(r"zip file (.+) in (.+)", command)
        if match:
            file_name = match.group(1).strip()
            folder_name = match.group(2).strip()
            folder_path = find_folder(folder_name)

            if folder_path:
                file_path = find_file(file_name)
                if file_path:
                    zip_path = os.path.join(folder_path, file_name + ".zip")
                    try:
                        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            zipf.write(file_path, arcname=file_name)
                        speak(f"File {file_name} has been zipped in {folder_name}.")
                    except Exception as e:
                        speak(f"Sorry, I couldn't zip the file due to: {e}")
                else:
                    speak(f"I couldn't find a file named {file_name} in {folder_name}.")
            else:
                speak(f"I couldn't find the folder {folder_name}.")
        else:
            speak("I didn't understand the zip file command. Please say 'zip file [file_name] in [folder_name]'.")

# New command for zipping a folder: "zip folder [folder_name] in [parent_folder]"
    elif "zip folder" in command and " in " in command:
    # Expected format: "zip folder [child_folder] in [parent_folder]"
        match = re.search(r"zip folder (.+) in (.+)", command)
        if match:
            child_folder = match.group(1).strip()
            parent_folder_str = match.group(2).strip()
            
            # Determine the parent's folder path based on the user's input
            if parent_folder_str.lower() == "desktop":
                parent_folder_path = get_desktop_path()
            elif os.path.isabs(parent_folder_str):
                parent_folder_path = parent_folder_str
            else:
                parent_folder_path = find_folder(parent_folder_str)
                if parent_folder_path is None:
                    # If not found, create it relative to the current working directory
                    os.makedirs(parent_folder_str, exist_ok=True)
                    parent_folder_path = os.path.abspath(parent_folder_str)
            
            # Now, try to find the child folder inside the determined parent folder
            child_folder_path = find_folder(child_folder)
            if child_folder_path:
                # Create the zip file path in the parent folder (child_folder.zip)
                zip_file_path = os.path.join(parent_folder_path, child_folder + ".zip")
                # shutil.make_archive expects a base name without extension.
                base_name = os.path.splitext(zip_file_path)[0]
                try:
                    shutil.make_archive(base_name, 'zip', child_folder_path)
                    speak(f"Folder '{child_folder}' has been zipped in '{parent_folder_path}'.")
                except Exception as e:
                    speak(f"Sorry, I couldn't zip the folder due to: {e}")
            else:
                speak(f"I couldn't find a folder named '{child_folder}' in '{parent_folder_path}'.")
        else:
            speak("I didn't understand the zip folder command. Please say 'zip folder [folder_name] in [parent_folder]'.")
            
    elif "compose email" in command:
        process_email_command(command)
    elif "check inbox" in command or "check unread emails" in command:
        check_unread_emails()

    # elif "search for" in command:
    #     handle_search(command)
    elif "play" in command and "song" in command:
        handle_play_song(command)
    elif "tell" in command and "time" in command:
        handle_time(command)
    elif "tell" in command and "date" in command:
        handle_date(command)
    elif "shutdown system" in command:
        handle_shutdown(command)
    elif "cancel shutdown" in command:
        handle_cancel_shutdown(command)
    elif "check status" in command:
        handle_check_status(command)
    elif "exit" in command or "bye" in command:
        handle_exit(command)
        
    else:
        # Fallback to Gemini for conversational queries
        response_text = get_gemini_response(command)
        speak(response_text)
