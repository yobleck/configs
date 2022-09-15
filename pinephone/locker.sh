#!/bin/bash
#echo auto >> /home/alarm/xtest.txt

if [ $(grep -r "RUNNING" /proc/asound | wc -l) -eq 0 ] && [ $(cut -f1 -d. /proc/uptime) -gt 200 ] && \
[ $(cat /sys/class/power_supply/axp20x-battery/status | grep "Discharging") ]
then
systemctl suspend
# see /usr/lib/systemd/system-sleep/sleep-end.sh
# and ~/.config/qtile/last_sleep_time
fi
