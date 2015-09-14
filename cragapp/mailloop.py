from imbox import Imbox
import re
import time
import logging
import requests
from models import Ad, User, VPS
from database import db_session
from lxml import etree
from io import StringIO
import os


logging.basicConfig(filename='logs/mailloop.log',level=logging.DEBUG)
    
def mail_loop(user):
    username = user.username
    password = user.mail_pass
    if   'gmail.com' in username: server = 'imap.gmail.com'
    elif 'yahoo.com' in username: server = 'imap.mail.yahoo.com'
    else: raise NotImplementedError("only yahoo.com and gmail.com imaps supported")

    imb = Imbox(server, username, password, ssl=True)
    msgs = imb.messages(unread=True,sent_from='robot@craigslist.org')

    v = VPS.query.filter(VPS.idvpss == user.idvpss).first()
    http_proxy = 'http://' + '@'.join([
            ':'.join([str(v.login), str(v.password)]),
            ':'.join([str(v.ip), str(v.port)])])
    https_proxy = http_proxy.replace('http', 'https')

    my_env = os.environ.copy()
    my_env["https_proxy"] = https_proxy
    my_env["http_proxy"] = http_proxy
    
    for uid, msg in msgs:
        imb.mark_seen(uid)
        confirm_url = re.findall('https://post.craigslist.org/./.+/.+\r',
            msg.body['plain'][0])[0].replace('\r','')
        
        subprocess.call(
            ["python","cragapp/admanager.py",
             "--action", "confirm",
             "--confirm_link", confirm_url,
             "--username",username],
            env=my_env)
        
if __name__ == '__main__':
    while 1:
        for user in User.query.all():
            mail_loop(user)
            time.sleep(1200)#every 20 minutes
