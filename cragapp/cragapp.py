#!./bin/python27
#root application. database to interface tie here, running crawler and poster is here also

from flask import Flask, render_template, url_for, request, redirect
from werkzeug import secure_filename

import logging
import datetime
import base64
import subprocess
import sys
import os
import sqlalchemy


from database import db_session
from models import VPS, User, Image, Ad, Area, Category


logging.basicConfig(filename='logs/cragapp.log',level=logging.DEBUG)


app = Flask(__name__)

@app.route('/')
def index():

        return render_template('index.html')


@app.route('/vps')
def vps():
        vpss_db = VPS.query.all()
        vpss = [{'idvpss':vps.idvpss,
                 'ip':vps.ip,
                 'port':vps.port,
                 'user':vps.login,
                 'password': vps.password} for vps in vpss_db]
        return render_template('vps-index.html', menu='vps', vpss=vpss)

@app.route('/vps/edit/<int:vps_id>')
def vps_edit(vps_id):
        vps        = VPS.query.filter(VPS.idvpss == vps_id).first()
        target_vps = {'idvpss':vps_id,'ip':vps.ip ,'port':vps.port,'user':vps.login}
        return render_template('vps-edit.html', menu='vps', target_vps=target_vps)

@app.route('/vps/create')
def vps_create():
    return render_template('vps-create.html', menu='vps')

@app.route('/vps/add', methods=['POST',])
def vps_add():
        ip, port, user, password = request.form['ip'], request.form['port'],request.form['user'], request.form['password']
        v = VPS(ip, port, user, password)
        db_session.add(v)
        
        try: db_session.commit()
        except Exception  as e:
                db_session.rollback()
                logging.error("Application did not create "+v.__repr__()+
                              " becouse " + e.message)
                raise Exception
        return "VPS created"


@app.route('/vps/delete/<vps_id>')
def vps_delete(vps_id):
        vps = VPS.query.filter(VPS.idvpss == vps_id).first()
        db_session.delete(vps)
        
        try:
                db_session.commit()
        except Exception as e:
                db_session.rollback()
                logging.error("Application did not delete "+vps.__repr__()+
                              " becouse " + e.message)
                raise Exception('DB commit is not OK')
        return "VPS deleted"

@app.route('/vps/update', methods=['POST',])
def vps_update():
        vps_id    = request.form['idvpss']
        ip        = request.form['ip']
        port      = request.form['port']
        login     = request.form['user']
        password  = request.form['password']

        vps = VPS.query.filter(VPS.idvpss==vps_id).first()

        vps.ip = ip
        vps.port = port
        vps.login= login
        if password: vps.password = password
        db_session.add(vps)
        try:
                db_session.commit()
        except Exception as e:
                logging.error("Application did not update "+vps.__repr__()+
                              " becouse " + e.message)
                db_session.rollback()
                raise Exception('DB commit is not OK')
        return "UPDATED"



@app.route('/users')
def user():
        users_db = User.query.all()
        users = [{'idusers'    :user.idusers,
                  'vps'        :VPS.query.filter(VPS.idvpss==user.idvpss).first().ip,
                  'username'   :user.username,
                  'password'   :user.password} for user in users_db]

        return render_template('user-index.html', menu='user', users=users)

@app.route('/user/create')
def user_create():
        vpss_db = VPS.query.all()
        vpss = [{'idvpss':vps.idvpss, 'ip':vps.ip, 'port':vps.port} for vps in vpss_db]
        return render_template('user-create.html', menu='user', vpss=vpss)

@app.route('/user/add', methods=['POST',])
def user_add():

        idvpss    = request.form['idvpss']
        username  = request.form['username']
        password  = request.form['password']
        mail_pass = request.form['mail_pass']

        u = User(idvpss, username, password, mail_pass)
        db_session.add(u)
        try:db_session.commit()
        except Exception as e:
                db_session.rollback()
                logging.error("Application did not create "+u.__repr__()+
                              " becouse " + e.message)
                raise Exception('DB commit is not OK')
        return "User created"


