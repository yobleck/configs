# Desktop Icons

from functools import partial
import shlex
import subprocess

from libqtile import qtile, images, hook
from libqtile.popup import Popup
from libqtile.widget import base
from xcffib.xproto import StackMode

def log(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


class simple_icon:
    """simple custom icon"""
    def __init__(self, name: str, img_path: str, cmd: str, x: int, y: int, size: int):
        self.name = name
        self.img_path = img_path
        self.cmd = cmd
        self.x = x
        self.y = y
        self.size = size

    def run_cmd(self):
        subprocess.Popen(shlex.split(self.cmd))


class xdg_desktop_icon:
    """xdg desktop spec compliant icon"""
    def __init__(self, file_path: str, x: int, y: int, size: int):
        self.file_path = file_path
        self.x = x
        self.y = y
        self.size = size
        with open(file_path, "r") as f:
            for line in f:
                var = line.split("=")
                if var[0] == "Name":
                    self.name = var[1].strip()
                elif var[0] == "Exec":
                    self.cmd = var[1].strip()
                elif var[0] == "Icon":  # TODO WARNING needs to be way more robust
                    self.img_path = f"/usr/share/icons/breath-dark/apps/48/{var[1].strip()}.svg"

    def run_cmd(self):
        subprocess.Popen(shlex.split(self.cmd))


class desktop_icons:
    def __init__(self, icons: list):
        self.icons = []
        for i in icons:  # ensure type correctness
            if type(i) in [simple_icon, xdg_desktop_icon]:
                self.icons.append(i)

        self.popups = []
        for e, i in enumerate(self.icons):
            self.popups.append(Popup(qtile, background="#00000000", foreground="#00aa00", x=i.x, y=i.y, width=i.size, height=i.size,
                            font="Noto Mono", font_size=12, border="#00ffff", border_width=2, opacity=1, wrap=True))
            # TODO ensure that window are always in the back and cant steal focus

            #self.popups[e].place()
            # place window. stackmode below is required to ensure the windows stay below all other windows
            self.popups[e].win.window.set_property("_NET_WM_STATE", (343,))  # "_NET_WM_STATE_BELOW" = (343,)
            self.popups[e].win.window.configure(x=i.x, y=i.y, width=i.size, height=i.size, stackmode=StackMode.Below)
            self.popups[e].win.paint_borders("#00ffff", 2)
            self.popups[e].unhide()

            # draw text
            self.popups[e].text = i.name
            self.popups[e].draw_text(x=2, y=self.popups[e].height-self.popups[e].font_size-2)
            self.popups[e].draw()

            # draw image
            img = images.Img.from_path(i.img_path)
            img.resize(height=self.popups[e].height-self.popups[e].font_size)
            surf, _ = images._decode_to_image_surface(img.bytes_img, img.width, img.height)
            self.popups[e].draw_image(surf, 0, 0)

            #self.popups[e].win.process_pointer_leave = partial(self.kill_popup, k=e)
            self.popups[e].win.process_button_click = partial(self.click_popup, k=e)

    def kill_popup(self, *args, k):
        self.popups[k].hide()
        self.popups[k].kill()

    def click_popup(self, x, y, button, k):
        if button == 1:
            self.icons[k].run_cmd()
        elif button == 3:
            self.popups[k].hide()
            self.popups[k].kill()

    def toggle_icons(self):
        pass  # TODO hide unhide icons based on active group or keybind etc.


class app_tray(base._TextBox):
    """TODO copy py_repl widget. have app icons in grid where user defines pos in window not by pixels
    but by column row pos"""
    def __init__(self):
        pass

    def _configure(self, qtile, bar):
        pass

    def leave_win(self, *args):
        pass

    def b_press(self, x, y, button):
        pass

