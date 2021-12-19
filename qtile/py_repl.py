#License here

import sys
import io
from typing import Any, List, Tuple
from importlib import metadata

from libqtile import bar, qtile, images
from libqtile.widget import base
from libqtile.popup import Popup

from internal_modifications import simple_repl


def log_test(i):  # TODO replace with official qtile logging
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


class REPL(base._TextBox):
    """A flexible textbox that can be updated from bound keys, scripts, and qshell."""
    defaults = [
        ("font", "sans", "Text font."),
        ("fontsize", None, "Font pixel size. Calculated if None."),
        ("fontshadow", None, "font shadow color, default is None(no shadow)."),
        ("padding", None, "Padding left and right. Calculated if None."),
        ("foreground", "#ffffff", "Foreground colour."),
        ("win_pos", (0,0), "Initial window coordinates as tuple (x, y)."),
        ("win_size", (500,500), "Window size as tuple (w, h)."),
        ("win_bordercolor", "#ff0000", "Window border color. Can be list of multiple values."),
        ("win_borderwidth", 2, "Window Border width."),
        ("win_foreground", "#ffffff", "Window text color"),
        ("win_background", "#000000", "Window background color"),
        ("win_opacity", 1, "Window opacity."),
        ("win_font", "sans", "Window text font."),
        ("win_fontsize", 12, "Window font pixel size. Calculated if None."),
        ("win_fontshadow", None, "Window font shadow color, default is None(no shadow)."),
        ("win_mousebutton_move", 3, "Mouse button that when clicked on repl window causes it to re-center under mouse."),
    ]

    def __init__(self, text="PY REPL", width=bar.CALCULATED, **config):
        base._TextBox.__init__(self, text=text, width=width, **config)
        self.add_defaults(REPL.defaults)
        self.add_callbacks({"Button1": self.open_win, "Button3":self.leave})
        self.og_bartext = self.text
        self.text = "_" + self.text
        self.win_opened = False

    def _configure(self, qtile, bar):
        base._TextBox._configure(self, qtile, bar)

        #self.popup = Popup(qtile, background="#000000", foreground="#00aa00", x=1280, y=720, width=500, height=500, font="Noto Mono",
                           #font_size=12, border=["#0000ff", "#0000ff", "#ffff00", "#ffff00"], border_width=5, opacity=0.90, wrap=True)

        self.popup = Popup(qtile, background=self.win_background, foreground=self.win_foreground,
                           x=self.win_pos[0], y=self.win_pos[1],
                           width=self.win_size[0], height=self.win_size[1],
                           font=self.win_font, font_size=self.win_fontsize, fontshadow=self.win_fontshadow,
                           border=self.win_bordercolor, border_width=self.win_borderwidth,
                           opacity=self.win_opacity, wrap=True)

        self.popup.layout.markup = False  # TODO PR to add this to popup options
        self.popup.layout.width = self.popup.width  # actually enforce line wrap. see PR above
        #self.popup.place()
        #self.popup.unhide()

        self.nl = "\n"
        self.old_text = ["Yobleck's simple python REPL (click to focus, esc to quit, F5/'cls'/'clear' to reset screen)",
                    f"Qtile: {metadata.distribution('qtile').version}",
                    f"Python: {sys.version.replace(self.nl, '')}", ">>> "]
        self.new_text = ""
        self.popup.text = lines_to_text(self.old_text) + "\u2588" #[-num_rows:]
        self.draw_y = 5
        self.popup.draw_text(x=2, y=self.draw_y)
        self.popup.draw()
        self.history = []  # command history for this popup instance. save across session with global var?
        self.history_index = -1  # is there a way to do this without the var?
        self.indentation_level = 0

        self.popup.win.process_key_press = self.key_press
        #self.popup.win.process_pointer_leave = self.leave
        self.popup.win.process_button_click = self.b_press
        self.popup.win.process_pointer_enter = self.enter

    def key_press(self, keycode):
        """Handle key presses."""
        try:
            keychr = chr(keycode)
            log_test(f"key {keycode}={keychr} pressed")  # TODO convert keycodes to text

            if keycode == 65307:  # escape
                self.leave()
                return
            elif keycode == 65474:  # F5 to clear screen
                self.old_text = [">>> "]
                self.new_text = ""
            # scrolling
            elif keycode == 65366:  # page down
                self.draw_y -= 5
            elif keycode == 65365:  # page up
                self.draw_y += 5
            elif keycode == 65288:  # backspace
                if self.new_text[-1] == "\n":
                    self.indentation_level -= 1
                self.new_text = self.new_text[:-1]
            elif keycode == 65289:  # tab. NOTE probably never going to have tab completion
                self.new_text += "\t"
            # history
            elif keycode in [65362, 65364]:  # up/down arrow keys. TODO double check with another non 60% keyboard
                if self.history:
                    if keycode == 65362 and self.history_index < len(self.history)-1:
                        self.history_index += 1
                        self.new_text = self.history[self.history_index]
                    elif keycode == 65364 and self.history_index > 0:
                        self.history_index -= 1
                        self.new_text = self.history[self.history_index]
            elif keycode == 65293:  # enter
                self.history.insert(0, self.new_text)
                self.history_index = -1
                if self.new_text:
                    if self.new_text in ["exit", "exit()", "quit", "quit()"] or "sys.exit" in self.new_text:
                        # exit commands. WARNING will eval("quit()") kill qtile? sys.exit solution will kill regardless of conditionals
                        self.leave()
                        return
                    elif self.new_text in ["clear", "cls"]:  # clear screen commands
                        self.old_text = [">>> "]
                        self.new_text = ""
                    elif self.new_text[-1] == ":":
                        self.indentation_level += 1
                        self.new_text += "\n" + "    "*indentation_level
                    else:
                        #old_text += new_text + "\n" + _simple_eval_exec(new_text) + ">>> "  # append input text, eval and append results
                        self.old_text[-1] += self.new_text
                        self.old_text.extend([ _simple_eval_exec(self.new_text), ">>> "])
                        self.new_text = ""
                        self.indentation_level = 0
            elif keycode in [65505, 65507, 65508, 65506, 65513, 65514, 65515]:  # range(65505, 65518) for mod keys?
                pass  # ignore modifiers and other non text keys. TODO modifier list that is cleared after non modifier is pressed. act on list?
            else:
                self.new_text += keychr

            # actually drawing text
            self.popup.clear()
            self.popup.text = lines_to_text(self.old_text) + self.new_text + "\u2588"  # TODO scroll to bottom after hitting enter
            self.popup.draw_text(x=2, y=self.draw_y)
            self.popup.draw()
            self.popup.text = lines_to_text(self.old_text) #[-num_rows:] [-num_rows:]
        except Exception as e:
            log_test(f"key press error: {e}")

    def leave(self, *args):  # close window when mouse leaves
        """Handle hiding repl window."""
        try:
            log_test("pointer leave")
            self.popup.hide()
            #self.popup.kill()
            self.cmd_update("_" + self.og_bartext)#"REPL Closed")
            self.win_opened = False
        except Exception as e:
            log_test(f"pointer leave error: {e}")

    def b_press(self, x, y, button):  # two functions cause mouse click doesn't work with *args
        """ Handle mouse button presses."""
        try:
            if button == 1:
                self.popup.win.focus(warp=False)
            elif button in [4,5]:
                if button == 4:  # mouse wheel up
                    self.draw_y += 5
                elif button == 5:  # down
                    self.draw_y -= 5
                self.popup.clear()  # NOTE DRY violation
                self.popup.text = lines_to_text(self.old_text) + self.new_text
                self.popup.draw_text(x=2, y=self.draw_y)
                self.popup.draw()
                self.popup.text = lines_to_text(self.old_text)
            elif button == self.win_mousebutton_move:  # move the window around (crudely)
                new_pos = (self.popup.x+x-self.popup.width//2, self.popup.y+y-self.popup.height//2)
                self.popup.win.place(new_pos[0], new_pos[1], self.popup.width, self.popup.height, self.popup.border_width, self.popup.border)
                self.popup.x, self.popup.y = new_pos  # .place() doesn't change these
            log_test(f"button {button} clicked")
        except Exception as e:
            log_test(f"button click error: {e}")

    def enter(self, *args):
        """Handle mouse enter window to focus."""
        try:
            self.popup.win.focus(warp=False)
            log_test("pointer enter")
        except Exception as e:
            log_test(f"pointer enter error: {e}")

    def open_win(self):
        """Open python repl in internal window."""
        if not self.win_opened:
            self.win_opened = True
            self.cmd_update(self.og_bartext)#"REPL Opened")
            #simple_repl()
            self.popup.place()
            self.popup.unhide()

    """def close_win(self):
        #Close python repl
        if self.win_opened:
            self.win_opened = False
            self.cmd_update("REPL Closed")
            self.leave()"""

    def cmd_update(self, text):
        """Update the text in a TextBox widget."""
        self.update(text)

    def cmd_get(self):
        """Retrieve the text in a TextBox widget."""
        return self.text 


# Helper functions
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
