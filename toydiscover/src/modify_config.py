from toycommons.storage.config import Config
from toycommons.drive import DriveConnect
from pymongo import MongoClient
from googleapiclient.discovery import build
from os import getenv
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from toycommons import ToyInfra
import google_auth_oauthlib
import flask
from toycommons.drive import DriveConnect


app = flask.Flask('authenticator')



def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'id_token': credentials.id_token}

@app.route("/")
def oauth2callback():
    # Receive an authorisation code from google
    flow = google_auth_oauthlib.flow.Flow.from_client_config(json.loads(drive_secret), scopes=DriveConnect.SCOPES)
    flow.redirect_uri = host_callback
    authorization_response = flask.request.url.replace('http://', 'https://')
    # Use authorisation code to request credentials from Google
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    credentials_to_dict(credentials)
    # Use the credentials to obtain user information and save it to the session
    # oauth2_client = build('oauth2','v2',credentials=credentials)
    # user_info = oauth2_client.userinfo().get().execute()
    infra.config.drive_token = credentials_to_dict(credentials)
    print('done, ctrl-c out of this.')
    return None


if __name__ == '__main__':
    host = getenv('host', 'mongodb://toydb')
    port = int(getenv('port', 27017))
    drive_port = int(getenv('drive_port', 8080))
    username = getenv('username') or 'root'
    password = getenv('password') or 'qwerty'
    init_drive = True if getenv('init_drive', False) else False
    drive_secret = getenv('drive_secret')
    config_json = getenv('config_json')

    infra = ToyInfra('admin', host=host, port=port, user=username, passwd=password, drive=False)
    if init_drive:
        if drive_secret is None:
            raise ValueError(f'Provide drive_secret')
        host_callback = getenv('drive_host', infra.config.base_url) + '/.auth/'
        secret = json.loads(drive_secret)
        flow = google_auth_oauthlib.flow.Flow.from_client_config(json.loads(drive_secret), scopes=DriveConnect.SCOPES)
        flow.redirect_uri = host_callback
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        print(f'Please visit {authorization_url}')
        try:
            app.run('0.0.0.0', drive_port)
        except KeyboardInterrupt:
            print('turning server off')
        # flow = InstalledAppFlow.from_client_config(secret, DriveConnect.SCOPES)
        # creds = flow.run_local_server(port=drive_port, host=host_callback, bind_addr='0.0.0.0')
        # infra.config.drive_token = json.loads(creds.to_json())
    if config_json:
        mod = json.loads(config_json)
        for k in mod:
            infra.config[k] = mod[k]