@app.route('/user/delete/<user_id>')
def user_delete(user_id):
        u = User.query.filter(User.idusers == user_id).first()
        db_session.delete(u)
        try:db_session.commit()
        except Exception as e:
                db_session.rollback()
                logging.error("Application did not delete "+u.__repr__()+
                              " becouse " + e.message)
                raise Exception('DB commit is not OK')
        return "User deleted"

@app.route('/user/edit/<int:user_id>')
def user_edit(user_id):
        user        = User.query.filter(User.idusers == user_id).first()
        target_user = {'idusers':user_id,'username':user.username}
        vps = VPS.query.filter(VPS.idvpss == user.idvpss).first()
        current_vps = {'idvpss':vps.idvpss, 'ip':vps.ip, 'port':vps.port}
        vpss = [{'idvpss':vp.idvpss, 'ip':vp.ip, 'port':vp.port}
                for vp in VPS.query.filter(VPS.idvpss != vps.idvpss).all()]
        return render_template('user-edit.html', menu='vps',
                               target_user=target_user,
                               vpss=vpss,
                               current_vps=current_vps)

@app.route('/user/update', methods=['POST',])
def user_update():
        idusers   = request.form['idusers']
        idvpss    = request.form['idvpss']
        username  = request.form['username']
        password  = request.form['password']
        mail_pass = request.form['mail_pass']
        
        user = User.query.filter(User.idusers==idusers).first()
        user.idvpss = idvpss
        user.username = username
        if password: user.password   = password
        if mail_pass: user.mail_pass = mail_pass
        
        db_session.add(user)
        try:db_session.commit()
        except Exception as e:
                db_session.rollback()
                logging.error("Application did not update "+user.__repr__()+
                              " becouse " + e.message)
                raise Exception('DB commit is not OK')
        return "UPDATED"

