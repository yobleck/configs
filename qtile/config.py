###YOBLECK's config###
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
###WARNING TODO CMD_ PREFIX IS BEING REMOVED
from typing import List  # noqa: F401
#import subprocess, time

from libqtile import bar, layout, widget, extension, hook, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen  # , KeyChord
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal  # , send_notification #used for popup testing

import accessibility as ac
import desktop_icons
from fah_widget import fah
from floating_window_snapping import move_snap_window
import internal_modifications as int_mod
import py_repl
import quick_settings_menu as qsm
#import window_preview


###Helper functions###
def log_test(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


def vsync_toggle(x):
    # TODO: use qtile.cmd_spawn or lazy to get status. on by default?
    # send_notification(title="test1", message="test2")
    pass


def toggle_bar(qtile, *args):  # Helper function for bar visibility
    qtile.cmd_hide_show_bar(*args)


def parse(text):  # Function for editing displayed wm_name
    for string in [" - YouTube", " \u2014 Mozilla Firefox", " \u2014 Konsole", "  \u2014 Kate", " \u2014 Dolphin", " - Chromium",
                   "Media Player Classic Qute Theater - ", " (UNREGISTERED)"]:
        text = text.replace(string, "")
    return text


"""import subprocess
def z1(qtile):
    log_test("here")
    try:
        subprocess.run(["sh", "/home/yobleck/.config/qtile/z1.sh"], shell=True)
        log_test("here2")
    except Exception as e:
        log_test(e)"""


def cycle_wallpaper(qtile):  # cycle between main wallpaper and black
    if qtile.current_screen.wallpaper == "/home/yobleck/Pictures/382337_4k_dn.png":
        qtile.current_screen.wallpaper = "/home/yobleck/Pictures/black.png"
    elif qtile.current_screen.wallpaper == "/home/yobleck/Pictures/black.png":
        qtile.current_screen.wallpaper = "/home/yobleck/Pictures/382337_4k_dn.png"

    qtile.paint_screen(qtile.current_screen, qtile.current_screen.wallpaper, qtile.current_screen.wallpaper_mode)


def tasklist_kill():  # kill current window when mouse middle clicks on tasklist widget
    for w in qtile.current_screen.bottom.widgets:
        if w.name == "tasklist":
            w.clicked.kill()
            break

# window preview stuff
# try:
#     win_pre = window_preview.window_preview()
# except Exception as e:
#     log_test(e)


###HOOKS###
@hook.subscribe.startup_once
def startup_once_stuff():
    # TODO: move all this stuff to a bash script to improve startup times?
    # configure monitors via nvidia settings. requires mod1+control+r to fix layout
    qtile.cmd_spawn("nvidia-settings --assign \"CurrentMetaMode=DPY-2: 2560x1440_60 +0+0 {ForceCompositionPipeline=On}, DPY-0: 1920x1080_144 +2560+0 {ForceCompositionPipeline=On}\"")
    # loginctl user-status suggests put above line in /etc/X11/xinit/xserverrc
    qtile.cmd_spawn("picom")  # compositor for window animations and transparency

    qtile.cmd_spawn("xinput --set-prop \"pointer:Logitech G602\" \"libinput Accel Profile Enabled\" 0, 1")  # mouse no accel
    qtile.cmd_spawn("xinput --set-prop \"pointer:Logitech G602\" \"libinput Accel Speed\" 0")  # mouse speed

    qtile.cmd_spawn("xset s off -dpms")
    qtile.cmd_spawn("xautolock -time 10 -locker /home/yobleck/.config/qtile/locker.sh")  # lock screen and monitors off
    # TODO: cant manually override while video is playing. pass through argument to shell script? or disable xautolock in manual script?

    qtile.cmd_spawn("/home/yobleck/.config/qtile/polkit_dumb_style/polkit-dumb-agent-style")  # , "-s", "gtk2" #qt5ct located in .bash_profile
    # polkit gui agent for kate, pamac etc #requires kdesu grrrr
    # recompiled for Qt themes TODO: color schemes
    # https://stackoverflow.com/questions/6740333/can-i-run-a-qt-application-with-a-specific-theme #https://cmake.org/runningcmake/

    # subprocess.Popen(["export", "QT_QPA_PLATFORMTHEME=\"qt5ct\""]); #see ~/.bash_profile

    qtile.cmd_spawn("/usr/lib/kdeconnectd")  # kdeconnect daemon
    qtile.cmd_spawn("kdeconnect-indicator")  # kdeconnect taskbar widget icon

    qtile.cmd_spawn("mocp -S")
    # qtile.cmd_spawn("xbindkeys")
    # TODO: sudo pacman -Sy as startup service
    # TODO: disable desktop_scroll service
    # qtile.cmd_spawn("gwe --hide-window")
    #qtile.cmd_spawn("python /home/yobleck/.moc/mpris2_bridge/moc-mpris/moc_mpris.py")  # allows moc to be controlled by other media keys/kdeconnect

    #qtile.cmd_spawn("kill -2 kglobalaccel5")
    #above is killed and allowed to respawn so that qtile keybinds override kde stuff TODO: how to stop said kde stuff from starting
    qtile.cmd_spawn("kill -2 kwalletd5")
    # subprocess.run(["sleep", "2"]) #Needed?
    #TODO plasma-dolphin.service?

    # qtile.cmd_spawn("kill -2 gwe");

    # TODO: plasmawindowed org.kde.plasma.mediacontroller --statusnotifier
    # qtile.cmd_spawn("plasmawindowed org.kde.plasma.mediacontroller --statusnotifier")


@hook.subscribe.startup
def startup_stuff():
    #subprocess.Popen(["xautolock", "-time", "10", "-locker", "/home/yobleck/.config/qtile/locker.sh"])
    qtile.cmd_spawn("xsetroot -cursor_name left_ptr")  # change mouse to breeze cursor
    int_mod.mouse_move(qtile)  # Mouse movements over root window change screen


@hook.subscribe.startup_complete
def startup_complete_stuff():
    pass


@hook.subscribe.shutdown
def shutdown_stuff():
    qtile.cmd_spawn("pkill mocp")
    pass

@hook.subscribe.client_focus
def client_focus_stuff(window):
    # take screenshot of window when focused
    win_pre.screenshot(window.wid)

# @hook.subscribe.client_killed
# def client_killed_stuff(window):
#     # remove screenshot file of window when killed
#     win_pre.clear_file(window.wid)

# @hook.subscribe.client_name_updated
# def client_name_updated_stuff(window):
#     if window == qtile.current_window:
#         win_pre.screenshot(window.wid)


@hook.subscribe.client_managed
def client_managed_stuff(window):
    if window.window.get_wm_class()[0] == "plasmawindowed":
        #log_test(window.window.get_property("WM_NAME", type="STRING", unpack=str))
        #time.sleep(0.5);
        if(window.window.get_name() == "Calendar"):
            #log_test("passed Cal name test")
            #qtile.cmd_spawn("wmctrl -r Calendar -e 0,2332,1223,225,193") # NOTE wmctrl uninstalled
            qtile.cmd_spawn("xdotool search \"Calendar\" windowsize 250 250 windowmove 2310 1166")
            #below doesnt respect different widgets
            #window.cmd_set_position_floating(2333, 1221)
            #window.cmd_set_size_floating(225, 193)

        #if(window.window.get_name() == "Legacy Application Launcher"):  # TODO use setattr to change win.win process_pointer_leave to close window
            #time.sleep(0.5)
            #qtile.cmd_spawn("wmctrl -r \'Application Menu\' -e 0,0,949,273,467")  # old new menu
            #qtile.cmd_spawn("xdotool search \"Legacy Application Launcher\" windowsize 468 612 windowmove 0 802")  # windowsize 416 544

        elif window.window.get_name() == "Audio Volume":
            #time.sleep(0.5);
            qtile.cmd_spawn("xdotool search \"Audio Volume\" windowsize 500 500 windowmove 2060 916")

    elif window.window.get_wm_class()[0] == "subl" and window.window.get_property("WM_NAME", type="STRING", unpack=str) in [[], None, ""]:
        # log_test("sublime detected")
        # log_test(window.window.get_property("WM_NAME", type="STRING", unpack=str))
        # Automatically hide sublime buy license popup
        #if window.window.get_property("WM_NAME", type="STRING", unpack=str) in [[], None, ""]:
            # log_test("killed sublime popup")
        window.kill()

    elif window.group.layout.name == "stack":
        # filter out floating windows including FAHStats 
        w = [w for w in window.group.windows if (False, False) == (w.floating, w.minimized)]
        #log_test(w)
        if len(w) < 2 and window.floating == False:
            window.group.layout.cmd_client_to_stack(1)

    # take screenshot of window for preview when window created
    #win_pre.screenshot(window.wid, 2)


###KEY BINDS###
mod = "mod4"  # TODO change to meta
terminal = guess_terminal()
def tee(s):
    log_test(s)
keys = [
    #Key([mod], "o", lazy.function(win_pre.after_startup), desc="test function"),
    #Key([mod, "shift"], "o", lazy.function(ac.play_audio, "mod o"), desc="test function 2"),
    # Switch between windows in current stack pane
    Key(["mod1"], "Tab", lazy.layout.down(),
        desc="Move focus down in stack pane"),
    Key(["mod1", "shift"], "Tab", lazy.layout.up(),
        desc="Move focus up in stack pane"),

    # move windows around in the columns layout
    Key([mod, "shift"], "Down", lazy.layout.shuffle_down(),
        desc="Move window down in current stack "),
    Key([mod, "shift"], "Up", lazy.layout.shuffle_up(),
        desc="Move window up in current stack "),
    Key([mod, "shift"], "Left", lazy.layout.shuffle_left(),
        desc="Move window left in current stack "),
    Key([mod, "shift"], "Right", lazy.layout.shuffle_right(),
        desc="Move window right in current stack "),

    # Switch window focus to other pane(s) of stack layout
    Key([mod], "space", lazy.layout.next(),
        desc="Switch window focus to other pane(s) of stack"),
    # Move window to another pane in stack layout
    Key([mod, "shift"], "space", lazy.layout.client_to_next(),
        desc="move window to other pane of split stack"),
    # Swap panes of split stack
    Key([mod, "control"], "space", lazy.layout.rotate(),
        desc="swap panes of split stack"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    #Key([mod, "shift"], "Return", lazy.layout.toggle_split(),
        #desc="Toggle between split and unsplit sides of stack"),  # other behavior with columns
    # Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Key([mod], "Return", lazy.spawn("konsole"), desc="Launch terminal"), # --style gtk2

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "Tab", lazy.prev_layout(), desc="Toggle between layouts backwards"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),  # replace with alt f4?

    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload qtile config"),
    Key([mod, "control", "shift"], "r", lazy.restart(), desc="Restart qtile"),
    Key([mod, "control", "shift"], "q", lazy.shutdown(), desc="Shutdown qtile"),
    Key([mod, "mod1"], "space", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key(["control", "mod1"], "space", lazy.spawn("krunner"), desc="launch/open krunner"),
    Key([mod], "p", lazy.run_extension(extension.J4DmenuDesktop(dmenu_lines=10, j4dmenu_generic=False, dmenu_font="Noto Mono",
                                                                dmenu_ignorecase=True, dmenu_bottom=True, j4dmenu_terminal=terminal))),
    Key([mod, "control"], "v", lazy.spawn("sh /home/yobleck/.config/qtile/toggle_vsync.sh"),
        # lazy.function(vsync_toggle),
        desc="toggle nvidia ForceCompositionPipeline"),
    Key([mod, "control"], "b", lazy.function(toggle_bar, "bottom"), desc="toggle bar visibility"),
    Key([mod, "control"], "t", lazy.function(toggle_bar, "top"), desc="toggle bar visibility"),
    Key([mod, "control"], "c", lazy.function(cycle_wallpaper), desc="cycle main and black wallpaper"),
    #Key([mod, "control"], "z", lazy.function(z1), desc="prune url"),

    # Media control
    Key([], "XF86AudioRaiseVolume",
        lazy.spawn("pulseaudio-ctl up"), lazy.spawn("paplay /home/yobleck/Music/volume_change/mc_pop/audio-volume-change.oga")),
    Key([], "XF86AudioLowerVolume",
        lazy.spawn("pulseaudio-ctl down"), lazy.spawn("paplay /home/yobleck/Music/volume_change/mc_pop/audio-volume-change.oga")),
    Key([], "XF86AudioMute",
        lazy.spawn("pulseaudio-ctl mute")),
    Key([], "XF86AudioPlay",
        lazy.spawn("playerctl play-pause")),
    Key([], "XF86AudioNext",
        lazy.spawn("playerctl next")),
    Key([], "XF86AudioPrev",
        lazy.spawn("playerctl previous")),#play next and prev

    # Run various programs
    #KeyChord(["control", "mod1"], "z", [
        Key(["control", "mod1"], "e", lazy.spawn("dolphin"), desc="launch dolphin file manager"),
        Key(["control", "mod1"], "r", lazy.spawn("konsole"), desc="launch konsole"),
        Key(["control", "mod1"], "g", lazy.spawn("chromium"), desc="launch chromium"),
        Key(["control", "mod1"], "h", lazy.spawn("konsole -e htop"), desc="launch htop"),
        Key(["control", "mod1"], "f", lazy.spawn("firefox"), desc="launch firefox"),
        Key(["control", "mod1"], "y", lazy.spawn("konsole -e ~/yt_dwnld.sh"), desc="launch youtube audio downloader"),
        Key(["control", "mod1"], "m", lazy.spawn("sh /home/yobleck/.config/qtile/mocp_launcher.sh"), desc="launch music player"),
        Key(["control", "mod1"], "s", lazy.spawn("steam"), desc="launch steam"),
        #Key(["control", "mod1"], "Escape", lazy.spawn("ksysguard"), desc="launch task manager"),
        Key(["control", "mod1"], "p", lazy.spawn("spectacle"), desc="launch scpectacle"),
        Key([mod], "Print", lazy.spawn("spectacle"), desc="launch scpectacle"),
        # mod + . for emoji selector
    #]),
    # lock screen #https://github.com/Raymo111/i3lock-color/blob/master/examples/lock.sh
    #Key([mod], "l", lazy.spawn("i3lock -n --pass-media-keys --timecolor=00ff00 --datecolor=00ff00 --blur 5 --clock --timestr=\"%H:%M\" --datestr=\"%Y-%m-%d\""),
        #desc="lock screen with i3lock"),
    #Key([mod], "l", lazy.spawn("xautolock -locknow -nowlocker i3lock"), desc="lock screen with i3lock"),
    Key([mod], "l", lazy.spawn("xautolock -locknow -nowlocker /home/yobleck/.config/qtile/locker.sh"), desc="lock screen with i3lock"),
    # work around to turn screen back on after locking: lazy.spawn("xset force reset"),

    # Move mouse with keyboard
    Key([mod, "mod1"], "Left", lazy.spawn("xdotool mousemove_relative -- -10 0"), desc="Move mouse left"),
    Key([mod, "control", "mod1"], "Left", lazy.spawn("xdotool mousemove_relative -- -100 0"), desc="Move mouse left a lot"),
    Key([mod, "mod1"], "Right", lazy.spawn("xdotool mousemove_relative 10 0"), desc="Move mouse right"),
    Key([mod, "control", "mod1"], "Right", lazy.spawn("xdotool mousemove_relative 100 0"), desc="Move mouse right a lot"),
    Key([mod, "mod1"], "Up", lazy.spawn("xdotool mousemove_relative -- 0 -10"), desc="Move mouse up"),
    Key([mod, "control", "mod1"], "Up", lazy.spawn("xdotool mousemove_relative -- 0 -100"), desc="Move mouse up a lot"),
    Key([mod, "mod1"], "Down", lazy.spawn("xdotool mousemove_relative 0 10"), desc="Move mouse down"),
    Key([mod, "control", "mod1"], "Down", lazy.spawn("xdotool mousemove_relative 0 100"), desc="Move mouse down a lot"),
    Key([mod, "control", "mod1"], "Return", lazy.spawn("xdotool click 1"), desc="Mouse left click"),
    Key([mod, "control", "mod1", "shift"], "Return", lazy.spawn("xdotool click 3"), desc="Mouse right click"),
]


###GROUPS AND LAYOUTS###
groups = []
groups.append(Group("web", matches=[Match(wm_class=["mpc-qt", "firefox"])]))
groups.append(Group("2nd", layout="stack", matches=[Match(wm_class=["dolphin"])]))  #, spawn="python /home/yobleck/fah/fah_stats.py"
groups.append(Group("F@H", layout="stack", spawn=["konsole", "FAHControl"]))
#groups.append(Group("htop", spawn="ksysguard"))  # --style gtk2
groups.append(Group("vg", matches=[Match(wm_class=["Steam", "MultiMC", "hl2_linux"])]))  # TODO: add video game match rules 

g_list = {"web": "a", "2nd": "s", "F@H": "d", "vg": "f"}  # "htop": "f",
for g in g_list.items():
    keys.extend([
        Key([mod], g[1], lazy.group[g[0]].toscreen(toggle=False),
            desc="Switch to group " + g[0]),
        Key([mod, "shift"], g[1], lazy.window.togroup(g[0]),
            desc="move focused window to group " + g[0]),
    ])

#log_test("\n\n\ncreating layouts\n");
layouts = [
    layout.Max(),
    layout.Stack(num_stacks=2, border_focus="#00aa00"),
    # Try more layouts by unleashing below layouts.
    # layout.Bsp(),
    layout.Columns(border_focus="#00aa00", border_width=1),
    #layout.Matrix(),
    #layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(previous_on_rm=True, active_bg="#00aa00"),
    # layout.VerticalTile(),
    # layout.Zoomy(),
    # layout.BrowserTab(), #these are just me yobleck messing around
    # layout.BrowserTab2(), #ditto
]
# print(BrowserTab2);


###SCREENS###
widget_defaults = dict(
    font="Noto Mono",
    fontsize=12,
    foreground="#00aa00",
    padding=3,
)
extension_defaults = widget_defaults.copy()


screens = [
    Screen(  # 1920x1080_144
        bottom=bar.Bar(
            [
                widget.CurrentLayout(mouse_callbacks={"Button3": lambda: qtile.cmd_prev_layout(),
                                                      "Button4": lambda: qtile.cmd_prev_layout(),
                                                      "Button5": lambda: qtile.cmd_next_layout()}
                                    ),
                widget.TextBox("|"),
                widget.GroupBox(active="#00aa00", inactive="#004400", block_highlight_text_color="#00aa00", disable_drag=True),
                #TODO: look at source code and find out how to disable click on focused group causing switch to another group
                widget.TextBox("|"),
                widget.Prompt(ignore_dups_history=True),
                widget.Chord(  # multi key binds but not holding all keys down at same time
                             chords_colors={'launch': ("#ff0000", "#ffffff"), }, name_transform=lambda name: name.upper(),
                            ),
                widget.TaskList(border="#00aa00", parse_text=parse,
                                mouse_callbacks={"Button2": tasklist_kill}#, "Button3": win_pre.show_preview}
                                ),  # TODO: test padding and margin with east asian chars
                #widget.WindowName(parse_text=parse),
                #widget.WindowTabs(parse_text=parse),
                widget.Notify(foreground="#00aa00", foreground_low="#004400", max_chars=100),
                widget.Systray(),
                #custom_command=("pamac checkupdates",3)   "sh /home/yobleck/.config/qtile/test.sh 1"   ("pamac checkupdates -q", 0)
                #widget.CheckUpdates(distro="Arch", execute="pamac-manager", update_interval="600", no_update_string=" U ",
                                    #colour_no_updates="#00aa00", colour_have_updates="#aa0000", custom_command_modify = (lambda x: x/2-1),
                                    #),
                widget.CheckUpdates(custom_command="pamac checkupdates -q; echo -n",  # custom_command_modify = (lambda x: x/2-1),
                                    execute="pamac-manager", update_interval="600", display_format="U:{updates}",
                                    no_update_string=" U ", colour_no_updates="#00aa00", colour_have_updates="#880000",
                                    ),  # TODO error_string when added in next update
                widget.Clock(format='%Y-%m-%dT%H:%M', fontsize=18, update_interval=60,
                             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.calendar")}
                             ),
                #https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
                #widget.CurrentScreen(mouse_callbacks={"Button1": lambda: qtile.focus_screen(0)}, font="Noto Mono"),
            ],
            24,
            background=["#00000000", "#00000022", "#00000055", "#00330088"],  # bar background
        ),
        wallpaper="/home/yobleck/Pictures/382337_4k_dn.png",
        wallpaper_mode="fill",
        #width=1920,
        #height=1080,
        #x=2560,
    ),
    Screen(  # 2560x1440_60
        bottom=bar.Bar(
            [
                #widget.LaunchBar(progs=[("start", "plasmawindowed org.kde.plasma.kicker", "kde start menu")],
                                 #default_icon="/usr/share/icons/manjaro/maia/maia.svg"),
                #widget.Image(filename="/usr/share/icons/manjaro/green/24x24.png",  # green.svg
                             #mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.kickofflegacy")}),
                widget.CurrentLayout(mouse_callbacks={"Button3": lambda: qtile.cmd_prev_layout(),
                                                      "Button4": lambda: qtile.cmd_prev_layout(),
                                                      "Button5": lambda: qtile.cmd_next_layout()}
                                    ),
                widget.TextBox("|"),
                widget.GroupBox(active="#00aa00", inactive="#004400", block_highlight_text_color="#00aa00", disable_drag=True),
                widget.TextBox("|"),
                widget.TaskList(border="#00aa00",parse_text=parse,
                                mouse_callbacks={"Button2": tasklist_kill}#, "Button3": win_pre.show_preview}
                                ),
                widget.Moc(foreground="#00aa00", update_interval=2,
                           mouse_callbacks={"Button3": lambda: qtile.cmd_spawn("mocp -s"),
                                            "Button4": lambda: qtile.cmd_spawn("mocp -r"),
                                            "Button5": lambda: qtile.cmd_spawn("mocp -f"),
                                            "Button8": lambda: qtile.cmd_spawn("mocp -k -2"),
                                            "Button9": lambda: qtile.cmd_spawn("mocp -k 2"),
                                            }
                           ),
                widget.Volume(volume_down_command="pulseaudio-ctl down",
                              volume_up_command="pulseaudio-ctl up",
                              mute_command="pulseaudio-ctl mute",
                              mouse_callbacks={"Button3": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.volume")}
                              ),
                widget.Clock(format='%a %H:%M', fontsize=18, update_interval=30,
                             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.calendar")}
                             ),
                #widget.CurrentScreen(mouse_callbacks={"Button1": lambda: qtile.focus_screen(1)}, font="Noto Mono"),
            ],
            24,
            background=["#00000000", "#00000022", "#00000055", "#00330088"],  # bar background
        ),
        top=bar.Bar(
            [
                widget.Image(filename="/home/yobleck/.config/qtile/icons/24x24.png",
                             mouse_callbacks={"Button1": int_mod.simple_start_menu}),  #  for text version noto fonts only
                fah.FaH(username="yobleck", json=True, is_popup=True, popup_struct=(5,1330,160,80,"#00aa00",1), update_interval=600),
                # qsm.Menu(button_list=[
                #     qsm.Button(text="Brightness Down", icon_path="~/.config/qtile/icons/low-brightness.svg", is_toggle=False, grid_pos=(0,0)),
                #     qsm.Button(text="Brightness Up", icon_path="~/.config/qtile/icons/high-brightness.svg", is_toggle=False, grid_pos=(1,0)),
                #     qsm.Button(text="Flashlight", icon_path="~/.config/qtile/icons/flashlight-on.svg", is_toggle=True, grid_pos=(2,0)),
                #     qsm.Button(text="Screen Rotation", icon_path="~/.config/qtile/icons/smartphone.svg", is_toggle=True, grid_pos=(0,1)),
                #     qsm.Button(text="Wifi", icon_path="~/.config/qtile/icons/network-wireless-connected-100.svg", is_toggle=True, grid_pos=(1,1)),
                #     qsm.Button(text="Bluetooth", icon_path="~/.config/qtile/icons/network-bluetooth.svg", is_toggle=True, grid_pos=(2,1)),
                #     ]),
                widget.Spacer(),
                py_repl.REPL(text="", fontsize=18,
                             win_foreground="#00aa00", win_pos=(100,100), win_size=(800,800),
                             win_font="Noto Mono", win_bordercolor=["#0000ff", "#0000ff", "#ffff00", "#ffff00"], win_borderwidth=4,
                             win_opacity=0.9  # text=" PY REPL"
                             ),
                # TODO kde system settings icon
                widget.TextBox(" "),
                widget.Image(filename="/home/yobleck/.config/qtile/icons/htop.svg",
                             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("konsole -e htop")}
                             ),
                widget.CPU(format="| CPU: {load_percent:04.1f}% {freq_current}GHz", update_interval=2),
                widget.ThermalSensor(foreground="#00aa00", font="Noto Mono", tag_sensor="Tctl", threshold=80, update_interval=2),
                widget.CPUGraph(frequency=2, fill_color="#00330055", graph_color="#00aa00"),
                widget.Memory(format="| Mem: {MemUsed:05.0f}{mm}B", update_interval=2),
                widget.Net(format="| Net: {down} ↓↑ {up}", update_interval=2),
                widget.NetGraph(frequency=2, fill_color="#00330055", graph_color="#00aa00"),
                widget.NvidiaSensors(format="| GPU: Fan:{fan_speed}, {temp}°C", foreground="#00aa00", threshold=80, update_interval=2),
            ],
            24,
            background=["#00330088", "#00000055", "#00000022", "#00000000"],
        ),
        wallpaper="/home/yobleck/Pictures/black.png",
        wallpaper_mode="fill",
        #width=2560,
        #height=1440,
    ),
]


###Misc settings###
# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", move_snap_window(snap_dist=20),# lazy.window.set_position_floating(border_snapping=True, snap_dist=20),
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
    Match(wm_class='confirm'),
    Match(wm_class='dialog'),
    Match(wm_class='download'),
    Match(wm_class='error'),
    Match(wm_class='file_progress'),
    Match(wm_class='notification'),
    Match(wm_class='splash'),
    Match(wm_class='toolbar'),
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(wm_class='popup_menu'),
    Match(wm_class="FAHStats"),  # folding @ home stats widget
    Match(wm_class="polkit-kde-authentication-agent-1"),  # WM_CLASS(STRING) = "polkit-kde-authentication-agent-1", ditto
    Match(wm_class="krunner"),
    Match(wm_class="kcalc"),
    Match(wm_class="plasmawindowed"),
    Match(wm_class="Panda3D"),
    Match(wm_class="Xephyr"),
    Match(wm_class="Vncviewer"),
    Match(wm_class="visualboyadvance-m"),
    Match(wm_class="megasync"),
    Match(title="Event Tester"),
    Match(title="Default - Wine desktop"),
    Match(title="SAF"),
],
    no_reposition_rules=[  # TODO: https://github.com/qtile/qtile/blob/579d189b244efea590dd2447110516cd413f10de/libqtile/layout/floating.py#L274
        Match(wm_class="FAHStats"),
        # Match(wm_class="plasmawindowed"), #only sort of works
], border_width=1)


auto_fullscreen = True
focus_on_window_activation = "smart"
#reconfigure_screens = True  # doesn't work with changes through nvidia settings?
auto_minimize = True  # some games auto min when focus lost


# Faked because java bs
wmname = "LG3D"
