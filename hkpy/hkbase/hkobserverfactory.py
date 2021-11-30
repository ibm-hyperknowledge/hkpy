###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import inspect
import logging
import os
from os.path import dirname, isfile, join
import traceback
import glob
import requests
import importlib.machinery

from hkpy.hkbase.observer.clients.observerclient import HKBase

clients_by_key = {}
clients_dirpath = join(dirname(__file__), 'observer', 'clients')
modules_filepaths = glob.glob(join(clients_dirpath, "*.py"))
for module_filepath in modules_filepaths:
    if isfile(module_filepath) and not module_filepath.endswith('__init__.py'):
        module_name = f"{module_filepath.replace(clients_dirpath, '').replace('.py', '').replace('/', '')}"
        loader = importlib.machinery.SourceFileLoader(module_name, module_filepath)
        module = loader.load_module(module_name)
        for class_name, klass in inspect.getmembers(module, inspect.isclass):
            if hasattr(klass, 'TYPE_KEY'):
                clients_by_key[klass.TYPE_KEY] = klass


def create_observer(hkbase: HKBase, observer_options=None, hkbase_options=None):
    if hkbase_options is None:
        hkbase_options = {}
    if observer_options is None:
        observer_options = {}

    try:

        response = requests.get(f'{hkbase.url}/observer/info', headers=hkbase_options)
        if not response.ok:
            raise Exception(f'[Code: {response.status_code}] {response.content}')

        info = response.json()

        klass = clients_by_key.get(info['type'], None)
        if klass is None:
            raise Exception(f"Cannot create a client for observer: {info['type']}")

        is_observer_service = observer_options.get('isObserverService', 'false').lower() == 'true'
        observer_service_params = {}
        if not is_observer_service:
            observer_service_default_url = observer_options.get('hkbaseObserverServiceUrl', None)
            observer_service_params['defaultUrl'] = info.get('hkbaseObserverServiceUrl', observer_service_default_url)
            observer_service_external_url = observer_options.get('hkbaseObserverServiceExternalUrl', None)
            observer_service_params['externalUrl'] = info.get('hkbaseObserverServiceExternalUrl', observer_service_external_url)
            observer_configuration = observer_options.get('hkbaseObserverConfiguration', None)
            observer_configuration = info.get('hkbaseObserverConfiguration', observer_configuration)
            observer_service_params['observerConfiguration'] = observer_configuration

        if observer_service_params.get('defaultUrl', False) and observer_service_params.get('observerConfiguration', False):
            default_url_with_protocol = observer_service_params['defaultUrl'].replace('http://', '').replace('https://', '')
            default_url_components = default_url_with_protocol.split(':')
            default_host = default_url_components[0]
            ping_result = os.system("ping -c 1 " + default_host)
            if ping_result == 0 or observer_service_params.get('externalUrl', None) is None:
                observer_service_params['url'] = observer_service_params['defaultUrl']
            else:
                observer_service_params['url'] = observer_service_params['externalUrl']
            response = requests.get(f"{observer_service_params['url']}/observer/info")
            if not response.ok:
                raise Exception(f'[Code: {response.status_code}] {response.content}')
            observer_service_info = response.json()
            observer_service_params['heartbeatInterval'] = observer_service_info.get('heartbeat', -1)

        return klass(hkbase, info, observer_options, hkbase_options, observer_service_params)

    except:
        traceback.print_exc()
        logging.error('Creating a default client')
        return clients_by_key['default'](hkbase, info, observer_options)
