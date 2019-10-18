import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from redis import Redis, RedisError
import json

from tornado.options import define, options

define("port", default=80, help="run on the given port", type=int)

rd = Redis('redis', 6379, 0, None, decode_responses=True, encoding='utf-8')  # todo param up?

class DiscoverHandler(tornado.web.RequestHandler):

    def bad_response(self, message):
        self.set_status(500)
        self.write(json.dumps({'success': False, 'message': message}))
        self.finish()
        return

    def post(self):
        try:
            inb = json.loads(self.request.body)
        except json.JSONDecodeError:
            return self.bad_response('Failed to parse inbound message')

        if inb.get('ver') != 1:
            return self.bad_response('version mismatch')  # todo module this up so versioning makes sense

        inb = inb.get('payload')
        if inb is None:
            return self.bad_response('Malformed inbound message')

        name = inb.get('name')
        desc = inb.get('description')

        st = self.settings['db']
        try:
            st.set(name, desc, ex=17800)  # todo expiry, dynamic names
        except RedisError:
            return self.bad_response('Database down')

        self.write(json.dumps({'success': True, 'message': 'registered'}))
        self.set_status(200)
        self.finish()
        return

    def get(self):
        st = self.settings['db']
        try:
            ks = st.keys('*')
            ret = {k:rd.get(k) for k in ks}
        except RedisError:
            return self.bad_response('Database down')

        self.set_status(200)
        self.write(json.dumps(ret))
        self.finish()
        return


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([(r"/?.+", DiscoverHandler)], db=rd)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
