###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import inspect
import logging
from os.path import dirname, basename, isfile, join
import traceback
import glob
import requests

from .observer.clients.observerclient import HKBase

classes = []
modules = glob.glob(join(dirname(__file__), 'observer', 'clients', "*.py"))
for m in modules:
    if isfile(m) and not m.endswith('__init__.py'):
        classes.extend(inspect.getmembers(m, inspect.isclass))

clients = {}
print('classes', classes)
for c in classes:
    print('c.__name__', c.__name__)
    print('c', c)
    clients[c.__name__] = c


def create_observer(hkbase: HKBase, observer_options=None, hkbase_options=None):
    if hkbase_options is None:
        hkbase_options = {}
    if observer_options is None:
        observer_options = {}

    try:

        response = requests.get(f'{hkbase.url}observer/info', headers=hkbase_options)
        if not response.ok:
            raise Exception(f'[Code: {response.status_code}] {response.content}')

        info = response.json()
        print('info', info)

        klass = clients.get(info['type'], None)
        if klass is None:
            raise Exception(f"Cannot create a client for observer: {info['type']}")

        is_observer_service = observer_options.get('isObserverService', 'false').lower() == 'true'
        observer_service_params = {}
        if not is_observer_service:
            observer_service_url = observer_options.get('hkbaseObserverServiceUrl', None)
            observer_service_url = info.get('hkbaseObserverServiceUrl', observer_service_url)
            observer_configuration = observer_options.get('hkbaseObserverConfiguration', None)
            observer_configuration = info.get('hkbaseObserverConfiguration', observer_configuration)
            observer_service_params['url'] = observer_service_url
            observer_service_params['observerConfiguration'] = observer_configuration

        if observer_service_params.get('url', False):
            response = requests.get(f"{observer_service_params['url']}/observer/info")
            if not response.ok:
                raise Exception(f'[Code: {response.status_code}] {response.content}')
            observer_service_info = response.json()
            observer_service_params['heartbeatInterval'] = observer_service_info.get('heartbeat', -1)

        return klass(hkbase, info, observer_options, hkbase_options, observer_service_params)

    except:
        traceback.print_exc()
        logging.error('Creating a default client')
        return clients['default'](hkbase, info, observer_options)
