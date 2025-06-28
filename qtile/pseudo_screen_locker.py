"""Pseudo screen locker that uses Qtile a popup window
Installation:
Put this file in the same folder as your config file (~/.config/qtile/)
In the config.py file put:
import pseudo_screen_locker as psl
sc = psl.PseudoScreenLocker(
    image_paths=["/path/to/image.png"],  # make sure this is a string in a list
    font="sans", font_size=24, foreground="#00aa00", background="#000000aa", text_pos=(1100, 780),
    key_bind=(["mod4"], "l"),
    update_interval=1.0)
# or you can put `Key([mod], "l", lazy.function(sc.lock), desc="lock screen"),` in your config keys list
"""

from datetime import datetime
from itertools import cycle
import os
import threading
# TODO installation instructions
import time
from typing import Any

from cairocffi import ImageSurface
from libqtile import hook, images, lazy, qtile, utils
from libqtile.config import Key
from libqtile.popup import Popup


def log_test(i: Any):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


class PseudoScreenLocker:  # TODO turn this into a configurable
    singleton = None

    def __init__(
            self, image_paths: list[str] = [""], background: str = "#000000ff", foreground: str = "#ffffff",
            image_size: tuple[int, int] = (1080, 1920),  # TODO implement
            font: str = "sans", font_size: int = 16,
            fake_password: str = "", text_pos: tuple = (0, 0),
            key_bind: tuple[list[str], str] | None = None,
            update_interval: float = 1) -> None:

        PseudoScreenLocker.singleton = self
        self.popups: list[Popup] = []  # List of popup windows. One per screen
        self.background: str = background
        self._backup_key_binds: dict = {}
        if key_bind:
            k = Key(*key_bind, lazy.lazy.function(self.lock), desc="lock screen")
            qtile.keys_map[qtile.core.lookup_key(k)] = k
            qtile.config.keys.append(k)
            qtile.core.grab_key(k)

        # text related vars
        self.foreground: str = foreground
        self.font: str = font
        self.font_size: int = font_size
        self._time: str = datetime.now().isoformat()
        self.update_interval = update_interval
        self.pass_prompt: str = "\nFake Password:"
        self.fake_password: str = fake_password
        self._user_input: str = ""
        self.text_pos: tuple = text_pos

        # image related vars
        self.image_paths: list[str] = image_paths
        self.image_size: tuple[int, int] = image_size
        # List of all images to be looped through.
        # Not to be confused with different images being displayed on different screens
        self.surfaces: list[ImageSurface] = []  # type images._SurfaceInfo?
        self.loop: cycle | None = None
        self._temp_loop_counter: int = 0

        self.timer: _RepeatTimer | None = None

        # remove lock file possibly left over from crash or improper shutdown
        if os.path.isfile(utils.get_cache_dir() + "/psl_lock"):
            os.remove(utils.get_cache_dir() + "/psl_lock")

    def lock(self, not_accessed_qtile) -> None:
        log_test(f"{time.ctime()} locking")
        if not self.popups:
            with open(utils.get_cache_dir() + "/psl_lock", "w") as f:
                # create lock file
                # log_test(utils.get_cache_dir())
                f.write("p")
                # pass
            for x, scrn in enumerate(qtile.screens):
                self.popups.append(Popup(
                    qtile, background=self.background, foreground=self.foreground,
                    x=scrn.x, y=scrn.y,
                    width=scrn.width, height=scrn.height,
                    font=self.font, font_size=self.font_size, border="#ff00ff", border_width=0, opacity=1, wrap=True))

                self.popups[x].win.process_button_click = self._click_popup
                self.popups[x].win.process_key_press = self._key_press
                self.popups[x].win.process_pointer_enter = self._enter_window

                self.popups[x].unhide()

            self._actually_draw()
            try:
                self.timer = _RepeatTimer(self.update_interval, self._actually_draw)
                self.timer.start()
            except Exception as e:
                log_test(e)
            self._backup_key_binds = qtile.keys_map  # TODO pass media keys option
            # log_test(self._backup_key_binds)
            qtile.keys_map = {}

    def _actually_draw(self, update_image: bool = True) -> None:
        # NOTE this function cant update all screens at the same time so they will appear out of sync
        # threading or multiprocessing?
        self._update_time()
        if self.surfaces and update_image and self.loop:  # don't update background image for typing updates
            # only update image once per update_interval so screens are the same
            self._temp_loop_counter = next(self.loop)

        for p in self.popups:
            p.clear()
            # draw image
            if self.surfaces:
                # pass
                p.draw_image(self.surfaces[self._temp_loop_counter], 0, 0)

            # draw text
            p.text = self._time + self.pass_prompt + len(self._user_input) * "*"
            p.draw_text(x=self.text_pos[0], y=self.text_pos[1])
            p.draw()

    def load_images(self) -> None:
        # NOTE this takes a really long time with lots of images.
        img_thread = threading.Thread(target=self._images_to_surfaces)
        img_thread.start()  # for now we run in a separate thread to try and de-prioritize loading
        # img_thread.join()

    def _images_to_surfaces(self) -> None:
        time.sleep(0.1)  # de-prioritize thread?
        for img in self.image_paths:
            if os.path.exists(os.path.expanduser(img)):
                i_temp = images.Img.from_path(img)
                # TODO resize by width or height or only use SVG, or let user decide?
                i_temp.resize(height=self.image_size[0], width=self.image_size[1])
                surf, _ = images.get_cairo_surface(i_temp.bytes_img, i_temp.width, i_temp.height)
                self.surfaces.append(surf)
            else:
                log_test(f"{datetime.now()} invalid image path: {img}")
        self.loop = cycle(range(len(self.surfaces)))

    def _close(self) -> None:
        """Close windows and clear variables"""
        qtile.keys_map = self._backup_key_binds  # BUG sometimes doesn't work. WHY? screen still off? dpms
        qtile.grab_keys()  # does this fix the bug above?
        try:
            if self.timer:  # just in case the function is run while already closed
                self.timer.cancel()  # BUG breaks if lock immediately after qtile loads
            self.timer = None
        except Exception as e:
            log_test(e)
        for p in self.popups:
            p.hide()
            p.kill()
        self.popups = []
        self._user_input = ""
        os.remove(utils.get_cache_dir() + "/psl_lock")
        # TODO refocus previous window

    def _click_popup(self, x, y, button) -> None:  # TODO remove this
        if button == 3:
            self._close()

    def _key_press(self, keycode) -> None:
        """Handle key press"""
        # log_test(f"s_l: key press: {keycode}")
        if keycode == 65293:  # enter
            if self._user_input == self.fake_password:
                self._close()
                return
            else:
                self._user_input = ""
        elif keycode == 65288:  # backspace
            self._user_input = self._user_input[:-1]  # pop() faster?
        elif 31 < keycode < 3900:  # most actually type able characters in this range?
            self._user_input += chr(keycode)
        self._actually_draw(update_image=False)

    @staticmethod
    @hook.subscribe.user("psl_lock_hook")
    def fire_hook():
        """qtile cmd-obj -o cmd -f fire_user_hook -a 'custom_hook_name'"""
        # NOTE This 'singleton' is required to bypass the hook not being able to pass self to the function
        PseudoScreenLocker.singleton.lock(qtile)

    def _enter_window(self, *args) -> None:
        """Handle mouse enter window to focus."""
        self.popups[0].win.focus(warp=False)

    def _update_time(self) -> None:
        self._time = datetime.now().isoformat()


class _RepeatTimer(threading.Timer):
    def run(self) -> None:
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
