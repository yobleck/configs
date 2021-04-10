#!/bin/bash

if [ $(grep -r "RUNNING" /proc/asound | wc -l) -eq 0 ];
then
xset s activate
i3lock -n --pass-media-keys --timecolor=00ff00 --datecolor=00ff00 --blur 5 --clock --timestr="%H:%M" --datestr="%Y-%m-%d"
xset s off
fi
