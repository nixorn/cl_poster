#!./bin/python27
#root application. database to interface tie here, running crawler and poster is here also

from flask import Flask, render_template, url_for, request, redirect
from werkzeug import secure_filename


import base64
import subprocess
import sys
import sqlalchemy


from database import db_session
from models import VPS, User, Image, Ad, Area, Category


#run loop
p = subprocess.Popen([sys.executable, './cragloop.py'],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)



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
        db_session.commit()
        return "VPS created"


@app.route('/vps/delete/<vps_id>')
def vps_delete(vps_id):
        vps = VPS.query.filter(VPS.idvpss == vps_id).first()
        db_session.delete(vps)
        db_session.commit()
        return "VPS deleted"

@app.route('/vps/update', methods=['POST',])
def vps_update():
        vps_id, ip, port, login, password = request.form['idvpss'], request.form['ip'], request.form['port'],request.form['user'], request.form['password']
        vps = VPS.query.filter(VPS.idvpss==vps_id).first()

        vps.ip = ip
        vps.port = port
        vps.login= login
        if password: vps.password = password
        db_session.add(vps)
        db_session.commit()
        return "UPDATED"



@app.route('/users')
def user():
        users_db = User.query.all()
        users = [{'idusers'    :user.idusers,
                  'idvpss'     :user.idvpss,
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


        u = User(idvpss, username, password)
        db_session.add(u)
        db_session.commit()
        return "User created"


@app.route('/user/delete/<user_id>')
def user_delete(user_id):
        u = User.query.filter(User.idusers == user_id).first()
        db_session.delete(u)
        db_session.commit()
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

        user = User.query.filter(User.idusers==idusers).first()
        user.idvpss = idvpss
        user.username = username
        if password: user.password = password

        db_session.add(user)
        db_session.commit()
        return "UPDATED"

@app.route('/ads')
def ads():

        #areas  = Area.auery.all()

        ads_db = Ad.query.all()
        ads = [{'idads'       : ad.idads,
                'description' : ad.description,
                'title'       : ad.title,
                'posting_time': ad.posting_time,
                'status'      : ad.status,
                'idusers'     : ad.idusers,
                'category'    : ad.idcategory,
                'allowed_actions': ad.allowed_actions,
                #'area_fname' : filter(lambda ar: ad.idarea==ar.idarea, areas).fullname,
                #'idarea'     : ad.idarea,
                'replymail'   : ad.replymail} for ad in ads_db]
        return render_template('ad-index.html', menu='ad', ads=ads)



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
        idusers           = request.form['idusers']
        idcategory        = request.form['category']
        idarea            = request.form['area']
        replymail         = request.form['replymail']
        allowed_actions   = "add"
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
               "Not posted",
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
        db_session.commit()

        return a.idads.__str__()

@app.route('/ad/delete/<ad_id>')
def ad_delete(ad_id):
        a = Ad.query.filter(Ad.idads == ad_id).first()
        db_session.delete(a)
        db_session.commit()
        return "Ad deleted"

@app.route('/ad/edit/<int:ad_id>')
def ad_edit(ad_id):
        ad        = Ad.query.filter(Ad.idads == ad_id).first()

        target_ad = {'idads'             : ad_id,
                     'idcrag'            : ad.idcrag,
                     'description'       : ad.description,
                     'title'             : ad.title,
                     'posting_time'      : ad.posting_time,
                     'status'            : ad.status,
                     'idusers'           : ad.idusers,
                     'category'          : ad.idcategory,
                     'area'              : ad.idarea,
                     'replymail'         : ad.replymail,
                     'contact_phone'     : ad.contact_phone,
                     'contact_name'      : ad.contact_name,
                     'postal'            : ad.postal,
                     'specific_location' : ad.specific_location}

        user = User.query.filter(User.idusers == ad.idusers).first()
        current_user = {'idusers':user.idusers, 'username':user.username}
        users = [{'idusers':us.idusers, 'username':us.username}
                 for us in User.query.filter(User.idusers != user.idusers).all()]

        category = Category.query.filter(Category.idcategory == ad.idcategory).first()
        current_category = {'category':ad.idcategory, 'cat_name':category.fullname}
        categories      = [{'category':cat.idcategory, 'cat_name':cat.fullname}
                           for cat in Category.query.filter(Category.idcategory
                                                            != category.idcategory).all()]

        area = Area.query.filter(Area.idarea == ad.idarea).first()

        current_area = {'area':ad.idarea,
                        'area_name': area.fullname}

        areas        = [{'area':ar.idarea, 'area_name':ar.fullname}
                         for ar in Area.query.filter(Area.idarea != ad.idarea).all()]

        images = [{'idimages':image.idimages,
                   'image':base64.b64encode(image.image),
                   'extension':image.extension}
                  for image in Image.query.all()]

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
                               hasno=hasno)

@app.route('/ad/update', methods=['POST'])
def ad_update():
        idads         = request.form['idads']
        idcrag        = request.form['idcrag']
        description   = request.form['description']
        title         = request.form['title']
        posting_time  = request.form['posting_time']
        status        = request.form['status']
        idusers       = request.form['idusers']
        idcategory    = request.form['category']
        idarea        = request.form['area']
        replymail     = request.form['replymail']
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
        db_session.commit()
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
                                db_session.commit()

        return "Images uploaded?"

@app.route('/delete_image/<idimages>')
def delete_image(idimages):
        i = Image.query.filter(Image.idimages == idimages).first()
        db_session.delete(i)
        db_session.commit()
        return "Image deleted"




@app.route('/scrap_ads/<idusers>', methods=['POST', 'GET'])
def scrap_ads(idusers):
        #pure python27 cragapp.py

        #subprocess.call(["python", "syncronizer.py", "--idads", idads])
        # on tornado
        subprocess.call(["python", "cragapp/syncronizer.py", "userscrap","--idusers", idusers])

        return "Ad scraped"

app.route('/scrap_ad/<idads>', methods=['POST', 'GET'])
def scrap_ads(idusers):
        #pure python27 cragapp.py

        #subprocess.call(["python", "syncronizer.py", "--idads", idads])
        # on tornado

        subprocess.call(["python", "cragapp/syncronizer.py", "adscrap","--idads", idads])

        return "Ad scraped"

@app.route('/manage/<action>/<idads>')
def manage_ad(action, idads):
        subprocess.call(["python", "cragapp/admanager.py", "--idads", idads, "--action", action])
        return "Success"


if __name__ == '__main__':
    app.run(debug=True)
