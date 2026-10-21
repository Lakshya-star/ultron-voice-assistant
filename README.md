# ULTRON — Desktop Voice Assistant (macOS edition)

A Siri-style voice assistant for your Mac with a glowing blue HUD, wake-word
detection ("Hey Ultron"), and a **fully local AI brain powered by Ollama**.
Built macOS-first: it uses your Mac's native `say` voice, `open -a` app
launching, `screencapture` screenshots, and AppleScript volume/power control.

---

## Features

| Say this… | Ultron does this |
|---|---|
| "Hey Ultron" | The panel pops to the front and starts listening (like Siri) |
| "Open YouTube" / "Open Google, GitHub, WhatsApp, Spotify…" | Opens the site in your browser |
| "Open YouTube **and search BGMI**" / "Search BGMI on YouTube" | Opens YouTube with results for BGMI |
| "Play Believer on YouTube" | Opens YouTube results for the song |
| "Search machine learning on Google" | Google search |
| "Open VS Code" / "Open Notepad (TextEdit), Calculator, Terminal, Paint (Preview), Chrome…" | Launches the app |
| "Make a folder called projects" / "Create folder ~/Documents/demo" | Creates the folder (Desktop or given path) |
| "Take a screenshot" | Saves to Pictures/UltronScreenshots (uses macOS `screencapture`) |
| "What's the time / date" | Tells you |
| "Volume up / volume down" | AppleScript volume control |
| "Tell me a joke" | A programmer joke, of course |
| "Remember that my exam is on Monday" | Saves to memory — "What do you remember?" recalls it |
| "System stats" | CPU / RAM / battery report |
| "Lock my Mac" | Puts the display to sleep |
| "Shutdown my Mac" / "Restart my Mac" | Asks "say yes to confirm" first |
| Anything else ("Explain quantum computing", "Write a poem about BGMI") | Answered by your local Ollama model |

---

## Setup on macOS (5 minutes)

### 1. Prerequisites

- Python 3.9+ (`python3 --version`). If missing: `brew install python` (tkinter is included).
- Ollama (you already have it):

```bash
ollama pull llama3.2
ollama serve      # if it isn't already running from the menu-bar app
```

Any model works — `llama3.2` is small and fast; use `llama3.1`, `qwen2.5`,
`mistral`, etc. if you prefer.

### 2. Install dependencies

Open Terminal **inside this folder**:

```bash
brew install portaudio        # needed by PyAudio for the microphone
python3 -m pip install -r requirements.txt
```

### 3. Grant macOS permissions (one-time, important!)

The terminal app you run Ultron from needs these in
**System Settings → Privacy & Security**:

- **Microphone** → enable for Terminal (or VS Code if you run it from there)
- **Screen Recording** → enable for the same app, for "take a screenshot"

### 4. Make VS Code launchable by voice (one-time)

Ultron tries the `code` command first, then `open -a "Visual Studio Code"`.
For the `code` command: open VS Code → `Cmd+Shift+P` →
**Shell Command: Install 'code' command in PATH**.

### 5. Run Ultron

```bash
python3 main.py
```

You'll see the blue Ultron panel. Say **"Hey Ultron"**, wait for the glow,
then say a command. You can also click **🎤 MIC** or just type in the box.

---

## Configuration — `config.json`

Created automatically next to the code; edit and restart:

```json
{
  "assistant_name": "Ultron",
  "user_name": "Lakshya",
  "wake_words": ["hey ultron", "ultron"],
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama3.2",
  "speech_rate": 175,
  "tts_voice_hint": "",
  "listen_timeout": 6
}
```

- Change `wake_words` to e.g. `["hey jarvis", "jarvis"]` anytime.
- `tts_voice_hint` on Mac: any voice from `say -v ?` (e.g. `"Daniel"`, `"Rishi"`).
- On Mac the voice is the native `say` command — no pyttsx3 needed.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Speech service unreachable" | Speech recognition needs internet; check connection |
| Ultron never wakes up | Privacy & Security → Microphone → allow your terminal app |
| Screenshots say permission failed | Privacy & Security → Screen Recording → allow your terminal app, then restart it |
| "Ollama brain is not reachable" | Run `ollama serve`; confirm model pulled: `ollama list` |
| VS Code won't open | Do step 4 above, or check the app is in /Applications |
| Assistant too slow to answer | Use a smaller model, e.g. `ollama pull qwen2.5:0.5b`, set it in config.json |

## Project layout

```
main.py       — entry point: wake-word flow + command pipeline
brain.py      — intent parser (fast skills) + Ollama chat fallback
actions.py    — the task engine: apps, sites, folders, screenshots, memory…
ears.py       — microphone + wake-word listening (SpeechRecognition)
voice.py      — text-to-speech (macOS `say`, pyttsx3 elsewhere)
ui.py         — the blue HUD window (Tkinter)
config.py     — settings loader
```

## Run a self-test (no mic needed)

```bash
python3 main.py --check
```
