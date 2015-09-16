import datetime
import logging
from models import Ad, Image, User, VPS, Category, Area
from database import db_session

def save_thing(thing):
    '''just commit something into db'''
    db_session.add(thing)
    try:
        db_session.commit()
    except:
        db_session.rollback()

def calc_posting_time(ad):
    #cases when not need to change something
    if ad.repost_timeout == '' or ad.posting_time == '': return ad.posting_time
    elif datetime.datetime.strptime(ad.posting_time, "%Y-%m-%d %H:%M")\
         > datetime.datetime.now():
        return ad.posting_time
    elif not ad.repost_timeout.isdigit(): return ad.posting_time

    timeout = int(ad.repost_timeout)*60*60#seconds
    posting_time = datetime.datetime.strptime(ad.posting_time, "%Y-%m-%d %H:%M")
    
    while posting_time < datetime.datetime.now():
        posting_time = posting_time\
            + datetime.timedelta(seconds = timeout)
    return posting_time.strftime("%Y-%m-%d %H:%M")
    

def add_sync_handle():
    '''ads with clid usualy scrapped, and if having duble titles in
    ads without clid(created) - need to hide scrapped,
    and transfer data from scraped to created'''
    print "clean_up started"
    #get not duble ads
    now = datetime.datetime.now()
    print "now is", now, "\n\n"
    ads = Ad.query.filter(Ad.is_duble == "0").all()
    print "ads", ads, "\n\n"
    
    ads_with_clid    = filter(lambda x: x.idcrag != '', ads)
    print "ads_with_clid", ads_with_clid, "\n\n"
    #app was add the ad,
    #but dont know aboubt that
    ads_for_update = filter(
        lambda x: x.idcrag == ''
        and x.status == "Not posted"
        and datetime.datetime.\
            strptime(x.posting_time,"%Y-%m-%d %H:%M") < now,
        ads)
    print "ads_for_update", ads_for_update
    titles_for_update = [x.title for x in ads_for_update]

    for duble in ads_with_clid[:]:
        if duble.title in titles_for_update:
            print "duble", duble, "\n"
            #ads with clid wich have same titles having ads without clid-
            #is dubles
            duble.is_duble = "1"
            save_thing(duble)

    #update every not duble ad (created) 
    #from duble ad with same name and max id(scraped)

    
    for ad in ads_for_update[:]:
        dubles = filter(                                       
            lambda x: x.title == ad.title #and x.idusers == ad.idusers,
            ,ads_with_clid)
        print dubles, type(dubles)
        
        try:
            if type(dubles) == type([]) and len(dubles) > 0:
                dubles.sort(key=lambda x: x.idads)
                duble_from_cl = dubles[-1]
                print ad.title, ad.idusers     
                ad.idcrag = duble_from_cl.idcrag
                ad.allowed_actions = duble_from_cl.allowed_actions
                ad.status = duble_from_cl.status
                
                if 'repost' in ad.allowed_actions and ad.repost_timeout:
                    ad.scheduled_action = 'repost'
                elif 'renew' in ad.allowed_actions and ad.repost_timeout:
                    ad.scheduled_action = 'renew'
                else:
                    ad.scheduled_action = ''
                    
                print "POSTING_TIME", ad.posting_time
                ad.posting_time = calc_posting_time(ad)
            save_thing(ad)
                
        except Exception as e:
            print 'EXCEPTION!',e.message
    #debug info
    return {"for_update": ads_for_update,
            "now": now,
            "with_clids": ads_with_clid,
            "ads": ads}

def duple_handle():        
    add_sync_handle()
    
if __name__ == "__main__":
    duple_handle()
