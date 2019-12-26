import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from time import time
import requests
from tornado.options import define, options

from toydiscover.report import ToyDiscoverReporter

define("port", default=80, help="run on the given port", type=int)

class ToyDiscovery:
    def __init__(self):
        self.cache_ex = 60  # todo this and that and those
        self.cache_time = 0
        self.cache = {}

    def get_services(self):
        if (self.cache_time - time()) < (0-self.cache_ex):
            rs = requests.get('http://toydiscover')  # todo this
            self.cache = rs.json()
            self.cache_time = time()
        return self.cache


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        srvs = self.settings['td'].get_services()
        self.write(f"Hello, this is an index!<br>")
        for srv in srvs:
            self.write(f"<a href=\"/{srvs[srv].get('host')}\">{srv}</a>:<i>{srvs[srv].get('desc')}</i><br>")
        self.finish()
        return


def main():
    reporter = ToyDiscoverReporter('toychest', 'Toychest', 'I am a little Teapot, short and 418.')
    reporter.ioloop()
    tornado.options.parse_command_line()
    application = tornado.web.Application([(r"/?.+", MainHandler)], td=ToyDiscovery()) # todo module this up
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
