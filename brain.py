"""Ultron brain — decides what to do with a command.

Two layers:
1. A fast offline intent parser for concrete tasks (open app, search,
   create folder, weather, timers, calculator, etc.) so 'open youtube
   and search bgmi' works instantly.
2. Ollama (localhost:11434) as the conversational fallback brain, so any
   question or chat is answered by your local LLM.
"""
import re
import time
import datetime
import threading
import requests
from collections import deque

import actions

SYSTEM_PROMPT = (
    "You are Ultron, a witty, loyal desktop voice assistant for your user. "
    "You speak in short, conversational sentences because your replies are spoken out loud. "
    "Never use markdown, bullet points, emojis or code blocks. "
    "This machine is a Mac - never mention Windows or paths like C:\\Users. "
    "You cannot create, open, write or find files yourself, and you must NEVER claim "
    "you performed an action, saved a file, or state where a file is located. "
    "If the user asks you to make or write a file or folder, tell them the command "
    "phrasing instead, e.g. 'make a folder called demo' or 'write a python program "
    "to print hello world'. For opening apps or websites and searching, tell them to "
    "phrase it as a direct command such as 'open youtube' or 'search bgmi on youtube'. "
    "Stay under 60 words unless asked for detail."
)


# ------------------------------------------------------------------ utils
def _after(text, *separators):
    """Lowercase text after the first matching separator, cleaned up."""
    low = text.lower()
    for sep in separators:
        if sep in low:
            out = low.split(sep, 1)[1]
            return re.sub(r"^(the |a |an |for |to |up |on |called |named )", "", out.strip()).strip(" .?!")
    return ""


def strip_wake(text, wake_words=("hey ultron", "ultron")):
    """Remove a leading wake word: 'hey ultron open youtube' -> 'open youtube'."""
    low = (text or "").lower().strip()
    for w in sorted(wake_words, key=len, reverse=True):
        if low.startswith(w):
            low = low[len(w):].lstrip(" ,.!?")
    return low


def parse_duration(text):
    """'5 minutes and 30 seconds' -> seconds (int). None if unparseable."""
    secs = 0.0
    found = re.findall(r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|minutes?|mins?|seconds?|secs?)", text)
    for num, unit in found:
        n = float(num)
        if unit.startswith("h"):
            secs += n * 3600
        elif unit.startswith("m"):
            secs += n * 60
        else:
            secs += n
    return int(secs) if secs > 0 else None


def _next_time(hour, minute, ampm):
    """The next datetime matching the given clock time (today, else tomorrow)."""
    now = datetime.datetime.now()
    h = hour
    if ampm:
        ampm = ampm.lower()
        if ampm == "pm" and h != 12:
            h += 12
        elif ampm == "am" and h == 12:
            h = 0
    when = now.replace(hour=h, minute=minute, second=0, microsecond=0)
    if when <= now:
        when += datetime.timedelta(days=1)
    return when


# ------------------------------------------------------------------ write files
_WRITE_LANGS = {
    "python": "py", "py": "py", "java": "java", "javascript": "js", "js": "js",
    "cpp": "cpp", "c++": "cpp", "c": "c", "html": "html", "css": "css",
    "sql": "sql", "swift": "swift", "kotlin": "kt", "bash": "sh", "shell": "sh",
}
_CODE_WORDS = ("program", "programme", "script", "code")
_PROSE_WORDS = ("essay", "story", "poem", "email", "letter", "note",
                "paragraph", "summary", "article", "speech")


