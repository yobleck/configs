#!/bin/bash
#echo auto >> /home/yobleck/xtest.txt
#if [ $(cut -f1 -d. /proc/uptime) -lt 500 ];
#then
if [ $(grep -r "RUNNING" /proc/asound | wc -l) -eq 0 ] && [ $(cut -f1 -d. /proc/uptime) -gt 500 ];
then
xset s activate
i3lock -n --pass-media-keys --time-color=00ff00 --date-color=00aa00 --blur 5 --clock --time-str="%H:%M" --date-str="%Y-%m-%d"
xset s off
fi
#fi
