"""Pseudo screen locker that uses Qtile a popup window"""

from datetime import datetime
from itertools import cycle
import os
import threading
# TODO installation instructions
import time
from typing import Any

from libqtile import qtile, images
from libqtile.popup import Popup


def log_test(i: Any):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


# TODO stop qtile keyboard shortcuts from working while window is open? or always force on top
# qtile.conn.conn.core.GrabKeyboard() /usr/lib/python3.11/site-packages/xcffib/xproto.py
class pseudo_screen_locker:  # TODO turn this into an extension?
    def __init__(
            self, image_paths: list[str] = [""], background: str = "#000000ff", foreground: str = "#ffffff",
            image_size: tuple[int, int] = (1080, 1920),  # TODO implement
            font: str = "sans", font_size: int = 16,
            fake_password: str = "", text_pos: tuple = (0, 0),
            update_interval: float = 1) -> None:

        self.background: str = background
        self.foreground: str = foreground
        self.font: str = font
        self.font_size: int = font_size

        # text related vars
        self._time: str = datetime.now().isoformat()
        self.update_interval = update_interval
        self.pass_prompt: str = "\nFake Password:"
        self.fake_password: str = fake_password
        self._user_input: str = ""
        self.text_pos: tuple = text_pos

        # image related vars
        self.image_paths: list[str] = image_paths
        self.popups: list[Popup] = []  # List of popup windows. One per screen
        # List of all images to be looped through.
        # Not to be confused with different images being displayed on different screens
        self.surfaces: list = []  # type images._SurfaceInfo?
        self.loop: cycle | None = None
        self.timer: _RepeatTimer | None = None

    def lock(self, unused_qtile) -> None:
        if not self.popups:
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

    def _actually_draw(self) -> None:
        # NOTE this function cant update all screens at the same time so they will appear out of sync
        # threading or multiprocessing?
        self._update_time()
        temp_loop_counter: int = 0
        if self.surfaces:
            temp_loop_counter = next(self.loop)  # once per draw cycle so image is the same on every screen
        for p in self.popups:
            p.clear()
            # draw image
            if self.surfaces:
                # pass
                p.draw_image(self.surfaces[temp_loop_counter], 0, 0)

            # draw text
            p.text = self._time + self.pass_prompt + self._user_input  # TODO replace user_input with len(user_input) * "*"
            p.draw_text(x=self.text_pos[0], y=self.text_pos[1])
            p.draw()

    def load_images(self) -> None:
        # NOTE this takes a really long time with lots of images. try caching results in pickle?
        img_thread = threading.Thread(target=self._images_to_surfaces)
        img_thread.start()  # for now we run in a separate thread to try and deprioritize loading
        # img_thread.join()

    def _images_to_surfaces(self) -> None:
        time.sleep(0.1)  # deprioritize thread?
        for img in self.image_paths:
            if os.path.exists(os.path.expanduser(img)):
                i_temp = images.Img.from_path(img)
                # TODO resize by width or height or only use svg, or let user decide?
                i_temp.resize(height=1440, width=2560)  # TODO don't hard code this
                surf, _ = images._decode_to_image_surface(i_temp.bytes_img, i_temp.width, i_temp.height)
                self.surfaces.append(surf)
            else:
                log_test(f"invalid image path: {img}")
        self.loop = cycle(range(len(self.surfaces)))

    def _close(self) -> None:
        """Close windows and clear variables"""
        try:
            self.timer.cancel()  # breaks if lock immediately after qtile loads
            self.timer = None
        except Exception as e:
            log_test(e)
        for p in self.popups:
            p.hide()
            p.kill()
        self.popups = []
        self._user_input = ""
        # TODO refocus previous window

    def _click_popup(self, x, y, button) -> None:
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
            self._user_input = self._user_input[:-1]
        elif 31 < keycode < 3900:  # most actually typeable characters in this range?
            self._user_input += chr(keycode)
        # self._actually_draw()  # TODO update text slow without this

    def _enter_window(self, *args) -> None:
        """Handle mouse enter window to focus."""
        self.popups[0].win.focus(warp=False)

    def _update_time(self) -> None:
        self._time = datetime.now().isoformat()


class _RepeatTimer(threading.Timer):
    def run(self) -> None:
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
