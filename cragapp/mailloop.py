from imbox import Imbox
import re
import time
import logging
import requests
from models import Ad, User, VPS
from database import db_session
from lxml import etree
from io import StringIO


logging.basicConfig(filename='logs/mailloop.log',level=logging.DEBUG)


def debug_html_content(filename, content):
    with open(filename, "w") as f:
        f.write(content)
        f.flush()
        f.close()

def accept_terms(body):
    '''body of "accept terms of use" page -> accept request to CL '''
    tree = etree.parse(StringIO(unicode(body)), etree.HTMLParser())
    cryptedStepCheck = tree.\
        xpath("//form[./input[@name='cryptedStepCheck']]"\
              +"/input[@name='cryptedStepCheck']/@value")[0]
    confirm_link = tree.xpath("//form/@action")[0]
    r = requests.post(confirm_link,
                      data={
                          "cryptedStepCheck":cryptedStepCheck,
                          "continue":"y"})
    debug_html_content("logs/accepting_terms.html",r.content)
    
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
    proxies = {'http': http_proxy,'https': http_proxy}
    
    for uid, msg in msgs:
        imb.mark_seen(uid)
        confirm_url = re.findall('https://post.craigslist.org/./.+/.+\r',
                                  msg.body['plain'][0])[0].replace('\r','')
        rsp = requests.get(confirm_url,proxies=proxies)
        logging.debug("confirmation request for url "+rsp.url\
                      +' have status '+ str(rsp.status_code))

        debug_html_content("logs/mail_confirm_"+username.split('@')[0]+'.html',
                           rsp.content)
                    
        if "Terms of Use" in rsp.content:
            accept_terms(rsp.content)
        
if __name__ == '__main__':
    while 1:
        for user in User.query.all():
            mail_loop(user)
            time.sleep(1200)#every 20 minutes
