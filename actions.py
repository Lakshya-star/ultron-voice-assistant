"""Ultron task engine — every 'do something' skill lives here.

Cross-platform: Windows (os.startfile / shutdown / pyautogui) and macOS
(open -a / say / osascript / screencapture) are both natively supported.
"""
import os
import sys
import ast
import re
import time
import random
import datetime
import platform
import subprocess
import webbrowser
from urllib.parse import quote_plus

import requests
import xml.etree.ElementTree as ET

IS_WINDOWS = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"

HOME = os.path.expanduser("~")

SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "stack overflow": "https://stackoverflow.com",
    "chatgpt": "https://chat.openai.com",
    "gemini": "https://gemini.google.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "spotify": "https://open.spotify.com",
    "linkedin": "https://www.linkedin.com",
    "twitter": "https://twitter.com",
    "reddit": "https://www.reddit.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
    "maps": "https://maps.google.com",
    "drive": "https://drive.google.com",
    "classroom": "https://classroom.google.com",
    "wikipedia": "https://www.wikipedia.org",
}

if IS_MAC:
    APPS = {
        # candidates are tried in order; 'code' CLI first for VS Code
        "vs code": [["code"], ["open", "-a", "Visual Studio Code"]],
        "vscode": [["code"], ["open", "-a", "Visual Studio Code"]],
        "visual studio code": [["code"], ["open", "-a", "Visual Studio Code"]],
        "notepad": [["open", "-a", "TextEdit"]],
        "calculator": [["open", "-a", "Calculator"]],
        "terminal": [["open", "-a", "Terminal"], ["open", "-a", "iTerm"]],
        "cmd": [["open", "-a", "Terminal"]],
        "file explorer": [["open", "."]],
        "explorer": [["open", "."]],
        "finder": [["open", "."]],
        "paint": [["open", "-a", "Preview"]],
        "chrome": [["open", "-a", "Google Chrome"], ["open", "-a", "Chromium"]],
        "safari": [["open", "-a", "Safari"]],
        "notes": [["open", "-a", "Notes"]],
        "mail": [["open", "-a", "Mail"]],
        "calendar": [["open", "-a", "Calendar"]],
        "music": [["open", "-a", "Music"]],
        "spotify app": [["open", "-a", "Spotify"]],
        "obs": [["open", "-a", "OBS"]],
    }
elif IS_WINDOWS:
    APPS = {
        "vs code": [["code"], ["code.cmd"], ["Code"]],
        "vscode": [["code"], ["code.cmd"], ["Code"]],
        "visual studio code": [["code"], ["code.cmd"], ["Code"]],
        "notepad": [["notepad"]],
        "calculator": [["calc"]],
        "terminal": [["cmd"]],
        "cmd": [["cmd"]],
        "file explorer": [["explorer"]],
        "explorer": [["explorer"]],
        "finder": [["explorer"]],
        "paint": [["mspaint"]],
        "chrome": [["chrome"]],
        "notes": [["notepad"]],
        "calendar": [["outlookcal:"]],
        "spotify app": [["spotify"]],
        "obs": [["obs64"], ["obs"]],
    }
else:  # Linux
    APPS = {
        "vs code": [["code"]],
        "vscode": [["code"]],
        "visual studio code": [["code"]],
        "notepad": [["gedit"], ["nano"]],
        "calculator": [["gnome-calculator"]],
        "terminal": [["x-terminal-emulator"]],
        "cmd": [["bash"]],
        "file explorer": [["xdg-open", "."]],
        "explorer": [["xdg-open", "."]],
        "finder": [["xdg-open", "."]],
        "paint": [["gimp"]],
        "chrome": [["google-chrome"]],
        "obs": [["obs"]],
    }

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.txt")
NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.txt")
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I told my computer I needed a break, and it said: no problem, I will go to sleep.",
    "Why did the developer go broke? Because he used up all his cache.",
    "There are only two hard things in computer science: cache invalidation, naming things, and off-by-one errors.",
    "I would tell you a UDP joke, but you might not get it.",
    "My code does not have bugs. It develops random, undocumented features.",
]
QUIZ_BANK = [
    ("Which language is known as the mother of all programming languages?",
     ["C", "Python", "COBOL", "Fortran"], "a"),
    ("What does HTTP stand for?",
     ["HyperText Transfer Protocol", "High Transfer Text Protocol",
      "HyperText Transmission Process", "Hyperlink Text Type Protocol"], "a"),
    ("Which company developed the macOS operating system?",
     ["Microsoft", "Apple", "IBM", "Google"], "b"),
    ("What is the time complexity of binary search on a sorted array?",
     ["O(n)", "O(n log n)", "O(log n)", "O(1)"], "c"),
    ("Which of these is NOT a Python data type?",
     ["tuple", "list", "dictionary", "arraylist"], "d"),
    ("Who is considered the father of the computer?",
     ["Alan Turing", "Charles Babbage", "John von Neumann", "Dennis Ritchie"], "b"),
]


