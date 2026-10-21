"""Ultron configuration — edit config.json to customise, this file holds defaults."""
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULTS = {
    "assistant_name": "Ultron",
    "user_name": "Lakshya",
    "wake_words": ["hey ultron", "ultron"],
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3.2",
    "speech_rate": 175,
    "tts_voice_hint": "",       # substring matched against installed voices, e.g. "David" or "Zira"
    "listen_timeout": 6,       # seconds to wait for a command after the wake word
    "ambient_calibration": 1.2 # seconds of ambient-noise calibration on startup
}


def load_config():
    cfg = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception as e:
            print(f"[config] could not read config.json ({e}); using defaults")
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
