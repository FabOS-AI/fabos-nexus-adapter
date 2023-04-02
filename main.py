import os
import time, threading
from nexus_adapter import do_update

UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", "120"))

def do_option_refresh():
    print(time.ctime())
    do_update()
    print('----- '*30)
    print(f"waiting for '{UPDATE_INTERVAL}'s ")
    threading.Timer(UPDATE_INTERVAL, do_option_refresh).start()

do_option_refresh()