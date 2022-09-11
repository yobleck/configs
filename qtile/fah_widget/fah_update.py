import json
import sys
import time

import requests
import setproctitle


setproctitle.setproctitle("FAHStats_updater");

def log(i):
    f = open("/home/yobleck/.config/qtile/qtile_log.txt", "a")
    f.write(str(i) + "\n")
    f.close()


while True:
    body = requests.get("https://api.foldingathome.org/user/yobleck").json()
    with open("/home/yobleck/.config/qtile/fah_widget/fah_stats.txt", "w") as f:
        json.dump(body, f)
    time.sleep(int(sys.argv[1]))
