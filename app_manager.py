import os
import shelve
from fuzzywuzzy import fuzz
import win32com.client

APP_CACHE_FILE = "app_cache.db"
app_cache = shelve.open(APP_CACHE_FILE)

def resolve_shortcut(shortcut_path):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        return shortcut.TargetPath
    except Exception as e:
        print(f"Error resolving shortcut {shortcut_path}: {e}")
        return None

def discover_apps():
    discovered_apps = {}
    start_menu_paths = [
        os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
    ]
    for start_menu in start_menu_paths:
        if not os.path.exists(start_menu):
            continue
        for root, dirs, files in os.walk(start_menu):
            for file in files:
                if file.endswith(".lnk"):
                    app_name = file.replace(".lnk", "").lower()
                    full_path = os.path.join(root, file)
                    target_path = resolve_shortcut(full_path)
                    if target_path and target_path.endswith(".exe"):
                        discovered_apps[app_name] = target_path
    return discovered_apps

def update_app_cache():
    discovered_apps = discover_apps()
    for app_name, path in discovered_apps.items():
        app_cache[app_name] = path
    return discovered_apps

def find_app(app_name):
    app_name = app_name.lower().strip()
    if app_name in app_cache:
        return app_cache[app_name]
    discovered_apps = update_app_cache()
    if app_name in discovered_apps:
        app_cache[app_name] = discovered_apps[app_name]
        return discovered_apps[app_name]
    best_match = None
    best_score = 0
    for name, path in discovered_apps.items():
        score = fuzz.partial_ratio(app_name, name)
        if score > 80 and score > best_score:
            best_match = path
            best_score = score
    if best_match:
        app_cache[app_name] = best_match
        return best_match
    return None

def close_app_cache():
    app_cache.close()
