import traceback

from .observerclient import ObserverClient
from hkpy import HKBase
import logging
import requests
from threading import Thread
import time


class ConfigurableObserverClient(ObserverClient):
    TYPE_KEY = 'configurable'

    def __init__(self,
                 hkbase: HKBase,
                 hkbase_options=None,
                 observer_service_options=None
                 ):
        super().__init__(hkbase)

        if observer_service_options is None:
            observer_service_options = {}
        self._observer_service_params = observer_service_options
        if hkbase_options is None:
            hkbase_options = {}

        self._hkbase_options = hkbase_options
        self._observer_service_url = observer_service_options.get('url', None)
        self._observer_configuration = observer_service_options.get('observerConfiguration', None)
        self._observer_service_heartbeat_interval = observer_service_options.get('heartbeatInteval', -1)

        self._heartbeat_timeout = None

    def uses_specialized_observer(self):
        return self._observer_service_url is not None and self._observer_configuration is not None

    def register_observer(self):
        logging.info('registering as observer of hkbase')
        headers = {'content-type': 'aplication/json'}
        self.set_hkkbase_options(headers)
        logging.info('registering specialized observer')
        response = requests.post(f"{self._observer_service_url}/observer", headers=headers)
        if not response.ok:
            raise Exception(f'[{response.status_code}] {response.content}')
        observer_id = response.json()['observerId']
        logging.info(f"registering with observerId: {observer_id}")
        self.set_heartbeat(observer_id)

    def set_heartbeat(self, observer_id: str):
        if self._observer_service_heartbeat_interval <= 0:
            return

        heartbeat_interval = self._observer_service_heartbeat_interval / 1000  # ms to s

        headers = {}
        self.set_hkkbase_options(headers)

        def heartbeat():
            while True:
                try:
                    response = requests.post(f"{self._observer_service_url}/observer/{observer_id}/heartbeat",
                                             headers=headers)
                except Exception as e:
                    traceback.print_exc()
                    logging.error(e)
                time.sleep(heartbeat_interval)

        heartbeat_thread = Thread(target=heartbeat)
        return heartbeat_thread

    def set_hkkbase_options(self, params):
        params.update(self._hkbase_options)