@app.route('/ads/')
@app.route('/ads/<params>')
def ads(params="is_duble=0"):

        #if you can write python eval exploit without dots, brackets etc -
        #i want to see it
        params = params.replace('.','')\
                       .replace('(','').replace(')','')\
                        .replace('[','').replace(']','')\
                        .replace('{','').replace('}','')

        #[("idads",1), ("idusers",1) ...]
        params = [tuple(param.split('=')) for param in
                           params.split('&')]

                
        sqlalchemy_expr = 'Ad.query.filter('+', '.join(
                ['Ad.'+param[0]+'=="'+param[1]+'"'
                 for param in params])+').all()'

        logging.debug('sqlalchemy filter expression is "'\
                      + sqlalchemy_expr + '"')
                
        ads_db = eval(sqlalchemy_expr)
        
        ads = [{'idads'           : ad.idads,
                'title'           : ad.title,
                'posting_time'    : ad.posting_time,
                'scheduled_action': ad.scheduled_action,
                'status'          : ad.status,
                'user'            : User.query.\
                filter(User.idusers == ad.idusers).first().username,
                'category'        : Category.query.\
                filter(Category.idcategory ==ad.idcategory).first().fullname,
                'allowed_actions' : ad.allowed_actions}
               for ad in ads_db]

        
        #get selected user from parameters and set it selected in response
        users = [{'idusers':user.idusers,'username':user.username, 'selected':''}
                 for user in User.query.all()]

        if 'idusers' in [p[0] for p in params]:
                #p[1] where p[0] == idusers                
                param_idusers = filter(lambda p: p[0] == "idusers", params)[0][1]

                cur_user = filter(lambda u: str(u['idusers']) == param_idusers
                                  ,users)[0]
                cur_user['selected'] = 'selected'
                users = [cur_user]\
                        + [{'idusers':'all', 'username':'all', 'selected':''}]\
                        + filter(lambda u: str(u['idusers']) != param_idusers
                                 ,users)
                
        else:
                users = [{'idusers':'all'
                          ,'username':'all'
                          ,'selected':'selected'}] \
                        + users
                
        #the same for category
        categories = [{'idcategory':cat.idcategory,
                       'fullname':cat.fullname,
                       'selected':''}
                       for cat in Category.query.all()]
        
        if 'idcategory' in [p[0] for p in params]:
                #p[1] where p[0] == idcategory
                param_idcategory = filter(lambda p: p[0] == "idcategory",
                                          params)[0][1]
                
                cur_category = \
                        filter(lambda c: str(c['idcategory']) == param_idcategory,
                               categories)[0]
                cur_category['selected'] = 'selected'

                categories =  [{'idcategory':'all',
                                'fullname':'all',
                                'selected':''}]\
                              +  [cur_category]\
                              + filter(lambda c: str(c['idcategory']) !=
                                       param_idcategory,
                                       categories)
        else:
                categories = [{'idcategory':'all',
                               'fullname':'all',
                               'selected':'selected'}]\
                             + categories

        statuses = [{'status':s[0],'selected':''}
                    for s in db_session.query(Ad.status).distinct().all()]

        if 'status' in [p[0] for p in params]:
                #p[1] where p[0] == status
                cur_status = filter(lambda p: p[0] == "status",
                                    params)[0][1] #p[1]
                statuses = [{'status':'all', 'selected':''}]\
                           + [{'status':cur_status,'selected':'selected'}]\
                           + filter(lambda s: s['status'] != cur_status, statuses)
        else: statuses = [{'status':'all', 'selected':'selected'}] + statuses

        scheduling = [{'value': 'all',
                       'selected':''},
                      {'value': 'add',
                       'selected':''},
                      {'value': 'delete',
                       'selected':''},
                      {'value': 'undelete',
                       'selected':''},
                      {'value':'renew',
                       'selected':''},
                      {'value':'repost',
                       'selected':''}]
        
        if 'scheduled_action' in [p[0] for p in params]:
                #p[1] where p[0] == status
                cur_scheduling = filter(lambda p: p[0] == "scheduled_action",
                                    params)[0][1] #p[1], value
                for sch in scheduling:
                        if sch['value'] == cur_scheduling:
                                sch['selected'] = 'selected'
                        
        
        return render_template('ad-index.html', menu='ad', ads=ads
                               ,users=users
                               ,categories=categories
                               ,statuses=statuses
                               ,scheduling=scheduling)

@app.route('/ad/create')
def ad_create():
        user_db = User.query.all()

        users = [{'idusers':user.idusers,'username':user.username} for user in user_db]
        categories = [{"category":cat.idcategory,
                       "cat_name":cat.fullname}for cat in Category.query.all()]

        #areas  = Area.auery.all()


        areas = [{'idarea'     : area.idarea,
                  'area_fname' : area.fullname} for area in Area.query.all() ]

        return render_template('ad-create.html', menu='ad', users=users,
                               categories=categories, areas=areas)

@app.route('/ad/add', methods=['POST',])
def ad_add():

        idcrag            = request.form['idcrag']
        description       = request.form['description']
        title             = request.form['title']
        posting_time      = request.form['posting_time']
        scheduled_action  = request.form['scheduled_action']
        repost_timeout    = request.form['repost_timeout']
        prev_action       = ""
        prev_act_time     = ""
        prev_act_stat     = ""
        status            = "Not posted"
        idusers           = request.form['idusers']
        idcategory        = request.form['category']
        idarea            = request.form['area']
        replymail         = None #request.form['replymail']
        allowed_actions   = "None,add"
        contact_phone     = request.form['contact_phone']
        contact_name      = request.form['contact_name']
        postal            = request.form['postal']
        specific_location = request.form['specific_location']
        haslicense        = request.form['has_license']
        license_info      = request.form['license']

        a = Ad(idcrag,
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
               license_info)

        db_session.add(a)
        
        try:db_session.commit()
        except Exception as e:
                db_session.rollback()
                logging.error("Application did not create "+a.__repr__()+
                              " becouse " + e.message)
                raise Exception('DB commit is not OK')

        return a.idads.__str__()

