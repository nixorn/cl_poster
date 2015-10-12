
#TODO: phantomjs proxy support
import os
import itertools
import operator
import argparse
import time
import subprocess
import logging
import tempfile
import json
from models import Ad, User, VPS, Area, Image, Category

logging.basicConfig(filename='logs/admanager.log',level=logging.DEBUG)

# definitions
def add(area, service, category,
        username, password, contact_phone, title, specific_location,
        postal, body, haslicense,license_info, proxy, images):

    json_config_dump = json.dumps(
            {'area':area,
             'service':service,
             'category':category,
             'username':username,
             'password':password,
             'contact_phone':contact_phone,
             'title':title,
             'specific_location':specific_location,
             'postal':postal,
             'body':body,
             'haslicense':haslicense,
             'license_info':license_info})
    
    config = tempfile.NamedTemporaryFile(suffix='.json')
    
    config.write (json_config_dump)
    config.flush()
    
    with open('logs/last_config.json', 'w') as f:
        f.write(json_config_dump)
        f.flush()

    env = os.environ.copy()
    env["http_proxy"] = proxy
    env['https_proxy'] = proxy.replace('http', 'https')

    try:
        out = subprocess.check_output(['./phantomjs', './cragapp/add_ad.js', config.name], env=env)
        print out
        logging.debug(out)
    except Exception as e:
        print e
        print e.message
        logging.error(e)
        #print e.output

def confirm(confirm_url,proxy) :
    env = os.environ.copy()
    env["http_proxy"] = proxy
    env['https_proxy'] = proxy.replace('http', 'https')
    try:
        out = subprocess.check_output(['./phantomjs',
            './cragapp/confirm.js',
            confirm_url], env=env)
        print out
        logging.debug(out)
        
    except Exception as e:
        print e
        print e.message
        logging.error(e)

        
def delete()  : pass
def repost()  : pass
def undelete(): pass
def renew()   : pass
def edit()    : pass

    
#
parser = argparse.ArgumentParser(description='Crawl from craiglist ad and store it into database.')
parser.add_argument('--idads',
                    help='id from internal database')

parser.add_argument('--action', required=True,
                    help='renew|delete|repost|add|undelete|edit|confirm|None')

parser.add_argument('--confirm_url',
                    help='Link for mail confirmation. Optional argument,'+\
                    'needed for confirmation only.')

parser.add_argument('--username',
                    help='user for login. needed if operation is confirm')

args = parser.parse_args()



my_env = os.environ.copy()



if args.idads:
    ad       = Ad.query.filter(Ad.idads == args.idads).first()
    images   = Image.query.filter(Image.idads == ad.idads).all()
    user     = User.query.filter(User.idusers == ad.idusers).first()
    vps      = VPS.query.filter(VPS.idvpss == user.idvpss).first()
    proxy='http://'+'@'.join([':'.join([vps.login, vps.password]), ':'.join([vps.ip, vps.port])])
    area     = Area.query.filter(Area.idarea == ad.idarea).first()
    category = Category.query.\
        filter(Category.idcategory == ad.idcategory).first()

if args.username:
    user = User.query.filter(User.username == args.username).first()
    vps      = VPS.query.filter(VPS.idvpss == user.idvpss).first()
    proxy='http://'+'@'.join([':'.join([vps.login, vps.password]), ':'.join([vps.ip, vps.port])])

if args.action == 'add':
    if ad.haslicense == '1':
        haslicense='yes'
        license_info = ad.license_info
    else:
        haslicense='no'
        license_info = ''
        
    add(area=area.clcode,
        service="so", #sevice offered
        category=category.numcode,
        username=user.username,
        password=user.password,
        contact_phone=ad.contact_phone,
        title=ad.title,
        specific_location=ad.specific_location,
        postal=ad.postal,
        body=ad.description,
        haslicense=haslicense,
        license_info=license_info,
        proxy=proxy,
        images=images)

elif args.action == "confirm"  :
    confirm(args.confirm_url, proxy)

elif args.action == "repost"   :
    repost()

elif args.action == "renew"    : renew()
elif args.action == "delete"   : delete()
elif args.action == "undelete" : undelete()
elif args.action == "edit"     : edit()
elif args.action == "None"     : pass
    



