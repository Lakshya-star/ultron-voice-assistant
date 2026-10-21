#!/usr/bin/env python3
"""ULTRON — a Siri-style desktop voice assistant with a local Ollama brain.

Usage:
    python main.py            # full experience (mic + UI + Ollama)
    python main.py --check    # self-test: intents, Ollama connectivity, no mic needed

Say "Hey Ultron" (or "Ultron") out loud, or type commands in the box.
Examples: "open youtube", "search bgmi on youtube", "make a folder called projects",
          "open vs code", "take a screenshot", "what's the time", any chat question.
"""
import sys
import re
import random
import threading

import config
import brain
import actions
from voice import speak


class UltronApp:
    def __init__(self):
        self.cfg = config.load_config()
        self.chat = brain.OllamaChat(self.cfg)
        self.ui = None
        self.ears = None
        self.busy = threading.Lock()  # one command at a time
        self.pending_confirm = None   # 'shutdown' | 'restart' while awaiting yes/no
        self.quiz = None              # active quiz question, or None

    # ------------------------------------------------------------------ helpers
    def say(self, text, also_log=True):
        if also_log:
            self.ui.show("ultron", text)
        speak(text,
              rate=self.cfg.get("speech_rate", 175),
              voice_hint=self.cfg.get("tts_voice_hint", ""))

    def status(self, text):
        if self.ui:
            self.ui.set_status(text)

    # ------------------------------------------------------------------ pipeline
    def handle_command(self, raw_text, source="voice"):
        """source='voice' when the text came after the wake word."""
        text = (raw_text or "").strip()
        if not text:
            self.say("I did not catch that.", also_log=True)
            return

        # strip any wake word the user prefixed ("hey ultron open youtube")
        text = brain.strip_wake(text, self.cfg.get("wake_words", ["ultron"]))
        if not text:
            self.say("Yes? I am listening.")
            return

        # waiting for the description of a file we are about to write
        if getattr(self, "_pending_write", None) and text:
            pintent, _ = brain.parse_intent(text.lower())
            if pintent is None:  # plain prose -> use it as the writing brief
                spec, self._pending_write = self._pending_write, None
                spec["desc"] = text
                self._write_file(spec)
                return
            self._pending_write = None  # the user moved on to another command

        if self.ui:
            self.ui.show("you", text)

        # active quiz: every reply is an answer (unless controlling the quiz)
        if self.quiz is not None:
            if re.search(r"(stop|end|quit|exit)( the)? quiz", text):
                self.quiz = None
                self.say("Quiz over. Back to regular service.")
                return
            if re.search(r"next question|another (one|question)", text):
                self._start_quiz()
                return
            self._handle_quiz_answer(text)
            return

        # pending yes/no confirmation for shutdown / restart
        if self.pending_confirm:
            kind = self.pending_confirm
            self.pending_confirm = None
            if re.search(r"\b(yes|yeah|yep|confirm|do it|sure|ok|okay)\b", text):
                self.say(f"Confirmed. {kind}ing in a few seconds. It was a pleasure serving you.")
                brain.do_shutdown(kind)
            else:
                self.say("Cancelled. Staying online.")
            return

        intent, arg = brain.parse_intent(text)
        if intent:
            reply = brain.execute(intent, arg, self.cfg)
            if reply == "__ASK_SHUTDOWN__":
                self.pending_confirm = "shutdown"
                self.say("Do you really want to shut the system down? Say yes to confirm.")
                return
            if reply == "__ASK_RESTART__":
                self.pending_confirm = "restart"
                self.say("Restart the system? Say yes to confirm.")
                return
            if isinstance(reply, tuple) and reply[0] == "__TIMER__":
                secs = reply[1]
                self._schedule_after(secs, "That is your timer. Time is up.")
                self.say(f"Timer set for {self._describe_duration(secs)}. "
                         "I will tell you when it is up.")
                return
            if isinstance(reply, tuple) and reply[0] == "__REMINDER__":
                _, secs, when, label = reply
                self._schedule_after(secs, f"This is your reminder: {label}.")
                self.say(f"Okay. I will remind you to {label} "
                         f"at {when.strftime('%I:%M %p')}.")
                return
            if isinstance(reply, tuple) and reply[0] == "__TRANSLATE__":
                self._ask_translate(reply[1], reply[2])
                return
            if isinstance(reply, tuple) and reply[0] == "__QUIZ__":
                self._start_quiz()
                return
            if isinstance(reply, tuple) and reply[0] == "__WRITE__":
                self._write_file(reply[1])
                return
            self.say(reply)
            return

        # no skill matched -> local LLM
        self._ask_ollama(text)

    def _ask_ollama(self, text):
        self.status("Thinking (local model)...")
        def worker():
            try:
                if not self.chat.available():
                    self.say("My Ollama brain is not reachable. Start Ollama and make sure "
                             f"the model '{self.chat.model}' is pulled. Meanwhile, I can still "
                             "run commands like open, search and create folder.")
                    return
                reply = self.chat.ask(text)
                self.say(reply)
            except Exception as e:
                self.say(f"My brain hit an error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------ timers / translate / quiz
    @staticmethod
    def _describe_duration(secs):
        secs = int(secs)
        h, rem = divmod(secs, 3600)
        m, s = divmod(rem, 60)
        parts = []
        if h:
            parts.append(f"{h} hour" + ("s" if h > 1 else ""))
        if m:
            parts.append(f"{m} minute" + ("s" if m > 1 else ""))
        if s and not h:
            parts.append(f"{s} second" + ("s" if s > 1 else ""))
        return " and ".join(parts) or "a moment"

    def _schedule_after(self, secs, message):
        """Speak a message after a delay, in a background thread."""
        def fire():
            self.say(message)
            if self.ui:
                self.ui.pop_to_front()
        t = threading.Timer(max(int(secs), 1), fire)
        t.daemon = True
        t.start()

    def _ask_translate(self, text, lang):
        self.status(f"Translating to {lang}...")

        def worker():
            try:
                if not self.chat.available():
                    self.say("Translation needs my local model, and Ollama is not "
                             "reachable right now. Start it with 'ollama serve'.")
                    return
                reply = self.chat.ask_once(
                    f"Translate the following text into {lang}. "
                    "Reply ONLY with the translation, no quotes, no explanation:\n" + text)
                self.say(f"In {lang}, that is: {reply}")
            except Exception as e:
                self.say(f"Translation failed: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _write_file(self, spec):
        """Generate content with the local LLM and save it as a real file."""
        desc = (spec.get("desc") or "").strip()
        if not desc:
            self._pending_write = spec  # the next thing said becomes the brief
            self.say("What should I write in it?")
            return
        lang = spec.get("lang")
        kind = spec.get("kind")
        filename = spec.get("filename")
        if filename and "." in filename:  # a named file decides its own type
            ext = filename.rsplit(".", 1)[1].lower()
            prose = ext in ("txt", "md", "csv", "json")
            if not prose and lang is None:
                lang = {"py": "python", "js": "javascript", "cpp": "c++"}.get(ext, ext)
        elif lang:
            ext, prose = brain._WRITE_LANGS[lang], False
        elif kind in brain._PROSE_WORDS or kind in ("file", None):
            ext, prose = "txt", True
        else:  # 'type a code...' with no language -> Python
            ext, lang, prose = "py", "python", False

        filename = filename or (actions.slugify(desc) + "." + ext)
        if "." not in filename:
            filename += "." + ext

        def worker():
            self.status("Writing it now...")
            try:
                if not self.chat.available():
                    self.say("Writing needs my local model. Start Ollama and try again.")
                    return
                if prose:
                    prompt = (f"Write a {kind or 'piece of writing'} on: {desc}. "
                              "Respond with ONLY the text itself — no explanations, "
                              "no markdown, no code fences.")
                else:
                    prompt = (f"Write a complete, working {lang} program that: {desc}. "
                              "Respond with ONLY the raw code — no explanations, "
                              "no markdown fences, no backticks.")
                content = self.chat.ask_once(prompt).strip()
                if content.startswith("```"):  # strip fences if the model added them anyway
                    content = re.sub(r"^```[\w]*\s*", "", content)
                    content = re.sub(r"\s*```$", "", content)
                if not content:
                    self.say("My brain returned nothing — try phrasing it differently.")
                    return
                path, lines = actions.write_file(spec.get("folder"), filename, content)
                self.say(f"Done. I have written {lines} lines to {path}.")
                if spec.get("open_in") == "vscode":
                    actions._run(["code", path])
                    self.say("Opening it in VS Code.")
            except Exception as e:
                self.say(f"Writing failed: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _start_quiz(self):
        def worker():
            self.status("Preparing a quiz question...")
            question, options, answer = None, None, None
            try:
                if self.chat.available():
                    out = self.chat.ask_once(
                        "Generate one multiple-choice question — general knowledge or computer "
                        "science. Write the question, then four options on separate lines, each "
                        "starting with 'a)', 'b)', 'c)', 'd)'. On the very last line write "
                        "'ANSWER: x' where x is the correct letter. Nothing else.")
                    am = re.search(r"ANSWER:\s*([a-d])\b", out, re.IGNORECASE)
                    if am:
                        q_part = out[:am.start()]
                        om = re.search(r"\s*a\)", q_part, re.IGNORECASE)
                        if om:
                            question = q_part[:om.start()].strip().strip('"')
                            options = [l.strip() for l in
                                       q_part[om.start():].strip().splitlines() if l.strip()]
                            answer = am.group(1).lower()
            except Exception:
                question = None
            if not question:
                q, opts, ans = random.choice(actions.QUIZ_BANK)
                question, answer = q, ans
                options = [f"{'abcd'[i]}) {t}" for i, t in enumerate(opts)]
            self.quiz = {"question": question, "options": options, "answer": answer}
            spoken = f"{question}. " + ". ".join(options) + ". Say the letter to answer."
            self.say(spoken)
        threading.Thread(target=worker, daemon=True).start()

    def _handle_quiz_answer(self, text):
        quiz = self.quiz
        letter = None
        m = re.search(r"(?:^|\s)(?:answer(?:\s+is)?\s*)?\(?([a-d])(?:[\)\.\s:]|$)", text)
        if m:
            letter = m.group(1).lower()
        else:
            low = text.lower()
            for i, opt in enumerate(quiz["options"]):
                content = re.sub(r"^[a-d]\)\s*", "", opt).lower()
                if content and content[:14] in low:
                    letter = "abcd"[i]
                    break
        if letter is None:
            self.say("Just say the letter — a, b, c or d.")
            return
        if letter == quiz["answer"]:
            self.say("Correct! Well done. Say 'next question' for another, "
                     "or 'stop quiz' to finish.")
        else:
            correct = quiz["options"]["abcd".index(quiz["answer"])]
            correct = re.sub(r"^[a-d]\)\s*", "", correct)
            self.say(f"Not quite. The correct answer was {correct}. "
                     "Say 'next question' for another, or 'stop quiz' to finish.")

    # ------------------------------------------------------------------ wake flow
    def _wake(self, remainder=None):
        with self.busy:
            if self.ears:
                self.ears.pause()  # silence the wake loop while we capture the command
            if self.ui:
                self.ui.set_awake(True)
            self.status("Awake — listening for your command...")
            try:
                if remainder:
                    # command came with the wake phrase: "hey ultron open youtube"
                    self.handle_command(remainder)
                else:
                    heard = self.ears.listen_command() if self.ears else None
                    self.handle_command(heard)
            finally:
                if self.ears:
                    self.ears.resume()
                if self.ui:
                    self.ui.set_awake(False)
                self.status(f"Say '{self.cfg['wake_words'][0]}' or use the mic / text box.")

    def _wake_async(self, remainder=None):
        threading.Thread(target=self._wake, args=(remainder,), daemon=True).start()

    # ------------------------------------------------------------------ startup
    def start(self):
        from ui import UltronUI
        from ears import Ears

        self.ui = UltronUI(self.cfg,
                           on_text_submit=lambda t: self._wake_async(t),
                           on_mic_press=lambda: self._wake_async(None))
        self.ui.show("sys", f"{self.cfg['assistant_name']} online. "
                            f"Wake word: '{self.cfg['wake_words'][0]}'.")

        try:
            self.ears = Ears(self.cfg, on_status=self.status,
                              on_heard=lambda t: self.ui.show("sys", f'heard: "{t}"'))
            threading.Thread(target=self._init_mic, daemon=True).start()
        except Exception as e:
            self.ui.show("sys", f"Microphone unavailable ({e}). "
                                "You can still type commands.")

        if self.chat.available():
            models = self.chat.models()
            short = ", ".join(models[:4]) or "none"
            self.ui.show("sys", f"Ollama online · model '{self.chat.model}' · available: {short}")
        else:
            self.ui.show("sys", "Ollama not reachable at "
                                f"{self.chat.url} — run `ollama serve` / `ollama pull "
                                f"{self.chat.model}` for conversational answers.")

        self.say(f"{self.cfg['assistant_name']} at your service, "
                 f"{self.cfg.get('user_name', 'sir')}. Say hey "
                 f"{self.cfg['assistant_name'].lower()} whenever you need me.")
        self.ui.run()

    def _init_mic(self):
        try:
            self.ears.calibrate()
            self.ears.start_background(on_wake=self._wake_async)
        except Exception as e:
            self.status(f"Mic init failed: {e}")

    # ------------------------------------------------------------------ mic test
    def run_mic_test(self):
        """Record 3 seconds and diagnose microphone + speech recognition."""
        import math
        import array
        import speech_recognition as sr

        print("=== Ultron microphone test ===\n")
        print("Input devices visible to Python:")
        try:
            for i, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"  [{i}] {name}")
        except Exception as e:
            print(f"  (could not list devices: {e})")

        from ears import Ears
        e = Ears(self.cfg)
        try:
            e.calibrate()
        except Exception as ex:
            print(f"\nCould not open the microphone: {ex}")
            print("On a Mac this usually means mic permission was refused.")
            return

        print("\nSay something for about 3 seconds (e.g. 'hello ultron')...")
        with e._get_mic() as source:
            audio = e.recognizer.listen(source, timeout=8, phrase_time_limit=3)

        # how loud was the recording? (RMS level in dB)
        samples = array.array('h', audio.get_raw_data())
        rms = math.sqrt(sum(float(s) * s for s in samples) / max(len(samples), 1))
        db = 20 * math.log10(rms + 1e-9)
        print(f"\nAverage input level: {db:.1f} dB (silence is around -90)")
        if db < -55:
            print("The microphone recorded silence. On macOS this almost always means")
            print("mic permission is missing: System Settings > Privacy & Security >")
            print("Microphone > turn ON for Terminal, then QUIT Terminal (Cmd+Q) and")
            print("reopen it and run this test again.")
            return

        print("Recognizing with Google (needs internet)...")
        try:
            heard = e.recognizer.recognize_google(audio, language="en-in")
            print(f'Heard: "{heard}"')
            print("\nMicrophone and speech recognition are working. If wake-up still")
            print("fails, speak the wake word clearly: 'Hey Ultron'.")
        except sr.UnknownValueError:
            print("Your voice was heard but not recognized — speak a little closer")
            print("and louder, and reduce background noise, then try again.")
        except sr.RequestError as ex:
            print(f"Could not reach the Google speech service (internet problem?): {ex}")

    # ------------------------------------------------------------------ self-test
    def run_self_test(self):
        print("=== Ultron self-test ===\n1) Intent parser")
        cases = [
            ("open youtube", ("open_site", "youtube")),
            ("hey ultron open vs code", ("open_app", "vs code")),
            ("open youtube and search bgmi", ("search_youtube", "bgmi")),
            ("search bgmi on youtube", ("search_youtube", "bgmi")),
            ("make a folder called projects", ("create_folder", "projects")),
            ("create folder d:/work/demo", ("create_folder", "d:/work/demo")),
            ("what's the time", ("time", "")),
            ("take a screenshot", ("screenshot", "")),
            ("remember that my exam is on monday", ("remember", "my exam is on monday")),
            ("tell me a joke", ("joke", "")),
            ("set a timer for 5 minutes", ("timer", "5 minutes")),
            ("set a timer for 1 hour and 30 seconds", ("timer", "1 hour and 30 seconds")),
            ("what's the weather in mumbai", ("weather", "mumbai")),
            ("what's the weather", ("weather", "")),
            ("tell me the news", ("news", 5)),
            ("what is 25 times 4", ("calc", "25 times 4")),
            ("calculate 15 percent of 200", ("calc", "15 percent of 200")),
            ("who is alan turing", ("wikipedia", "alan turing")),
            ("tell me about machine learning", ("wikipedia", "machine learning")),
            ("take a note buy milk tomorrow", ("note_add", "buy milk tomorrow")),
            ("read my notes", ("notes_read", "")),
            ("translate good morning to hindi", ("translate", ("good morning", "hindi"))),
            ("quiz me", ("quiz", "")),
            ("play music", ("media", "playpause")),
            ("pause music", ("media", "playpause")),
            ("next song", ("media", "next")),
            ("previous track", ("media", "prev")),
            ("tell me about my mac", ("mac_info", "")),
            ("play believer on youtube", ("play_youtube", "believer")),
            ("what is the time", ("time", "")),
            ("open netflix", ("open_site", "netflix")),
        ]
        ok = True
        for text, expected in cases:
            got = brain.parse_intent(text)
            flag = "OK " if got == expected else "FAIL"
            if got != expected:
                ok = False
            print(f"  [{flag}] {text!r:45} -> {got}")

        # reminders carry a computed datetime — check intent and label only
        intent, arg = brain.parse_intent("remind me to submit the assignment at 5:30 pm")
        good = intent == "reminder" and arg[0] == "submit the assignment"
        ok = ok and good
        print(f"  [{'OK ' if good else 'FAIL'}] 'remind me to submit the assignment at 5:30 pm' "
              f"-> ('reminder', ({arg[0]!r}, <datetime>))")

        print("\n2) Writing")
        for phrase, want in [
            ("write a python program to print hello world",
             {"lang": "python", "desc": "print hello world"}),
            ("write an essay on pollution",
             {"kind": "essay", "desc": "pollution"}),
            ("type a code to print hello world in jarvis folder",
             {"folder": "jarvis", "desc": "print hello world"}),
            ("make a program called demo.py to add two numbers",
             {"filename": "demo.py", "desc": "add two numbers"}),
            ("write a java program to print hello world in vscode",
             {"lang": "java", "open_in": "vscode", "desc": "print hello world"}),
            ("make a sit.py file to print hello world",
             {"filename": "sit.py", "desc": "print hello world"}),
            ("make an iron.py file in template folder",
             {"filename": "iron.py", "folder": "template"}),
            ("make a new file",
             {"kind": "file", "desc": ""}),
            ("create a file called notes.txt with my homework plan",
             {"filename": "notes.txt", "desc": "my homework plan"}),
        ]:
            wintent, spec = brain.parse_intent(phrase)
            good = wintent == "write_file" and isinstance(spec, dict) and \
                all(spec.get(k) == v for k, v in want.items())
            ok = ok and good
            print(f"  [{'OK ' if good else 'FAIL'}] {phrase!r} -> {spec}")

        # folder names must not swallow a trailing 'in vscode'
        saved = actions.create_folder
        captured = {}
        def fake_create(name, parent=None):
            captured["name"], captured["parent"] = name, parent
            return "ok"
        actions.create_folder = fake_create
        brain.execute("create_folder", "jarvis in vscode", {})
        actions.create_folder = saved
        good = captured["name"] == "jarvis"
        ok = ok and good
        print(f"  [{'OK ' if good else 'FAIL'}] 'create a folder jarvis in vscode' "
              f"-> folder name {captured.get('name')!r}")

        print("\n3) Calculator")
        for expr in ["what is 25 times 4", "calculate 15 percent of 200",
                     "what is 100 divided by 7"]:
            print("  ", repr(expr), "->", actions.calculate(
                brain.parse_intent(expr)[1]))
        if actions.calculate("what is 25 times 4") != "That is 100.":
            ok = False
            print("   CALC CHECK FAILED")

        print("\n4) Folder creation")
        print("  ", actions.create_folder("__ultron_test__",
                                          parent="/tmp" if sys.platform != "win32" else None))

        print("\n5) Ollama")
        if self.chat.available():
            print("   Ollama reachable. Models:", self.chat.models())
        else:
            print(f"   Ollama NOT reachable at {self.chat.url} (that's fine in this sandbox; "
                  "on your PC run: ollama serve && ollama pull " + self.chat.model + ")")
        print("\nSelf-test " + ("PASSED" if ok else "FINISHED WITH FAILURES"))
        return ok


def main():
    app = UltronApp()
    if "--mic-test" in sys.argv:
        app.run_mic_test()
        sys.exit(0)
    if "--check" in sys.argv:
        sys.exit(0 if app.run_self_test() else 1)
    app.start()


if __name__ == "__main__":
    main()
