import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from time import time
import requests

from tornado.options import define, options

define("port", default=80, help="run on the given port", type=int)

class ToyDiscoveryHandler:
    def __init__(self):
        self.cache_ex = 18700 # todo this and that and those
        self.cache_time = 0
        self.cache = {}

    def get_services(self):
        if (self.cache_time - time()) < (0-self.cache_ex):
            rs = requests.get('http://toydiscover')
            self.cache = rs.json()
        return self.cache

    def report(self):
        requests.post('http://toydiscover', json={'ver': 1, 'payload': {'name': 'cooldude', 'description': 'WEEE'}})

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.settings['td'].report()  # testing

        srvs = self.settings['td'].get_services()
        self.write(f"Hello, this is an index!<br>")
        for srv in srvs:
            self.write(f"{srv}:<i>{srvs[srv]}</i><br>")
        self.finish()
        return


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([(r"/?.+", MainHandler)], td=ToyDiscoveryHandler())
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
