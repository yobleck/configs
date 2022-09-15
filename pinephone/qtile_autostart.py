import json
import os
import shlex  # from shlex import split?
import subprocess
import sys
import time

import pam
import setproctitle;


setproctitle.setproctitle("Qtile_autostart");
INSTALL_PATH = "/home/alarm/.config/qtile"  # replace with read from config
ETC_PATH = "/home/alarm/.config/qtile/etc"  # how to get this without knowing where it is?


def log(i):
    with open(f"{INSTALL_PATH}/test.log", "a") as f:
        f.write(f"{time.asctime()}: {str(i)}\n")


def load_envars() -> None:
    """Load environment variables"""
    #load programs that require root like lisgd? or systemd service unit?
    os.setgid(1000)
    os.setuid(1000)

    for x in range(10):
        if not os.path.exists(f"/tmp/.X{x}-lock"):
            break
    os.environ["DISPLAY"] =  f":{x}"
    os.environ["XDG_VTNR"] = "2"
    with open(f"/proc/{os.getpid()}/sessionid", "r") as f:
        os.environ["XDG_SESSION_ID"] = f.readline().strip()

    # misc other envars
    with open(f"{ETC_PATH}/envars.json", "r") as f:
        envars = json.load(f)
    for key, value in envars.items():
        os.environ[key] = value

    # create .Xauthority file https://github.com/fairyglade/ly/blob/master/src/login.c
    os.chdir(envars["HOME"])
    os.system(f"/usr/bin/xauth add :{x} . `/usr/bin/mcookie`")


def main() -> int:
    try:
	    log("start")
	    os.system(f"chvt 2")  # change vt focus
	    username = "alarm"
	    password = "123456"
	    pam_obj = pam.PamAuthenticator()
	    pam_obj.authenticate(username, password, call_end=False)
	    log("second auth")
	    pam_obj.open_session()
	    # set env vars. TODO more stuff from printenv
	    load_envars()

	    # start DE/WM
	    log("start X")
	    xorg = subprocess.Popen(["/usr/bin/X", f"{os.environ['DISPLAY']}", f"vt{os.environ['XDG_VTNR']}"])
	    time.sleep(0.2)  # should use xcb.connect() to verify connection is possible but too lazy
	    log("start qtile")
	    dewm = subprocess.Popen(["/usr/bin/sh", f"{ETC_PATH}/xsetup.sh", "/usr/bin/qtile",  "start"])
	    dewm.wait()
	    xorg.terminate()
	    pam_obj.close_session()
	    pam_obj.end()
	    log("close child")
    except Exception as e:
        log(e)

    return 0


if __name__ == "__main__":
    main()
