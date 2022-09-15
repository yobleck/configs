# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import subprocess
import time
from typing import List  # noqa: F401

from libqtile import bar, hook, layout, qtile, widget
from libqtile.config import Click, Drag, DropDown, Group, Key, Match, ScratchPad, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

import desktop_icons
import internal_modifications as int_mod
import quick_settings_menu as qsm

# helper functions
def log(i):
    with open("/home/alarm/.config/qtile/qtile_log.txt", "a") as f:
        f.write(f"{i}\n")


def bat_func():
	out = ""
	with open("/sys/class/power_supply/axp20x-battery/status", "r") as f:
		stat = f.read().strip("\n")
	if stat == "Charging":
		out += "^"
	elif stat == "Discharging":
		out += "v"
	else:
		out += "?"
	with open("/sys/class/power_supply/axp20x-battery/capacity", "r") as f:
		out += f.read().strip("\n") + "%"
	return out


def screen_rotate():
    rotation = [x for x in subprocess.check_output(["xrandr", "--query", "--verbose"]).decode().split("\n") if "DSI-1" in x][0].split()[5]
    if rotation == "normal":
        qtile.cmd_spawn("xrandr -o right")
        qtile.cmd_spawn("xinput set-prop 'pointer:Goodix Capacitive TouchScreen' --type=float 'Coordinate Transformation Matrix' 0 1 0 -1 0 1 0 0 1")
        # restart lisgd with -o 1
    elif rotation == "right":
        qtile.cmd_spawn("xrandr -o normal")
        qtile.cmd_spawn("xinput set-prop 'pointer:Goodix Capacitive TouchScreen' --type=float 'Coordinate Transformation Matrix' 0 0 0 0 0 0 0 0 0")
        # restart lisgd with -o 0


def screen_on_off(qtile):
    if time.time() > os.stat("/home/alarm/.config/qtile/last_sleep_time").st_mtime + 1:
        state = subprocess.check_output(["xinput", "list-props", "12"]).decode().split("\n")
        if state[0] == "Device \'Goodix Capacitive TouchScreen\':":
            log(state[1][-1])
            # check if touch screen is enabled or not
            if state[1][-1] == "1":
                qtile.cmd_spawn("xinput disable 12")
                qtile.cmd_spawn("xset dpms force off")
            elif state[1][-1] == "0":
                qtile.cmd_spawn("xinput enable 12")
                qtile.cmd_spawn("xset dpms force on")
        else:
            log("device 12 is not the touch screen")
    else:  # make sure touch screen is enabled after sleep
        qtile.cmd_spawn("xinput enable 12")


@hook.subscribe.startup_once
def initial_startup():
    #qtile.cmd_spawn("lisgd -d /dev/input/event1 -g '2,UD,*,*,R,xdotool click 3'")  xdotool key Down/Up/Left/Right multiple times
    #qtile.cmd_spawn("onboard")
    #qtile.cmd_spawn("xrandr --output DSI-1 --brightness 0.7")
    qtile.cmd_spawn("xautolock -time 1 -locker /home/alarm/.config/qtile/locker.sh")

@hook.subscribe.startup_complete
def startup_complete_stuff():
    desktop_icons.desktop_icons([
    desktop_icons.simple_icon("ST", "/home/alarm/.config/qtile/icons/xterm.svg", "st -e xonsh", 50, 100, 100),
    desktop_icons.simple_icon("NNN", "/home/alarm/.config/qtile/icons/xterm.svg", "st -e nnn -H", 250, 100, 100),
    desktop_icons.simple_icon("Firefox", "/usr/share/icons/hicolor/128x128/apps/firefox.png", "firefox", 450, 100, 100)
    ])

mod = "mod4"
terminal = guess_terminal()

