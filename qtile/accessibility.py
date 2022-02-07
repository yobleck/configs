"""
Read contents of widgets on bars on all screens out loud
with text to speech(tts) engine for accessibility
"""

import subprocess
from multiprocessing import Process

from libqtile.log_utils import logger
from libqtile.utils import get_cache_dir


def log_test(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


"""Curently tested options are:
name, install method, help/man
gtts, pip install gtts, https://gtts.readthedocs.io/en/latest/
    gtts requires an audio player like mpv, vlc, mocp, or aplay
    and an internet connection to the google translate servers
    but it sound better than espeak
espeak, pamac install espeak / pacman -S espeak, espeak --help
    espeak requires fewer dependencies, no internet connection
    and is more configurable
    but it sound worse
"""
ENGINE = "espeak"

if ENGINE == "gtts":
    try:
        from gtts import gTTS  # pip install gtts
    except ImportError:
        log_test("could not import gtts. make sure it is installed \
            with \'pip install gtts\'")
        logger.warning(f"Could not import gtts. make sure it is installed")


def get_text(qtile):
    """Primary function to be run from config with
    import tts
    lazy.function(tts.get_text)
    """
    try:
        text = ""
        for i, s in enumerate(qtile.screens):
            text += "Screen number " + str(i) + ". "
            for pos in ["top", "bottom", "left", "right"]:
                if hasattr(s, pos):
                    bar = getattr(s, pos)  # can return None
                    if bar:
                        text += bar.cmd_info()["position"].capitalize() + " bar. "
                        for w in bar.widgets:
                            #text += w.__class__.__name__ + " widget. "
                            text += _parse_widget(w)
        log_test(text)
        """Sending the text to the TTS engine may take awhile so mp
        is to ensure that qtile doesn't freeze during that time
        """
        p = Process(target=_play_audio, args=(text,), daemon=True)
        p.start()
        p.join()
        #log_test(p.is_alive())
        #log_test("finished")
    except Exception as e:
        log_test(e)
        logger.warning(f"TTS failed: {e}")


def _parse_widget(widget):
    """Handles each widget case by case.
    Add new widgets here.
    """
    match widget.__class__.__name__:
        case "Clock":
            return "The time is " + widget.text + ". "
        case "Volume":
            return "Volume is at " + widget.text + ". "
        case "TextBox":
            return widget.text + ". "
        case "CurrentLayout":
            return "The current layout is " + widget.text + ". "
        case "CheckUpdates":
            return widget.text + " updates available. "
        case "Notify":
            if widget.text:
                return "Notification: " + widget.text + ". "
            else:
                return "No new notifications. "
        case "CPU":
            return widget.text + ". "
        case "Memory":
            return widget.text + ". "
        #case "GroupBox":
            #pass  # how to tell what current group is?
        #case "TaskList":
            #pass
        case _:
            return widget.__class__.__name__ + " widget. "


def _play_audio(text):
    """Sends the text to the text to speech engine and plays it.
    The TTS engine can be swapped out for any other engine.
    """
    if ENGINE == "gtts":
        try:
            folder = get_cache_dir()
            gTTS(text).save(folder + "/gtts.mp3")
            # NOTE put audio player here
            subprocess.Popen(["mpv", folder + "/gtts.mp3"])
        except Exception as e:
            log_test(e)
            logger.warning(f"gTTS failed: {e}")

    elif ENGINE == "espeak":
        # NOTE see espeak --help for more options
        subprocess.Popen(["espeak", "-s", "150", "-v", "en-german-5", text])
