# __YOBLECK's config__
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
# WARNING TODO CMD_ PREFIX IS BEING REMOVED
import os
import re
from typing import List  # noqa: F401
# import subprocess
# import time

from libqtile import bar, layout, widget, extension, hook, qtile
from libqtile.config import Click, Drag, Group, InvertMatch, Key, Match, MatchAll, Screen  # , KeyChord
from libqtile.lazy import lazy
# from libqtile.utils import guess_terminal  # , send_notification #used for popup testing

# import accessibility as ac
# import desktop_icons
from fah_widget import fah
from floating_window_snapping import move_snap_window
import internal_modifications as int_mod
from layout.columns_tweak import Col
import pseudo_screen_locker as psl
# import pseudo_screen_locker_im as psl_im
import py_repl
# import voice_control
# import quick_settings_menu as qsm
# import screen_locker
import start_menu
# import window_preview


# __Helper functions__
def log_test(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


def vsync_toggle(x):
    # TODO: use qtile.cmd_spawn or lazy to get status. on by default?
    # send_notification(title="test1", message="test2")
    pass


def reload_nvidia(qtile):
    qtile.spawn("nvidia-settings --assign CurrentMetaMode='DPY-1: 2560x1440_165 @2560x1440 +2560+0 {ForceCompositionPipeline=On, ViewPortIn=2560x1440, ViewPortOut=2560x1440+0+0}, DPY-3: nvidia-auto-select @2560x1440 +0+0 {ForceCompositionPipeline=On, ViewPortIn=2560x1440, ViewPortOut=2560x1440+0+0}'")


def toggle_bar(qtile, *args):  # Helper function for bar visibility
    qtile.hide_show_bar(*args)  # cmd_


def parse(text):  # Function for editing displayed wm_name
    for string in [" - YouTube", " \u2014 Mozilla Firefox", " \u2014 Konsole", "  \u2014 Kate",
                   " \u2014 Dolphin", " - Chromium", " - Thunar", " - Sublime Text (UNREGISTERED)",
                   "Media Player Classic Qute Theater - ", "yobleck@yobleck: ",
                   " - mpv"]:
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
        if w.name == "tasklist" and w.clicked:
            w.clicked.kill()
            break


def tasklist_minimize():  # minimize current window when mouse right clicks on tasklist widget
    for w in qtile.current_screen.bottom.widgets:
        if w.name == "tasklist" and w.clicked:
            w.clicked.toggle_minimize()
            break


if qtile.core.info()["backend"] == "x11":
    # temp_path: str = "/home/yobleck/Pictures/transparency/video/flou/11/"  # NOTE end path with /
    # temp_file_list: list[str] = []
    # for x in range(1, 17, 1):  # make sure to change this to the number of frames + 1
    #     temp_file_list.append(f"{temp_path}{x:03d}_rembg.png")  # _out or _rembg  sometimes 00
    sc = psl.PseudoScreenLocker(
        image_paths=["/home/yobleck/Pictures/tjbxp4i12v5a1_transparent2.png"],
        # image_paths=["/home/yobleck/Pictures/834420.png", "/home/yobleck/Pictures/834420_bonfire.png"],
        # image_paths=["/home/yobleck/Pictures/transparency/new_folder_2/pajama_fox_trans.png"],
        # image_paths=temp_file_list,
        image_size=(1440, 2560),
        font="Hack", fontsize=24, foreground="#00aa00", background="#000000aa", text_pos=(1100, 780),
        fake_password="lock",
        key_bind=(["mod4"], "o"),
        update_interval=1.0)
    # sc2 = psl_im.PseudoScreenLockerIM(
    #     # image_paths=["/home/yobleck/Pictures/tjbxp4i12v5a1_transparent2.png"],
    #     # image_size=(1440, 2560),
    #     font="Hack", font_size=24, foreground="#00aa00", background="#00000000", text_pos=(1100, 780),
    #     fake_password="lock",
    #     key_bind=(["mod4"], "i"),
    #     update_interval=1.0)


# window preview stuff
# try:
#     win_pre = window_preview.window_preview()
# except Exception as e:
#     log_test(e)


# __HOOKS__
@hook.subscribe.startup_once
def startup_once_stuff():
    if qtile.core.info()["backend"] == "x11":
        # TODO: move all this stuff to a bash script to improve startup times?
        # configure monitors via nvidia settings. requires mod1+control+r to fix layout
        # old 1080p one qtile.cmd_spawn("nvidia-settings --assign \"CurrentMetaMode=DPY-2: 2560x1440_60 +0+0 {ForceCompositionPipeline=On}, DPY-0: 1920x1080_144 +2560+0 {ForceCompositionPipeline=On}\"")
        # qtile.spawn("nvidia-settings --assign CurrentMetaMode='DPY-1: 2560x1440_165 @2560x1440 +2560+0 {ForceCompositionPipeline=On, ViewPortIn=2560x1440, ViewPortOut=2560x1440+0+0}, DPY-3: nvidia-auto-select @2560x1440 +0+0 {ForceCompositionPipeline=On, ViewPortIn=2560x1440, ViewPortOut=2560x1440+0+0}'")
        qtile.spawn("nvidia-settings --assign CurrentMetaMode='DPY-4: 2560x1440_60 @2560x1440 +0+0 {ViewPortIn=2560x1440, ViewPortOut=2560x1440+0+0, ForceCompositionPipeline=On}, DPY-1: 2560x1440_165 @2560x1440 +2560+0 {ViewPortIn=2560x1440, ViewPortOut=2560x1440+0+0, ForceCompositionPipeline=On}'")
        # qtile.cmd_spawn("xrandr --output DP-0 --primary --mode 2560x1440 --rate 165 --output DP-2 --mode 2560x1440 --rate 60 --left-of DP-0")
        # loginctl user-status suggests put above line in /etc/X11/xinit/xserverrc
        qtile.spawn("picom")  # compositor for window animations and transparency

        qtile.spawn("xinput --set-prop \"pointer:Logitech G602\" \"libinput Accel Profile Enabled\" 0, 1, 0")  # mouse no accel
        qtile.spawn("xinput --set-prop \"pointer:Logitech G602\" \"libinput Accel Speed\" 0")  # mouse speed
        # qtile.spawn("setxkbmap -option ctrl:nocaps -option compose:ralt")
        # moved to /etc/X11/xorg.conf.d/00-keyboard.conf also try /etc/vconsole.conf or /etc/default/keyboard

        qtile.spawn("xset s off -dpms")
        qtile.spawn("xautolock -time 10 -locker /home/yobleck/.config/qtile/locker.sh")  # lock screen and monitors off
        # TODO: cant manually override while video is playing. pass through argument to shell script? or disable xautolock in manual script?

        qtile.spawn("xsetroot -cursor_name left_ptr")
        qtile.spawn("xrdb -merge /home/yobleck/.Xresources")

    # BUG not working? requires kdesu?
    # qtile.spawn("/home/yobleck/.config/qtile/polkit_dumb_style/polkit-dumb-agent-style")  # , "-s", "gtk2" #qt5ct located in .bash_profile
    # qtile.spawn("/usr/lib/mate-polkit/polkit-mate-authentication-agent-1")
    qtile.spawn("/usr/lib/xfce-polkit/xfce-polkit")
    # polkit gui agent for kate, pamac etc #requires kdesu grrrr
    # recompiled for Qt themes TODO: color schemes
    # https://stackoverflow.com/questions/6740333/can-i-run-a-qt-application-with-a-specific-theme #https://cmake.org/runningcmake/

    # subprocess.Popen(["export", "QT_QPA_PLATFORMTHEME=\"qt5ct\""]); #see ~/.bash_profile

    # qtile.spawn("/usr/bin/kdeconnectd")  # kdeconnect daemon
    # qtile.spawn("kdeconnect-indicator")  # kdeconnect taskbar widget icon
    # qtile.spawn("mocp -S")  # old and broken. recompile from scratch? find new player?
    # qtile.cmd_spawn("gwe --hide-window")
    # qtile.cmd_spawn("python /home/yobleck/.moc/mpris2_bridge/moc-mpris/moc_mpris.py")  # allows moc to be controlled by other media keys/kdeconnect

    # qtile.cmd_spawn("kill -2 gwe");


@hook.subscribe.startup
def startup_stuff():
    if qtile.core.info()["backend"] == "x11":
        # subprocess.Popen(["xautolock", "-time", "10", "-locker", "/home/yobleck/.config/qtile/locker.sh"])
        # log_test("change cursor size?")
        # log_test(os.environ)
        qtile.spawn("xsetroot -cursor_name left_ptr", shell=True)  # change mouse to breeze cursor
    # log_test(f"x: {x}")
    int_mod.mouse_move(qtile)  # Mouse movements over root window change screen


@hook.subscribe.startup_complete
def startup_complete_stuff():
    sc.load_images()  # process images after qtile finishes loading to avoid startup lag


@hook.subscribe.shutdown
def shutdown_stuff():
    qtile.spawn("pkill mocp")
    pass


# @hook.subscribe.user("psl_lock_hook")
# def psl_hook():
#     sc.fire_hook()

# @hook.subscribe.client_focus
# def client_focus_stuff(window):
#     # take screenshot of window when focused
#     win_pre.screenshot(window.wid)

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
    # if window.window.get_wm_class()[0] == "plasmawindowed":
    #     if window.window.get_name() == "Audio Volume":
    #         # time.sleep(0.5);
    #         qtile.spawn("xdotool search \"Audio Volume\" windowsize 500 500 windowmove 2060 916")
    if window.window.get_wm_class()[0] == "pavucontrol-qt":
        qtile.spawn("xdotool search \"Volume Control\" windowsize 800 500 windowmove 1758 914")

    elif window.window.get_wm_class()[0] == "sublime_text" and window.window.get_property("WM_NAME", type="STRING", unpack=str) in [[], None, ""]:
        # log_test("sublime detected")
        # log_test(window.window.get_property("WM_NAME", type="STRING", unpack=str))
        # Automatically hide sublime buy license popup
        # if window.window.get_property("WM_NAME", type="STRING", unpack=str) in [[], None, ""]:
        #     log_test("killed sublime popup")
        # NOTE this auto kills the buy license popup window but also kills error messages and the save before quit popup
        window.kill()
        # pass

    # take screenshot of window for preview when window created
    # win_pre.screenshot(window.wid, 2)


# __KEY BINDS__
mod = "mod4"  # TODO change to meta
terminal = "kitty"  # guess_terminal()

keys = [
    # Key([mod], "o", lazy.function(sc.lock), desc="test function"),
    # Key([mod, "shift"], "o", lazy.function(ac.play_audio, "mod o"), desc="test function 2"),

    # Cycle through windows
    Key(["mod1"], "Tab", lazy.layout.down(),
        desc="Cycle through all windows"),
    Key(["mod1", "shift"], "Tab", lazy.layout.up(),
        desc="Cycle through all windows in reverse"),
    Key([mod], "space", lazy.layout.next(),
        desc="Cycle through windows in column"),
    Key([mod, "shift"], "space", lazy.layout.previous(),
        desc="Cycle through windows in column in reverse"),

    # Move windows around in the columns layout
    Key([mod, "shift"], "Down", lazy.layout.shuffle_down(),
        desc="Move window down in current stack"),
    Key([mod, "shift"], "Up", lazy.layout.shuffle_up(),
        desc="Move window up in current stack"),
    Key([mod, "shift"], "Left", lazy.layout.shuffle_left(),
        desc="Move window left in current stack"),
    Key([mod, "shift"], "Right", lazy.layout.shuffle_right(),
        desc="Move window right in current stack"),

    # Adjust width of columns
    Key([mod, "control"], "Left", lazy.layout.grow_left(),
        desc="Adjust column to the left"),
    Key([mod, "control"], "Right", lazy.layout.grow_right(),
        desc="Adjust column to the right"),

    Key([mod], "Return", lazy.layout.toggle_split()),
    Key([mod, "shift"], "l", lazy.layout.client_to_next(),
        desc="move window to other pane of split stack"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "Tab", lazy.prev_layout(), desc="Toggle between layouts in reverse"),

    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),  # replace with alt f4?

    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload qtile config"),
    Key([mod, "control", "shift"], "r", lazy.restart(), desc="Restart qtile"),
    Key([mod, "control", "shift"], "q", lazy.shutdown(), desc="Shutdown qtile"),
    Key([mod, "control", "shift"], "b", lazy.function(reload_nvidia), desc="reload nvidia driver"),

    Key([mod, "mod1"], "space", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    # Key(["control", "mod1"], "space", lazy.spawn("krunner"), desc="launch/open krunner"),
    Key([mod], "p", lazy.run_extension(extension.J4DmenuDesktop(dmenu_lines=10, j4dmenu_generic=False, dmenu_font="Hack",
                                                                dmenu_ignorecase=True, dmenu_bottom=True, j4dmenu_terminal=terminal))),

    # Key([mod, "control"], "v", lazy.spawn("sh /home/yobleck/.config/qtile/toggle_vsync.sh"), desc="toggle nvidia ForceCompositionPipeline"),
    Key([mod, "control"], "b", lazy.function(toggle_bar, "bottom"), desc="toggle bar visibility"),
    Key([mod, "control"], "t", lazy.function(toggle_bar, "top"), desc="toggle bar visibility"),
    Key([mod, "control"], "c", lazy.function(cycle_wallpaper), desc="cycle main and black wallpaper"),
    # Key([mod, "control"], "z", lazy.function(z1), desc="prune url"),

    # Media control
    Key([], "XF86AudioRaiseVolume",
        lazy.spawn("pamixer -i 5"), lazy.spawn("paplay /home/yobleck/Music/volume_change/mc_pop/audio-volume-change.oga")),
    Key([], "XF86AudioLowerVolume",
        lazy.spawn("pamixer -d 5"), lazy.spawn("paplay /home/yobleck/Music/volume_change/mc_pop/audio-volume-change.oga")),
    Key([], "XF86AudioMute",
        lazy.spawn("pamixer -t")),
    Key([], "XF86AudioPlay",
        lazy.spawn("playerctl play-pause")),
    Key([], "XF86AudioNext",
        lazy.spawn("playerctl next")),
    Key([], "XF86AudioPrev",
        lazy.spawn("playerctl previous")),  # play next and prev

    # Run various programs
    # nnn envars  $NNN_TRASH=1 $NNN_PLUG='p:mocplay;k:kdeconnect;d:!dragon-drag-and-drop -x $nnn*;x:dnd'
    # Key(["control", "mod1"], "e", lazy.spawn(f"{terminal} nnn -H -J -T v -A"), desc="launch nnn"),
    Key(["control", "mod1"], "e", lazy.spawn("thunar"), desc="launch thunar"),
    Key(["control", "mod1"], "r", lazy.spawn(terminal), desc="launch terminal emulator"),
    # Key(["control", "mod1"], "g", lazy.spawn("chromium"), desc="launch chromium"),
    Key(["control", "mod1"], "h", lazy.spawn(f"{terminal} btm"), desc="launch process manager"),
    Key(["control", "mod1"], "c", lazy.spawn(f"{terminal} --name qalc --title qalc \
        -o remember_window_size=no -o initial_window_width=500 -o initial_window_height=500 qalc"), desc="launch qalculate"),
    Key(["control", "shift"], "Escape", lazy.spawn(f"{terminal} btm"), desc="launch task manager"),
    Key(["control", "mod1"], "f", lazy.spawn("firefox"), desc="launch Firefox"),
    Key(["control", "mod1"], "y", lazy.spawn(f"{terminal} /home/yobleck/yt_dwnld.sh"), desc="launch YouTube audio downloader"),
    Key(["control", "mod1"], "m", lazy.spawn("sh /home/yobleck/.config/qtile/mocp_launcher.sh"), desc="launch music player"),
    Key(["control", "mod1"], "s", lazy.spawn("steam"), desc="launch steam"),
    Key(["control", "mod1"], "p", lazy.spawn("flameshot gui"), desc="launch screen shot tool"),
    # Key(["control", "mod1"], "z", lazy.spawn("/home/yobleck/ai/llama/training_data/screenshot.sh"), desc="launch spectacle"),  # remove once done with llama
    Key([mod], "Print", lazy.spawn("flameshot gui"), desc="launch screen shot tool"),
    Key([mod], "c", lazy.spawn("xdotool key Menu"), desc="menu key workaround for nuphy air 75 assistant super+c key"),
    # mod + . for emoji selector

    # lock screen #https://github.com/Raymo111/i3lock-color/blob/master/examples/lock.sh
    Key([mod], "l", lazy.spawn("xautolock -locknow -nowlocker /home/yobleck/.config/qtile/locker.sh"), desc="lock screen"),
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


# __GROUPS AND LAYOUTS__
groups = []
groups.append(Group("1st", matches=[Match(wm_class=re.compile(r"^(mpc\-qt|mpv)$"))], screen_affinity=0))  #
groups.append(Group("2nd", layout="col", matches=[Match(wm_class=re.compile(r"^(dolphin-emu)$"))], screen_affinity=1))  # , spawn="python /home/yobleck/fah/fah_stats.py"
groups.append(Group("3rd", layout="col"))  # , spawn=[terminal, "FAHControl"]
groups.append(Group("vg", matches=[Match(wm_class=re.compile(r"^(steam|polymc|hl2_linux|steam_app_1888160)$"))]))  # TODO: add video game match rules 
# 
g_list = {"1st": "a", "2nd": "s", "3rd": "d", "vg": "f"}
for g in g_list.items():
    keys.extend([
        Key([mod], g[1], lazy.group[g[0]].toscreen(toggle=False),
            desc="Switch to group " + g[0]),
        Key([mod, "shift"], g[1], lazy.window.togroup(g[0]),
            desc="move focused window to group " + g[0]),
    ])


layouts = [
    layout.Max(),
    # layout.Stack(num_stacks=2, border_focus="#00aa00"),
    # layout.Columns(border_focus="#00aa00", border_focus_stack="#00aa00", border_normal="#000000", border_width=1),
    Col(border_focus="#00aa00", border_focus_stack="#00aa00", border_normal="#000000", border_width=1, fair=True, min_columns=2),
]


# __SCREENS__
widget_defaults = dict(
    font="Hack",
    fontsize=12,
    foreground="#00aa00",  # steam green #4C5844
    padding=3,
)
extension_defaults = widget_defaults.copy()


screens = [
    Screen(  # 2560x1440_165
        bottom=bar.Bar(
            [
                widget.CurrentLayout(mouse_callbacks={"Button3": lambda: qtile.prev_layout(),
                                                      "Button4": lambda: qtile.prev_layout(),
                                                      "Button5": lambda: qtile.next_layout()}
                                     ),
                widget.TextBox("|"),
                widget.GroupBox(active="#00aa00", inactive="#004400", block_highlight_text_color="#00aa00", disable_drag=True),
                # TODO: look at source code and find out how to disable click on focused group causing switch to another group
                widget.TextBox("|"),
                widget.Prompt(ignore_dups_history=True),
                # widget.Chord(  # multi key binds but not holding all keys down at same time
                #     chords_colors={'launch': ("#ff0000", "#ffffff"), }, name_transform=lambda name: name.upper(),
                # ),
                widget.TaskList(border="#00aa00", parse_text=parse,
                                mouse_callbacks={"Button2": tasklist_kill, "Button3": tasklist_minimize},  # , "Button3": win_pre.show_preview}
                                unfocused_border="#004400"
                                ),  # TODO: test padding and margin with east asian chars
                # widget.WindowName(parse_text=parse),
                # widget.WindowTabs(parse_text=parse),
                widget.Notify(foreground="#00aa00", foreground_low="#004400", max_chars=100),
                widget.Systray(),
                widget.CheckUpdates(distro="Arch_checkupdates",  # custom_command_modify = (lambda x: x/2-1),
                                    execute=terminal + " --hold checkupdates", update_interval=3600, display_format="U:{updates}",
                                    no_update_string=" U ", colour_no_updates="#00aa00", colour_have_updates="#880000",
                                    ),  # TODO error_string when added in next update
                # execute="GTK_THEME=Breeze-Dark pamac-manager"
                widget.Clock(format="%Y-%m-%dT%H:%M", fontsize=18, update_interval=60,
                             mouse_callbacks={"Button1": int_mod.simple_calendar}
                             ),
                # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
                # widget.CurrentScreen(mouse_callbacks={"Button1": lambda: qtile.focus_screen(0)}),
            ],
            24,
            background=["#00000000", "#00000022", "#00000055", "#00330088"],  # bar background
        ),
        wallpaper="/home/yobleck/Pictures/382337_4k_dn.png",
        wallpaper_mode="fill",
    ),
    Screen(  # 2560x1440_60
        bottom=bar.Bar(
            [
                widget.CurrentLayout(mouse_callbacks={"Button3": lambda: qtile.prev_layout(),
                                                      "Button4": lambda: qtile.prev_layout(),
                                                      "Button5": lambda: qtile.next_layout()}
                                     ),
                widget.TextBox("|"),
                widget.GroupBox(active="#00aa00", inactive="#004400", block_highlight_text_color="#00aa00", disable_drag=True),
                widget.TextBox("|"),
                widget.TaskList(border="#00aa00", parse_text=parse,
                                mouse_callbacks={"Button2": tasklist_kill, "Button3": tasklist_minimize},  # , "Button3": win_pre.show_preview}
                                unfocused_border="#004400"
                                ),
                # widget.Moc(update_interval=2,
                #            play_color="#00aa00", noplay_color="#004400",
                #            mouse_callbacks={"Button3": lambda: qtile.spawn("mocp -s"),
                #                             "Button4": lambda: qtile.spawn("mocp -r"),
                #                             "Button5": lambda: qtile.spawn("mocp -f"),
                #                             "Button8": lambda: qtile.spawn("mocp -k -2"),
                #                             "Button9": lambda: qtile.spawn("mocp -k 2"),
                #                             }
                #            ),
                widget.Mpris2(poll_interval=2, width=400, no_metadata_text="No metadata",
                              playing_text="Playing", paused_text="Paused",
                              ),
                widget.Volume(get_volume_command="pamixer --get-volume-human",
                              volume_down_command="pamixer -d 5",
                              volume_up_command="pamixer -i 5",
                              volume_app="pavucontrol-qt",
                              mute_command="pamixer -t",
                              check_mute_command="pamixer --get-mute",
                              check_mute_string="true",
                              update_interval=0.5,  # TODO inc/dec/mute volume should trigger update function
                              ),
                widget.Clock(format="%a %H:%M", fontsize=18, update_interval=30,
                             mouse_callbacks={"Button1": int_mod.simple_calendar}
                             ),
                # widget.CurrentScreen(mouse_callbacks={"Button1": lambda: qtile.focus_screen(1)}),
            ],
            24,
            background=["#00000000", "#00000022", "#00000055", "#00330088"],  # bar background
        ),
        top=bar.Bar(
            [
                # widget.Image(filename="/home/yobleck/.config/qtile/icons/24x24.png",
                #              mouse_callbacks={"Button1": int_mod.simple_start_menu}),
                start_menu.StartMenu(filename="/home/yobleck/.config/qtile/icons/arch_green.png",  #  \ue9f1
                                     win_pos=(0, 24), win_bordercolor="#aa00aa",
                                     win_opacity=0.9, win_font="Hack", win_fontsize=10,
                                     win_icon_paths=["/home/yobleck/.config/qtile/icons/system-shutdown.png",
                                                     "/home/yobleck/.config/qtile/icons/system-reboot.png",
                                                     "/home/yobleck/.config/qtile/icons/system-log-out.png"],
                                     ),
                # fah.FaH(username="yobleck", json=True, is_popup=True, popup_struct=(5, 1330, 160, 80, "#00aa00", 1), update_interval=3600),
                # qsm.Menu(button_list=[
                #     qsm.Button(text="Brightness Down", icon_path="~/.config/qtile/icons/low-brightness.svg", is_toggle=False, grid_pos=(0,0)),
                #     qsm.Button(text="Brightness Up", icon_path="~/.config/qtile/icons/high-brightness.svg", is_toggle=False, grid_pos=(1,0)),
                #     qsm.Button(text="Flashlight", icon_path="~/.config/qtile/icons/flashlight-on.svg", is_toggle=True, grid_pos=(2,0)),
                #     qsm.Button(text="Screen Rotation", icon_path="~/.config/qtile/icons/smartphone.svg", is_toggle=True, grid_pos=(0,1)),
                #     qsm.Button(text="Wifi", icon_path="~/.config/qtile/icons/network-wireless-connected-100.svg", is_toggle=True, grid_pos=(1,1)),
                #     qsm.Button(text="Bluetooth", icon_path="~/.config/qtile/icons/network-bluetooth.svg", is_toggle=True, grid_pos=(2,1)),
                #     ]),
                widget.Spacer(),
                # voice_control.VoiceControl(),
                # NOTE replaced by native qtile repl command
                # py_repl.REPL(text="", fontsize=18,
                #              win_foreground="#00aa00", win_pos=(400, 400), win_size=(800, 800),
                #              win_font="Hack", win_bordercolor=["#0000ff", "#0000ff", "#ffff00", "#ffff00"], win_borderwidth=4,
                #              win_opacity=0.9  # text=" PY REPL"  changed to:  and 
                #              ),
                widget.TextBox(" "),
                widget.Image(filename="/home/yobleck/.config/qtile/icons/htop.png",
                             mouse_callbacks={"Button1": lambda: qtile.spawn(f"{terminal} btm")}
                             ),
                widget.CPU(format="| CPU: {load_percent:04.1f}% {freq_current}GHz", update_interval=2),
                widget.ThermalSensor(foreground="#00aa00", tag_sensor="Tctl", threshold=80, update_interval=2),
                widget.CPUGraph(frequency=2, fill_color="#00330055", graph_color="#00aa00"),
                widget.Memory(format="| Mem: {MemUsed:02.1f}{mm}B", measure_mem="G", update_interval=2),
                # widget.DF(format="| df: {uf}{m}/{r:.0f}%", warn_space=100, update_interval=30, visible_on_warn=False),
                widget.TextBox("| df:"),
                widget.GenPollCommand(cmd="df -H / | tail -n 1 |  awk '{print $4\"B\"}'", shell=True, update_interval=30),
                widget.Net(format="| Net: {down:3.0f}{down_suffix:<2} ↓↑ {up:3.0f}{up_suffix:<2}", update_interval=2),
                widget.NetGraph(frequency=2, fill_color="#00330055", graph_color="#00aa00"),
                widget.NvidiaSensors(format="| GPU: Fan:{fan_speed}, {temp}°C", foreground="#00aa00", threshold=80, update_interval=2),
            ],
            24,
            background=["#00330088", "#00000055", "#00000022", "#00000000"],
        ),
        wallpaper="/home/yobleck/Pictures/black.png",
        wallpaper_mode="fill",
    ),
]


# __Misc settings__
# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", move_snap_window(snap_dist=20),  # lazy.window.set_position_floating(border_snapping=True, snap_dist=20),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
follow_mouse_focus = True
bring_front_click = True
cursor_warp = False
floats_kept_above = True
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
    # Match(wm_class="FAHStats"),  # folding @ home stats widget
    Match(wm_class="polkit-kde-authentication-agent-1"),  # WM_CLASS(STRING) = "polkit-kde-authentication-agent-1", ditto
    Match(wm_class="krunner"),
    Match(title="qalc"),  # TODO remove
    Match(wm_class="qalc"),
    Match(wm_class="plasmawindowed"),  # TODO remove
    Match(wm_class="Panda3D"),
    Match(wm_class="Xephyr"),
    Match(wm_class="Vncviewer"),
    Match(wm_class="visualboyadvance-m"),
    Match(wm_class="mgba"),
    Match(wm_class="megasync"),
    Match(wm_class="spectacle"),  # TODO remove
    Match(title="Event Tester"),
    Match(title="Default - Wine desktop"),
    Match(title="SAF"),
    Match(title="800x600 - Wine desktop"),
    Match(wm_class="explorer.exe"),
    Match(wm_class="gamescope"),
    MatchAll(Match(wm_class="steamwebhelper"), InvertMatch(Match(title="Steam"))),
    Match(wm_class="zenity"),
    Match(wm_class="pavucontrol"),
],
    no_reposition_rules=[  # TODO: https://github.com/qtile/qtile/blob/579d189b244efea590dd2447110516cd413f10de/libqtile/layout/floating.py#L274
        Match(wm_class="FAHStats"),
        # Match(wm_class="plasmawindowed"), #only sort of works
], border_focus="#cccc00", border_normal="#888800", border_width=1)


auto_fullscreen = True
focus_on_window_activation = "smart"
# reconfigure_screens = True  # doesn't work with changes through nvidia settings?
auto_minimize = True  # some games auto min when focus lost


# Faked because java bs
wmname = "LG3D"