@app.route('/ad/delete/<ad_id>')
def ad_delete(ad_id):
        a = Ad.query.filter(Ad.idads == ad_id).first()
        db_session.delete(a)
        try:db_session.commit()
        except Exception as e:
                db_session.rollback()
                logging.error("Application did not delete "+a.__repr__()+
                              " becouse " + e.message)
                raise Exception('DB commit is not OK')
        return "Ad deleted"

@app.route('/ad/edit/<int:ad_id>')
def ad_edit(ad_id):
        ad        = Ad.query.filter(Ad.idads == ad_id).first()

        target_ad = {'idads'             : ad_id,
                     'idcrag'            : ad.idcrag,
                     'description'       : ad.description,
                     'title'             : ad.title,
                     'posting_time'      : ad.posting_time,
                     'repost_timeout'    : ad.repost_timeout,
                     'status'            : ad.status,
                     'idusers'           : ad.idusers,
                     'category'          : ad.idcategory,
                     'area'              : ad.idarea,
                     'replymail'         : ad.replymail,
                     'contact_phone'     : ad.contact_phone,
                     'contact_name'      : ad.contact_name,
                     'postal'            : ad.postal,
                     'specific_location' : ad.specific_location,
                     'license_info'      : ad.license_info
        }

        user = User.query.filter(User.idusers == ad.idusers).first()
        current_user = {'idusers':user.idusers, 'username':user.username}
        users = [{'idusers':us.idusers, 'username':us.username}
                 for us in User.query.filter(User.idusers != user.idusers).all()]

        category = Category.query.filter(Category.idcategory == ad.idcategory).first()
        current_category = {'category':ad.idcategory, 'cat_name':category.fullname}
        categories      = [{'category':cat.idcategory, 'cat_name':cat.fullname}
                           for cat in Category.query.\
                           filter(Category.idcategory
                                  != category.idcategory).all()]

        area = Area.query.filter(Area.idarea == ad.idarea).first()

        current_area = {'area':ad.idarea,
                        'area_name': area.fullname}

        areas        = [{'area':ar.idarea, 'area_name':ar.fullname}
                         for ar in Area.query.filter(Area.idarea != ad.idarea).all()]

        images = [{'idimages':image.idimages,
                   'image':base64.b64encode(image.image),
                   'extension':image.extension}
                  for image in Image.query.filter(Image.idads == ad.idads).all()]

        scheduled_action = {'action':ad.scheduled_action,
                            'name': ad.scheduled_action.capitalize()}

        allowed_actions = [{'action':action, 'name': action.capitalize()}
                           for action in
                           filter(lambda ac: ac !=scheduled_action['action'],
                                  ad.allowed_actions.split(','))] 

        if ad.haslicense =='1':
                has   = 'selected'
                hasno = ''
        else:
                has   = ''
                hasno = 'selected'

        
        return render_template('ad-edit.html', menu='ad',
                               target_ad=target_ad,
                               users=users,
                               current_user=current_user,
                               images=images,
                               current_category=current_category,
                               categories=categories,
                               current_area=current_area,
                               areas=areas,
                               has=has,
                               hasno=hasno,
                               scheduled_action=scheduled_action,
                               allowed_actions=allowed_actions)

