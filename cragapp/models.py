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
    idvpss     = Column(Integer, ForeginKey('vpss.idvpss'))                  
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
    idads         = Column(Integer, ForeginKey('ads.idads'))
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

class Ad(Base):
    __tablename__ = 'ads'
    idads         = Column(Integer, primary_key=True)
    idcrag        = Column(String(25), unique = True)
    description   = Column(Text)
    title         = Column(String(100)) 
    posting_time  = Column(String(5))
    status        = Column(String(30))
    idusers       = Column(Integer, ForeginKey('users.idusers'))
    category      = Column(String(20))
    idarea        = Column(Integer, ForeginKey('area.idarea'))
    replymail     = Column(String(50))
    contact_phone     = Column(String(50))
    contact_name      = Column(String(255))
    postal            = Column(String(25))
    specific_location = Column(String(50))
    parent_id         = Column(Integer, ForeignKey('ads.idads'))

    def __init__(self,
                 idcrag,
                 description,
                 title,
                 posting_time,
                 status,
                 idusers,
                 category,
                 area,
                 replymail,
                 contact_phone, 
                 contact_name,  
                 postal,
                 specific_location):
        self.idcrag            = idcrag
        self.description       = description  
        self.title             = title        
        self.posting_time      = posting_time 
        self.status            = status       
        self.idusers           = idusers      
        self.category          = category     
        self.area              = area         
        self.replymail         = replymail
        self.contact_phone     = contact_phone 
        self.contact_name      = contact_name  
        self.postal            = postal
        self.specific_location = specific_location
        

    def __repr__(self):
        return '<Ad %r>' % (self.title)

