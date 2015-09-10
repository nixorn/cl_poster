#database models for autogenerate and manage tables in database

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.sqlite import INTEGER, VARCHAR, TEXT, BLOB
from sqlalchemy.orm import relationship
from database import Base

class VPS(Base):
    __tablename__ = 'vpss'
    idvpss   = Column(INTEGER, primary_key=True)
    ip       = Column(VARCHAR(15))
    port     = Column(VARCHAR(5))
    login    = Column(VARCHAR(50))
    password = Column(VARCHAR(50))


    def __init__(self,ip,port,login,password ):
        self.ip      = ip
        self.port    = port
        self.login   = login
        self.password= password

    def __repr__(self):
        return str({'idvpss':self.idvpss,
                    'ip':self.ip,
                    'port':self.port,
                    'user':self.login,
                    'password': self.password})

class User(Base):
    __tablename__ = 'users'
    idusers    = Column(INTEGER, primary_key=True)
    idvpss     = Column(INTEGER, ForeignKey('vpss.idvpss'))
    username   = Column(VARCHAR(50), unique = True)
    password   = Column(VARCHAR(50))
    mail_pass  = Column(VARCHAR(50))


    def __init__(self, idvpss,username,password, mail_pass):
        self.idvpss   = idvpss
        self.username = username
        self.password = password
        self.mail_pass = mail_pass


    def __repr__(self):
        return '<User %r>' % (str(self.username))


class Image(Base):
    __tablename__ = 'images'
    idimages      = Column(INTEGER, primary_key=True)
    extension     = Column(VARCHAR(10))
    mime          = Column(VARCHAR(15))
    filename      = Column(VARCHAR(50))
    #link on craiglist to prevent downloading the same picture
    craglink      = Column(VARCHAR(255), unique=True)
    idads         = Column(INTEGER, ForeignKey('ads.idads'))
    image         = Column(BLOB)

    def __init__(self, idads, extension, mime, filename, image, craglink=''):
        self.idads     = idads
        self.extension = extension
        self.mime      = mime
        self.filename  = filename
        self.craglink  = craglink
        self.image     = image

    def __repr__(self):
        return '<Image %r, id:%r>' % (self.filename, str(self.idimages))




class Area(Base):
    __tablename__ = "area"
    #http://moscow.craigslist.org/res... moscow is urlname
    #Moscow is fullname
    #clcode is part of data of form response of creation ad. looks like "mos" or "isp"
    idarea    = Column(INTEGER, primary_key=True)
    urlname   = Column(VARCHAR(20), unique = True)
    fullname  = Column(VARCHAR(25), unique = True)
    clcode    = Column(VARCHAR(4) , unique = True)

    def __init__(self, urlname, fullname, clcode):
        self.urlname  = urlname
        self.fullname = fullname
        self.clcode   = clcode


    def __repr__(self):
        return '<Area %r, id:%r>' % (self.fullname, str(self.idarea))

class Category(Base):
    __tablename__ = 'category'
    idcategory    = Column(INTEGER, primary_key=True)
    fullname      = Column(VARCHAR(100))
    clcode        = Column(VARCHAR(4))
    numcode       = Column(INTEGER)
    def __init__(self, fullname, clcode, numcode):

        self.fullname = fullname
        self.clcode   = clcode
        self.numcode  = numcode

    def __repr__(self):
        return '<Category %r, id:%r >' % (self.fullname,str(self.idcategory))


    
    
class Ad(Base):
    __tablename__ = 'ads'
    idads         = Column(INTEGER, primary_key=True)
    idcrag        = Column(VARCHAR(25), default='')
    description   = Column(TEXT)
    title         = Column(VARCHAR(100))
    posting_time  = Column(VARCHAR(25))
    scheduled_action = Column(VARCHAR(25))  #will happen in posting_time. one of allowed actions or None
    repost_timeout  = Column(VARCHAR(10)) #""|"48"|"72" hrs
    prev_action   = Column(VARCHAR(25))
    prev_act_time = Column(VARCHAR(25))
    prev_act_stat = Column(VARCHAR(20))
    status        = Column(VARCHAR(30))
    idusers       = Column(INTEGER, ForeignKey('users.idusers'))
    idcategory    = Column(INTEGER, ForeignKey('category.idcategory'))
    idarea        = Column(INTEGER, ForeignKey('area.idarea'))
    replymail     = Column(VARCHAR(50))
    allowed_actions   = Column(VARCHAR(100))
    contact_phone     = Column(VARCHAR(50))
    contact_name      = Column(VARCHAR(255))
    postal            = Column(VARCHAR(25))
    specific_location = Column(VARCHAR(50))
    parent_id         = Column(INTEGER, ForeignKey('ads.idads'))
    haslicense        = Column(VARCHAR(1)) # '1' or '0'
    license_info      = Column(VARCHAR(100))
    #dubles defines by admanager clean_up function
    is_duble          = Column(VARCHAR(1), default='0')
    
    def __init__(self,
                 idcrag,
                 description,
                 title,
                 posting_time,
                 scheduled_action,
                 repost_timeout,
                 prev_action,   
                 prev_act_time, 
                 prev_act_stat, 
                 status,
                 idusers,
                 idcategory,
                 idarea,
                 replymail,
                 allowed_actions,
                 contact_phone,
                 contact_name,
                 postal,
                 specific_location,
                 haslicense,
                 license_info):
        self.idcrag            = idcrag
        self.description       = description
        self.title             = title
        self.posting_time      = posting_time
        self.scheduled_action  = scheduled_action
        self.repost_timeout    = repost_timeout
        self.status            = status
        self.idusers           = idusers
        self.idcategory        = idcategory
        self.idarea            = idarea
        self.replymail         = replymail
        self.allowed_actions   = allowed_actions
        self.contact_phone     = contact_phone
        self.contact_name      = contact_name
        self.postal            = postal
        self.specific_location = specific_location
        self.haslicense        = haslicense
        self.license_info      = license_info

    def __repr__(self):
        return '<Ad %r, id:%r>' % (self.title, str(self.idads))
