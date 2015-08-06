#!./bin/python 
from flask import Flask, render_template, url_for, request, redirect

import MySQLdb
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


#base64 image for RSS 
#with open("test_img.jpg", "rb") as image_file:
#        encoded_image = base64.b64encode(image_file.read())


                            


    

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


@app.route('/send/<app_id>')
def send(app_id=None):
    if app_id :
        pass

if __name__ == '__main__':
    app.run(debug=True)
