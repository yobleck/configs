#!/bin/bash
#this script checks to see if nvidia ForceCompositionPipeline is on or off then toggles it

if grep -q "ForceCompositionPipeline=On" <<< $(nvidia-settings -q CurrentMetaMode 2>/dev/null); then
    #echo "it's on";
    nvidia-settings --assign "CurrentMetaMode=DPY-2: 2560x1440_60 +0+0 {ForceCompositionPipeline=Off}, \
    DPY-0: 1920x1080_144 +2560+0 {ForceCompositionPipeline=Off}" 2>/dev/null;
    #echo "turning off";
    notify-send "vsync off";
    
else #grep -q "ForceCompositionPipeline=Off" <<< $(nvidia-settings -q CurrentMetaMode 2>/dev/null); then
    #echo "it's off";
    nvidia-settings --assign "CurrentMetaMode=DPY-2: 2560x1440_60 +0+0 {ForceCompositionPipeline=On}, \
    DPY-0: 1920x1080_144 +2560+0 {ForceCompositionPipeline=On}" 2>/dev/null;
    #echo "turning on";
    notify-send "vsync on";

#else
    #echo "something went wrong";
fi