keys = [
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(),
        desc="Move window focus to other window"),

    Key(["mod1"], "Tab", lazy.layout.down(),
        desc="Move focus down in stack pane"),
    Key(["mod1", "shift"], "Tab", lazy.layout.up(),
        desc="Move focus up in stack pane"),
    Key([mod, "shift"], "space", lazy.layout.client_to_next(),
        desc="Move window to other pane of split stack"),

    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
        desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
        desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
        desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(),
        desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(),
        desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(),
        desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    #Key([mod, "shift"], "Return", lazy.layout.toggle_split(),
        #desc="Toggle between split and unsplit sides of stack"),

    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),

    Key([mod, "control", "shift"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "control", "shift"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([], "XF86PowerOff", lazy.function(screen_on_off), desc="Power button"),
    Key(["mod1"], "space", lazy.spawncmd(),
        desc="Spawn a command using a prompt widget"),
	Key([], "XF86AudioRaiseVolume", lazy.spawn("pulsemixer --change-volume +5"), desc="Volume up"),
    Key([], "XF86AudioLowerVolume", lazy.spawn("pulsemixer --change-volume -5"), desc="Volume down"),
]

groups = [Group(i) for i in "1234"]

for i in groups:
    keys.extend([
        # mod1 + letter of group = switch to group
        Key([mod], i.name, lazy.group[i.name].toscreen(),
            desc="Switch to group {}".format(i.name)),

        # mod1 + shift + letter of group = switch to & move focused window to group
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name, switch_group=True),
            desc="Switch to & move focused window to group {}".format(i.name)),
        # Or, use below if you prefer not to switch to that group.
        # # mod1 + shift + letter of group = move focused window to group
        # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
        #     desc="move focused window to group {}".format(i.name)),
    ])

groups.append(ScratchPad("scratchpad", [DropDown("vkbd", "onboard", width=1.0, height=0.5, x=0.0, y=0.5)]))

layouts = [
    # layout.Columns(border_focus_stack=['#d75f5f', '#8f3d3d'], border_width=4),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
     layout.Stack(num_stacks=2),
    # layout.TreeTab(),
     layout.VerticalTile(),
]

widget_defaults = dict(
    font='sans',
    fontsize=24,
    padding=3,
	foreground="#ff9900",
    background="#000000dd",
)
extension_defaults = widget_defaults.copy()


screens = [
    Screen(
        bottom=bar.Bar(
            [
                widget.CurrentLayout(font="Noto Mono"),
                widget.GroupBox(padding_x=15),
                widget.Prompt(),
                #widget.WindowName(mouse_callbacks={"Button1": lazy.layout.down()}),
                widget.TaskList(max_title_width=360),
                widget.Chord(
                    chords_colors={
                        'launch': ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                widget.Notify(),
		        widget.Systray(),
                widget.TextBox("vkbd", mouse_callbacks={"Button1": lazy.group["scratchpad"].dropdown_toggle("vkbd")}),
                #widget.QuickExit(),
            ],
            48,
			background="#aa000011",
        ),
		top=bar.Bar(
			[
				widget.Clock(format="%Y-%m-%dT%H:%M"),
				widget.Spacer(),
                qsm.Menu(button_list=[
                    qsm.Button(text="Brightness Down", icon_path="~/.config/qtile/icons/low-brightness.svg", is_toggle=False, cmd="brightnessctl s 10%-", grid_pos=(0,0)),
                    qsm.Button(text="Brightness Up", icon_path="~/.config/qtile/icons/high-brightness.svg", is_toggle=False, cmd="brightnessctl s +10%", grid_pos=(1,0)),
                    qsm.Button(text="Flashlight", icon_path="~/.config/qtile/icons/flashlight-on.svg", is_toggle=True, grid_pos=(2,0)),
                    qsm.Button(text="Screen Rotation", icon_path="~/.config/qtile/icons/smartphone.svg", is_toggle=False, cmd=screen_rotate, grid_pos=(0,1)),
                    qsm.Button(text="Wifi", icon_path="~/.config/qtile/icons/network-wireless-connected-100.svg", is_toggle=False, cmd="rfkill toggle wlan", grid_pos=(1,1)),
                    qsm.Button(text="Bluetooth", icon_path="~/.config/qtile/icons/network-bluetooth.svg", is_toggle=False, cmd="rfkill toggle bluetooth", grid_pos=(2,1)),
                ]),
                widget.Spacer(),
                widget.CPU(format="{load_percent:04.1f}%", update_interval=2),
				widget.GenPollText(func=bat_func, update_interval=60),
				widget.Image(filename="/home/alarm/.config/qtile/icons/pine64_orange.svg",
							mouse_callbacks={"Button1": int_mod.simple_start_menu}),
			],
			36,
			background="#00000011",
		),
        wallpaper="/home/alarm/unnamed1.jpg",
        wallpaper_mode="fill",
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    *layout.Floating.default_float_rules,
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
    #Match(wm_class="onboard"),
],
no_reposition_rules=[Match(wm_class="svkbd"),
                     #Match(wm_class="onboard"),
                    ],
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

wmname = "Qtile"
