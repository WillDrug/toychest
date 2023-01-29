import flask
from flask import Flask, request, render_template, abort,
from toycommons import ToyInfra, InfraException
from toycommons.model.service import Service
from toycommons.model.command import Command
from pymongo.errors import OperationFailure
from os import path, getenv
from itertools import chain
from time import time

app = Flask(__name__)
tc = ToyInfra('toychest', user='root', passwd='qwerty')
tc.drive.add_directory(tc.name)

toychest_data = tc.get_own_config()  # command action sync domain toychest filename toychest.json

times = [5, 30, 180, 3000, -1]
app.config.setdefault('backoff', times[0])


@app.route("/")
def index():
    services = tc.discover.get_services()
    services.extend([Service(**q) for q in toychest_data.data['cards']])
    tags = []
    for service in services:
        if service.host.startswith('/'):
            service.host = tc.self_url + service.host
        elif not service.host.startswith('http'):
            service.host = tc.get_url(service.host)
        if service.image is not None and not service.image.startswith('http'):
            service.image = f'{tc.self_url}/dynamic/{service.image}'
        if service.tags is None:
            service.tags = ()
        tags = list(set(chain(*[q.tags for q in services if q.tags is not None])))

    return render_template('index.html', url=tc.self_url, data=toychest_data.data, services=services, tags=tags)


@app.route('/dynamic/<path:filename>')
def dynamic(filename):
    if not path.exists(path.join(app.static_folder, filename)):
        data = tc.drive.file_by_name(filename, folder='toychest')
        if data is not None:
            with open(path.join(app.static_folder, filename), 'wb') as f:
                f.write(data)

    return app.send_static_file(filename)


@app.route('/g/<service_name>')
def google_doc(service_name):
    # expect to request an existing card (!)
    card = next((x for x in toychest_data.data['cards'] if x.get('name')), None)
    if card is None:
        return '', 404
    fid = card.get('g_doc')
    gdoc = tc.drive.get_google_doc(fileid, domain=tc.name, get_synced=True, command_queue=tc.commands)
    return render_template('google_doc.html', document=gdoc.data.as_html(), url=tc.self_url)


@app.route('/command', methods=['POST', 'GET'])
def command():
    if tc.cache.backoff == -1 or (tc.cache.backed_off is not None and time() - tc.cache.backed_off < tc.cache.backoff):
        return abort(500, 'Fuck You.')
    tc.cache.backed_off = None
    result = None

    if request.method == 'POST':
        data = request.form.to_dict()
        try:
            extra_tc = ToyInfra('admin', user=data.pop('user'), passwd=data.pop('password'))
            c = Command(**data)
            extra_tc.commands.insert(c)
        except OperationFailure as e:
            try:
                idx = times.index(tc.cache.backoff)
            except ValueError:
                idx = -1
            idx += 1
            try:
                tc.cache.backoff = times[idx]
            except IndexError:
                tc.cache.backoff = -1
            tc.cache.backed_off = time()
        except Exception as e:
            result = f'{e.__class__}: {e.__str__()}'
        else:
            result = 'Ok'
            tc.cache.backoff = None
    return render_template('command.html', url=tc.self_url, data=toychest_data,
                           fields=Command.all_fields(), result=result)
