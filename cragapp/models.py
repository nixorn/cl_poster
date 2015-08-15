#database models for autogenerate and manage tables in database

from sqlalchemy import Column, Integer, String, Text, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from database import Base

class VPS(Base):
    __tablename__ = 'vpss'
    idvpss   = Column(Integer, primary_key=True)
    ip       = Column(String(15))                  
    port     = Column(String(5))
    login    = Column(String(50))
    password = Column(String(50))

    
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
    idusers    = Column(Integer, primary_key=True)
    idvpss     = Column(Integer, ForeignKey('vpss.idvpss'))                  
    username   = Column(String(50), unique = True)
    password   = Column(String(50))

    
    def __init__(self, idvpss,username,password):
        self.idvpss   = idvpss   
        self.username = username 
        self.password = password 

        
    def __repr__(self):
        return '<User %r>' % (str(self.username))
    

class Image(Base):
    __tablename__ = 'images'
    idimages      = Column(Integer, primary_key=True)
    extension     = Column(String(10))
    #link on craiglist to prevent downloading the same picture
    craglink      = Column(String(255), unique=True) 
    idads         = Column(Integer, ForeignKey('ads.idads'))
    image         = Column(LargeBinary)

    def __init__(self, idads, extension, craglink, image):
        self.idads     = idads
        self.extension = extension
        self.craglink  = craglink 
        self.image     = image
        
    def __repr__(self):
        return '<Image %r>' % (str(self.idimages))




class Area(Base):
    __tablename__ = "area"
    #http://moscow.craigslist.org/res... moscow is urlname                  
    #Moscow is fullname                                                 
    #clcode is part of data of form response of creation ad. looks like "mos" or "isp"
    idarea    = Column(Integer, primary_key=True)
    urlname   = Column(String(20), unique = True)
    fullname  = Column(String(25), unique = True)
    clcode    = Column(String(4) , unique = True)

    def __init__(self, urlname, fullname, clcode):
        self.urlname  = urlname
        self.fullname = fullname
        self.clcode   = clcode
        

    def __repr__(self):
        return '<Area %r>' % (self.fullname)

class Category(Base):
    __tablename__ = 'category'
    idcategory    = Column(Integer, primary_key=True)
    fullname      = Column(String(100))
    clcode        = Column(String(4))
    numcode       = Column(Integer)
    def __init__(self, fullname, clcode, numcode):

        self.fullname = fullname
        self.clcode   = clcode
        self.numcode  = numcode        

    def __repr__(self):
        return '<Category %r>' % (self.fullname)
    
class Ad(Base):
    __tablename__ = 'ads'
    idads         = Column(Integer, primary_key=True)
    idcrag        = Column(String(25), unique = True)
    description   = Column(Text)
    title         = Column(String(100)) 
    posting_time  = Column(String(5))
    status        = Column(String(30))
    idusers       = Column(Integer, ForeignKey('users.idusers'))
    idcategory    = Column(Integer, ForeignKey('category.idcategory'))
    idarea        = Column(Integer, ForeignKey('area.idarea'))
    replymail     = Column(String(50))
    contact_phone     = Column(String(50))
    contact_name      = Column(String(255))
    postal            = Column(String(25))
    specific_location = Column(String(50))
    parent_id         = Column(Integer, ForeignKey('ads.idads'))
    haslicense        = Column(String(1)) # '1' or '0'
    license_info      = Column(String(100))

    def __init__(self,
                 idcrag,
                 description,
                 title,
                 posting_time,
                 status,
                 idusers,
                 idcategory,
                 idarea,
                 replymail,
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
        self.status            = status       
        self.idusers           = idusers      
        self.idcategory        = idcategory     
        self.idarea            = idarea         
        self.replymail         = replymail
        self.contact_phone     = contact_phone 
        self.contact_name      = contact_name  
        self.postal            = postal
        self.specific_location = specific_location
        self.haslicense        = haslicense  
        self.license_info      = license_info
        
    def __repr__(self):
        return '<Ad %r>' % (self.title)

