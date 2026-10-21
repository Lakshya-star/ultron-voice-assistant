"""Ultron ears — microphone listening and wake-word detection.

Two separate microphone objects are used: one held by the background
wake-word loop, one for capturing commands. (Opening the same
sr.Microphone object in two context managers at once raises an
AssertionError on macOS.)

Everything the recognizer hears is reported through on_heard so the UI
can show exactly what Google understood — invaluable for debugging.
"""
import re
import threading
import traceback

import speech_recognition as sr


def _levenshtein(a, b):
    """Small edit-distance helper for forgiving wake-word matching."""
    if abs(len(a) - len(b)) > 3:
        return 99
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1,        # deletion
                         cur[j - 1] + 1,     # insertion
                         prev[j - 1] + (ca != cb))  # substitution
        prev = cur
    return prev[-1]


class Ears:
    def __init__(self, cfg, on_status=None, on_heard=None):
        self.cfg = cfg
        self.wake_words = [w.lower() for w in cfg.get("wake_words", ["ultron"])]
        self.on_status = on_status or (lambda txt: None)
        self.on_heard = on_heard or (lambda txt: None)
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1
        self.recognizer.energy_threshold = 200  # auto-tuned by ambient calibration
        self._stop = threading.Event()
        self._paused = threading.Event()  # set while a command is being captured
        self.cmd_mic = None  # one-shot command listening
        self.bg_mic = None   # background wake-word loop

    # ------------------------------------------------------------------ devices
    def _get_mic(self):
        if self.cmd_mic is None:
            self.cmd_mic = sr.Microphone()
        return self.cmd_mic

    def calibrate(self):
        with self._get_mic() as source:
            self.recognizer.adjust_for_ambient_noise(
                source, duration=self.cfg.get("ambient_calibration", 1.2))
        self.on_status("Microphone calibrated.")

    # ------------------------------------------------------------------ one-shot
    def _hear_once(self, timeout, phrase_time_limit=10):
        """Record + recognise one utterance. Returns lowercase text or None."""
        with self._get_mic() as source:
            audio = self.recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        try:
            text = self.recognizer.recognize_google(audio, language="en-in")
            text = text.lower().strip()
            if text:
                self.on_heard(text)
            return text
        except sr.UnknownValueError:
            self.on_status("I picked up sound but couldn't make out words.")
            return None
        except sr.RequestError:
            self.on_status("Speech service unreachable — check internet.")
            return None

    def listen_command(self):
        """Listen for one command (after the wake word / mic button)."""
        try:
            self.on_status("Listening...")
            return self._hear_once(timeout=self.cfg.get("listen_timeout", 6))
        except sr.WaitTimeoutError:
            self.on_status("I didn't hear anything.")
            return None
        except OSError:
            self.on_status("No microphone found.")
            return None

    # ------------------------------------------------------------------ wake word
    def _contains_wake(self, text):
        """Forgiving wake-word match: exact, compact, or close-spelling."""
        low = " ".join(text.lower().split())
        compact = low.replace(" ", "")
        for w in self.wake_words:
            if w in low or w.replace(" ", "") in compact:
                return True
        # 'Ultron' is an unusual word — Google often returns these spellings:
        variants = ("ul tron", "all tron", "al tron", "ol tron", "alltran",
                    "altran", "oltran", "ultrun", "ultrone")
        if any(v in low for v in variants):
            return True
        # last resort: fuzzy match on the compact text vs the wake word
        target = self.wake_words[0].replace(" ", "")
        if _levenshtein(compact[-(len(target) + 2):], target) <= 2:
            return True
        return False

    def _strip_wake(self, text):
        low = text.lower()
        for w in sorted(self.wake_words, key=len, reverse=True):
            if low.startswith(w):
                rest = low[len(w):].lstrip(" ,.!?")
                if rest:
                    return rest
                return None
            if w in low:
                return low.split(w, 1)[1].strip(" ,.!?") or None
        return None

    def pause(self):
        """Suspend the background wake loop (used while capturing a command)."""
        self._paused.set()

    def resume(self):
        self._paused.clear()

    def start_background(self, on_wake):
        """Continuously listen; when the wake word is heard, run on_wake(remainder).

        If the wake phrase already contains the command ('hey ultron open youtube'),
        the remainder is passed straight through.
        """
        def loop():
            self.on_status(f"Say '{self.wake_words[0]}'...")
            while not self._stop.is_set():
                if self._paused.is_set():
                    self._stop.wait(0.25)
                    continue
                try:
                    if self.bg_mic is None:
                        self.bg_mic = sr.Microphone()
                    with self.bg_mic as source:
                        audio = self.recognizer.listen(
                            source, timeout=None, phrase_time_limit=12)
                    text = None
                    try:
                        text = self.recognizer.recognize_google(audio, language="en-in").lower()
                    except sr.RequestError:
                        self.on_status("Speech service unreachable — check internet.")
                        self._stop.wait(3)
                    except sr.UnknownValueError:
                        continue
                    if text:
                        self.on_heard(text)  # show in the panel what was understood
                    if text and self._contains_wake(text):
                        self.on_status("Wake word detected!")
                        on_wake(self._strip_wake(text))
                except OSError:
                    self.on_status("No microphone found — use the text box or mic button.")
                    self._stop.wait(5)
                except Exception:
                    traceback.print_exc()
                    self._stop.wait(1)

        threading.Thread(target=loop, daemon=True).start()

    def stop(self):
        self._stop.set()


def clean_query(text):
    """Normalise a raw transcript for the brain."""
    return re.sub(r"\s+", " ", text or "").strip().strip(".,!?")
