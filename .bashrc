#
# ~/.bashrc
#

[[ $- != *i* ]] && return

colors() {
	local fgc bgc vals seq0

	printf "Color escapes are %s\n" '\e[${value};...;${value}m'
	printf "Values 30..37 are \e[33mforeground colors\e[m\n"
	printf "Values 40..47 are \e[43mbackground colors\e[m\n"
	printf "Value  1 gives a  \e[1mbold-faced look\e[m\n\n"

	# foreground colors
	for fgc in {30..37}; do
		# background colors
		for bgc in {40..47}; do
			fgc=${fgc#37} # white
			bgc=${bgc#40} # black

			vals="${fgc:+$fgc;}${bgc}"
			vals=${vals%%;}

			seq0="${vals:+\e[${vals}m}"
			printf "  %-9s" "${seq0:-(default)}"
			printf " ${seq0}TEXT\e[m"
			printf " \e[${vals:+${vals+$vals;}}1mBOLD\e[m"
		done
		echo; echo
	done
}
export -f colors;
[ -r /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion

# Change the window title of X terminals
case ${TERM} in
	xterm*|rxvt*|Eterm*|aterm|kterm|gnome*|interix|konsole*)
		PROMPT_COMMAND='echo -ne "\033]0;${USER}@${HOSTNAME%%.*}:${PWD/#$HOME/\~}\007"'
		;;
	screen*)
		PROMPT_COMMAND='echo -ne "\033_${USER}@${HOSTNAME%%.*}:${PWD/#$HOME/\~}\033\\"'
		;;
esac

use_color=true

# Set colorful PS1 only on colorful terminals.
# dircolors --print-database uses its own built-in database
# instead of using /etc/DIR_COLORS.  Try to use the external file
# first to take advantage of user additions.  Use internal bash
# globbing instead of external grep binary.
safe_term=${TERM//[^[:alnum:]]/?}   # sanitize TERM
match_lhs=""
[[ -f ~/.dir_colors   ]] && match_lhs="${match_lhs}$(<~/.dir_colors)"
[[ -f /etc/DIR_COLORS ]] && match_lhs="${match_lhs}$(</etc/DIR_COLORS)"
[[ -z ${match_lhs}    ]] \
	&& type -P dircolors >/dev/null \
	&& match_lhs=$(dircolors --print-database)
[[ $'\n'${match_lhs} == *$'\n'"TERM "${safe_term}* ]] && use_color=true

if ${use_color} ; then
	# Enable colors for ls, etc.  Prefer ~/.dir_colors #64489
	if type -P dircolors >/dev/null ; then
		if [[ -f ~/.dir_colors ]] ; then
			eval $(dircolors -b ~/.dir_colors)
		elif [[ -f /etc/DIR_COLORS ]] ; then
			eval $(dircolors -b /etc/DIR_COLORS)
		fi
	fi

	if [[ ${EUID} == 0 ]] ; then
		PS1='\[\033[01;31m\][\h\[\033[01;36m\] \W\[\033[01;31m\]]\$\[\033[00m\] '
	else
		PS1='\[\033[01;32m\][\u\[\033[01;37m\] \W\[\033[01;32m\]]\$\[\033[00m\] ' #@\h removed
	fi

	alias ls='ls --color=auto'
	alias grep='grep --colour=auto'
	alias egrep='egrep --colour=auto'
	alias fgrep='fgrep --colour=auto'
else
	if [[ ${EUID} == 0 ]] ; then
		# show root@ when we don't have colors
		PS1='\u@\h \W \$ '
	else
		PS1='\u@\h \w \$ '
	fi
fi

unset use_color safe_term match_lhs sh

alias cp="cp -i"                          # confirm before overwriting something
alias df='df -h'                          # human-readable sizes
alias free='free -m'                      # show sizes in MB
alias np='nano -w PKGBUILD'
alias more=less

xhost +local:root > /dev/null 2>&1

complete -cf sudo

# Bash won't get SIGWINCH if another process is in the foreground.
# Enable checkwinsize so that bash will check the terminal size when
# it regains control.  #65623
# http://cnswww.cns.cwru.edu/~chet/bash/FAQ (E11)
shopt -s checkwinsize

shopt -s expand_aliases

# export QT_SELECT=4

# Enable history appending instead of overwriting.  #139609
shopt -s histappend

#
# # ex - archive extractor
# # usage: ex <file>
ex ()
{
  if [ -f $1 ] ; then
    case $1 in
      *.tar.bz2)   tar xjf $1   ;;
      *.tar.gz)    tar xzf $1   ;;
      *.bz2)       bunzip2 $1   ;;
      *.rar)       unrar x $1     ;;
      *.gz)        gunzip $1    ;;
      *.tar)       tar xf $1    ;;
      *.tbz2)      tar xjf $1   ;;
      *.tgz)       tar xzf $1   ;;
      *.zip)       unzip $1     ;;
      *.Z)         uncompress $1;;
      *.7z)        7z x $1      ;;
      *)           echo "'$1' cannot be extracted via ex()" ;;
    esac
  else
    echo "'$1' is not a valid file"
  fi
}

