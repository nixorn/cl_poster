from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import subprocess
import sys

from cragapp.cragapp import app



#run cragloop
p = subprocess.Popen(['python', './cragapp/cragloop.py'],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT
#run mailloop
p = subprocess.Popen(['python', './cragapp/mailloop.py'],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5000)
IOLoop.instance().start()
