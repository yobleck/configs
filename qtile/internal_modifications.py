from xcffib.xproto import EventMask

from libqtile import qtile, images
from libqtile.popup import Popup

"""
Avoid including `self`
"""

def log_test(i):
    f = open("/home/yobleck/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


def mouse_move(qtile):
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
        assert qtile is not None
        if qtile.config.follow_mouse_focus and not qtile.config.cursor_warp:
            if hasattr(event, "root_x") and hasattr(event, "root_y"):
                screen = qtile.find_screen(event.root_x, event.root_y)
                if screen:
                    index_under_mouse = screen.index
                    if index_under_mouse != qtile.current_screen.index:
                        qtile.focus_screen(index_under_mouse, warp=False)
        qtile.process_button_motion(event.event_x, event.event_y)
    setattr(qtile.core, "handle_MotionNotify", screen_change)

####

def border_snap(window):
    #log_test("starting")
    def cmd_set_position_floating( x, y, border_snapping=False, snap_dist=10): #window,
        #log_test("set_pos")
        """Move floating window to x and y.
        Border snapping makes floating window's borders
        stick to other borders for easy alignment
        """
        if border_snapping:
            window.tweak_float(**window._borders_touch(x, y, snap_dist))
        else:
            window.tweak_float(x=x, y=y)

    def _get_borders(): #window
        #log_test("get_borders")
        """Generate list of 4-tuples describing
        the borders of every window and screen.
        """
        borders = []
        for s in window.qtile.screens:
            borders.append((s.x, s.y, s.x+s.width, s.y+s.height))
            for w in s.group.windows:
                if not w.hidden:
                    borders.append(w.edges)
        borders.remove(window.edges)
        return borders

    def _borders_touch( x, y, snap_dist): #window,
        #log_test("borders_touch")
        """Compares this window's borders to the borders of other
        windows/screens to see if they touch.
        """
        overlap_args = {"x": x, "y": y}
        borders = window._get_borders()
        for b in borders:
            # Are the two borders on the same line
            if any(i in [window.edges[0], window.edges[2]] for i in [b[0], b[2]]):
                # Are they actually overlapping
                if window.edges[1] < b[3] and window.edges[3] > b[1]:
                    # Has the mouse moved outside of the snap area
                    if any(abs(window.edges[i]-x) < snap_dist for i in [0, 2]):
                        try:
                            # Window should snap so don't move along this axis
                            del overlap_args["x"]
                        except Exception:
                            pass
            # Repeat for y
            if any(i in [window.edges[1], window.edges[3]] for i in [b[1], b[3]]):
                if window.edges[0] < b[2] and window.edges[2] > b[0]:
                    if any(abs(window.edges[i]-y) < snap_dist for i in [1, 3]):
                        try:
                            del overlap_args["y"]
                        except Exception:
                            pass
        return overlap_args
    
    setattr(window, "_get_borders", _get_borders)
    setattr(window, "_borders_touch", _borders_touch)
    setattr(window, "cmd_set_position_floating", cmd_set_position_floating)
    #log_test("finishing")

####

def simple_start_menu():
    #https://github.com/m-col/qtile-config/blob/master/notification.py
    try:
        #log_test(1)
        popup = Popup(qtile, background="#002200", x=0, y=24, width=100, height=50, font_size=10, border="#ff00ff", border_width=1,
                    foreground="#ffffff", opacity=0.9)

        popup.place()
        popup.unhide()
        popup.text = "Reboot    Shutdown"
        popup.draw_text(x=2, y=popup.height-popup.font_size-1)  # TODO don't hard code this
        #log_test(2)
        popup.draw()
        #log_test(3)
        #popup.win.window.set_property("_NET_WM_STATE", "Above")
        popup.win.window.set_property("_NET_WM_NAME", "simple start menu")
        popup.win.update_name()

        try:  # TODO simplify this mess
            icon_file_list = ["/usr/share/icons/breath2-dark/actions/24/system-reboot.svg",
                              "/usr/share/icons/breath2-dark/actions/24/system-shutdown.svg"]
            icon_list = [images.Img.from_path(f) for f in icon_file_list]
            [i.resize(height=popup.height) for i in icon_list]
            surface_list = []
            for x in icon_list:
                s, _ = images._decode_to_image_surface(x.bytes_img, x.width, x.height)
                surface_list.append(s)
            [popup.draw_image(s, int(popup.width/len(surface_list))*i, -5) for i, s in enumerate(surface_list)]
            #log_test(4)
        except Exception as e:
            log_test("image_load error: {0}".format(e))

        def click(x, y, button):
            action_list = ["systemctl reboot", "systemctl poweroff"]
            try:
                if button == 1:
                    x_pos = int(x/popup.width*len(action_list))
                    #log_test("clicked on: " + action_list[x_pos])
                    qtile.cmd_spawn(action_list[x_pos])
                else:
                    popup.hide()
                    popup.kill()
            except Exception as e:
                log_test("click error: {0}".format(e))
        popup.win.process_button_click = click

        def leave(*args):
            try:
                #log_test(args)
                popup.hide()
                popup.kill()
            except Exception as e:
                log_test("leave error: {0}".format(e))
        popup.win.process_pointer_leave = leave
    except Exception as e:
        log_test("popup_test error: {0}".format(e))

    
