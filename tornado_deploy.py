from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from cragapp import cragapp

http_server = HTTPServer(WSGIContainer(cragapp))
http_server.listen(5000)
IOLoop.instance().start()
