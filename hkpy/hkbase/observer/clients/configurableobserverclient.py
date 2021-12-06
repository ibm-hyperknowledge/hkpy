###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import traceback
import logging
import requests
import signal
from abc import ABC

from hkpy.hkbase.observer.clients.observerclient import ObserverClient, HKBase


class ConfigurableObserverClient(ObserverClient):
    """
    Abstract class that defines the behaviour of a configurable observer client
    """
    TYPE_KEY = 'configurable'

    def __init__(self,
                 hkbase: HKBase,
                 hkbase_options=None,
                 observer_service_options=None
                 ):
        """
         Parameters
        ----------
        hkbase: (HKBase) HKBase object that the client will observe
        hkbase_options: (Dict) options to be used when communicating with hkbase
        observer_service_params: (Dict) observer service parameters (if using specialized observer)
        observer_service_params['url']: (str) url of the hkbase observer service
        observer_service_params['observerConfiguration']: (Dict) the ObserverConfiguration of this client,
        that includes which notification filters should be applied and the desired notification format.
        The definition of ObserverConfiguration fields and possible filters is provided in OpenAPI/Swagger format at:
        "https://github.ibm.com/keg-core/hkbase-observer/blob/main/docs/spec.yml" or acessing the
        hkbaseObserverServiceUrl through a browser (Swagger UI)
        observer_service_params['heartbeatInterval']: (int) heartbeat interval of the hkbase observer service
        if this interval is greater than 0, a recurrent heartbeat function will be set when a specialized observer
        is initialized. This function makes a request to the heartbeat endpoint of the hkbase observer service to
        reset the configuration timeout if the server stops receiving the heartbeat for this observer configuration
        it will be erased after it times out and the notifications will stop being emmited for its clients
        """
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
        signal.alarm(0)
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
