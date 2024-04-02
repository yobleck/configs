"""Pseudo screen locker that uses Qtile a popup window"""

from datetime import datetime
import os
import threading

from libqtile import qtile, images
from libqtile.popup import Popup


def log_test(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


class lock_screen:  # TODO turn this into an extension?
    def __init__(
            self, image_path: str = "", background: str = "#000000ff", foreground: str = "#ffffff",
            font: str = "sans", font_size: int = 16,
            fake_password: str = "", text_pos: tuple = (0, 0)) -> None:

        self.image_path = image_path
        if self.image_path is None:  # TODO ensure valid image
            pass
        self.background: str = background
        self.foreground: str = foreground
        self.font: str = font
        self.font_size: int = font_size

        self.time: str = datetime.now().isoformat()
        self.prompt: str = "\nFake Password:"
        self.fake_password: str = fake_password
        self.user_input: str = ""
        self.text_pos: tuple = text_pos

        self.popups: list = []
        self.surface = None
        if os.path.exists(os.path.expanduser(self.image_path)):  # TODO move this to __init__?
            img = images.Img.from_path(self.image_path)
            # TODO resize by width or height or only use svg, or let user decide?
            img.resize(height=1440, width=2560)  # TODO don't hard code this
            self.surface, _ = images._decode_to_image_surface(img.bytes_img, img.width, img.height)

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
                self.timer = _RepeatTimer(1, self._actually_draw)
                self.timer.start()
            except Exception as e:
                log_test(e)

    def _actually_draw(self) -> None:
        # NOTE this function is slow to run and holding down a key can cause lag
        self._update_time()
        for x in range(len(qtile.screens)):
            self.popups[x].clear()
            # draw image
            if self.surface:
                self.popups[x].draw_image(self.surface, 0, 0)

            # draw text
            self.popups[x].text = self.time + self.prompt + self.user_input  # TODO replace user_input with len(user_input) * "*"
            self.popups[x].draw_text(x=self.text_pos[0], y=self.text_pos[1])
            self.popups[x].draw()

    def _close(self) -> None:
        """Close windows and clear variables"""
        try:
            self.timer.cancel()
            self.timer = None
        except Exception as e:
            log_test(e)
        for x in range(len(qtile.screens)):
            self.popups[x].hide()
            self.popups[x].kill()
        self.popups = []
        self.user_input = ""
        # TODO refocus previous window

    def _click_popup(self, x, y, button) -> None:
        if button == 3:
            self._close()

    def _key_press(self, keycode) -> None:
        """Handle key press"""
        # log_test(f"s_l: key press: {keycode}")
        if keycode == 65293:  # enter
            if self.user_input == self.fake_password:
                self._close()
                return
            else:
                self.user_input = ""
        elif keycode == 65288:  # backspace
            self.user_input = self.user_input[:-1]
        elif 31 < keycode < 3900:  # actually typeable characters?
            self.user_input += chr(keycode)
        self._actually_draw()

    def _enter_window(self, *args) -> None:
        """Handle mouse enter window to focus."""
        self.popups[0].win.focus(warp=False)

    def _update_time(self) -> None:
        self.time = datetime.now().isoformat()


class _RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
