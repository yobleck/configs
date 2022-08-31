# Hover over window widget to show preview
from functools import partial
import os
import shlex
import subprocess

from libqtile import qtile, images, hook
from libqtile.popup import Popup 


def log(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


class window_preview:
    def __init__(self, bar = "bottom", height: int = 180):
        self.popup = None
        self.win_height = height

    def screenshot(self, wid: int):
        # take screenshot of window
        s = subprocess.Popen(["sh", "/home/yobleck/.config/qtile/window_preview.sh", str(wid)])
        #s.wait()  #TODO get rid of this since screenshots not happening before creating popup anymore?
        # TODO error handling?

    def clear_file(self, wid: int):
        # remove screenshot of window when killed
        try:
            os.remove(f"/home/yobleck/.config/qtile/window_preview_images/{wid}.png")
        except Exception as e:
            log("failed to delete file: " + str(e))

    def show_preview(self):  # TODO activate this when mouse hovers over tasklsit widget
        # display preview of window next to taskbar where clicked
        for widget in qtile.current_screen.bottom.widgets:
            if widget.name == "tasklist":
                window = widget.clicked

                draw_image = False
                try:
                    img = images.Img.from_path(f"/home/yobleck/.config/qtile/window_preview_images/{window.wid}.png")
                    img.resize(height=self.win_height)
                    surf, _ = images._decode_to_image_surface(img.bytes_img, img.width, img.height)
                    width = img.width
                    height = self.win_height
                    x, _ = qtile.core.get_mouse_position()
                    x = x - width//2
                    y = qtile.current_screen.height - self.win_height - qtile.current_screen.bottom.height
                    draw_image = True
                except:  # no image available
                    width = 100
                    height = 12 + 4
                    x, _ = qtile.core.get_mouse_position()
                    x = x - width//2
                    y = qtile.current_screen.height - height - qtile.current_screen.bottom.height

                self.popup = Popup(qtile, background="#00000000", x=x, y=y, width=width, height=height,
                                font_size=12, border="#ff00ff", border_width=1, foreground="#00ff00", opacity=0.8)
                self.popup.place()
                self.popup.unhide()
                if draw_image:
                    self.popup.draw_image(surf, 0, 0)

                self.popup.text = window.name
                self.popup.draw_text(x=2, y=self.popup.height-self.popup.font_size-2)
                self.popup.draw()

                self.popup.win.process_button_click = partial(self._focus_window, win=window)
                self.popup.win.process_pointer_leave = self._leave

    def _focus_window(self, *args, win):
        # focus window on click
        qtile.current_group.focus(win)
        self._leave()

    def _leave(self, *args):
        self.popup.hide()
        self.popup.kill()