# ---------------------------------------------------------------- helpers
def _run(cmd_list):
    """Launch a command in the background, never blocking Ultron."""
    try:
        subprocess.Popen(cmd_list, shell=IS_WINDOWS)
        return True
    except FileNotFoundError:
        return False


def _mac_app_exists(display_name):
    for base in ("/Applications", os.path.join(HOME, "Applications")):
        for name in (display_name, display_name + ".app"):
            if os.path.isdir(os.path.join(base, name)):
                return True
    return False


# ---------------------------------------------------------------- browsing / apps
def open_website(name_or_url):
    key = name_or_url.lower().strip()
    if key in SITES:
        webbrowser.open(SITES[key])
        return f"Opening {key.capitalize()}."
    if key.startswith(("http://", "https://")) or "." in key:
        url = key if key.startswith(("http://", "https://")) else f"https://{key}"
        webbrowser.open(url)
        return f"Opening {key}."
    return None


def open_app(name):
    key = name.lower().strip()
    if key in APPS:
        for candidate in APPS[key]:
            # 'open -a AppName' only works if the app is really installed
            if IS_MAC and candidate[:2] == ["open", "-a"] and not _mac_app_exists(candidate[2]):
                continue
            if _run(candidate):
                return f"Opening {key.capitalize()}."
        hint = ""
        if key in ("vs code", "vscode", "visual studio code") and IS_MAC:
            hint = " In VS Code, press Command+Shift+P and run 'Shell Command: Install code command in PATH'."
        return f"I could not find {key} on this Mac.{hint}"
    return None


def search_youtube(query):
    webbrowser.open("https://www.youtube.com/results?search_query=" + quote_plus(query))
    return f"Searching YouTube for {query}."


def search_google(query):
    webbrowser.open("https://www.google.com/search?q=" + quote_plus(query))
    return f"Searching Google for {query}."


def play_on_youtube(query):
    webbrowser.open("https://www.youtube.com/results?search_query=" + quote_plus(query))
    return f"Playing the top results for {query} on YouTube. Hit play on the one you like."


def create_folder(name, parent=None):
    name = name.strip().strip('"\'')
    if not name:
        return "What should I name the folder?"
    bad = '<>:"|?*' if IS_MAC else '<>:"/\\|?*'
    clean = "".join(c for c in name if c not in bad).strip()
    if not clean:
        return "That folder name has no valid characters."
    if parent:
        base = os.path.expanduser(parent)
    else:
        base = os.path.join(HOME, "Desktop") if os.path.isdir(os.path.join(HOME, "Desktop")) else os.getcwd()
    path = os.path.join(base, clean)
    os.makedirs(path, exist_ok=True)
    return f"Folder created: {path}"


def slugify(text, max_words=4, max_len=40):
    """'print hello world fast' -> 'print_hello_world' (for auto-naming files)."""
    words = re.sub(r"[^a-z0-9 ]", " ", text.lower()).split()
    return ("_".join(words[:max_words])[:max_len]).strip("_") or "file"


def write_file(folder, filename, content):
    """Write text content to folder/filename (folder=None -> Desktop).
    A missing folder name is created on the Desktop. Returns (path, line_count)."""
    desktop = os.path.join(HOME, "Desktop")
    base = desktop if os.path.isdir(desktop) else os.getcwd()
    if not folder:
        folder = base
    else:
        folder = os.path.expanduser(folder)
        if not os.path.isdir(folder):
            folder = os.path.join(base, folder)
        os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content if content.endswith("\n") else content + "\n")
    return path, content.count("\n") + 1


def take_screenshot():
    folder = os.path.join(HOME, "Pictures", "UltronScreenshots")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"shot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    if IS_MAC:
        try:
            subprocess.run(["screencapture", "-x", path], check=True)
            return f"Screenshot saved to {path}"
        except Exception:
            return "The macOS screencapture command failed — grant Screen Recording permission to your terminal app."
    try:
        import pyautogui
    except Exception:
        return "PyAutoGUI is not installed, so I cannot take a screenshot."
    pyautogui.screenshot().save(path)
    return f"Screenshot saved to {path}"


