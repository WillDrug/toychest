from toycommons.model.exceptions import AuthException
from flask import Flask, request, render_template, abort
from toycommons.model.service import Service
from toycommons.model.message import Command
from pymongo.errors import OperationFailure
from toycommons.drive.document import HTMLConverter, CSSStructure
from os import path
from itertools import chain
from time import time
from os import getenv
from toycommons import ToyInfra
import json
import flask

app = Flask(__name__)
tc = ToyInfra('toychest', user=getenv('MONGO_USER'), passwd=getenv('MONGO_PASSWORD')) #, ignore_drive_errors=True)

times = [5, 30, 180, 3000, -1]
app.config.setdefault('backoff', times[0])


tc.drive.add_directory(tc.name)
toychest_data = tc.get_own_config()  # command action sync domain toychest filename toychest.json
app.config.update(toychest_data.data)


def get_servable_docs():
    gdocs = []
    for f in tc.drive.list_google_docs(folder=tc.name):
        if 'description' not in f:
            continue
        if ';' not in f['description']:
            continue
        srv = {'name': f['name']}
        local_name, srv['description'], *srv['tags'] = f['description'].split(';')
        srv['host'] = f'/g/{local_name}'

        # override from json if needed (shouldn't be)
        # like
        #     "how-toychest-was-built": {
        #         "tags": ["Article", "Technology"]
        #     }
        srv.update(app.config.get('gdocs', {}).get(local_name, {}))
        gdocs.append(Service(**srv))

    return gdocs


def get_doc_id(name):
    for f in tc.drive.list_google_docs(folder=tc.name):
        if 'description' not in f:
            continue
        if ';' not in f['description']:
            continue
        doc_name, _ = f['description'].split(';')
        if doc_name == name:
            return f['id']
    return None

@app.route("/")
def index():
    services = tc.discover.get_services()
    services.extend([Service(**q) for q in app.config.get('cards', [])])
    services.extend(get_servable_docs())

    tags = []
    for service in services:
        if service.host.startswith('/'):
            service.host = tc.get_self_url(origin=flask.request.origin, headers=flask.request.headers) + service.host
        elif not service.host.startswith('http'):
            service.host = tc.get_url(service.host, origin=flask.request.origin, headers=flask.request.headers)
        if service.image is not None and not service.image.startswith('http'):
            service.image = f'{tc.get_self_url(origin=flask.request.origin, headers=flask.request.headers)}/dynamic/{service.image}'
        if service.tags is None:
            service.tags = ()
        tags = list(set(chain(*[q.tags for q in services if q.tags is not None])))

    return render_template('index.html', url=tc.get_self_url(origin=flask.request.origin, headers=flask.request.headers),
                           data=app.config, services=services, tags=tags)


@app.route('/dynamic/<path:filename>')
def dynamic(filename):
    c = tc.commands.receive('toychest', filename)  # expecting only sync for now
    if not path.exists(path.join(app.static_folder, filename)) or c is not None:
        data = tc.drive.file_by_name(filename, folder=tc.name)
        if data is not None:
            with open(path.join(app.static_folder, filename), 'wb') as f:
                f.write(data)

    return app.send_static_file(filename)


@app.route('/g/<url_name>')
def google_doc(url_name):
    # expect to request an existing card (!)
    fid = get_doc_id(url_name)
    if fid is None:
        return '', 404

    gdoc = tc.drive.get_google_doc(url_name, fid, filename=f'{url_name}.gdoc',
                                   domain=tc.name, get_synced=True, command_storage=tc.commands,
                                   cache_images=True, image_folder=app.static_folder,
                                   uri_prepend=f'{tc.get_self_url(origin=flask.request.origin, headers=flask.request.headers)}/static/')
    classes = CSSStructure(outer_div='container-doc main-body container')
    cards = get_servable_docs()
    cards = [q for q in cards if url_name not in q.host]
    html_converter = HTMLConverter(gdoc.data, css_classes=classes, ignore_black_white=True)
    return render_template('google_doc.html', document=html_converter.body_as_html(), data=app.config,
                           url=tc.get_self_url(origin=flask.request.origin, headers=flask.request.headers), cards=cards)


@app.route('/command', methods=['POST', 'GET'])
def command():
    if tc.cache.backoff == -1 or (tc.cache.backed_off is not None and time() - tc.cache.backed_off < tc.cache.backoff):
        return abort(500, 'Fuck You.')
    tc.cache.backed_off = None
    result = None

    if request.method == 'POST':
        data = request.form.to_dict()
        try:  # todo: switch this to API auth instead of internal one.
            if tc.config.command_access_token is None or tc.config.command_access_token != data.get('token'):
                raise AuthException(f'Oh no, no')
            del data['token']
            if data['domain'] == '':
                data['domain'] = None
            for k in list(data.keys()):
                if data[k] is None or data[k] == '':
                    del data[k]
            c = Command(**data)
            if c.domain is None and c.recipient == 'config' and c.message == 'sync':
                config = tc.drive.file_by_id(tc.config.config_file_id)
                config = json.loads(config.decode())
                for k in config:
                    tc.config[k] = config[k]
            elif c.domain == tc.name and c.recipient == f'{tc.name}.json' and c.message == 'sync':
                # this is a dirty hack, this should be better
                toychest_data.sync()
                app.config.update(toychest_data.data)
            else:
                tc.commands.send(c)
        except AuthException as e:
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
            # no result, no info.
        except Exception as e:
            result = f'{e.__class__}: {e.__str__()}'
        else:
            result = 'Ok'
            tc.cache.backoff = None

    data = app.config
    return render_template('command.html', url=tc.get_self_url(origin=flask.request.origin,
                                                               headers=flask.request.headers), data=data,
                           result=result)
