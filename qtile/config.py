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

from typing import List  # noqa: F401

from xcffib.xproto import EventMask

from libqtile import bar, layout, widget, extension, hook, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen  # , KeyChord
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal  # , send_notification


# Helper functions
def log_test(i):
    f = open("/home/yobleck/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


def vsync_toggle(x):
    # TODO: use qtile.cmd_spawn or lazy to get status. on by default?
    # send_notification(title="test1", message="test2")
    pass


#import subprocess;
@hook.subscribe.startup_once
def initial_startup_stuff():
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

    # qtile.cmd_spawn("mocp -S")
    # qtile.cmd_spawn("xbindkeys")
    # TODO: sudo pacman -Sy as startup service
    # TODO: disable desktop_scroll service
    # qtile.cmd_spawn("gwe --hide-window") WARNING: linux5.10 and nvidia 465 broken cant overclock

    # TODO: need /usr/lib/klauncher --fd=8 kdeinit5 kinit kactivitymanagerd kioclient exec .exe and kded5 so kde apps start quickly?
    qtile.cmd_spawn("kill -2 kglobalaccel5")
    #above is killed and allowed to respawn so that qtile keybinds override kde stuff TODO: how to stop said kde stuff from starting
    qtile.cmd_spawn("kill -2 kwalletd5")
    # subprocess.run(["sleep", "2"]) #Needed?

    # qtile.cmd_spawn("kill -2 gwe");

    # TODO: plasmawindowed org.kde.plasma.mediacontroller --statusnotifier
    # qtile.cmd_spawn("plasmawindowed org.kde.plasma.mediacontroller --statusnotifier")


def mouse_move(qtile):
    qtile.core._root.set_attribute(eventmask=(EventMask.StructureNotify
                                              | EventMask.SubstructureNotify
                                              | EventMask.SubstructureRedirect
                                              | EventMask.EnterWindow
                                              | EventMask.LeaveWindow
                                              | EventMask.ButtonPress
                                              | EventMask.PointerMotion))

    def screen_change(event):
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


@hook.subscribe.startup
def startup_stuff():
    #subprocess.Popen(["xautolock", "-time", "10", "-locker", "/home/yobleck/.config/qtile/locker.sh"])
    qtile.cmd_spawn("xsetroot -cursor_name left_ptr")  # change mouse to breeze cursor
    mouse_move(qtile)


@hook.subscribe.startup_complete
def startup_complete_stuff():
    for s in qtile.screens:
        if s.height == 1440:
            s.top.show(is_show=False)  # Hide top bar by default


@hook.subscribe.shutdown
def shutdown_stuff():
    #kill or restart sddm. not needed with ly
    #or systemctl poweroff
    #kill xbindkeys and mocp server and xautolock
    pass

#TODO:mouse callback on bar widgets?


###KEY BINDS###
mod = "mod4"
terminal = guess_terminal()
"""
from time import sleep
from libqtile.popup import Popup
def popup_test(qtile):
    try:
        send_notification("popup_test_1", "this is test #1")
        popup = Popup(qtile, background="#005500", width=500, height=500, font_size=64, border="#0000ff", border_width=5,
                    foreground="#ffffff", opacity=0.8)
        #popup.layout.text = "hello world"
        #popup.layout.text = "henlo"
        #popup.drawer.textlayout(text="hello world",colour=popup.foreground,font_family=popup.font,
                                #font_size=popup.font_size,font_shadow=popup.fontshadow).draw(x=50,y=50)
        #popup.drawer.draw(width=100)
        
        popup.place()
        popup.draw_text(x=50, y=50)
        popup.draw()
        popup.unhide()
        sleep(5)
        popup.kill()
        send_notification("popup_test_2", str(popup.layout.text))
    except Exception as e:
        send_notification("er", str(e))
"""


def toggle_bar(qtile, *args):
    qtile.cmd_hide_show_bar(*args)


keys = [
    # Key([mod], "o", lazy.function(popup_test), desc="popup"),
    # Switch between windows in current stack pane
    Key(["mod1"], "Tab", lazy.layout.down(),
        desc="Move focus down in stack pane"),
    Key(["mod1", "shift"], "Tab", lazy.layout.up(),
        desc="Move focus up in stack pane"),

    # move windows around in the columns layout
    Key([mod, "shift"], "k", lazy.layout.shuffle_down(),
        desc="Move window down in current stack "),
    Key([mod, "shift"], "i", lazy.layout.shuffle_up(),
        desc="Move window up in current stack "),
    Key([mod, "shift"], "j", lazy.layout.shuffle_left(),
        desc="Move window left in current stack "),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
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
    Key([mod, "shift"], "Return", lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack"),  # other behavior with columns
    # Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Key([mod], "Return", lazy.spawn("konsole"), desc="Launch terminal"), # --style gtk2

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "Tab", lazy.prev_layout(), desc="Toggle between layouts backwards"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),

    Key([mod, "control", "shift"], "r", lazy.restart(), desc="Restart qtile"),
    Key([mod, "control", "shift"], "q", lazy.shutdown(), desc="Shutdown qtile"),
    Key(["mod1"], "space", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key(["control", "mod1"], "space", lazy.spawn("krunner"), desc="launch/open krunner"),
    Key([mod], "p", lazy.run_extension(extension.J4DmenuDesktop(dmenu_lines=20, j4dmenu_generic=False, dmenu_ignorecase=True, dmenu_bottom=True))),
    Key([mod, "control"], "v", lazy.spawn("sh /home/yobleck/.config/qtile/toggle_vsync.sh"),
        # lazy.function(vsync_toggle),
        desc="toggle nvidia ForceCompositionPipeline"),
    Key([mod, "control"], "b", lazy.function(toggle_bar, "bottom"), desc="toggle bar visibility"),
    Key([mod, "control"], "t", lazy.function(toggle_bar, "top"), desc="toggle bar visibility"),

    # Volume control
    Key([], "XF86AudioRaiseVolume",
        lazy.spawn("pulseaudio-ctl up"), lazy.spawn("paplay /home/yobleck/Music/volume_change/mc_pop/audio-volume-change.oga")),
    Key([], "XF86AudioLowerVolume",
        lazy.spawn("pulseaudio-ctl down"), lazy.spawn("paplay /home/yobleck/Music/volume_change/mc_pop/audio-volume-change.oga")),
    Key([], "XF86AudioMute",
        lazy.spawn("pulseaudio-ctl mute")),
    #Key([], "XF86AudioNext",
        #lazy.spawn("pulseaudio-ctl mute")),
    #Key([], "XF86AudioPrev",
        #lazy.spawn("pulseaudio-ctl mute")),#play next and prev

    # Run various programs
    #KeyChord(["control", "mod1"], "z", [
        Key(["control", "mod1"], "e", lazy.spawn("dolphin"), desc="launch dolphin file manager"),  # --style gtk2 export QT_QPA_PLATFORMTHEME=\"qt5ct\"
        Key(["control", "mod1"], "r", lazy.spawn("konsole"), desc="launch konsole"),
        Key(["control", "mod1"], "g", lazy.spawn("chromium"), desc="launch chromium"),
        Key(["control", "mod1"], "f", lazy.spawn("firefox"), desc="launch firefox"),
        Key(["control", "mod1"], "y", lazy.spawn("konsole -e ~/yt_dwnld.sh"), desc="launch youtube audio downloader"),
        Key(["control", "mod1"], "m", lazy.spawn("sh /home/yobleck/.config/qtile/mocp_launcher.sh"), desc="launch music player"),
        Key(["control", "mod1"], "s", lazy.spawn("steam"), desc="launch steam"),
        Key([mod], "3270_PrintScreen", lazy.spawn("spectacle"), desc="launch scpectacle"),
    #]),
    # lock screen #https://github.com/Raymo111/i3lock-color/blob/master/examples/lock.sh
    #Key([mod], "l", lazy.spawn("i3lock -n --pass-media-keys --timecolor=00ff00 --datecolor=00ff00 --blur 5 --clock --timestr=\"%H:%M\" --datestr=\"%Y-%m-%d\""),
        #desc="lock screen with i3lock"),
    #Key([mod], "l", lazy.spawn("xautolock -locknow -nowlocker i3lock"), desc="lock screen with i3lock"),
    Key([mod], "l", lazy.spawn("xautolock -locknow -nowlocker /home/yobleck/.config/qtile/locker.sh"), desc="lock screen with i3lock"),
    # work around to turn screen back on after locking: lazy.spawn("xset force reset"),
]


###GROUPS AND LAYOUTS###
groups = []
groups.append(Group("web", matches=[Match(wm_class=["mpc-qt", "firefox"])]))
groups.append(Group("2nd", layout="stack", spawn="python /home/yobleck/fah/fah_stats.py", matches=[Match(wm_class=["dolphin"])]))
groups.append(Group("F@H", layout="stack", spawn=["konsole", "FAHControl"]))
groups.append(Group("htop", spawn="ksysguard"))  # --style gtk2
groups.append(Group("game", matches=[Match(wm_class=["Steam", "MultiMC5", "hl2_linux"])]))  # TODO: add video game match rules

g_list = {"web": "a", "2nd": "s", "F@H": "d", "htop": "f", "game": "g"}
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
    font='sans',
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()


# Function for editing displayed wm_name
def parse(text):
    for string in [" - YouTube", " \u2014 Mozilla Firefox", " \u2014 Konsole", "  \u2014 Kate", " \u2014 Dolphin", " - Chromium",
                   "Media Player Classic Qute Theater - "]:
        text = text.replace(string, "")
    return text


screens = [
    Screen(  # 1920x1080_144
        bottom=bar.Bar(
            [
                widget.CurrentLayout(foreground="#00aa00", font="Noto Mono", mouse_callbacks={"Button3": lambda: qtile.cmd_prev_layout(),
                                                                                              "Button4": lambda: qtile.cmd_prev_layout(),
                                                                                              "Button5": lambda: qtile.cmd_next_layout()}
                                    ),
                widget.TextBox("|", foreground="#00aa00"),
                widget.GroupBox(active="#00aa00", inactive="#004400", block_highlight_text_color="#00aa00", disable_drag=True, font="Noto Mono"),
                #TODO: look at source code and find out how to disable click on focused group causing switch to another group
                widget.TextBox("|", foreground="#00aa00"),
                widget.Prompt(ignore_dups_history=True),
                widget.Chord(  # multi key binds but not holding all keys down at same time
                             chords_colors={'launch': ("#ff0000", "#ffffff"), }, name_transform=lambda name: name.upper(),
                            ),
                widget.TaskList(foreground="#00aa00", border="#00aa00", font="Noto Mono",
                                parse_text=parse,
                                mouse_callbacks={"Button2": lambda: qtile.current_window.kill()}
                                ),  # TODO: test padding and margin with east asian chars
                #widget.WindowName(parse_text=parse),
                #widget.WindowTabs(parse_text=parse),
                widget.Notify(foreground="#00aa00", foreground_low="#004400", max_chars=100, font="Noto Mono"),
                widget.Systray(),
                #custom_command=("pamac checkupdates",3)   "sh /home/yobleck/.config/qtile/test.sh 1"   ("pamac checkupdates -q", 0)
                #widget.CheckUpdates(distro="Arch", execute="pamac-manager", update_interval="600", no_update_string=" U ",
                                    #colour_no_updates="#00aa00", colour_have_updates="#aa0000", custom_command_modify = (lambda x: x/2-1),
                                    #),
                widget.CheckUpdates(custom_command="pamac checkupdates -q; echo -n",  # custom_command_modify = (lambda x: x/2-1),
                                    execute="pamac-manager", update_interval="600", display_format="U:{updates}",
                                    no_update_string=" U ", font="Noto Mono", colour_no_updates="#00aa00", colour_have_updates="#880000",
                                    ),
                widget.Clock(format='%Y-%m-%dT%H:%M', fontsize=18, foreground="#00aa00", font="Noto Mono",
                             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.calendar")}
                             ),
                #https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
                #widget.QuickExit(),
                #widget.CurrentScreen(mouse_callbacks={"Button1": lambda: qtile.focus_screen(0)}, font="Noto Mono"),
            ],
            24,
            #opacity=0.5,
            background=["#00000000", "#00000022", "#00000055", "#00330088"],  # bar background
        ),
        wallpaper="~/Pictures/382337_4k_dn.png",
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
                widget.Image(filename="/usr/share/icons/manjaro/green/24x24.png",  # green.svg
                             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.kickofflegacy")}),
                widget.CurrentLayout(foreground="#00aa00", font="Noto Mono", mouse_callbacks={"Button3": lambda: qtile.cmd_prev_layout(),
                                                                                              "Button4": lambda: qtile.cmd_prev_layout(),
                                                                                              "Button5": lambda: qtile.cmd_next_layout()
                                                                                              }
                                    ),
                widget.TextBox("|", foreground="#00aa00"),
                widget.GroupBox(active="#00aa00", inactive="#004400", block_highlight_text_color="#00aa00", disable_drag=True, font="Noto Mono"),
                widget.TextBox("|", foreground="#00aa00"),
                widget.TaskList(foreground="#00aa00", border="#00aa00", font="Noto Mono",
                                parse_text=parse,
                                mouse_callbacks={"Button2": lambda: qtile.current_window.kill()}
                                ),  # TODO: get tasklist win under mouse not of focused
                widget.Moc(foreground="#00aa00", update_interval=2, font="Noto Mono",
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
                              foreground="#00aa00", font="Noto Mono"
                              ),
                widget.Clock(format='%a %H:%M', fontsize=18, foreground="#00aa00", font="Noto Mono",
                             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.calendar")}
                             ),
                #widget.CurrentScreen(mouse_callbacks={"Button1": lambda: qtile.focus_screen(1)}, font="Noto Mono"),
            ],
            24,
            #opacity=0.9,
            background=["#00000000", "#00000022", "#00000055", "#00330088"],  # bar background
        ),
        top=bar.Bar(
            [
                widget.Spacer(),
                widget.CPU(foreground="#00aa00", font="Noto Mono", format="CPU: {freq_current}GHz {load_percent}%", update_interval=2),
                widget.CPUGraph(frequency=2, font="Noto Mono", fill_color="#00330055", graph_color="#00aa00"),
                widget.Memory(foreground="#00aa00", font="Noto Mono", format="| Mem: {MemUsed:.0f}{mm}/{MemTotal:.0f}{mm}", update_interval=2),
                widget.Net(foreground="#00aa00", font="Noto Mono", format="| Net: {down} ↓↑ {up}", update_interval=2),
                widget.NetGraph(frequency=2, font="Noto Mono", fill_color="#00330055", graph_color="#00aa00"),
                widget.NvidiaSensors(format="| GPU: Fan:{fan_speed}, {temp}°C", foreground="#00aa00", font="Noto Mono",
                                     threshold=80, update_interval=2),
            ],
            24,
            background=["#00330088", "#00000055", "#00000022", "#00000000"],
        ),
        wallpaper="~/Pictures/382337_4k_dn.png",
        wallpaper_mode="fill",
        #width=2560,
        #height=1440,
    ),
]


###Misc settings###
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
main = None  # WARNING: this is deprecated and will be removed soon
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
    Match(wm_class="plasmawindowed"),
    Match(wm_class="Panda3D"),
    Match(wm_class="Xephyr"),
    Match(title="Event Tester"),
],
    no_reposition_rules=[  # TODO: https://github.com/qtile/qtile/blob/579d189b244efea590dd2447110516cd413f10de/libqtile/layout/floating.py#L274
        Match(wm_class="FAHStats"),
        #Match(wm_class="plasmawindowed"), #only sort of works
])


