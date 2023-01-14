from flask import Flask, request, render_template
from toycommons import ToyInfra
from toycommons.model.service import Service
from os import path, getenv
from itertools import chain


app = Flask(__name__)
tc = ToyInfra('toychest', user='root', passwd='qwerty')
tc.drive.add_directory('toychest')
toychest_data = tc.get_own_config()  # command action sync domain toychest filename toychest.json

@app.route("/")
def index():
    services = tc.discover.get_services()
    services.extend([Service(**q) for q in toychest_data.data['cards']])
    for service in services:
        if not service.host.startswith('http'):
            service.host = tc.get_url(service.host)
        if service.image is not None and not service.image.startswith('http'):
            service.image = f'{tc.self_url}/dynamic/{service.image}'
        if service.tags is None:
            service.tags = ()
    toychest_data.data['tags'] = list(set(chain(*[q.tags for q in services if q.tags is not None])))

    return render_template('index.html', url=tc.self_url, data=toychest_data.data, services=services)

@app.route('/dynamic/<path:filename>')
def dynamic(filename):
    if not path.exists(path.join(app.static_folder, filename)):
        data = tc.drive.file_by_name(filename, folder='toychest')
        if data is not None:
            with open(path.join(app.static_folder, filename), 'wb') as f:
                f.write(data)

    return app.send_static_file(filename)
