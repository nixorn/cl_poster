#!./bin/python 

#while server manipulate database via GUI, mainloop send ads.
#statuses of ads changes and tracks here



import time
import base64
import datetime
import logging
import subprocess

from database import db_session
from models import VPS, Ad

logging.basicConfig(filename='cragloop.log',level=logging.ERROR)

def loop():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    ads = Ad.query.filter(Ad.posting_time == now).all()

    for ad in ads:
        action = ad.scheduled_action
        idads  = str(ad.idads)
        posting_time = datetime.datetime.strptime(ad.posting_time,
                                                  "%Y-%m-%d %H:%M")
        os_process_code = subprocess.call(
            ["python","cragapp/admanager.py","--idads", idads, "--action", action,
             "&&",
             "python","cragapp/syncronizer.py","adscrap","--idads", idads]) 
        ad.prev_action = ad.scheduled_action
        ad.prev_act_time = ad.posting_time
        if os_process_code == 2:
            ad.prev_act_stat = 'Error'
            logging.error('admanager didnt '
                          + action
                          + 'on ad'+ad.title
                          +' id:'+str(ad.idads))
        else: ad.prev_act_stat = 'OK'
        ad.scheduled_action = ''
        ad.posting_time     = ''
        
        if ad.repost_timeout and ad.repost_timeout != 'none':
            timeout = int(ad.repost_timeout)*60*60#seconds
            #will try renew, if not possible - try repost,
            #if not possible- log error 
            if "renew" in ad.allowed_actions: action = "renew"
            elif "repost" in ad.allowed_actions: action = "repost"
            else:
                logging.error('repost/renew not aviable for '+
                              +ad.__repr__())
                action = ""

            if action:
                ad.scheduled_action = action
                ad.posting_time = (posting_time
                    + datetime.timedelta(seconds = timeout)).\
                    strftime("%Y-%m-%d %H:%M")
            
        db_session.add(ad)
        
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            logging.error("cragloop can not commit this ad because:"+e.message)


while 1:
    loop()
    time.sleep(20)
