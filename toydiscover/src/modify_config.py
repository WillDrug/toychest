from toycommons.config import Config
from toycommons.drive import DriveConnect
from pymongo import MongoClient
from os import getenv
import json
from google_auth_oauthlib.flow import InstalledAppFlow
# fixme this is bullshit :\


if __name__ == '__main__':
    host = getenv('host', 'mongodb://toydb')
    port = int(getenv('port', 27017))
    drive_port = int(getenv('drive_port', 8080))
    username = getenv('username') or 'root'
    password = getenv('password') or 'qwerty'
    init_drive = True if getenv('init_drive', False) else False
    drive_secret = getenv('drive_secret')
    config_json = getenv('config_json')


    client = MongoClient(host=host, port=port, username=username, password=password)
    config = Config(client.toyinfra.mainline)

    host_callback = getenv('drive_host', config.base_url)

    if init_drive:
        if drive_secret is None:
            raise ValueError(f'Provide drive_secret')
        secret = json.loads(drive_secret)
        flow = InstalledAppFlow.from_client_config(secret, DriveConnect.SCOPES)
        creds = flow.run_local_server(port=drive_port, host=host_callback, bind_addr='0.0.0.0')
        config.drive_token = json.loads(creds.to_json())
    if config_json:
        mod = json.loads(config_json)
        for k in mod:
            config[k] = mod[k]