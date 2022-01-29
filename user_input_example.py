import sys, tty, termios, select
"""
#blocking. program sleeps while waiting to user input
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

while True:
    ch = getch()
    print(ch,end="\n\033[F")
    if ch == "q":
        print("end")
        break

"""
#Non blocking a.k.a. busy waiting. useful for when stuff needs to happen without user input
def getch_noblock():
    fd = sys.stdin #.fileno();
    old_settings = termios.tcgetattr(fd)
    #new_settings = termios.tcgetattr(fd)
    #new_settings[3] = new_settings[3] & ~termios.ECHO #no echo
    try:
        tty.setcbreak(fd)
        r, _, _ = select.select([fd],[],[],.01) #timeout. smaller = more responsive but more cpu usage
        if(r):
            ch = sys.stdin.read(1) #TODO: handle special escape chars like ^[ arrow keys
        else:
            ch = -1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

while True:
    ch = getch_noblock()
    print(ch, end="\n\033[F")
    if ch == "q":
        print("end")
        break
#"""

""" # getch no block without select or tty modules
def getch_noblock() -> str:  # handle user input. blocking mode
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new = old_settings
    new[3] &= ~termios.ICANON
    new[6][termios.VMIN] = 0
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSADRAIN, new)
    try:
        #tty.setcbreak(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
"""
