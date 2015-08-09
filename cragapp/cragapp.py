#!./bin/python 
from flask import Flask, render_template, url_for, request, redirect
from werkzeug import secure_filename

import base64
import subprocess
import sys
import sqlalchemy


from database import db_session, engine, md
from models import VPS, User, Image, Ad


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
        print "THAT IS YOUR ID", request.form['idvpss'],request.form['ip'], request.form['\
port'],request.form['user']
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
                  'password'   :user.password,
                  'accountID'  :user.accountID} for user in users_db]
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
        accountID = request.form['accountID']
        
        u = User(idvpss, username, password, accountID)
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
        target_user = {'idusers':user_id,'username':user.username ,'accountID':user.accountID}
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
        accountID = request.form['accountID']
        
        user = User.query.filter(User.idusers==idusers).first()
        user.idvpss = idvpss   
        user.username = username         
        user.accountID = accountID
        if password: user.password = password
        
        db_session.add(user)
        db_session.commit()
        return "UPDATED"

@app.route('/ads')
def ads():
        ads_db = Ad.query.all()
        ads = [{'idads'        :ad.idads,
                'description' :ad.description,
                'title'       :ad.title,
                'posting_time':ad.posting_time,
                'status'      :ad.status,
                'idusers'     :ad.idusers,
                'category'    :ad.category,   
                'area'        :ad.area,
                'replymail'   :ad.replymail    } for ad in ads_db]
        return render_template('ad-index.html', menu='ad', ads=ads)



@app.route('/ad/create')
def ad_create():
        user_db = User.query.all()
        for i in user_db: print dir(i)
        users = [{'idusers':user.idusers,'username':user.username} for user in user_db]
        
        return render_template('ad-create.html', menu='ad', users=users)

@app.route('/ad/add', methods=['POST',])
def ad_add():
        description   = request.form['description']
        title         = request.form['title']
        posting_time  = request.form['posting_time']

        idusers       = request.form['idusers']
        category      = request.form['category']
        area          = request.form['area']
        replymail     = request.form['replymail']
        
        a = Ad(description,title,posting_time,"not_posted",idusers,category,area,replymail)
        db_session.add(a)
        db_session.commit()
        return "Ad created"

@app.route('/ad/delete/<ad_id>')
def ad_delete(ad_id):
        a = Ad.query.filter(Ad.idads == ad_id).first()
        db_session.delete(a)
        db_session.commit()
        return "Ad deleted"

@app.route('/ad/edit/<int:ad_id>')
def ad_edit(ad_id):
        ad        = Ad.query.filter(Ad.idads == ad_id).first()
        
        target_ad = {'idads'         : ad_id,
                     'description'   : ad.description,
                     'title'         : ad.title,
                     'posting_time'  : ad.posting_time,
                     'status'        : ad.status,
                     'idusers'       : ad.idusers,
                     'category'      : ad.category,
                     'area'          : ad.area,
                     'replymail'     : ad.replymail}
        
        user = User.query.filter(User.idusers == ad.idusers).first()
        current_user = {'idusers':user.idusers, 'username':user.username}
        users = [{'idusers':us.idusers, 'username':us.username}
                for us in User.query.filter(User.idusers != user.idusers).all()]

        images = [{'idimages':image.idimages, 'image':base64.b64encode(image.image), 'extension':image.extension}
                  for image in Image.query.all()]
        return render_template('ad-edit.html', menu='ad',
                               target_ad=target_ad,
                               users=users,
                               current_user=current_user,
                               images=images)

@app.route('/ad/update', methods=['POST'])
def ad_update():

        idads        = request.form['idads']
        description  = request.form['description']
        title        = request.form['title']
        posting_time = request.form['posting_time']
        status       = request.form['status']
        idusers      = request.form['idusers']
        category     = request.form['category']
        area         = request.form['area']
        replymail    = request.form['replymail']

        print "FORUPDATE",idads,description,title,posting_time,status,idusers,category,area,replymail


        ad = Ad.query.filter(Ad.idads==idads).first()


        ad.description = description
        ad.title       = title
        ad.posting_time= posting_time
        ad.status      = status
        ad.idusers     = idusers
        ad.category    = category
        ad.area        = area
        ad.replymail   = replymail
        
        
        db_session.add(ad)
        db_session.commit()
        return "UPDATED"


#base64 image for RSS 
#with open("test_img.jpg", "rb") as image_file:
#        encoded_image = base64.b64encode(image_file.read())
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
                                i = Image(idads=idads,
                                          extension=extension,
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



if __name__ == '__main__':
    app.run(debug=True)
