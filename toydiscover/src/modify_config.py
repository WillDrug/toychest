from toycommons.storage.config import Config
from toycommons.drive import DriveConnect
from pymongo import MongoClient
from os import getenv
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from toycommons import ToyInfra

if __name__ == '__main__':
    host = getenv('host', 'mongodb://toydb')
    port = int(getenv('port', 27017))
    drive_port = int(getenv('drive_port', 8080))
    username = getenv('username') or 'root'
    password = getenv('password') or 'qwerty'
    init_drive = True if getenv('init_drive', False) else False
    drive_secret = getenv('drive_secret')
    config_json = getenv('config_json')

    infra = ToyInfra('admin', host=host, port=port, user=username, passwd=password)

    host_callback = getenv('drive_host', infra.config.base_url).replace('https://', '').replace('http://', '')

    if init_drive:
        if drive_secret is None:
            raise ValueError(f'Provide drive_secret')
        secret = json.loads(drive_secret)
        flow = InstalledAppFlow.from_client_config(secret, DriveConnect.SCOPES)
        creds = flow.run_local_server(port=drive_port, host=host_callback, bind_addr='0.0.0.0')
        print(creds.to_json())
        infra.config.drive_token = json.loads(creds.to_json())
    if config_json:
        mod = json.loads(config_json)
        for k in mod:
            infra.config[k] = mod[k]