# ---------------------------------------------------------------- media control
def media_control(cmd):
    """cmd in {'playpause', 'next', 'prev'} — controls Spotify, then Apple Music."""
    if IS_MAC:
        apple = {"playpause": "playpause", "next": "next track", "prev": "previous track"}
        for app in ("Spotify", "Music"):
            if _mac_app_exists(app):
                script = f'tell application "{app}" to {apple[cmd]}'
                try:
                    subprocess.run(["osascript", "-e", script], check=True,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return {"playpause": "Toggling music.", "next": "Next track.",
                            "prev": "Previous track."}[cmd]
                except Exception:
                    continue
        return "I could not find Spotify or Apple Music running."
    try:
        import pyautogui
        key = {"playpause": "playpause", "next": "nexttrack", "prev": "prevtrack"}[cmd]
        pyautogui.press(key)
        return {"playpause": "Toggling music.", "next": "Next track.",
                "prev": "Previous track."}[cmd]
    except Exception:
        return "Media control is not available on this machine."


# ---------------------------------------------------------------- calculator
_WORD_OPS = [
    ("divided by", "/"), ("multiplied by", "*"), ("times", "*"),
    ("plus", "+"), ("minus", "-"), ("into", "*"), ("x", "*"),
    ("percent of", "%*"),
]


def _words_to_expr(text):
    expr = " " + text.lower() + " "
    expr = re.sub(r"what(?:'s| is)|calculate|compute|equals?", " ", expr)
    for word, sym in _WORD_OPS:
        expr = expr.replace(" " + word + " ", f" {sym} ")
    # "25 percent of 200" style
    expr = re.sub(r"(\d+(?:\.\d+)?)\s*%\s*\*", r"(\1/100)*", expr.replace(" of ", " %* "))
    return expr.strip()


_ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                  ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
                  ast.Pow, ast.USub, ast.UAdd)


def looks_like_math(text):
    """True if the text is an arithmetic phrase Ultron can evaluate."""
    expr = _words_to_expr(text)
    if not re.search(r"\d", expr):
        return False
    stripped = expr.replace(" ", "")
    return bool(re.fullmatch(r"[\d.+\-*/%()]+", stripped)) and re.search(r"[\d]", stripped)


def calculate(text):
    """Evaluate an arithmetic phrase safely (AST-checked, no eval of names)."""
    expr = _words_to_expr(text)
    expr = expr.replace("^", "**")
    if not looks_like_math(expr):
        return None
    try:
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, _ALLOWED_NODES):
                return None
        result = eval(compile(tree, "<calc>", "eval"))
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 4)
        return f"That is {result:,}."
    except Exception:
        return None


# ---------------------------------------------------------------- weather
def get_weather(city=""):
    """Live weather from wttr.in (no API key needed)."""
    try:
        url = f"https://wttr.in/{quote_plus(city)}?format=j1" if city else "https://wttr.in/?format=j1"
        r = requests.get(url, timeout=15, headers={"User-Agent": "UltronAssistant/1.0"})
        data = r.json()
        cur = data["current_condition"][0]
        place = city if city else data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", "your area")
        desc = cur["weatherDesc"][0]["value"]
        out = (f"In {place} it is {cur['temp_C']} degrees Celsius, {desc.lower()}, "
               f"feels like {cur['FeelsLikeC']}. Humidity is {cur['humidity']} percent, "
               f"and the wind is {cur['windspeedKmph']} kilometres per hour.")
        return out
    except Exception:
        return "I could not fetch the weather — the service may be unreachable."


# ---------------------------------------------------------------- news
def get_news(count=5):
    """Top headlines from Google News (India edition, English)."""
    try:
        r = requests.get("https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
                         timeout=15, headers={"User-Agent": "UltronAssistant/1.0"})
        root = ET.fromstring(r.content)
        titles = [item.find("title").text for item in root.iter("item") if item.find("title") is not None]
        if not titles:
            return "I could not find any headlines right now."
        top = titles[:count]
        out = "Here are the top headlines. " + ". ".join(top)
        return out + ". That is all for now."
    except Exception:
        return "I could not fetch the news — the service may be unreachable."


# ---------------------------------------------------------------- wikipedia
def wikipedia_summary(query, sentences=2):
    """Short factual answer from Wikipedia's API (no extra package needed)."""
    try:
        headers = {"User-Agent": "UltronAssistant/1.0 (personal project)"}
        # resolve the best title first, so 'who is steve jobs' works
        r = requests.get("https://en.wikipedia.org/w/api.php",
                         params={"action": "opensearch", "format": "json", "limit": 1,
                                 "search": query}, headers=headers, timeout=15)
        titles = r.json()[1]
        if not titles:
            return f"I could not find anything about {query}."
        r = requests.get("https://en.wikipedia.org/w/api.php",
                         params={"action": "query", "format": "json", "prop": "extracts",
                                 "exintro": 1, "explaintext": 1, "redirects": 1,
                                 "exsentences": sentences, "titles": titles[0]},
                         headers=headers, timeout=15)
        pages = r.json()["query"]["pages"]
        extract = list(pages.values())[0].get("extract", "")
        if not extract:
            return f"I could not find anything about {query}."
        return extract.strip().replace("\n", " ")
    except Exception:
        return f"I could not reach Wikipedia just now."


