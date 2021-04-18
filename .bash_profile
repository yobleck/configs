#
# ~/.bash_profile
#
export QT_QPA_PLATFORMTHEME="qt5ct" #for using kde qt apps outside kde
export XCURSOR_THEME=breeze_cursors #for setting cursor to correct theme over windows
xsetroot -cursor_name left_ptr # ditto but over qtile root window and bar
[[ -f ~/.bashrc ]] && . ~/.bashrc