def parse_write(q):
    """'write a python program to print hello world in myfolder folder',
    'make a sit.py file in template folder' -> ('write_file', spec) or None."""
    spec = {"lang": None, "filename": None, "folder": None,
            "open_in": None, "kind": None, "desc": ""}

    m = re.search(r"^(?:write|type|dictate)\s+(?:me\s+)?(?:an?\s+)?(?:new\s+)?(.+)$", q)
    if not m:
        # 'make a sit.py file ...' — the filename comes first
        m = re.search(r"^(?:make|create)\s+(?:me\s+)?(?:an?\s+)?(?:new\s+)?"
                      r"([\w.\-]+\.(?:py|java|js|txt|html|css|cpp|c|md|json|csv|"
                      r"sh|kt|swift|sql))\s*(?:file|script|program|programme)?\s*(.*)$", q)
        if not m:
            m = re.search(r"^(?:create|make)\s+(?:me\s+)?(?:an?\s+)?(?:new\s+)?"
                          r"(program|programme|script|code|essay|story|poem|email|letter|"
                          r"file|note|article|speech)\b\s*(.*)$", q)
            if not m:
                return None
            rest = (m.group(1) + " " + m.group(2)).strip()
        else:
            spec["filename"] = m.group(1)
            rest = m.group(2).strip()
    else:
        rest = m.group(1)

    # '... in the jarvis folder' (may directly follow the filename)
    fm = re.search(r"(?:^|\s+)in\s+(?:the\s+)?([\w .\-]+?)\s+folder\s*$", rest)
    if fm:
        spec["folder"] = fm.group(1).strip()
        rest = rest[:fm.start()].strip()
    # '... in vscode' -> open the finished file there
    om = re.search(r"(?:^|\s+)in\s+(?:vs\s?code|vscode|visual studio code)\s*$", rest)
    if om:
        spec["open_in"] = "vscode"
        rest = rest[:om.start()].strip()
    # '... called hello.py'
    nm = re.search(r"\s+(?:called|named)\s+([\w.\-]+)", rest)
    if nm:
        spec["filename"] = nm.group(1)
        rest = (rest[:nm.start()] + " " + rest[nm.end():]).strip()

    for w in _CODE_WORDS + _PROSE_WORDS + ("file",):
        if re.search(rf"\b{w}\b", rest):
            spec["kind"] = w
            break

    for lang in sorted(_WRITE_LANGS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(lang)}\b", rest):
            spec["lang"] = "python" if lang == "py" else lang
            rest = re.sub(rf"\b{re.escape(lang)}\b", "", rest, count=1)
            break

    desc = re.sub(r"^(?:a|an|the|new)?\s*(?:new\s+)?(?:" +
                  "|".join(_CODE_WORDS + _PROSE_WORDS + ("file",)) +
                  r")\s*(?:about|to|for|on|that|which|saying|with)?\s*", "", rest.strip())
    desc = (desc or ("" if spec["kind"] else rest)).strip()
    desc = re.sub(r"^(?:about|to|for|on|that|which|saying|with)\s+", "", desc)
    spec["desc"] = desc
    return ("write_file", spec)


