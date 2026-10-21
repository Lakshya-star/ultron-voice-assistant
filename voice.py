"""Ultron voice — text-to-speech, safe to call from any thread.

On macOS the built-in `say` command is used (best quality, zero setup).
Elsewhere pyttsx3 is used.
"""
import subprocess
import threading

IS_MAC = __import__("sys").platform == "darwin"

_engine = None
_lock = threading.Lock()


def _get_engine(rate, voice_hint):
    global _engine
    if _engine is None:
        import pyttsx3
        _engine = pyttsx3.init()
        _engine.setProperty("rate", rate)
        if voice_hint:
            for v in _engine.getProperty("voices"):
                if voice_hint.lower() in (v.name or "").lower():
                    _engine.setProperty("voice", v.id)
                    break
    return _engine


def speak(text, rate=175, voice_hint=""):
    """Speak text out loud; also prints so the UI/logs can show it."""
    if IS_MAC:
        try:
            cmd = ["say", "-r", str(rate)]
            if voice_hint:
                cmd += ["-v", voice_hint]
            cmd.append(text)
            subprocess.run(cmd, check=False)
            return
        except Exception as e:
            print(f"[voice] macOS say failed ({e}); falling back to pyttsx3")
    try:
        with _lock:
            eng = _get_engine(rate, voice_hint)
            eng.say(text)
            eng.runAndWait()
    except Exception as e:
        print(f"[voice] TTS unavailable: {e}")