# ---------------------------------------------------------------- notes
def note_add(text):
    text = (text or "").strip().lstrip(":").strip()
    if not text:
        return "What should I note down?"
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M] ") + text + "\n")
    return "Noted. Say 'read my notes' whenever you want them."


def notes_read():
    if not os.path.exists(NOTES_FILE):
        return "You have no notes yet. Say 'take a note' followed by the text."
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if not lines:
        return "Your notes are empty."
    out = f"You have {len(lines)} note{'s' if len(lines) > 1 else ''}. "
    if len(lines) > 5:
        out += "The last five are. " + ". ".join(l.split("] ", 1)[-1] for l in lines[-5:])
    else:
        out += ". ".join(l.split("] ", 1)[-1] for l in lines)
    return out + "."


# ---------------------------------------------------------------- mac info
def mac_info():
    if IS_MAC:
        try:
            chip = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                  capture_output=True, text=True, timeout=5).stdout.strip()
        except Exception:
            chip = f"{os.cpu_count()} core processor"
        ver, _, _ = platform.mac_ver()
        mem_gb = None
        try:
            import psutil
            mem_gb = round(psutil.virtual_memory().total / 1024 ** 3)
        except Exception:
            pass
        uptime = None
        try:
            import psutil
            up = time.time() - psutil.boot_time()
            h, m = int(up // 3600), int((up % 3600) // 60)
            uptime = f"{h} hours {m} minutes"
        except Exception:
            pass
        out = f"You are on a Mac running macOS {ver}, with a {chip}"
        if mem_gb:
            out += f" and {mem_gb} gigabytes of memory"
        out += "."
        if uptime:
            out += f" It has been up for {uptime}."
        return out
    return f"This machine runs {platform.system()} {platform.release()}, {os.cpu_count()} cores."


# ---------------------------------------------------------------- misc info
def tell_time():
    return "It is " + datetime.datetime.now().strftime("%I:%M %p") + "."


def tell_date():
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %d %B %Y')}."


def tell_joke():
    return random.choice(JOKES)


def volume(direction, steps=8):
    if IS_MAC:
        # AppleScript volume control — no extra permissions needed
        delta = steps * 5 if direction == "up" else -steps * 5
        script = (f"set volume output volume ((output volume of (get volume settings)) + {delta})")
        try:
            subprocess.run(["osascript", "-e", script], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Volume {direction}."
        except Exception:
            return "I could not change the volume."
    try:
        import pyautogui
    except Exception:
        return "PyAutoGUI is not installed, so I cannot change the volume."
    key = "volumeup" if direction == "up" else "volumedown"
    for _ in range(steps):
        pyautogui.press(key)
    return f"Volume {direction}."


def remember(fact):
    fact = fact.strip()
    if not fact:
        return "What should I remember?"
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M] ") + fact + "\n")
    return "Noted. I will remember that."


def recall():
    if not os.path.exists(MEMORY_FILE):
        return "My memory is empty."
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if not lines:
        return "My memory is empty."
    return "Here is what I remember: " + " ... ".join(lines[-10:])


def system_stats():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.4)
        ram = psutil.virtual_memory().percent
        bat = psutil.sensors_battery()
        out = f"CPU is at {cpu} percent, memory at {ram} percent"
        if bat:
            out += f", and battery is at {bat.percent} percent"
        return out + "."
    except Exception:
        return "Install psutil (pip install psutil) for system stats."


def lock_pc():
    if IS_MAC:
        _run(["pmset", "displaysleepnow"])
    elif IS_WINDOWS:
        _run(["rundll32.exe", "user32.dll,LockWorkStation"])
    else:
        _run(["loginctl", "lock-session"])
    return "Locking the screen."


def power(kind):
    """kind: 'shutdown' or 'restart'. The brain asks for confirmation first."""
    if IS_MAC:
        action = "shut down" if kind == "shutdown" else "restart"
        _run(["osascript", "-e", f"tell application \"System Events\" to {action}"])
    elif IS_WINDOWS:
        _run(["shutdown", "/s", "/f", "/t", "5"] if kind == "shutdown"
             else ["shutdown", "/r", "/f", "/t", "5"])
    else:
        _run(["shutdown", "-h", "now"] if kind == "shutdown" else ["shutdown", "-r", "now"])
