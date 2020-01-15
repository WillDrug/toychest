# TODO: auto-downloaded code through some stuff

import requests, threading

class ToyDiscoverReporter:
    WAIT_SECONDS = 25

    def __init__(self, host, name, description):
        self.ver = 1
        self.host = host
        self.name = name
        self.description = description

    def report(self):  # todo: param the URI up may be?
        try:
            requests.post(f'http://toydiscover', json={'ver': self.ver, 'payload': {'host': self.host,
                                                                                   'name': self.name,
                                                                                   'description': self.description}})
            return True
        except requests.exceptions.ConnectionError as e:
            # fixme: logging
            return False

    def ioloop(self):
        if self.report():
            threading.Timer(ToyDiscoverReporter.WAIT_SECONDS, self.ioloop).start()