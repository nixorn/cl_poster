from sqlalchemy import Column, Integer, String, Text, ForeignKey
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
    idvpss     = Column(Integer)                  
    username   = Column(String(50), unique = True)
    password   = Column(String(50))
    accountID  = Column(Integer)
    
    def __init__(self, idvpss,username,password,accountID):
        self.idvpss   = idvpss   
        self.username = username 
        self.password = password 
        self.accountID= accountID
        
    def __repr__(self):
        return '<User %r>' % (str(self.username))
    

class Image(Base):
    __tablename__ = 'images'
    idimages      = Column(Integer, primary_key=True)
    idads         = Column(Integer)
    image         = Column(Text)

    def __init__(self, idads, image):
        self.idads    = idads
        self.image    = image
        
    def __repr__(self):
        return '<Image %r>' % (str(self.idimages))




class Ad(Base):
    __tablename__ = 'ads'
    idads         = Column(Integer, primary_key=True)
    description   = Column(Text)
    title         = Column(String(100)) 
    posting_time  = Column(String(5))
    status        = Column(String(30))
    idusers       = Column(Integer)
    category      = Column(String(20))
    area          = Column(String(5))
    replymail     = Column(String(50))

    def __init__(self,
                 description,
                 title,
                 posting_time,
                 status,
                 idusers,
                 category,
                 area,
                 replymail):
        self.description   = description  
        self.title         = title        
        self.posting_time  = posting_time 
        self.status        = status       
        self.idusers       = idusers      
        self.category      = category     
        self.area          = area         
        self.replymail     = replymail    

    def __repr__(self):
        return '<Ad %r>' % (self.title)

