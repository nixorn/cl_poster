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

    config = tempfile.NamedTemporaryFile()
    config.write (
        json.dumps(
            {'service':service,
             'category':category,
             'username':username,
             'passwoed':password,
             'contact_phone':contact_phone,
             'title':title,
             'specific_location':specific_location,
             'postal':postal,
             'body':body,
             'haslicense':haslicense,
             'license_info':license_info}))
    config.flush()

    out = subprocess.check_output(['./phantomjs', './add_ad.js', config.name])
    

def delete()  : pass
def repost()  : pass
def undelete(): pass
def renew()   : pass
def edit()    : pass
def confirm() : pass
    
#
parser = argparse.ArgumentParser(description='Crawl from craiglist ad and store it into database.')
parser.add_argument('--idads',
                    help='id from internal database')

parser.add_argument('--action', required=True,
                    help='renew|delete|repost|add|undelete|edit|confirm|None')

parser.add_argument('--confirm_link',
                    help='Link for mail confirmation. Optional argument,'+\
                    'needed for confirmation only.')

parser.add_argument('--username',
                    help='user for login. needed if operation is confirm')

args = parser.parse_args()



my_env = os.environ.copy()

print 'enviropment', my_env

if args.idads:
    ad       = Ad.query.filter(Ad.idads == args.idads).first()
    images   = Image.query.filter(Image.idads == ad.idads).all()
    user     = User.query.filter(User.idusers == ad.idusers).first()
    vps      = VPS.query.filter(VPS.idvpss == user.idvpss).first()
    area     = Area.query.filter(Area.idarea == ad.idarea).first()
    category = Category.query.\
        filter(Category.idcategory == ad.idcategory).first()

if args.username:
    user = User.query.filter(User.username == args.username).first()

if args.action == "add":
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
        haslicense=ad.haslicense,
        license_info=ad.license_info,
        proxy='@'.join(':'.join([VPS.login, VPS.password]), ':'.join([VPS.ip,VPS.port]))
        images=images)
    
elif args.action == "delete"   : delete()
elif args.action == "repost"   : repost()
elif args.action == "undelete" : undelete()
elif args.action == "renew"    : renew()
elif args.action == "edit"     : edit()
elif args.action == "confirm"  : confirm()
elif args.action == "None"     : pass
    



