# Pinephone quick settings popup menu
import os

from libqtile import bar, configurable, images, qtile
from libqtile.widget import base
from libqtile.popup import Popup


def log(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


class Button(configurable.Configurable):
    """Button helper class."""

    defaults = [
    ("text", "default button", "display text of button"),
    ("icon_path", "/home/yobleck/.config/qtile/icons/pine64_orange.svg", "file path of button icon image"),
    ("is_toggle", True, "does the button toggle between two states(True) or jsut run one cmd(False)"),
    ("cmd", ("echo test1", "echo test2"), "one string or python function if not is_toggle or tuple of 2 strings or functions if is_toggle"),
    ("grid_pos", (0, 0), "2 tuple of the buttons location on the grid (col, row). make sure not to overlap"),
    ]

    def __init__(self, **config):
        configurable.Configurable.__init__(self, **config)
        self.add_defaults(Button.defaults)
        self.icon_path = os.path.abspath(os.path.expanduser(self.icon_path))
        self.toggled = None
        if self.is_toggle:
            self.toggled = False
            try:
                assert type(self.cmd) == tuple
                assert len(self.cmd) == 2
            except AssertionError:
                log(f"incorrect command type: {self.cmd}")

    def run_cmd(self) -> None:
        #log("running command")
        if self.is_toggle:
            if self.toggled:
                if callable(self.cmd):
                    self.cmd()
                else:
                    qtile.spawn(self.cmd[1])
                self.toggled = False
                return
            if callable(self.cmd):
                self.cmd()
            else:
                qtile.cmd_spawn(self.cmd[0])
            self.toggled = True
            return
        if callable(self.cmd):
            self.cmd()
            return
        qtile.cmd_spawn(self.cmd)


default_button = Button(cmd=("kcalc", "konsole"), grid_pos=(0,0))
button2 = Button(text="default button 2", cmd=("kcalc", "konsole"), grid_pos=(1,0))
button3 = Button(text="default button 3",cmd=("kcalc", "konsole"), grid_pos=(2,1))


class Menu(base._TextBox):
    defaults = [
        ("font", "sans", "Text font."),
        ("fontsize", None, "Font pixel size. Calculated if None."),
        ("fontshadow", None, "font shadow color, default is None(no shadow)."),
        ("padding", None, "Padding left and right. Calculated if None."),
        ("foreground", "#ffffff", "Foreground colour."),
        ("win_bordercolor", "#ff0000", "Window border color. Can be list of multiple values."),
        ("win_borderwidth", 1, "Window Border width."),
        ("win_foreground", "#ffffff", "Window text color"),
        ("win_background", "#000000", "Window background color"),
        ("win_opacity", 1, "Window opacity."),
        ("win_font", "sans", "Window text font."),
        ("win_fontsize", 12, "Window font pixel size. Calculated if None."),
        ("win_fontshadow", None, "Window font shadow color, default is None(no shadow)."),
        ("button_list", [default_button, button2, button3], "list of Button class objects that will be shown in popup window"),  # one default button?
        ("grid_size", (3,2), "size of icon grid as tuple of intergers (cols, rows)"),
    ]

    def __init__(self, text="quick settings menu", width=bar.CALCULATED, **config):  # TODO proper text in bar
        base._TextBox.__init__(self, text=text, width=width, **config)
        self.add_defaults(Menu.defaults)
        self.add_callbacks({"Button1": self.toggle_window})
        self.win_opened = False
        self.button_grid = [[None for _ in range(self.grid_size[1])] for _ in range(self.grid_size[0])]

    def _configure(self, qtile, bar):
        base._TextBox._configure(self, qtile, bar)
        log("configure qsm")
        try:
            for but in self.button_list:
                if (type(but.grid_pos[0]), type(but.grid_pos[1])) == (int, int) \
                and but.grid_pos[0] <= self.grid_size[0] and but.grid_pos[1] <= self.grid_size[1]:
                    if self.button_grid[but.grid_pos[0]][but.grid_pos[1]] is None:
                        self.button_grid[but.grid_pos[0]][but.grid_pos[1]] = but
                else:
                    log("button or grid parameters are incorrect")
            log(self.button_grid)
        except Exception as e:
            log(e)

        self.tall = Popup(qtile, background=self.win_background, foreground=self.win_foreground,
                           x=0, y=bar.height, width=720, height=720,
                           font=self.win_font, font_size=self.win_fontsize, fontshadow=self.win_fontshadow,
                           border=self.win_bordercolor, border_width=self.win_borderwidth,
                           opacity=self.win_opacity, wrap=True)
        self.tall.win.process_button_click = self.click
        self.popup_draw(self.tall)

        self.wide = Popup(qtile, background=self.win_background, foreground=self.win_foreground,
                           x=0, y=bar.height, width=1440, height=360,
                           font=self.win_font, font_size=self.win_fontsize, fontshadow=self.win_fontshadow,
                           border=self.win_bordercolor, border_width=self.win_borderwidth,
                           opacity=self.win_opacity, wrap=True)
        self.wide.win.process_button_click = self.click
        self.popup_draw(self.wide)

    def popup_draw(self, popup) -> None:
        for x, row in enumerate(self.button_grid):
            for y, but in enumerate(row):
                if but:
                    # draw button icon
                    img = images.Img.from_path(but.icon_path)
                    # img.resize(height=but.size)
                    img.resize(height=popup.height//self.grid_size[1]//2)
                    surf, _ = images.get_cairo_surface(img.bytes_img, img.width, img.height)
                    popup.draw_image(surf, but.grid_pos[0]*(popup.width//self.grid_size[0])+img.width//4,
                                           but.grid_pos[1]*(popup.height//self.grid_size[1])+img.height//2)
                    # draw button text
                    popup.text = but.text
                    popup.draw_text(but.grid_pos[0]*(popup.width//self.grid_size[0])+img.width//2,
                                    but.grid_pos[1]*(popup.height//self.grid_size[1])+img.height*1.5)
                    popup.draw()

    def toggle_window(self) -> None:
        popup = self.get_rotation()
        if self.win_opened:
            popup.hide()
            self.win_opened = False
        else:
            popup.place()
            popup.unhide()
            self.win_opened = True

    def get_rotation(self) -> None:
        # TODO get screen rotation cmd
        return self.wide

    def click(self, x, y, button) -> None:
        popup = self.get_rotation()
        try:
            self.button_grid[int(x/popup.width*self.grid_size[0])][int(y/popup.height*self.grid_size[1])].run_cmd()
        except AttributeError as e:  # no button at that pos
            log(e)

    def cmd_update(self, text):
        self.update(text)
