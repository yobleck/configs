#YOBLECK's config
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

from libqtile import bar, layout, widget, hook, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile import extension;

#helper functions
def log_test(i):
    f = open("/home/yobleck/qtile_log.txt","a");
    f.write(str(i) + "\n");
    f.close();


import subprocess;
@hook.subscribe.startup_once
def initial_startup_stuff():
    #configure monitors via nvidia settings. requires mod1+control+r to fix layout
    qtile.cmd_spawn("nvidia-settings --assign \"CurrentMetaMode=DPY-2: 2560x1440_60 +0+0 {ForceCompositionPipeline=On}, DPY-0: 1920x1080_144 +2560+0 {ForceCompositionPipeline=On}\"");
    #loginctl user-status suggests put above line in /etc/X11/xinit/xserverrc
    qtile.cmd_spawn("picom"); #compositor for window animations and transparency
    
    qtile.cmd_spawn("xinput --set-prop \"pointer:Logitech G602\" \"libinput Accel Profile Enabled\" 0, 1"); #mouse no accel
    qtile.cmd_spawn("xinput --set-prop \"pointer:Logitech G602\" \"libinput Accel Speed\" 0"); #mouse speed
    
    qtile.cmd_spawn("xset s off -dpms");
    qtile.cmd_spawn("xautolock -time 10 -locker /home/yobleck/.config/qtile/locker.sh"); #lock screen and monitors off
    #TODO: cant manually override while video is playing. pass through argument to shell script? or disable xautolock in manual script?
    
    qtile.cmd_spawn("/home/yobleck/.config/qtile/polkit_dumb_style/polkit-dumb-agent-style"); #, "-s", "gtk2" #qt5ct located in .bash_profile
    #polkit gui agent for kate, pamac etc #requires kdesu grrrr
    #recompiled for Qt themes TODO: color schemes
    #https://stackoverflow.com/questions/6740333/can-i-run-a-qt-application-with-a-specific-theme #https://cmake.org/runningcmake/
    
    #subprocess.Popen(["export", "QT_QPA_PLATFORMTHEME=\"qt5ct\""]); #see ~/.bash_profile
    
    qtile.cmd_spawn("/usr/lib/kdeconnectd"); #kdeconnect daemon
    qtile.cmd_spawn("kdeconnect-indicator"); #kdeconnect taskbar widget icon
    
    #qtile.cmd_spawn("mocp -S");
    #qtile.cmd_spawn("xbindkeys");
    #TODO: sudo pacman -Sy as startup service
    #TODO: disable desktop_scroll service
    qtile.cmd_spawn("gwe --hide-window");
    
    #TODO: need /usr/lib/klauncher --fd=8 kdeinit5 kinit kactivitymanagerd kioclient exec .exe and kded5 so kde apps start quickly?
    qtile.cmd_spawn("kill -2 kglobalaccel5");
    #above is killed and allowed to respawn so that qtile keybinds override kde stuff TODO: how to stop said kde stuff from starting
    qtile.cmd_spawn("kill -2 kwalletd5");
    subprocess.run(["sleep", "2"]); #Needed?
    
    qtile.cmd_spawn("kill -2 gwe");


@hook.subscribe.startup
def startup_stuff():
    #subprocess.Popen(["xautolock", "-time", "10", "-locker", "/home/yobleck/.config/qtile/locker.sh"]);
    qtile.cmd_spawn("xsetroot -cursor_name left_ptr"); #change mouse to breeze cursor


@hook.subscribe.shutdown
def shutdown_stuff():
    #kill or restart sddm. not needed with ly
    #or systemctl poweroff
    #kill xbindkeys and mocp server and xautolock
    pass;
    
#TODO:mouse callback on bar widgets?

mod = "mod4"
terminal = guess_terminal()

