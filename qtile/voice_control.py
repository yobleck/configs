import multiprocessing as mp
import subprocess
import string
import time
from typing import Any

from libqtile import bar, qtile
from libqtile.widget import base


def log_test(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


class VoiceControl(base._TextBox):
    """Voice activated commands prototype
    https://github.com/ggerganov/whisper.cpp
    TODO should just call a bash script instead of multiprocessing
    """

    defaults = [
        ("record_len", 3, "Duration of audio recording. Temp till figure out auto cut off at quiet"),
        ("cache_path", "/home/yobleck/.cache/qtile/", "Path to qtile cache folder"),
        ("whisper_path", "/home/yobleck/ai/whisper/whisper.cpp/", "Path to whisper.cpp folder"),
        ("audio_device", "pulse", "Device arecord(1) gets its audio from. Use arecord --list-pcms"),
        ("v_cmds",
         {"hey computer open a terminal": "kitty",
          "hey computer open a browser": "firefox",
          "hey computer open a file browser": "dolphin",
          "hey computer open youtube": "firefox https://www.youtube.com/feed/channels"},
         "Dict of voice commands and their actions. cmds should be all lowercase"
         ),
    ]  # type: list[tuple[str, Any, str]]

    def __init__(self, text=" ", width=bar.CALCULATED, **config):
        base._TextBox.__init__(self, text=text, width=width, **config)
        self.add_defaults(VoiceControl.defaults)
        self.status_thread = None
        self.text: str = "VC"

    def _configure(self, qtile, bar):
        base._TextBox._configure(self, qtile, bar)
        self.add_callbacks({"Button1": self.activate})

    def activate(self):
        if self.status_thread is None or not self.status_thread.is_alive():  # stops multiple instances
            try:
                rec = mp.Process(target=self._record)
                rec.daemon = True
                rec.start()

                whis = mp.Process(target=self._whisper)
                whis.daemon = True
                whis.start()

                self.status_thread = mp.Process(target=self._run)
                self.status_thread.daemon = True
                self.status_thread.start()
                # TODO clear out zombie threads
            except Exception as e:
                log_test(f"voice control error: {e}")

    def _record(self):
        """Record audio"""
        subprocess.run(f"arecord -D {self.audio_device} -d {self.record_len} -f S16_LE -r 16000 {self.cache_path}voice_control.wav",
                       shell=True)

    def _whisper(self):
        """Convert audio to text with whisper.cpp program"""
        time.sleep(self.record_len)
        subprocess.run(f"./main -t 8 -nt -otxt -of {self.cache_path}voice_control -f {self.cache_path}voice_control.wav",  # ~/test.wav
                       cwd=self.whisper_path, shell=True)

    def _run(self):
        """Process text and attempt to run command"""
        time.sleep(self.record_len + 2)
        with open("/home/yobleck/.cache/qtile/voice_control.txt", "r") as f:
            # strip leading/trailing newlines, spaces, and punctuation
            txt = f.readline().strip("\n").strip().translate(str.maketrans("", "", string.punctuation)).lower()
            log_test(f"voice control output: {txt}")
        if txt == "blankaudio":
            return
        for key in self.v_cmds.keys():
            # log_test(f"key: {key}")
            if txt in key:
                # This is where the command will be run
                log_test(f"run cmd: {self.v_cmds[txt]}")
                qtile.cmd_spawn(self.v_cmds[txt])
                return
        log_test("no command found")
