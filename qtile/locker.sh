#!/bin/bash
#echo auto >> /home/yobleck/xtest.txt

# check for sound playing, computer has been on for more than 5 min, screen not already locked
if [ $(grep -r "RUNNING" /proc/asound | wc -l) -eq 0 ] && \
   [ $(cut -f1 -d. /proc/uptime) -gt 300 ] && \
   [ ! -f ~/.cache/qtile/psl_lock ];
then
    echo "$(date) xautolock triggered" >> ~/.config/qtile/qtile_log.txt
    xset s activate
    #i3lock -n --pass-media-keys --time-color=00ff00 --date-color=00aa00 --blur 5 --clock --time-str="%H:%M" --date-str="%Y-%m-%d"
    qtile cmd-obj -o cmd -f fire_user_hook -a psl_lock_hook &>> /dev/null #~/temp_buffer.txt
    xset s off
fi