keys = [
    # Switch between windows in current stack pane
    #Key([mod], "k", lazy.layout.down(),
        #desc="Move focus down in stack pane"),
    #Key([mod], "i", lazy.layout.up(),
        #desc="Move focus up in stack pane"),
    #alt tab variant
    Key(["mod1"], "Tab", lazy.layout.down(),
        desc="Move focus down in stack pane"),
    Key(["mod1", "shift"], "Tab", lazy.layout.up(),
        desc="Move focus up in stack pane"),

    #move windows around in the columns layout
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
        desc="Toggle between split and unsplit sides of stack"),
    #Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "Return", lazy.spawn("konsole"), desc="Launch terminal"), # --style gtk2

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "Tab", lazy.prev_layout(), desc="Toggle between layouts backwards"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),

    Key([mod, "control"], "r", lazy.restart(), desc="Restart qtile"),
    Key([mod, "control", "shift"], "q", lazy.shutdown(), desc="Shutdown qtile"),
    Key([mod], "r", lazy.spawn("konsole"), desc="Spawn a command using a prompt widget"),
    Key(["mod1"], "space", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key(["control", "mod1"], "space", lazy.spawn("krunner"), desc="launch/open krunner"),
    Key([mod], "p", lazy.run_extension(extension.J4DmenuDesktop(dmenu_lines=20, j4dmenu_generic=False, dmenu_ignorecase=True, dmenu_bottom=True))),
    Key([mod, "control"], "v", lazy.spawn("sh /home/yobleck/.config/qtile/toggle_vsync.sh"), desc="toggle nvidia ForceCompositionPipeline"),
    
    #volume control
    Key([], "XF86AudioRaiseVolume",
        lazy.spawn("pulseaudio-ctl up"),lazy.spawn("paplay /home/yobleck/Music/volume_change/mc_pop/audio-volume-change.oga")),
    Key([], "XF86AudioLowerVolume",
        lazy.spawn("pulseaudio-ctl down"),lazy.spawn("paplay /home/yobleck/Music/volume_change/mc_pop/audio-volume-change.oga")),
    Key([], "XF86AudioMute",
        lazy.spawn("pulseaudio-ctl mute")),
    #Key([], "XF86AudioNext",
        #lazy.spawn("pulseaudio-ctl mute")),
    #Key([], "XF86AudioPrev",
        #lazy.spawn("pulseaudio-ctl mute")),#play next and prev
    
    #run various programs
    Key([mod], "e", lazy.spawn("dolphin"), desc="launch dolphin file manager"), # --style gtk2 export QT_QPA_PLATFORMTHEME=\"qt5ct\" 
    Key(["control", "mod1"], "g", lazy.spawn("chromium"), desc="launch chromium web browser"),
    Key(["control", "mod1"], "f", lazy.spawn("firefox"), desc="launch firefox web browser"),
    Key(["control", "mod1"], "y", lazy.spawn("konsole -e ~/yt_dwnld.sh"), desc="launch youtube audio downloader"),
    Key(["control", "mod1"], "m", lazy.spawn("sh /home/yobleck/.config/qtile/mocp_launcher.sh"), desc="launch music player"),
    
    #lock screen #https://github.com/Raymo111/i3lock-color/blob/master/examples/lock.sh
    #Key([mod], "l", lazy.spawn("i3lock -n --pass-media-keys --timecolor=00ff00 --datecolor=00ff00 --blur 5 --clock --timestr=\"%H:%M\" --datestr=\"%Y-%m-%d\""), 
        #desc="lock screen with i3lock"),
    #Key([mod], "l", lazy.spawn("xautolock -locknow -nowlocker i3lock"), desc="lock screen with i3lock"),
    Key([mod], "l", lazy.spawn("xautolock -locknow -nowlocker /home/yobleck/.config/qtile/locker.sh"), desc="lock screen with i3lock"),
    #work around to turn screen back on after locking: lazy.spawn("xset force reset"),
]


groups = [];
groups.append(Group("web", matches=[Match(wm_class=["mpc-qt", "firefox"])]));
groups.append(Group("2nd", layout="stack", spawn="python /home/yobleck/fah/fah_stats.py"));
groups.append(Group("F@H", layout="stack", spawn=["FAHControl", "konsole"])); #TODO: add konsole -e cd fah; FAHClient
groups.append(Group("htop", spawn="ksysguard")); # --style gtk2
groups.append(Group("game", matches=[Match(wm_class=["Steam", "MultiMC5"])])); #TODO: add video game match rules

