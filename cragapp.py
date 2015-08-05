#!./bin/python 
from flask import Flask, render_template, url_for

import MySQLdb
import base64
import subprocess
import sys


#run loop
p = subprocess.Popen([sys.executable, './cragloop.py'],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)


#base64 image for RSS 
#with open("test_img.jpg", "rb") as image_file:
#        encoded_image = base64.b64encode(image_file.read())

db = MySQLdb.connect(host="localhost", user="root", passwd="passwd", db="cragapp", charset='utf8')
db.autocommit(True)

                            


    

app = Flask(__name__)

@app.route('/')
def index():

        return render_template('index.html')

@app.route('/adlist')
def adlist():
    return 'Hello World!'

@app.route('/show_ad')
def show_ad(ad_num):
    pass

@app.route('/userlist')
def userlist():
    pass

@app.route('/vps', methods=['GET',])
def vps():
        pass


@app.route('/vps/add', methods=['POST',])
def vps_add(ip, port, login, password):
        pass

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
    app.run()