@app.route('/ad/update', methods=['POST'])
def ad_update():
        idads         = request.form['idads']
        idcrag        = request.form['idcrag']
        description   = request.form['description']
        title         = request.form['title']
        posting_time  = request.form['posting_time']
        scheduled_action = request.form['scheduled_action']
        repost_timeout   = request.form['repost_timeout']
        status        = request.form['status']
        idusers       = request.form['idusers']
        idcategory    = request.form['category']
        idarea        = request.form['area']
        replymail     = None#request.form['replymail']
        contact_phone = request.form['contact_phone']
        contact_name  = request.form['contact_name']
        postal        = request.form['postal']
        specific_location = request.form['specific_location']
        haslicense        = request.form['has_license']
        license_info      = request.form['license']

        ad = Ad.query.filter(Ad.idads==idads).first()

        ad.description = description
        ad.idcrag      = idcrag
        ad.title       = title
        ad.posting_time= posting_time
        ad.scheduled_action = scheduled_action
        ad.repost_timeout   = repost_timeout
        ad.status      = status
        ad.idusers     = idusers
        ad.idcategory  = idcategory
        ad.idarea      = idarea
        ad.replymail   = replymail
        ad.contact_phone = contact_phone
        ad.contact_name  = contact_name
        ad.postal        = postal
        ad.specific_location = specific_location
        ad.haslicense        = haslicense
        ad.license_info      = license_info


        db_session.add(ad)
        try:db_session.commit()
        except Exception as e:
                logging.error("Application did not update "+ad.__repr__()+
                              " becouse " + e.message)
                db_session.rollback()
                raise Exception('DB commit is not OK')
        return "UPDATED"



ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
        return '.' in filename and \
                filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload_images', methods=['POST','GET'])
def upload_images():

        if request.method == 'POST':
                idads        = request.form['idads']
                images       = request.files.getlist('images[]')

                for image in images:
                        if image and allowed_file(image.filename):
                                extension = image.filename.split('.')[-1]
                                if extension == "jpg": mime = "image/jpeg"
                                else: mime = "image/"+extension
                                i = Image(idads=idads,
                                          extension=extension,
                                          mime=mime,
                                          filename=image.filename,
                                          image=image.read())
                                db_session.add(i)
                                try:
                                        db_session.commit()
                                
                                except:
                                        db_session.rollback()
                                        raise Exception('DB commit is not OK')

        return "Images uploaded?"

@app.route('/delete_image/<idimages>')
def delete_image(idimages):
        i = Image.query.filter(Image.idimages == idimages).first()
        db_session.delete(i)
        
        try:
                db_session.commit()
        except:
                db_session.rollback()
                raise Exception("DB commit is not OK")
        return "Image deleted"


@app.route('/scrap_ads/<idusers>', methods=['POST', 'GET'])
def scrap_ads(idusers):
        u = User.query.filter(User.idusers == idusers).first()
        v = VPS.query.filter(VPS.idvpss == u.idvpss).first()
        proxy = 'https://' + ':'.join([str(v.ip), str(v.port)])
        my_env = os.environ.copy()
        my_env["https_proxy"] = proxy
        subprocess.call(["python",
                         "cragapp/syncronizer.py",
                         "userscrap",
                         "--idusers",
                         idusers], env=my_env)

        return "Ad scraped"

app.route('/scrap_ad/<idads>', methods=['POST', 'GET'])
def scrap_ad(idads):
        a = Ad.query.filter(Ad.idads == idads).first()
        u = User.query.filter(User.idusers == a.idusers).first()
        v = VPS.query.filter(VPS.idvpss == u.idvpss).first()
        proxy = 'https://' + ':'.join([str(v.ip), str(v.port)])
        my_env = os.environ.copy()
        my_env["https_proxy"] = proxy

        subprocess.call(["python",
                         "cragapp/syncronizer.py",
                         "adscrap",
                         "--idads",
                         idads], env=my_env)

        return "Ad scraped"

@app.route('/manage/<action>/<idads>')
def manage_ad(action, idads):
        a = Ad.query.filter(Ad.idads == idads).first()
        u = User.query.filter(User.idusers == a.idusers).first()
        v = VPS.query.filter(VPS.idvpss == u.idvpss).first()
        proxy = 'https://' + ':'.join([str(v.ip), str(v.port)])
        my_env = os.environ.copy()
        my_env["https_proxy"] = proxy
        subprocess.call(["python",
                         "cragapp/admanager.py",
                         "--idads",
                         idads,
                         "--action",
                         action],env=my_env)
        return "Success"

@app.route('/time')
def show_time():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    app.run(debug=True)
