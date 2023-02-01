from flask import Flask, request, render_template, abort
from toycommons import ToyInfra
from toycommons.model.service import Service
from toycommons.model.command import Command
from pymongo.errors import OperationFailure
from toycommons.drive.document import HTMLConverter, CSSStructure
from os import path
from itertools import chain
from time import time


app = Flask(__name__)
tc = ToyInfra('toychest', user='root', passwd='qwerty')
tc.drive.add_directory(tc.name)

toychest_data = tc.get_own_config()  # command action sync domain toychest filename toychest.json

times = [5, 30, 180, 3000, -1]
app.config.setdefault('backoff', times[0])


def get_servable_docs():
    gdocs = []
    for f in tc.drive.list_google_docs(folder=tc.name):
        if 'description' not in f:
            continue
        if ';' not in f['description']:
            continue
        srv = {'name': f['name']}
        local_name, srv['description'] = f['description'].split(';')
        srv['host'] = f'/g/{local_name}'
        srv.update(toychest_data.data.get('gdocs', {}).get(srv['host'], {}))
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
    services.extend([Service(**q) for q in toychest_data.data['cards']])
    services.extend(get_servable_docs())

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
    resync = False
    q = tc.commands.get_queue(action='sync', domain=tc.name, file=filename)
    for c in q:
        try:
            q.send(True)
        except StopIteration:
            pass
        resync = True
    if not path.exists(path.join(app.static_folder, filename)) or resync:
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
                                   domain=tc.name, get_synced=True, command_queue=tc.commands,
                                   cache_images=True, image_folder=app.static_folder,
                                   uri_prepend=f'{tc.self_url}/static/')
    classes = CSSStructure(outer_div='container-doc main-body container')
    cards = get_servable_docs()
    cards = [q for q in cards if url_name not in q.host]
    html_converter = HTMLConverter(gdoc.data, css_classes=classes, ignore_black_white=True)
    return render_template('google_doc.html', document=html_converter.body_as_html(), data=toychest_data.data,
                           url=tc.self_url, cards=cards)


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
            for k in list(data.keys()):
                if data[k] is None or data[k] == '':
                    del data[k]
            c = Command(**data)
            if c.action == 'configstr':
                current = extra_tc.config[c.name]
                if current is None or not isinstance(current, str):
                    raise ArithmeticError(f'Wrong datatype or no config field')
                extra_tc.config[c.name] = c.str_value
            elif c.action == 'configint':
                current = extra_tc.config[c.name]
                if current is None or not isinstance(current, int):
                    raise ArithmeticError(f'Wrong datatype or no config field')
                extra_tc.config[c.name] = int(c.num_value)
            else:
                extra_tc.commands.insert(c)
        except OperationFailure:
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
    return render_template('command.html', url=tc.self_url, data=toychest_data.data,
                           fields=Command.all_fields(), result=result)
