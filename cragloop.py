#!./bin/python 

#while server manipulate database via GUI, mainloop send ads.
import MySQLdb
import base64
import time
import socks

from rss_render import render

db = MySQLdb.connect(host="localhost", user="root", passwd="passwd", db="cragapp", charset='utf8')
db.autocommit(True)


def send(adid):
    sql = """
    SELECT 
    `ads`.`description`,
    `ads`.`title`,
    `ads`.`status`,
    `ads`.`category`,
    `ads`.`area`,
    `ads`.`replymail`,
    `users`.`username`,
    `users`.`password`,
    `users`.`accountID`,
    `vpss`.`ip`,
    `vpss`.`port`
    FROM `cragapp`.`ads` 
    INNER JOIN `cragapp`.`users` ON `ads`.`idusers`  = `users`.`idusers`
    INNER JOIN `cragapp`.`vpss`  ON `users`.`idvpss` = `vpss`.`idvpss`
    WHERE (`ads`.`status` = 'not_sended' or `ads`.`status` is null)
    `ads`.`idads` = %s;"""

    cursor = db.cursor()
    cursor.execute(sql,(adid,))
    description, title, status, category, area, replymail, username, password, acountID, ip, port = cursor.fetchone()
    
    cursor.close()

    sql = """
    SELECT 
    `images`.`image`
    FROM `cragapp`.`images` 
    WHERE `images`.`idads` = %s;"""

    cursor = db.cursor()
    cursor.execute(sql,(adid,))
    images = [x[0] for x in  cursor.fetchall()]
    
    cursor.close()
    
    s = socks.socksocket() # Same API as socket.socket in the standard lib
        
    s.set_proxy(socks.SOCKS5, ip+":"+port) # SOCKS4 and SOCKS5 use port 1080 by default
    
    s.connect(("https://post.craigslist.org/bulk-rss/post", 80))
    s.sendall("POST / HTTP/1.1 \n Content-Type: application/x-www-form-urlencoded \n\n" + \
              render(replymail,title,description,username,password,acountID,category,area,images))
    print s.recv(4096)

def loop():
    hour = str(time.localtime().tm_hour)
    minute = str(time.localtime().tm_min)
    if len(hour) == 1: hour = '0' + hour 
    if len(minute) == 1: minute = '0' + minute
    now = hour + ':' + minute
    sql = "SELECT `ads`.`idads` FROM `cragapp`.`ads` WHERE `ads`.`posting_time` = %s;"
    cursor = db.cursor()
    cursor.execute(sql,(now,))
    data = cursor.fetchall()
    cursor.close()
    print now

    for ad in data:
        send(ad[0])
    

while 1:
    loop()
    time.sleep(30)
