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

logging.basicConfig(filename='logs/cragloop.log',level=logging.ERROR)

def loop():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    #get ads having scheduling actions
    ads = Ad.query.filter(Ad.posting_time == now).all()

    for ad in ads:
        action = ad.scheduled_action
        idads  = str(ad.idads)
        posting_time = datetime.datetime.strptime(ad.posting_time,
                                                  "%Y-%m-%d %H:%M")

        u = User.query.filter(User.idusers == ad.idusers).first()
        v = VPS.query.filter(VPS.idvpss == u.idvpss).first()
        proxy = 'https://' + ':'.join([str(v.ip), str(v.port)])
        my_env = os.environ.copy()
        my_env["https_proxy"] = proxy
        
        os_process_code = subprocess.call(
            ["python","cragapp/admanager.py","--idads", idads, "--action", action,
             "&&",
             "python","cragapp/syncronizer.py","adscrap","--idads", idads],
            env=my_env)
        
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

        #digit repost timeout is sign of necessity of doing reposts
        #statuses no matter(yet)
        if ad.repost_timeout \
           and ad.repost_timeout != 'none'\
            and ad.repost_timeout.isdigit():
            timeout = int(ad.repost_timeout)*60*60#seconds
            #will try renew, if not possible - try repost,
            #if not possible- log error 
            if "renew" in ad.allowed_actions: action = "renew"
            elif "repost" in ad.allowed_actions: action = "repost"
            else:
                logging.error('repost/renew not aviable for '+
                              +ad.__repr__())
                action = ""
                
            #(posting_time > now) must be True. 
            def calc_posting_time(posting_time):
                while posting_time < datetime.datetime.now():
                    posting_time = posting_time\
                        + datetime.timedelta(seconds = timeout)
                return posting_time
            
            if action:
                ad.scheduled_action = action
                ad.posting_time = calc_posting_time(posting_time).\
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
