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

__all__ = ['create_observer']


def initialize_clients_by_key():
    clients_by_key_dict = {}
    clients_dirpath = join(dirname(__file__), 'observer', 'clients')
    modules_filepaths = glob.glob(join(clients_dirpath, "*.py"))
    for module_filepath in modules_filepaths:
        if isfile(module_filepath) and not module_filepath.endswith('__init__.py'):
            module_name = f"{module_filepath.replace(clients_dirpath, '').replace('.py', '').replace('/', '')}"
            loader = importlib.machinery.SourceFileLoader(module_name, module_filepath)
            module = loader.load_module(module_name)
            for class_name, klass in inspect.getmembers(module, inspect.isclass):
                if hasattr(klass, 'TYPE_KEY'):
                    clients_by_key_dict[klass.TYPE_KEY] = klass
    return clients_by_key_dict


clients_by_key = initialize_clients_by_key()


def create_observer(hkbase: HKBase, observer_options=None, hkbase_options=None):
    """
    Instantiate an observer client.
    This method will ask the target HKBase which observer configuration it supports (REST or RabbitMQ)
    and will instantiate the appropriate client with the provided configurations.

    Parameters
    ----------
    hkbase: (HKBase) HKBase object that the client will observe
    observer_options: (Dict)  Observer options that are used to initialize the observer client.
    observer_options['hkbaseObserverService']: (bool) if true, the factory method will assume that it
    is being called from the hkbaseObserverService and will ignore hkbaseObserverServiceUrl,
    hkbaseObserverServiceExternalUrl and hkbaseObserverConfiguration options.
    observer_options['hkbaseObserverService']: (str) url of the hkbaseObserverService to be used
    if hkbase does not inform one.
    observer_options['hkbaseObserverServiceExternalUrl']: (str) external url of the hkbaseObserverService to be used if
    hkbaseObserverServiceUrl is not accessible to client and hkbase does not provide one.
    observer_options['hkbaseObserverConfiguration']: (Dict) the ObserverConfiguration of this client, that includes
    which notification filters should be applied and the desired notification format
    The definition of ObserverConfiguration fields and possible filters is provided in OpenAPI/Swagger format at:
    "https://github.ibm.com/keg-core/hkbase-observer/blob/main/docs/spec.yml" or acessing the
    hkbaseObserverServiceUrl through a browser (Swagger UI)
    observer_options['certificate']: (str) if hkbase uses RabbitMQ notifcation, AMQP certificate can be passed
    observer_options['port']: (int) if hkbase uses REST notification, the port te be used when instantiating flask app
    for receiving callback requests can be passed
    observer_options['address']: (str) if hkbase uses REST notification, the address use when instantiating flask app
    for receiving callback requests can be passed
    hkbase_options: (Dict) options that sould be passed when making requests to hkbase (e.g., headers)

    Returns
    -------
    (ObserverClient) instance of ObserverClient or one of its subclasses
    """
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

        is_observer_service = observer_options.get('isObserverService', False)
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
        logging.error('Could not initialize observer client')
