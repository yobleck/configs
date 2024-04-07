# License here
# WARNING TODO cmd_ prefix being removed
from typing import Any, List, Tuple
from importlib import metadata

from libqtile import bar, qtile, images
from libqtile.log_utils import logger
from libqtile.popup import Popup
from libqtile.widget import base, image  # TODO image vs. images


def log_test(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


class StartMenu(image.Image):
    """A simple start menu with three options: shutdown/poweroff, reboot, and logoff/end session"""
    defaults = [
        ("win_pos", (0, 0), "Initial window coordinates as tuple (x, y)."),
        ("win_size", (150, 50), "Window size as tuple (w, h)."),
        ("win_bordercolor", "#ff0000", "Window border color. Can be list of multiple values."),
        ("win_borderwidth", 1, "Window Border width."),
        ("win_foreground", "#ffffff", "Window text color"),
        ("win_background", "#000000", "Window background color"),
        ("win_opacity", 1, "Window opacity."),
        ("win_font", "sans", "Window text font."),
        ("win_fontsize", 12, "Window font pixel size. Calculated if None."),
        ("win_fontshadow", None, "Window font shadow color, default is None(no shadow)."),
        ("win_icon_paths", None, "List (len 3) of the file paths for the shutdown, reboot and log off buttons."),
        ("action_list",
         ["systemctl poweroff", "systemctl reboot", "qtile cmd-obj -o cmd -f shutdown"],
         "List of commands to be preformed when clicking on buttons"
         ),
    ]

    def __init__(self, text="PY REPL", length=bar.CALCULATED, **config):
        image.Image.__init__(self, length, **config)
        self.add_defaults(StartMenu.defaults)
        self.add_callbacks({"Button1": self.open_win})
        self.win_opened: bool = False

    def create_win(self) -> None:
        try:
            self.popup = Popup(qtile, background=self.win_background, foreground=self.win_foreground,
                               x=self.win_pos[0], y=self.win_pos[1],
                               width=self.win_size[0], height=self.win_size[1],
                               font=self.win_font, font_size=self.win_fontsize, fontshadow=self.win_fontshadow,
                               border=self.win_bordercolor, border_width=self.win_borderwidth,
                               opacity=self.win_opacity, wrap=True)

            self.popup.layout.markup = False  # TODO PR to add this to popup options
            self.popup.layout.width = self.popup.width  # actually enforce line wrap. see PR above

            self.popup.text = "Shutdown  Reboot  Logoff"
            self.popup.draw_text(x=2, y=self.popup.height - self.popup.font_size - 2)  # TODO don't hard code this
            self.popup.draw()

            if type(self.win_icon_paths) is list and all(type(wip) is str for wip in self.win_icon_paths):
                icon_list: list = [images.Img.from_path(f) for f in self.win_icon_paths]
                [i.resize(height=self.popup.height) for i in icon_list]
                surface_list: list = []
                for x in icon_list:
                    s, _ = images._decode_to_image_surface(x.bytes_img, x.width, x.height)
                    surface_list.append(s)
                [self.popup.draw_image(s, int(self.popup.width / len(surface_list)) * i, -5) for i, s in enumerate(surface_list)]
            else:
                logger.warning("win_icon_paths not formatted correctly")
            # self.popup.win.window.set_property("_NET_WM_NAME", "simple start menu")
            # self.popup.win.update_name()

            self.popup.win.process_pointer_leave = self.leave
            self.popup.win.process_button_click = self.b_press
            self.popup.win.process_pointer_enter = self.enter
        except Exception as e:
            log_test(f"create window failed: {e}")

    def b_press(self, x, y, button) -> None:  # two functions because mouse click doesn't work with *args
        """ Handle mouse button presses."""
        try:
            if button == 1:
                x_pos: int = int(x / self.popup.width * len(self.action_list))
                # log_test("clicked on: " + self.action_list[x_pos])
                qtile.spawn(self.action_list[x_pos])

            # log_test(f"button {button} clicked")
        except Exception as e:
            log_test(f"button click error: {e}")

    def enter(self, *args) -> None:
        """Handle mouse enter window to focus."""
        try:
            self.popup.win.focus(warp=False)
            # log_test("pointer enter")
        except Exception as e:
            log_test(f"pointer enter error: {e}")

    def open_win(self) -> None:
        """Open start menu with internal popup window."""
        if not self.win_opened:  # stops duplicates
            self.create_win()
            self.win_opened = True
            self.popup.place()
            self.popup.unhide()

    def leave(self, *args) -> None:  # close window when mouse leaves
        """Handle closing start menu window."""
        try:
            # log_test("pointer leave")
            self.popup.hide()
            self.popup.kill()  # BUG v0.23 new stacking require full kill and remake of window to stay on top
            self.win_opened = False
        except Exception as e:
            log_test(f"pointer leave error: {e}")