# custom
alias cls="clear"
alias quit="exit"
alias cd..="echo \"you meant cd ..\";cd .."
alias heaven="cd /var/tmp/pamac-build-yobleck/unigine-heaven/src/Unigine_Heaven-4.0; ./heaven"
alias superposition="cd /var/tmp/pamac-build-yobleck/unigine-superposition/src/Unigine_Superposition-1.1; ./Superposition"
alias superpostion="echo \"you meant superposition\"; cd /var/tmp/pamac-build-yobleck/unigine-superposition/src/Unigine_Superposition-1.1; ./Superposition"

#monitors cpu clock speed in MHz
cpuclocktemp(){
    echo "temperature:"
    echo "scale=2;$(cat /sys/class/hwmon/hwmon1/temp1_input)/1000" | bc
    echo "clock speeds:"
    cat /proc/cpuinfo | grep '^[c]pu MHz'
}
export -f cpuclocktemp
alias cpuclock="watch -n2 -x bash -c \"cpuclocktemp\""
#TODO: replace above and below with python curses application for nicer formatting
#monitors various bits of info about the gpu    see "nvidia-smi --help-query-gpu" of "nvidia-smi --query" for more info
gpuinfotemp(){
    nvidia-smi --query-gpu=clocks.current.graphics --format=csv
    nvidia-smi --query-gpu=clocks.current.memory --format=csv
    nvidia-smi --query-gpu=memory.used --format=csv
    nvidia-smi --query-gpu=temperature.gpu --format=csv
    nvidia-smi --query-gpu=fan.speed --format=csv
    nvidia-smi --query-gpu=power.draw --format=csv
}
export -f gpuinfotemp
alias gpuinfo="watch -n2 -x bash -c \"gpuinfotemp\""
alias greenwithenvy="flatpak run com.leinardi.gwe"

#counter strike source dedicated server shortcut
alias cssds="/home/yobleck/.steam/steamcmd/css/srcds_run -console -game cstrike -maxplayers 32 -port 27015 -sv_airaccelerate 150 +map surf_utopia_njv"
surf(){
    if [[ $1 == "h" || $1 == "-h" || $1 == "--help" ]]; then
        echo "list of surf maps in /home/yobleck/.steam/steamcmd/css/cstrike/maps/"
        ls /home/yobleck/.steam/steamcmd/css/cstrike/maps/surf*.bsp
    elif [ -z "$1" ]; then
        echo "no map supplied, defaulting to surf_utopia_njv"
        echo "running dedicated server, launching steam and running CS:S"
        tmux new-session "/home/yobleck/.steam/steamcmd/css/srcds_run -console -game cstrike \
                          -maxplayers 32 -port 27015 -tickrate 100 -sv_airaccelerate 150 +map surf_utopia_njv" \; \
        split-window "steam -applaunch 240 +connect 10.0.0.136:27015"
    else
        echo "running dedicated server with map $1, launching steam and running CS:S"
        tmux new-session "/home/yobleck/.steam/steamcmd/css/srcds_run -console -game cstrike \
                          -maxplayers 32 -port 27015 -tickrate 100 -sv_airaccelerate 150 +map $1" \; \
        split-window "steam -applaunch 240 +connect 10.0.0.136:27015"
    fi
    echo "successful shutdown"
}
export -f surf

#image upscaling
alias waifu2x="waifu2x-ncnn-vulkan"

#alias fahthrottle="cpulimit -p $(pgrep FahCore_22) -l 80"
fahthrottle(){
    cpulimit -p $(pgrep FahCore_22 || pgrep FahCore_21) -l $1
}
export -f fahthrottle

clip(){
    qdbus org.kde.klipper /klipper setClipboardContents "$*" 2>/dev/null
}
export -f clip

alias musicbee="wine \"/home/yobleck/.wine/drive_c/Program Files (x86)/MusicBee3/MusicBee.exe\""
alias kiwix="env XDG_CONFIG_HOME=/usr/share/color-schemes/Breath.colors kiwix-desktop"
alias gtav_radio="cd /home/yobleck/gtav_radio; python gtav_radio.py"
alias mocs="python /home/yobleck/.moc/sort/sorter.py"
alias qtile="startx /usr/bin/qtile start"

#sudo -E /home/yobleck/desktop_scroll/scroll.sh
