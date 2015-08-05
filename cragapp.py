#!./bin/python 
from flask import Flask, render_template, url_for, request

import MySQLdb
import base64
import subprocess
import sys

from database import db_session
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
    vpss = [{'idvpss':1, 'ip':'34.123.26.33', 'port':'3263', 'user':'user', 'password': 'passw12344567'}, {'idvpss':2, 'ip':'34.123.26.34', 'port':'3263', 'user':'user2', 'password': 'sdggergtg'}]
    return render_template('vps-index.html', menu='vps', vpss=vpss)

@app.route('/vps/edit/<int:target_id>')
def vps_edit(target_id):
    vpss = [{'idvpss':1, 'ip':'34.123.26.33', 'port':'3263', 'user':'user', 'password': 'passw12344567'}, {'idvpss':2, 'ip':'34.123.26.34', 'port':'3263', 'user':'user2', 'password': 'sdggergtg'}]
    for vps in vpss:
        if vps.get('idvpss') == target_id:
            target_vps = vps
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
        return "Hello dude"

@app.route('/vps/delete', methods=['POST',])
def vps_delete(vps_id):
        pass

@app.route('/vps/update', methods=['POST',])
def vps_update(vps_id, ip, port, login, password):
        pass


@app.route('/send/<app_id>')
def send(app_id=None):
    if app_id :
        pass

if __name__ == '__main__':
    app.run(debug=True)
