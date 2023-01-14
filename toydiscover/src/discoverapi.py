from fastapi import FastAPI, Request
from toycommons import ToyInfra
from toycommons.model.service import Service
from time import time
from os import getenv
from fastapi_utils.tasks import repeat_every
import json
import threading



def prepare_app(tc):
    app = FastAPI()

    service_data = {}  # non-db held service registry. If scaled, update to use db

    def clean():
        nonlocal service_data
        service_data = {k: service_data[k] for k in service_data
                        if time() - service_data[k]['reported'] < tc.config.discovery_ttl + 5}  # todo: config up grace

    @app.post("/services")
    async def update_service(service: Service):
        service_data.update({service.host: {'service': service,
                                            'reported': time()}})
        return {"message": service}

    @app.get("/services")
    async def get_services():
        clean()
        return [q['service'] for q in service_data.values()]

    @app.on_event("startup")
    @repeat_every(seconds=tc.config.drive_config_sync_ttl)
    async def update_config():
        # tc.get_own_config(ignore_cache=True) -> into tc.config
        config = tc.drive.file_by_id(tc.config.config_file_id)
        config = json.loads(config.decode())  # todo error dodge?
        for k in config:
            tc.config[k] = config[k]

    return app


tc = ToyInfra('toydiscover', user='root', passwd='qwerty')  # todo env
app = prepare_app(tc)
