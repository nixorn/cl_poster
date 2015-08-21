#!./bin/python 

#while server manipulate database via GUI, mainloop send ads.



import time
import base64
import datetime
#import socks
import subprocess

from database import db_session
from models import VPS, Ad


def loop():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print now

    ads = Ad.query.filter(Ad.posting_time == now).all()

    for ad in ads:
        action = ad.scheduled_action
        idads  = str(ad.idads)
        print "ad",idads,"action", action
        subprocess.call(["python", "cragapp/admanager.py", "--idads", idads, "--action", action,
                         "&&", "python", "cragapp/syncronizer.py","adscrap","--idads", idads]) 
    

while 1:
    loop()
    time.sleep(20)