# ------------------------------------------------------------------ intents
def parse_intent(query):
    """Return (handler_name, argument) or (None, None) if no intent matches."""
    q = strip_wake(query)

    # greetings
    if q in ("", "hey", "hello", "hi", "hey there", "hello there"):
        return ("greet", "")
    if re.fullmatch(r"(hey |hello |hi )?(ultron)?[.! ]*", q) and q in ("hey ultron", "hello", "hi", "hey", "ultron"):
        return ("greet", "")

    # ---- timers: 'set a timer for 5 minutes'
    m = re.search(r"(?:set|start|make)?\s*(?:a\s+)?timer\s+for\s+(.+)", q)
    if m:
        return ("timer", m.group(1))

    # ---- reminders: 'remind me to X at 5:30 pm' / 'remind me at 5 pm to X'
    m = re.search(r"remind me (?:to|about)?\s+(.*?)\s+(?:at|by)\s+"
                  r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", q)
    if m:
        label = m.group(1).strip(" ,") or "your reminder"
        try:
            when = _next_time(int(m.group(2)), int(m.group(3) or 0), m.group(4))
            return ("reminder", (label, when))
        except ValueError:
            pass
    m = re.search(r"remind me (?:at|by)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s+(?:to|about)?\s+(.+)", q)
    if m:
        try:
            when = _next_time(int(m.group(1)), int(m.group(2) or 0), m.group(3))
            return ("reminder", (m.group(4).strip(), when))
        except ValueError:
            pass

    # ---- media control: 'play music', 'next song' (before play <song> on youtube)
    if re.fullmatch(r"(?:play|resume|pause|stop)(?: the)? music", q):
        return ("media", "playpause")
    if re.fullmatch(r"(?:next|skip)(?: song| track| this)?", q):
        return ("media", "next")
    if re.fullmatch(r"(?:previous|last|back)(?: song| track)?", q):
        return ("media", "prev")

    # ---- weather: 'what's the weather (in mumbai)'
    if "weather" in q or "temperature outside" in q:
        m = re.search(r"(?:in|for|at)\s+([a-z\s]+?)\s*$", q)
        city = m.group(1).strip() if m else ""
        if city in ("like", "today", "now", "right now", "there"):
            city = ""
        return ("weather", city)

    # ---- news: 'tell me the news', 'news headlines'
    if re.search(r"\bnews\b|headlines|what.s happening", q):
        return ("news", 5)

    # ---- notes: 'take a note buy milk' / 'read my notes'
    m = re.search(r"(?:take|make|write)(?:\s+me)?(?:\s+a)?\s+note[:\s]+(.+)", q)
    if m:
        return ("note_add", m.group(1).strip())
    if re.search(r"read (?:my|the) notes|what are my notes|my notes", q):
        return ("notes_read", "")

    # ---- write files: 'write a python program to print hello world'
    wf = parse_write(q)
    if wf:
        return wf

    # ---- translate: 'translate good morning to hindi'
    m = re.search(r"translate\s+(.+?)\s+(?:to|into|in)\s+([a-z ]+)$", q)
    if m:
        return ("translate", (m.group(1).strip(), m.group(2).strip()))

    # ---- quiz: 'quiz me'
    if re.search(r"\bquiz\b|\btrivia\b|ask me a question|test my knowledge", q):
        return ("quiz", "")

    # ---- identity (before 'who is X' wikipedia)
    if re.search(r"(your name|who are you|who made you|who built you)", q):
        return ("identity", "")

    # ---- mac info
    if re.search(r"about (?:my|this) (?:mac|computer|machine)|my mac", q):
        return ("mac_info", "")

    # ---- wikipedia: 'who is X', 'tell me about X', 'wikipedia X'
    m = re.search(r"who (?:is|was|are|were)\s+(.+)", q)
    if m:
        return ("wikipedia", m.group(1).strip(" ?"))
    m = re.search(r"tell me about\s+(.+)", q)
    if m:
        return ("wikipedia", m.group(1).strip(" ?"))
    m = re.search(r"(?:search\s+)?wikipedia\s+(?:for\s+)?(.+)", q)
    if m:
        return ("wikipedia", m.group(1).strip(" ?"))

    # ---- searching / playing
    yt_search = re.search(
        r"(?:search|find|look up|look for)\s+(.*?)\s+(?:on|in)\s+(?:youtube|yt)", q) or \
        re.search(r"(?:on\s+)?(?:youtube|yt)\s*[,:-]?\s*(?:search|find|play)\s+(.*)", q) or \
        re.search(r"search\s+(?:youtube|yt)\s+(?:for\s+)?(.*)", q)
    if yt_search:
        return ("search_youtube", yt_search.group(1).strip())

    if re.search(r"(search|find|look up|look for).*\bon google\b", q):
        return ("search_google", _after(q, "on google", "google for", "google"))
    if q.startswith(("search", "google")) and "wikipedia" not in q:
        return ("search_google", re.sub(r"^(search|google)(\s+for)?", "", q).strip())

    if re.search(r"play\s+(.*?)\s+on\s+(?:youtube|yt)", q) or re.match(r"(play|put on)\s+.+", q):
        m = re.search(r"(?:play|put on)\s+(.*?)(?:\s+on\s+(?:youtube|yt))?$", q)
        if m and m.group(1) not in ("music",):
            return ("play_youtube", m.group(1).strip())

    # ---- open sites / apps
    if re.match(r"(open|launch|start|run)\b", q):
        target = re.sub(r"^(open|launch|start|run)\s+(the\s+|up\s+)?", "", q).strip()
        target = re.sub(r"\s+(app|application|website|site)$", "", target).strip()
        if target in actions.SITES:
            return ("open_site", target)
        # 'open youtube and search bgmi'
        combo = re.match(r"(open\s+)?(.*?)\s+(?:and\s+)?(?:then\s+)?search\s+(.*)", q)
        if combo and combo.group(2) in actions.SITES:
            return ("search_youtube" if "youtube" in combo.group(2) else "search_google", combo.group(3).strip())
        if target in actions.APPS:
            return ("open_app", target)
        if target:
            return ("open_site", target)
        return (None, None)

    # ---- calculator: 'what is 25 times 4', 'calculate 15 percent of 200'
    m = re.match(r"(?:what(?:'s| is| are)|calculate|compute|how much is)\s+(.+)", q)
    if m and actions.looks_like_math(m.group(1)):
        return ("calc", m.group(1))

    # ---- folder creation
    m = re.search(r"(?:make|create)(?:\s+me)?(?:\s+a)?(?:\s+new)?\s+(?:folder|directory)"
                  r"(?:\s+(?:called|named|name))?([:/\\].*| .*)?", q)
    if m:
        arg = m.group(1) or ""
        arg = re.sub(r"^\s*(called|named|name)\s+", "", arg).strip()
        # 'create a folder test on the desktop' -> the folder is 'test'
        arg = re.sub(r"\s+on\s+(?:the\s+|my\s+)?(?:desktop|documents|downloads)\s*$", "", arg).strip()
        return ("create_folder", arg)

    # ---- system
    if "screenshot" in q:
        return ("screenshot", "")
    if re.search(r"\b(volume|sound)\s*(up|louder|raise)", q):
        return ("volume_up", "")
    if re.search(r"\b(volume|sound)\s*(down|lower|quieter)", q):
        return ("volume_down", "")
    if re.search(r"what(?:'s| is) the time|tell me the time|current time", q):
        return ("time", "")
    if re.search(r"what(?:'s| is) (?:the |today'?s )?date|tell me the date|today'?s date", q):
        return ("date", "")
    if "joke" in q:
        return ("joke", "")
    if re.search(r"(system|cpu|ram|battery|memory) (stats|status|usage|info)", q):
        return ("stats", "")
    if re.search(r"lock (the |my )?(pc|computer|system|laptop|screen)", q):
        return ("lock", "")
    if re.search(r"shut ?down (the |my )?(pc|computer|system|laptop)", q):
        return ("shutdown", "")
    if re.search(r"restart (the |my )?(pc|computer|system|laptop)", q):
        return ("restart", "")

    # ---- memory
    if re.search(r"remember (that|this)?\s+", q):
        return ("remember", _after(q, "remember that", "remember this", "remember"))
    if re.search(r"what (do you remember|did i ask you to remember|have i told you)", q):
        return ("recall", "")

    # ---- wikipedia fallback for 'what is X' (time/date already handled above)
    m = re.match(r"what(?:'s| is| are| was)\s+(.+)", q)
    if m:
        return ("wikipedia", m.group(1).strip(" ?"))

    return (None, None)


# ------------------------------------------------------------------ execution
def execute(intent, arg, cfg):
    """Run a matched intent. Returns a spoken reply (str), or a marker tuple
    ('__TIMER__'|'__REMINDER__'|'__TRANSLATE__'|'__QUIZ__', ...) for main.py."""
    name = cfg.get("assistant_name", "Ultron")
    user = cfg.get("user_name", "")

    if intent == "greet":
        hour = time.localtime().tm_hour
        part = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening"
        return f"Good {part}{', ' + user if user else ''}. {name} at your service."
    if intent == "search_youtube":
        return actions.search_youtube(arg)
    if intent == "search_google":
        return actions.search_google(arg)
    if intent == "play_youtube":
        return actions.play_on_youtube(arg)
    if intent == "open_site":
        reply = actions.open_website(arg)
        return reply or f"I don't know the site {arg}, opening a search instead."
    if intent == "open_app":
        reply = actions.open_app(arg)
        return reply or f"Which app should I open?"
    if intent == "create_folder":
        parent = None
        m = re.search(r"\sin\s+([a-zA-Z]:[\\/].*|[~/].*)$", arg)
        if m:
            parent = m.group(1).strip()
            arg = arg[: m.start()].strip()
        else:
            # 'create a folder jarvis in vscode' -> the folder is 'jarvis';
            # a trailing 'in <word>' is not part of the name (real paths matched above)
            arg = re.sub(r"\s+in\s+[\w\s.\-]+$", "", arg).strip()
        return actions.create_folder(arg, parent)
    if intent == "screenshot":
        return actions.take_screenshot()
    if intent == "volume_up":
        return actions.volume("up")
    if intent == "volume_down":
        return actions.volume("down")
    if intent == "time":
        return actions.tell_time()
    if intent == "date":
        return actions.tell_date()
    if intent == "joke":
        return actions.tell_joke()
    if intent == "stats":
        return actions.system_stats()
    if intent == "lock":
        return actions.lock_pc()
    if intent == "remember":
        return actions.remember(arg)
    if intent == "recall":
        return actions.recall()
    if intent == "identity":
        return f"I am {name}, your desktop assistant, running on a local brain. You built me, I obey you."
    if intent == "shutdown":
        return "__ASK_SHUTDOWN__"
    if intent == "restart":
        return "__ASK_RESTART__"

    # ---- new families
    if intent == "timer":
        secs = parse_duration(arg)
        if not secs:
            return "For how long should I set the timer? For example, 'set a timer for 5 minutes'."
        return ("__TIMER__", secs)
    if intent == "reminder":
        label, when = arg
        secs = (when - datetime.datetime.now()).total_seconds()
        return ("__REMINDER__", secs, when, label)
    if intent == "media":
        return actions.media_control(arg)
    if intent == "weather":
        return actions.get_weather(arg)
    if intent == "news":
        return actions.get_news(arg)
    if intent == "calc":
        return actions.calculate(arg) or "I could not work that sum out."
    if intent == "wikipedia":
        return actions.wikipedia_summary(arg)
    if intent == "note_add":
        return actions.note_add(arg)
    if intent == "notes_read":
        return actions.notes_read()
    if intent == "translate":
        text, lang = arg
        return ("__TRANSLATE__", text, lang)
    if intent == "quiz":
        return ("__QUIZ__",)
    if intent == "write_file":
        return ("__WRITE__", arg)
    if intent == "mac_info":
        return actions.mac_info()

    return None


def do_shutdown(kind):
    """kind: 'shutdown' or 'restart' — platform handled inside actions.power."""
    actions.power(kind)


# ------------------------------------------------------------------ ollama
class OllamaChat:
    """Thin wrapper around Ollama's local HTTP API with a rolling memory."""

    def __init__(self, cfg):
        self.url = cfg.get("ollama_url", "http://localhost:11434")
        self.model = cfg.get("ollama_model", "llama3.2")
        self.name = cfg.get("assistant_name", "Ultron")
        self.history = deque(maxlen=12)

    def available(self):
        try:
            r = requests.get(f"{self.url}/api/tags", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def models(self):
        try:
            r = requests.get(f"{self.url}/api/tags", timeout=2)
            return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            return []

    def ask(self, user_text, temperature=0.7, timeout=90):
        self.history.append({"role": "user", "content": user_text})
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + list(self.history),
            "stream": False,
            "options": {"temperature": temperature},
        }
        r = requests.post(f"{self.url}/api/chat", json=payload, timeout=timeout)
        r.raise_for_status()
        reply = r.json()["message"]["content"].strip()
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def ask_once(self, user_text, temperature=0.4, timeout=90):
        """One-off question that does not pollute the conversation memory."""
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": "You are a helpful assistant. "
                         "Reply concisely, plain text only, no quotes or explanation."} ,
                         {"role": "user", "content": user_text}],
            "stream": False,
            "options": {"temperature": temperature},
        }
        r = requests.post(f"{self.url}/api/chat", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
