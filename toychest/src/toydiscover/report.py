# TODO: auto-downloaded code through some stuff

import requests, threading

class ToyDiscoverReporter:
    WAIT_SECONDS = 25
    WAIT_SECONDS_FAILURE = 120

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
            print(f'I am a console output debug line. Kill me. {e.__class__} : {e.__str__()}')
            return False

    def ioloop(self):
        if self.report():
            threading.Timer(ToyDiscoverReporter.WAIT_SECONDS, self.ioloop).start()
        else:
            threading.Timer(ToyDiscoverReporter.WAIT_SECONDS_FAILURE, self.ioloop).start()