#TODO: use for loops so this isn't as copy paste
keys.extend([
    Key([mod], "a", lazy.group["web"].toscreen(toggle=False),
            desc="Switch to group web"),
    Key([mod], "s", lazy.group["2nd"].toscreen(toggle=False),
            desc="Switch to group 2nd"),
    Key([mod], "d", lazy.group["F@H"].toscreen(toggle=False),
            desc="Switch to group F@H"),
    Key([mod], "f", lazy.group["htop"].toscreen(toggle=False),
            desc="Switch to group htop"),
    Key([mod], "g", lazy.group["game"].toscreen(toggle=False),
            desc="Switch to group game"),
    
    Key([mod, "shift"], "a", lazy.window.togroup("web"),
            desc="move focused window to group web"),
    Key([mod, "shift"], "s", lazy.window.togroup("2nd"),
            desc="move focused window to group 2nd"),
    Key([mod, "shift"], "d", lazy.window.togroup("F@H"),
            desc="move focused window to group F@H"),
    Key([mod, "shift"], "f", lazy.window.togroup("htop"),
            desc="move focused window to group htop"),
    Key([mod, "shift"], "g", lazy.window.togroup("game"),
            desc="move focused window to group game"),
    ]);
"""
g_list = ["web":"a", "2nd":"s", "F@H":"d", "htop":"f", "misc":"g"];
for g in g_list:
    keys.extend([
        Key([mod], g_list[g], lazy.group[g].toscreen(toggle=False),
                desc="Switch to group "+g),
        Key([mod, "shift"], g_list[g], lazy.window.togroup(g),
            desc="move focused window to group "+g),
        ]);
"""


#log_test("\n\n\ncreating layouts\n");
layouts = [
    layout.Max(),
    layout.Stack(num_stacks=2, border_focus="#00aa00"),
    # Try more layouts by unleashing below layouts.
    # layout.Bsp(),
    layout.Columns(border_focus="#00aa00"),
    #layout.Matrix(),
    #layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    #layout.TreeTab(previous_on_rm=True, active_bg="#00aa00"),
    # layout.VerticalTile(),
    # layout.Zoomy(),
    #layout.BrowserTab(), #these are just me yobleck messing around
    #layout.BrowserTab2(), #ditto
]
#print(BrowserTab2);


