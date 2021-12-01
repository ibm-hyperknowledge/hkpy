###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import traceback
import logging
import requests
import signal

from hkpy.hkbase.observer.clients.observerclient import ObserverClient, HKBase


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
        self._observer_service_heartbeat_interval = observer_service_options.get('heartbeatInterval', -1)

        self._heartbeat_timeout = None
        self._observer_id = None

    def uses_specialized_observer(self):
        return self._observer_service_url is not None and self._observer_configuration is not None

    def register_observer(self):
        headers = {'content-type': 'application/json'}
        self.set_hkkbase_options(headers)
        logging.info(f"registered as observer of hkbase observer service({self._observer_service_url}) "
                     f"with configuration:")
        logging.info(self._observer_configuration)
        response = requests.post(f"{self._observer_service_url}/observer", headers=headers,
                                 json=self._observer_configuration)
        if not response.ok:
            raise Exception(f'[{response.status_code}] {response.content}')
        observer_id = response.json()['observerId']
        logging.info(f"registered with observerId: {observer_id}")
        self.set_heartbeat(observer_id)
        self._observer_id = observer_id
        return observer_id

    def unregister_observer(self):
        if self._observer_id is None:
            return
        logging.info(f'unregistering observer {self._observer_id}')
        headers = {'content-type': 'application/json'}
        self.set_hkkbase_options(headers)
        logging.info(self._observer_configuration)
        response = requests.delete(f"{self._observer_service_url}/observer/{self._observer_id}", headers=headers)
        if not response.ok:
            raise Exception(f'[{response.status_code}] {response.content}')
        logging.info(f'unregistered observer {self._observer_id}')
        self._observer_id = None

    def set_heartbeat(self, observer_id: str):
        if self._observer_service_heartbeat_interval <= 0:
            return

        heartbeat_interval = int(self._observer_service_heartbeat_interval / 1000)  # ms to s

        headers = {}
        self.set_hkkbase_options(headers)

        def heartbeat(signum, frame):
            try:
                response = requests.post(f"{self._observer_service_url}/observer/{observer_id}/heartbeat",
                                         headers=headers)
                response.raise_for_status()
            except Exception as e:
                traceback.print_exc()
                logging.error(e)
            signal.alarm(heartbeat_interval)

        signal.signal(signal.SIGALRM, heartbeat)
        signal.alarm(heartbeat_interval)

    def set_hkkbase_options(self, params):
        params.update(self._hkbase_options)
