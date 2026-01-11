import calendar
from datetime import datetime
# import io
# import os
# import pty
# import subprocess
# import sys
# from importlib import metadata

from libqtile import qtile, images
from libqtile.popup import Popup

from xcffib.xproto import EventMask

"""
Avoid including `self`
"""


def log_test(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


def mouse_move(qtile):
    """add pointer motion event mask to root window to ensure
    that screen focus changes when mouse moves to a new monitor"""
    qtile.core.eventmask = (EventMask.StructureNotify
                            | EventMask.SubstructureNotify
                            | EventMask.SubstructureRedirect
                            | EventMask.EnterWindow
                            | EventMask.LeaveWindow
                            | EventMask.ButtonPress
                            | EventMask.PointerMotion)
    qtile.core._root.set_attribute(eventmask=qtile.core.eventmask)

    def screen_change(event):
        """Check screen under mouse if mouse over root window and change focus accordingly"""
        assert qtile is not None  # crash if no qtile?
        if qtile.config.follow_mouse_focus and not qtile.config.cursor_warp:
            if hasattr(event, "root_x") and hasattr(event, "root_y"):
                screen = qtile.find_screen(event.root_x, event.root_y)
                if screen:
                    index_under_mouse = screen.index
                    if index_under_mouse != qtile.current_screen.index:
                        # log_test(f"changed screen from {qtile.current_screen.index} to {index_under_mouse}")
                        qtile.focus_screen(index_under_mouse, warp=False)
        qtile.process_button_motion(event.event_x, event.event_y)
    setattr(qtile.core, "handle_MotionNotify", screen_change)

####


# def simple_start_menu():
#     # https://github.com/m-col/qtile-config/blob/master/notification.py
#     # TODO move definitions outside of this function so that they are only called once
#     # i.e. popup = should be outside but popup.place should remain
#     try:
#         # log_test(1)
#         popup = Popup(qtile, background="#000000", x=0, y=24, width=100, height=50, fontsize=10, border="#aa00aa",
#                       border_width=1, foreground="#ffffff", opacity=0.9)

#         popup.place()
#         popup.unhide()
#         popup.layout.text = "Reboot    Shutdown"
#         popup.draw_text(x=2, y=popup.height - popup.fontsize - 1)  # TODO don't hard code this
#         # log_test(2)
#         popup.draw()
#         # log_test(3)
#         # popup.win.window.set_property("_NET_WM_STATE", "Above")
#         popup.win.window.set_property("_NET_WM_NAME", "simple start menu")
#         popup.win.update_name()

#         try:  # TODO simplify this mess
#             icon_file_list = ["/home/yobleck/.config/qtile/icons/system-reboot.svg",
#                               "/home/yobleck/.config/qtile/icons/system-shutdown.svg"]
#             icon_list = [images.Img.from_path(f) for f in icon_file_list]
#             [i.resize(height=popup.height) for i in icon_list]
#             surface_list = []
#             for x in icon_list:
#                 s, _ = images.get_cairo_surface(x.bytes_img, x.width, x.height)
#                 surface_list.append(s)
#             [popup.draw_image(s, int(popup.width / len(surface_list)) * i, -5) for i, s in enumerate(surface_list)]
#             # log_test(4)
#         except Exception as e:
#             log_test(f"image_load error: {e}")

#         def click(x, y, button):
#             action_list = ["systemctl reboot", "systemctl poweroff"]
#             try:
#                 if button == 1:
#                     x_pos = int(x / popup.width * len(action_list))
#                     # log_test("clicked on: " + action_list[x_pos])
#                     qtile.spawn(action_list[x_pos])
#                 else:
#                     popup.hide()
#                     popup.kill()
#             except Exception as e:
#                 log_test(f"click error: {e}")
#         popup.win.process_button_click = click

#         def leave(*args):
#             try:
#                 # log_test(args)
#                 popup.hide()
#                 popup.kill()
#             except Exception as e:
#                 log_test(f"leave error: {e}")
#         popup.win.process_pointer_leave = leave
#     except Exception as e:
#         log_test(f"simple start menu error: {e}")


def simple_calendar():
    try:
        calendar.setfirstweekday(6)
        now = datetime.now()
        month: int = now.month
        year: int = now.year
        popup = Popup(qtile, background="#000000", x=2300, y=1210, width=256, height=200, font="Hack", fontsize=20,
                      border="#aa00aa", border_width=1, foreground="#00aa00", opacity=0.9, text_alignment="left")

        popup.place()
        popup.unhide()
        popup.layout.text = calendar.month(year, month)
        popup.draw_text(x=8, y=4)
        popup.draw()
        popup.win.window.set_property("_NET_WM_NAME", "simple calendar")
        popup.win.update_name()

        def click(x, y, button):
            try:
                nonlocal month
                nonlocal year
                if button == 1:
                    month += 1
                    if month == 13:
                        month = 1
                        year += 1
                    popup.clear()
                    popup.layout.text = calendar.month(year, month)
                    popup.draw_text(x=8, y=4)
                    popup.draw()
                elif button == 3:
                    month -= 1
                    if month == 0:
                        month = 12
                        year -= 1
                    popup.clear()
                    popup.layout.text = calendar.month(year, month)
                    popup.draw_text(x=8, y=4)
                    popup.draw()
                else:
                    popup.hide()
                    popup.kill()
            except Exception as e:
                log_test(f"click error: {e}")
        popup.win.process_button_click = click

        def leave(*args):
            try:
                popup.hide()
                popup.kill()
            except Exception as e:
                log_test(f"leave error: {e}")
        popup.win.process_pointer_leave = leave
    except Exception as e:
        log_test(f"simple calendar error: {e}")


# def simple_terminal():
#     try:
#         buffer = []

#         def read(fd):
#             nonlocal buffer
#             data = os.read(fd, 1024)
#             buffer.append(data.decode())
#             return data

#         popup = Popup(qtile, background="#000000", x=500, y=500, width=400, height=400, font="Hack", fontsize=16,
#                       border="#aa00aa", border_width=1, foreground="#00aa00", opacity=0.9, text_alignment="left")

#         popup.place()
#         popup.unhide()
#         popup.layout.text = "first"
#         popup.draw_text(x=8, y=4)
#         popup.draw()
#         popup.win.window.set_property("_NET_WM_NAME", "simple terminal")
#         popup.win.update_name()

#         def click(x, y, button):
#             try:
#                 nonlocal buffer
#                 if button == 1:
#                     popup.clear()
#                     popup.layout.text = str(buffer)
#                     popup.draw_text(x=8, y=4)
#                     popup.draw()
#                 elif button == 3:
#                     pass
#                 else:
#                     popup.hide()
#                     popup.kill()
#             except Exception as e:
#                 log_test(f"click error: {e}")
#         popup.win.process_button_click = click

#         def keypress(keycode):
#             nonlocal buffer
#             buffer.append(chr(keycode))
#             popup.clear()
#             popup.layout.text = buffer[-1]
#             popup.draw_text(x=8, y=4)
#             popup.draw()
#         popup.win.process_key_press = keypress

#         def enter(*args):
#             """Handle mouse enter window to focus."""
#             try:
#                 popup.win.focus(warp=False)
#             except Exception as e:
#                 log_test(f"pointer enter error: {e}")
#         popup.win.process_pointer_enter = enter

#         def leave(*args):
#             try:
#                 popup.hide()
#                 popup.kill()
#             except Exception as e:
#                 log_test(f"leave error: {e}")
#         popup.win.process_pointer_leave = leave

#         # pty.spawn(["/bin/bash", "/home/yobleck/test/pty.sh"], read)
#         mfd, sfd = os.forkpty()
#         p = subprocess.run(["/bin/bash"], preexec_fn=os.setsid, stdin=sfd, stdout=sfd, stderr=sfd)
#         os.read(mfd, 4096).decode()
#         os.write(mfd, "w\n".encode())
#         os.close(mfd)
#         os.close(sfd)
#         p.kill()

#     except Exception as e:
#         log_test(f"simple terminal error: {e}")