widget_defaults = dict(
    font='sans',
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen( #1920x1080_144
        bottom=bar.Bar(
            [
                widget.CurrentLayout(foreground="#00aa00", font="Noto Mono"),
                widget.TextBox("|", foreground="#00aa00"),
                widget.GroupBox(active="#00aa00", inactive="#004400", block_highlight_text_color="#00aa00", disable_drag=True, font="Noto Mono"),
                #TODO: look at source code and find out how to disable click on focused group causing switch to another group
                widget.TextBox("|", foreground="#00aa00"),
                widget.Prompt(ignore_dups_history=True),
                widget.TaskList(foreground="#00aa00", border="#00aa00", font="Noto Mono",
                                mouse_callbacks={"Button2": lambda: qtile.current_window.kill()}), #TODO: test padding and margin with east asian chars
                widget.Chord( #multi key binds but not holding all keys down at same time
                    chords_colors={
                        'launch': ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                widget.Notify(foreground="#00aa00", foreground_low="#004400", max_chars=50, font="Noto Mono"),
                widget.Systray(),
                #custom_command=("pamac checkupdates",3)   "sh /home/yobleck/.config/qtile/test.sh 1"   ("pamac checkupdates -q", 0)
                #widget.CheckUpdates(distro="Arch", execute="pamac-manager", update_interval="600", no_update_string=" U ",
                                    #colour_no_updates="#00aa00", colour_have_updates="#aa0000", custom_command_modify = (lambda x: x/2-1),
                                    #),
                widget.CheckUpdates(custom_command="pamac checkupdates -q; echo -n", #custom_command_modify = (lambda x: x/2-1),
                                    execute="pamac-manager", update_interval="600",
                                    no_update_string=" U ", font="Noto Mono", colour_no_updates="#00aa00", colour_have_updates="#aa0000",
                                    ),
                widget.Clock(format='%Y-%m-%dT%H:%M', fontsize=18, foreground="#00aa00", font="Noto Mono",
                             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.calendar")}), #https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
                #widget.QuickExit(),
            ],
            24,
            opacity=0.8,
            background=["#000000","#000000","#000000","#003300"], #bar background
        ),
        wallpaper="~/Pictures/382337_4k_dn.png",
        wallpaper_mode="fill",
    ),
    Screen( #2560x1440_60
        bottom=bar.Bar(
            [
                #widget.LaunchBar(progs=[("start", "plasmawindowed org.kde.plasma.kicker", "kde start menu")],
                                 #default_icon="/usr/share/icons/manjaro/maia/24x24.png"),
                widget.Image(filename="/usr/share/icons/manjaro/green/24x24.png",
                             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.kickofflegacy")}),
                widget.CurrentLayout(foreground="#00aa00", font="Noto Mono"),
                widget.TextBox("|", foreground="#00aa00"),
                widget.GroupBox(active="#00aa00", inactive="#004400", block_highlight_text_color="#00aa00", disable_drag=True, font="Noto Mono"),
                widget.TextBox("|", foreground="#00aa00"),
                widget.TaskList(foreground="#00aa00", border="#00aa00", font="Noto Mono",
                                mouse_callbacks={"Button2": lambda: qtile.current_window.kill()}), #TODO: get tsklst win under mouse not of focused
                widget.Moc(foreground="#00aa00", update_interval=2, font="Noto Mono",
                           mouse_callbacks={"Button2": lambda: qtile.cmd_spawn("mocp -s")}),
                widget.Volume(volume_down_command="pulseaudio-ctl down",
                              volume_up_command="pulseaudio-ctl up",
                              mute_command="pulseaudio-ctl mute",
                              foreground="#00aa00", font="Noto Mono"
                              ),
                widget.Clock(format='%a %H:%M',fontsize=18, foreground="#00aa00", font="Noto Mono",
                             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("plasmawindowed org.kde.plasma.calendar")}),
            ],
            24,
            opacity=0.9,
            background=["#000000","#000000","#000000","#003300"], #bar background
        ),
        wallpaper="~/Pictures/382337_4k_dn.png",
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

#Misc settings
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
    Match(wm_class="FAHStats"), #folding @ home stats widget
    Match(wm_class="polkit-kde-authentication-agent-1"), #WM_CLASS(STRING) = "polkit-kde-authentication-agent-1", ditto
    Match(wm_class="krunner"),
    Match(wm_class="plasmawindowed"),
    Match(wm_class="Panda3D"),
    #Match(title="mocp"),
    ],
no_reposition_rules=[ #TODO: https://github.com/qtile/qtile/blob/579d189b244efea590dd2447110516cd413f10de/libqtile/layout/floating.py#L274
    Match(wm_class="FAHStats"),
    #Match(wm_class="plasmawindowed"), #only sort of works
    ]
)
#import time;
@hook.subscribe.client_managed #TODO: put cal and start in scratchpad?
def kde_widgets(window):
    if(window.window.get_wm_class()[1] == "plasmawindowed"):
        #log_test("passed wm_class test");
        #log_test(window.window.get_name());
        #https://github.com/qtile/qtile/blob/master/libqtile/backend/x11/window.py
        #log_test(window.window.get_property("WM_NAME", type="STRING", unpack=str));
        #time.sleep(0.5);
        if(window.window.get_name() == "Calendar"):
            #log_test("passed Cal name test");
            #qtile.cmd_spawn("wmctrl -r Calendar -e 0,2332,1223,225,193"); # NOTE wmctrl uninstalled
            qtile.cmd_spawn("xdotool search \"Calendar\" windowsize 225 193 windowmove 2333 1221");
            #below doesnt respect different widgets
            #window.cmd_set_position_floating(2333, 1221);
            #window.cmd_set_size_floating(225, 193);
        
        if(window.window.get_name() == "Legacy Application Launcher"):
            #log_test("passed App menu name test");
            #qtile.cmd_spawn("wmctrl -r \'Application Menu\' -e 0,0,949,273,467"); #old new menu
            qtile.cmd_spawn("xdotool search \"Legacy Application Launcher\" windowsize 416 544 windowmove 0 869"); #windowsize 416 544
            

auto_fullscreen = True
focus_on_window_activation = "smart"
#reconfigure_screens = True; #doesn't work with chances through nvidia settings?
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
