#!./bin/python 

from cragapp.database import init_db

init_db()


from cragapp.models import Area, Category
from cragapp.database import engine, db_session

AREAS = [{"urlname":"longisland", "fullname":"Long Island", "clcode":"isp"},
         {"urlname":"newyork"   , "fullname":"New York"   , "clcode":"nyc"},
         {"urlname":"moscow"    , "fullname":"Moscow"     , "clcode":"mos"}]


#insert areas into db, because it need in admanager
for area in AREAS:
    a = Area(area['urlname'],  #http://moscow.craigslist.org/res... moscow is urlname
             area['fullname'], #Moscow or Long Island
             area['clcode'])   #part of data of form response of creation ad. looks like "mos" or "isp"
    db_session.add(a)
    db_session.commit()



CATEGORIES =[
    {'clcode':'aos','fullname':'automotive services'         ,'numcode':106},
    {'clcode':'bts','fullname':'beauty services'             ,'numcode':138},
    {'clcode':'cps','fullname':'computer services'           ,'numcode':76 },
    {'clcode':'crs','fullname':'creative services'           ,'numcode':77 },
    {'clcode':'cys','fullname':'cycle services'              ,'numcode':158},
    {'clcode':'evs','fullname':'event services'              ,'numcode':79 },
    {'clcode':'fgs','fullname':'farm & garden services'      ,'numcode':154},
    {'clcode':'fns','fullname':'financial services'          ,'numcode':104},
    {'clcode':'hss','fullname':'household services'          ,'numcode':80 },
    {'clcode':'lbs','fullname':'labor & moving'              ,'numcode':82 },
    {'clcode':'lgs','fullname':'legal services'              ,'numcode':103},
    {'clcode':'lss','fullname':'lessons & tutoring'          ,'numcode':81 },
    {'clcode':'mas','fullname':'marine services'             ,'numcode':156},
    {'clcode':'pas','fullname':'pet services'                ,'numcode':155},
    {'clcode':'rts','fullname':'real estate services'        ,'numcode':105},
    {'clcode':'sks','fullname':'skilled trade services'      ,'numcode':83 },
    {'clcode':'biz','fullname':'small biz ads'               ,'numcode':4  },
    {'clcode':'ths','fullname':'therapeutic services'        ,'numcode':148},
    {'clcode':'trv','fullname':'travel/vacation services'    ,'numcode':140},
    {'clcode':'wet','fullname':'writing/editing/translation' ,'numcode':139}]

#insert categories into db
for category in CATEGORIES:
    c = Category(category['fullname'], 
                 category['clcode'],
                 category['numcode'])   
    db_session.add(c)
    db_session.commit()