#import time;
@hook.subscribe.client_managed  # TODO: put cal and start in scratchpad?
def kde_widgets(window):
    if(window.window.get_wm_class()[1] == "plasmawindowed"):
        #log_test("passed wm_class test")
        #log_test(window.window.get_name())
        #https://github.com/qtile/qtile/blob/master/libqtile/backend/x11/window.py
        #log_test(window.window.get_property("WM_NAME", type="STRING", unpack=str))
        #time.sleep(0.5);
        if(window.window.get_name() == "Calendar"):
            #log_test("passed Cal name test")
            #qtile.cmd_spawn("wmctrl -r Calendar -e 0,2332,1223,225,193") # NOTE wmctrl uninstalled
            qtile.cmd_spawn("xdotool search \"Calendar\" windowsize 225 193 windowmove 2333 1221")
            #below doesnt respect different widgets
            #window.cmd_set_position_floating(2333, 1221)
            #window.cmd_set_size_floating(225, 193)

        if(window.window.get_name() == "Legacy Application Launcher"):
            #log_test("passed App menu name test")
            #qtile.cmd_spawn("wmctrl -r \'Application Menu\' -e 0,0,949,273,467")  # old new menu
            qtile.cmd_spawn("xdotool search \"Legacy Application Launcher\" windowsize 416 544 windowmove 0 869")  # windowsize 416 544


auto_fullscreen = True
focus_on_window_activation = "smart"
#reconfigure_screens = True; #doesn't work with changes through nvidia settings?
#auto_minimize = True; #some games auto min when focus lost


# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
