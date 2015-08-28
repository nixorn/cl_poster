from imbox import Imbox
import re
import time
import logging
import requests
from models import Ad, User, VPS
from database import db_session

logging.basicConfig(filename='logs/mailloop.log',level=logging.DEBUG)

def mail_loop(user):
    username = user.username
    password = user.mail_pass
    if   'gmail.com' in username: server = 'imap.gmail.com'
    elif 'yahoo.com' in username: server = 'imap.mail.yahoo.com'
    else: raise NotImplementedError("only yahoo.com and gmail.com imaps supported")

    imb = Imbox(server, username, password, ssl=True)
    msgs = imb.messages(unread=True,sent_from='robot@craigslist.org')

    vps = VPS.query.filter(VPS.idvpss == user.idvpss).first()
    http_proxy = 'http://' + ':'.join([vps.ip, vps.port])
    https_proxy = http_proxy.replace('http', 'https')
    proxies = {'http': http_proxy,'https': http_proxy}
    
    for uid, msg in msgs:
        imb.mark_seen(uid)
        confirm_url = re.findall('https://post.craigslist.org/./.+/.+\r',
                                  msg.body['plain'][0])[0].replace('\r','')
        rsp = requests.get(confirm_url,proxies=proxies)
        logging.debug("confirmation request for url "+rsp.url\
                      +' have status '+ str(rsp.status_code))
        with open("logs/mail_confirm_"+username.split('@')[0]+'.html', 'w') as f:
            f.write(rsp.content)
            f.flush()
            f.close()
    
if __name__ == '__main__':
    while 1:
        for user in User.query.all():
            mail_loop(user)
            sleep(1200)#every 20 minutes
