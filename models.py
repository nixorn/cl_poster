from sqlalchemy import Column, Integer, String, Text
from database import Base

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
                 idads,
                 description,
                 title,
                 posting_time,
                 status,
                 idusers,
                 category,
                 area,
                 replymail):
        self.idads         = idads        
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


class Image(Base):
    __tablename__ = 'images'
    idimages      = Column(Integer, primary_key=True)
    idads         = Column(Integer)
    image         = Column(Text)

    def __init__(self, idimages, idads, image):
        self.idimages = idimages
        self.idads    = idads
        self.image    = image
        
    def __repr__(self):
        return '<Image %r>' % (str(self.idimages))


class User(Base):
    __tablename__ = 'users'
    idusers    = Column(Integer, primary_key=True)
    idvpss     = Column(Integer)
    username   = Column(String(50), unique = True)
    password   = Column(String(50))
    accountID  = Column(Integer)

    def __init__(self, idimages, idads, image):
        self.idimages = idimages
        self.idads    = idads
        self.image    = image
        
    def __repr__(self):
        return '<Image %r>' % (str(self.idimages))
    

    CREATE TABLE `vpss` (
          `idvpss` int(11) NOT NULL AUTO_INCREMENT,
          `ip` varchar(45) DEFAULT NULL,
          `port` varchar(45) DEFAULT '1080',
          `login` varchar(45) DEFAULT NULL,
          `password` varchar(45) DEFAULT NULL,
          PRIMARY KEY (`idvpss`)
        ) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
