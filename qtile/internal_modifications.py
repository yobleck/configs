import sys
from importlib import metadata
import io

from xcffib.xproto import EventMask

from libqtile import qtile, images
from libqtile.popup import Popup

"""
Avoid including `self`
"""

def log_test(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
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
        assert qtile is not None  # crash if no qtile?
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
    #TODO move definitions outside of this function so that they are only called once
    #i.e. popup = should be outside but popup.place should remain
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
            icon_file_list = ["/home/yobleck/.config/qtile/icons/system-reboot.svg",
                              "/home/yobleck/.config/qtile/icons/system-shutdown.svg"]
            icon_list = [images.Img.from_path(f) for f in icon_file_list]
            [i.resize(height=popup.height) for i in icon_list]
            surface_list = []
            for x in icon_list:
                s, _ = images._decode_to_image_surface(x.bytes_img, x.width, x.height)
                surface_list.append(s)
            [popup.draw_image(s, int(popup.width/len(surface_list))*i, -5) for i, s in enumerate(surface_list)]
            #log_test(4)
        except Exception as e:
            log_test(f"image_load error: {e}")

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
                log_test(f"click error: {e}")
        popup.win.process_button_click = click

        def leave(*args):
            try:
                #log_test(args)
                popup.hide()
                popup.kill()
            except Exception as e:
                log_test(f"leave error: {e}")
        popup.win.process_pointer_leave = leave
    except Exception as e:
        log_test(f"popup_test error: {e}")

####

def simple_repl():
    try:
        popup = Popup(qtile, background="#000000", foreground="#00aa00", x=1280, y=720, width=500, height=500, font="Noto Mono", font_size=12,
                      border=["#0000ff", "#0000ff", "#ffff00", "#ffff00"], border_width=5, opacity=0.90, wrap=True)

        popup.layout.markup = False  # TODO PR to add this to popup options
        popup.layout.width = popup.width  # actually enforce line wrap. see PR above
        popup.place()
        popup.unhide()

        #num_cols = popup.width//8  # 8 assumes Noto Mono font at size 12
        #num_rows = popup.height//15  # ditto
        nl = "\n"
        old_text = ["Yobleck's simple python REPL (click to focus, esc to quit, F5/'cls'/'clear' to reset screen)",
                    f"Qtile: {metadata.distribution('qtile').version}",
                    f"Python: {sys.version.replace(nl, '')}", ">>> "]
        new_text = ""
        popup.text = lines_to_text(old_text) + "\u2588" #[-num_rows:]
        draw_y = 5
        popup.draw_text(x=2, y=draw_y)
        popup.draw()
        #globals()["tert"] = "terting"
        history = []  # command history for this popup instance. save across session with global var?
        history_index = -1  # is there a way to do this without the var?
        indentation_level = 0

        def key_press(keycode):
            try:
                nonlocal new_text
                nonlocal old_text
                nonlocal draw_y
                nonlocal history_index
                nonlocal indentation_level
                keychr = chr(keycode)
                log_test(f"key {keycode}={keychr} pressed")  # TODO convert keycodes to text

                if keycode == 65307:  # escape
                    leave()
                    return
                elif keycode == 65474:  # F5 to clear screen
                    old_text = [">>> "]
                    new_text = ""
                # scrolling
                elif keycode == 65366:  # page down
                    draw_y -= 5
                elif keycode == 65365:  # page up
                    draw_y += 5
                elif keycode == 65288:  # backspace
                    if new_text[-1] == "\n":
                        indentation_level -= 1
                    new_text = new_text[:-1]
                # history
                elif keycode in [65362, 65364]:  # up/down arrow keys. TODO double check with another non 60% keyboard
                    if history:
                        if keycode == 65362 and history_index < len(history)-1:
                            history_index += 1
                            new_text = history[history_index]
                        elif keycode == 65364 and history_index > 0:
                            history_index -= 1
                            new_text = history[history_index]
                elif keycode == 65293:  # enter
                    history.insert(0, new_text)
                    history_index = -1
                    if new_text:
                        if new_text in ["exit", "exit()", "quit", "quit()"] or "sys.exit" in new_text:
                            # exit commands. WARNING will eval("quit()") kill qtile? sys.exit solution will kill regardless of conditionals
                            leave()
                            return
                        elif new_text in ["clear", "cls"]:  # clear screen commands
                            old_text = [">>> "]
                            new_text = ""
                        elif new_text[-1] == ":":
                            indentation_level += 1
                            new_text += "\n" + "    "*indentation_level
                        else:
                            #old_text += new_text + "\n" + _simple_eval_exec(new_text) + ">>> "  # append input text, eval and append results
                            old_text[-1] += new_text
                            old_text.extend([ _simple_eval_exec(new_text), ">>> "])
                            new_text = ""
                            indentation_level = 0
                elif keycode in [65505, 65507, 65508, 65506, 65513, 65514, 65515]:  # range(65505, 65518) for mod keys?
                    pass  # ignore modifiers and other non text keys. TODO modifier list that is cleared after non modifier is pressed. act on list?
                else:
                    new_text += keychr

                # actually drawing text
                popup.clear()
                popup.text = lines_to_text(old_text) + new_text + "\u2588"  # TODO scroll to bottom after hitting enter
                popup.draw_text(x=2, y=draw_y)
                popup.draw()
                popup.text = lines_to_text(old_text) #[-num_rows:] [-num_rows:]
            except Exception as e:
                log_test(f"key press error: {e}")
        popup.win.process_key_press = key_press

        def leave(*args):  # close window when mouse leaves
            try:
                log_test("pointer leave")
                popup.hide()
                popup.kill()
            except Exception as e:
                log_test(f"pointer leave error: {e}")
        #popup.win.process_pointer_leave = leave
        
        # focus window
        def b_press(x, y, button):  # two functions cause mouse click doesn't work with *args
            try:
                nonlocal draw_y
                if button == 1:
                    popup.win.focus(warp=False)
                elif button in [4,5]:
                    if button == 4:  # mouse wheel up
                        draw_y += 5
                    elif button == 5:  # down
                        draw_y -= 5
                    popup.clear()  # NOTE DRY violation
                    popup.text = lines_to_text(old_text) + new_text
                    popup.draw_text(x=2, y=draw_y)
                    popup.draw()
                    popup.text = lines_to_text(old_text)
                elif button == 8:  # move the window around (crudely)
                    new_pos = (popup.x+x-popup.width//2, popup.y+y-popup.height//2)
                    popup.win.place(new_pos[0], new_pos[1], popup.width, popup.height, popup.border_width, popup.border)
                    popup.x, popup.y = new_pos  # .place() doesn't change these
                log_test(f"button {button} clicked")
            except Exception as e:
                log_test(f"button click error: {e}")
        popup.win.process_button_click = b_press
        def enter(*args):
            try:
                popup.win.focus(warp=False)
                log_test("pointer enter")
            except Exception as e:
                log_test(f"pointer enter error: {e}")
        popup.win.process_pointer_enter = enter

    except Exception as e:
        log_test(f"repl error: {e}")

def lines_to_text(in_list):
    out_str = "\n".join(in_list)
    return out_str

def _simple_eval_exec(_some_long_var_name):
    try:
        old_stdout = sys.stdout  # capture stdout and convert to string. WARNING may leave stdout in weird state
        sys.stdout = io.StringIO()
        output1 = eval(_some_long_var_name, globals(), locals())  # TODO clean up the try except so they make more sense
        output2 = sys.stdout.getvalue()
        sys.stdout = old_stdout
        #log_test("out1: " + str(output1) + " out2: " +str(output2))
        return "".join(x for x in [str(output1), output2] if x != "None") #str(output1) + "\n" + str(output2) # 
    except Exception as e:
        sys.stdout = old_stdout
        if isinstance(e, SyntaxError) and "invalid syntax" in str(e):
            try:
                exec(_some_long_var_name, globals())  # how to capture results of exec and pass through to globals?
                #globals()["xt"]=5
                return "" #"temp read only. creating and changing vars might crash qtile"
            except Exception as e:
                return str(e)
        else:
            return str(e)
    #else:
        #sys.stdout = old_stdout
        #return "idk when this runs. if you're reading this something weird happened"
