#!./bin/python 

#WILL DROP DATABASE!!! testing script. 

import MySQLdb
import base64


#base64 image for RSS test ad 
with open("test_img.jpg", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())



#database init stuff
db = MySQLdb.connect(host="localhost", user="root", passwd="passwd", db="cragapp", charset='utf8')
db.autocommit(True)
cursor = db.cursor()

#drop database
sql = "DROP TABLE `ads`; DROP TABLE `users`; DROP TABLE `vpss`;"
try:
    cursor.execute(sql)
    
except: print "Is no database here."
cursor.close()

#recreate database.
cursor = db.cursor()
sql = """
CREATE TABLE `ads` (
  `idads` int(11) NOT NULL AUTO_INCREMENT,
  `description` mediumtext,
  `title` varchar(45) DEFAULT NULL,
  `image` longtext,
  `posting_time` varchar(10) DEFAULT NULL,
  `status` varchar(45) DEFAULT 'not_sended',
  `idusers` int(11) DEFAULT NULL,
  `category` varchar(45) DEFAULT NULL,
  `area` varchar(45) DEFAULT NULL,
  `replymail` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idads`),
  UNIQUE KEY `idads_UNIQUE` (`idads`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE `users` (
  `idusers` int(11) NOT NULL AUTO_INCREMENT,
  `idvpss` int(11) DEFAULT NULL,
  `login` varchar(45) DEFAULT NULL,
  `password` varchar(45) DEFAULT NULL,
  `accountID` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idusers`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `vpss` (
  `idvpss` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(45) DEFAULT NULL,
  `port` varchar(45) DEFAULT  '1080',
  PRIMARY KEY (`idvpss`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""
cursor.execute(sql)
cursor.close()


#test rows
#VPS's
cursor = db.cursor()
VPS = [('127.0.0.1', 5000, None, None),
       ('23.105.132.100', 8091, None, None)]

sql = """
INSERT INTO `cragapp`.`vpss`  (`ip`, `port`)
VALUES (%s, %s);"""

cursor.executemany(sql, VPS)


#users
users = [(1,"murchendaizer@gmail.com", "roottoor", "0"),]

sql = """
INSERT INTO `cragapp`.`users`
( `idvpss`,
 `login`,
 `password`,
 `accountID`)
VALUES
(%s,%s,%s,%s);"""

cursor.executemany(sql, users)
cursor.close()


#ads
cursor = db.cursor()
ads = [('murchendaize@gmail.com',             #replymail
        'I want nothing',                     #title
        'Just a guy who dont want see anyone',#description
        encoded_image,                        #base64 image
        '13:50',                              #posting time
        'not_sended',                         #status
        1,                                    #users.idusers
        'sls',                                #category
        'plm'                                 #area
    ),('murchendaize@gmail.com',             #replymail
        'I want nothing',                     #title
        'Just a guy who dont want see anyone',#description
        encoded_image,                        #base64 image
        '13:50',                              #posting time
        'not_sended',                         #status
        1,                                    #users.idusers
        'sls',                                #category
        'plm'                                 #area
    )]

sql = """
INSERT INTO ads (replymail, title, description, image, posting_time, status, idusers,category, area) 
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"""

cursor.executemany(sql, ads)
cursor.close()
db.close()
