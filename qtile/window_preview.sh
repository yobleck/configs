#!/bin/sh
import -window $1 -geometry 320x180 /home/yobleck/.config/qtile/window_preview_images/$1.png \
&>> /home/yobleck/.config/qtile/qtile_log.txt
