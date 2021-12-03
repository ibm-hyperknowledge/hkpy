###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import traceback
import urllib.parse
from typing import Optional
import requests
from flask import jsonify, request
from flask import Flask
from flask_cors import CORS
from threading import Thread
import logging
import socket

from hkpy.hkbase.observer.clients.configurableobserverclient import ConfigurableObserverClient
from hkpy.hkbase.observer.clients.configurableobserverclient import HKBase


class RESTObserverClient(ConfigurableObserverClient):
    TYPE_KEY = 'rest'

    def __init__(self,
                 hkbase: HKBase,
                 info=None,
                 observer_options=None,
                 hkbase_options=None,
                 observer_service_params=None,
                 flask_app: Optional = None
                 ):
        """
        Parameters
        ----------
        hkbase: (HKBase) HKBase object that the client will observe
        info: (Dict) info observer info from hkbase
        observer_options: (Dict) observer initialization options
        observer_options['port']: (int) port te be used when instantiating flask app for receiving callback requests
        observer_options['address']: (str) address use when instantiating flask app for receiving callback requests
        hkbase_options: (Dict) options to be used when communicating with hkbase
        observer_service_params: (Dict) observer service parameters (if using specialized observer)
        flask_app: (Flask) flask application to be used for registering notification callback endpoints
        if None is provided this client will instantiate a flask app automatically.
        """
        super().__init__(hkbase, hkbase_options, observer_service_params)

        if observer_options is None:
            observer_options = {}

        self._port = observer_options.get('port', 0)
        self._address = observer_options.get('address', 'localhost')
        self._flask_app = flask_app
        self._listening_path = None

        if self._port == 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self._address, 0))
            self._port = sock.getsockname()[1]
            sock.close()

        self._use_internal_flask_app = False
        if self._flask_app is None:
            self._use_internal_flask_app = True

    def init(self):
        logging.info("initializing REST observer client")
        try:
            if self._use_internal_flask_app:
                self._flask_app = Flask(__name__)
                CORS(self._flask_app)
                thread = Thread(target=self._flask_app.run, kwargs=dict(host=self._address, port=self._port))
                thread.start()
                logging.info(f"Flask Server initialized at port {self._port} for receiving callback requests of "
                             f"HKBase notifications")
            listening_path = f"http://{self._address}:{self._port}"
            self._listening_path = listening_path
            self.setup_endpoints()
            if self.uses_specialized_observer():
                self._observer_configuration['callbackEndpoint'] = listening_path
                self.register_observer()
            else:
                headers = {}
                self.set_hkkbase_options(headers)
                encoded_listening_path = urllib.parse.quote_plus(listening_path)
                response = requests.put(f'{self._hkbase.url}/observer/{encoded_listening_path}', headers=headers)
                if 400 <= response.status_code < 500:
                    logging.warning('observer already registered')
                    return
                elif not response.ok:
                    raise Exception(f'[{response.status_code}] {response.content}')
                logging.info('registered as observer of hkbase')
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            raise e

    def deinit(self):
        logging.info('Deiniting observer')
        if self._observer_id is not None:
            self.unregister_observer()
        elif self._listening_path is not None:
            headers = {}
            self.set_hkkbase_options(headers)
            encoded_listening_path = urllib.parse.quote_plus(self._listening_path)
            response = requests.delete(f'{self._hkbase.url}/observer/{encoded_listening_path}', headers=headers)
            response.raise_for_status()
        if self._use_internal_flask_app and self._flask_app is not None:
            response = requests.post(f'{self._listening_path}/shutdown')
            response.raise_for_status()
            logging.info(f'Flask Server at port {self._port} was stopped')
        self._listening_path = None
        self._flask_app = None
        self._use_internal_flask_app = False
        self._port = None
        logging.info('Observer deinited')

    def setup_endpoints(self):
        """
        - `POST /repository/<repoName>`: Repository `repoName` was created. - `DELETE /repository/<repoName>`:
        Repository `repoName` was deleted. ### Entities changes HKBase calls the following endpoints passing a JSON
        Array of strings, elements in this array are the IDs of affected entities. - `POST
        /repository/<repoName>/entity`: Entities were added to repository `repoName`; - `PUT
        /repository/<repoName>/entity`: Entities were changed in repository `repoName`; - `DELETE
        /repository/<repoName>/entity`: Entites were removed from repository `repoName`.
        """

        notification_callback = self.notify

        def repository_callback(action, repo_name):
            notification = {
                'action': action,
                'object': 'repository',
                'args': {'repository': repo_name}
            }
            notification_callback(notification)

        def entities_callback(action, repo_name, entities):
            notification = {
                'action': action,
                'object': 'entities',
                'args': {'repository': repo_name, 'entities': entities}
            }
            notification_callback(notification)

        def created_repository_callback(repo_name: str):
            repository_callback('create', repo_name)
            return jsonify(None), 200

        def deleted_repository_callback(repo_name: str):
            repository_callback('delete', repo_name)
            return jsonify(None), 200

        def added_entities_callback(repo_name: str):
            entities = request.json
            entities_callback('create', repo_name, entities)
            return jsonify(None), 200

        def changed_entities_callback(repo_name: str):
            entities = request.json
            entities_callback('update', repo_name, entities)
            return jsonify(None), 200

        def removed_entities_callback(repo_name: str):
            entities = request.json
            entities_callback('delete', repo_name, entities)
            return jsonify(None), 200

        def shutdown_callback():
            shutdown_function = request.environ.get('werkzeug.server.shutdown')
            if shutdown_function is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            shutdown_function()
            return jsonify(None), 200

        self._flask_app.route(f'/repository/<repo_name>', methods=['POST'])(created_repository_callback)
        self._flask_app.route(f'/repository/<repo_name>', methods=['DELETE'])(deleted_repository_callback)
        self._flask_app.route(f'/repository/<repo_name>/entity', methods=['POST'])(added_entities_callback)
        self._flask_app.route(f'/repository/<repo_name>/entity', methods=['PUT'])(changed_entities_callback)
        self._flask_app.route(f'/repository/<repo_name>/entity', methods=['DELETE'])(removed_entities_callback)
        self._flask_app.route(f'/shutdown', methods=['POST'])(shutdown_callback)
