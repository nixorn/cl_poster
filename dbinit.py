#!./bin/python 

from cragapp.database import init_db

init_db()


from cragapp.models import Area
from cragapp.database import engine, db_session

AREAS = [{"urlname":"longisland", "fullname":"Long Island", "clcode":"isp"},
         {"urlname":"newyork"   , "fullname":"New York"   , "clcode":"nyc"},
         {"urlname":"moscow"    , "fullname":"Moscow"     , "clcode":"mos"}]


#insert areas into db, because it need in admanager
for area in AREAS:
    a = Area(area['urlname'], area['fullname'], area['clcode'])
    db_session.add(a)
    db_session.commit()
