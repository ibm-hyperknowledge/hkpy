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

from hkpy.hkbase.observer.clients.configurableobserverclient import ConfigurableObserverClient as ObserverClient
from hkpy.hkbase.observer.clients.configurableobserverclient import HKBase


class RESTObserverClient(ObserverClient):
    TYPE_KEY = 'rest'

    def __init__(self,
                 hkbase: HKBase,
                 info=None,
                 observer_options=None,
                 hkbase_options=None,
                 observer_service_params=None,
                 flask_app: Optional = None
                 ):
        super().__init__(hkbase, hkbase_options, observer_service_params)

        if observer_options is None:
            observer_options = {}

        self._port = observer_options.get('port', 0)
        self._address = observer_options.get('address', 'http://localhost')
        self._flask_app = flask_app

    def init(self):
        self.setup_endpoints()
        try:
            listening_path = f"{self._address}:{self._port}"
            if self._flask_app is None:
                self._flask_app = Flask(__name__)
                CORS(self._flask_app)
                thread = Thread(target=self._flask_app.run, kwargs=dict(host=self._address, port=self._port))
                thread.start()
            if self.uses_specialized_observer():
                self._observer_configuration['callbackEndpoint'] = listening_path
                self.register_observer()
            else:
                logging.info('registering as observer of hkbase')
                headers = {}
                self.set_hkkbase_options(headers)
                encoded_self_path = urllib.parse.quote_plus(f'http://{self._address}:{self._port}/')
                response = requests.put(f'{self._hkbase.url}/observer/{encoded_self_path}', headers=headers)
                if 400 <= response.status_code < 500:
                    logging.warning('observer already registered')
                    return
                elif not response.ok:
                    raise Exception(f'[{response.status_code}] {response.content}')
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            raise e

    def setup_endpoints(self):
        """
        - `POST /repository/<repoName>`: Repository `repoName` was created. - `DELETE /repository/<repoName>`:
        Repository `repoName` was deleted. ### Entities changes HKBase calls the following endpoints passing a JSON
        Array of strings, elements in this array are the IDs of affected entities. - `POST
        /repository/<repoName>/entity`: Entities were added to repository `repoName`; - `PUT
        /repository/<repoName>/entity`: Entities were changed in repository `repoName`; - `DELETE
        /repository/<repoName>/entity`: Entites were removed from repository `repoName`.
        """

        def repository_callback(action, repo_name, notification_callback):
            notification = {
                'action': action,
                'object': 'repository',
                'args': {'repository': repo_name}
            }
            notification_callback(notification)

        def entities_callback(action, repo_name, entities, notification_callback):
            notification = {
                'action': action,
                'object': 'entities',
                'args': {'repository': repo_name, 'entities': entities}
            }
            notification_callback(notification)

        def created_repository_callback(repo_name: str, notification_callback):
            repository_callback('create', repo_name, notification_callback)
            return jsonify(None), 200

        def deleted_repository_callback(repo_name: str, notification_callback):
            repository_callback('delete', repo_name, notification_callback)
            return jsonify(None), 200

        def added_entities(repo_name: str, notification_callback):
            entities = request.json
            entities_callback('create', repo_name, entities, notification_callback)
            return jsonify(None), 200

        def changed_entities(repo_name: str, notification_callback):
            entities = request.json
            entities_callback('update', repo_name, entities, notification_callback)
            return jsonify(None), 200

        def removed_entities(repo_name: str, notification_callback):
            entities = request.json
            entities_callback('delete', repo_name, entities, notification_callback)
            return jsonify(None), 200

        self._flask_app.route(f'/repository/<repo_name>', methods=['POST'])(created_repository_callback)
        self._flask_app.route(f'/repository/<repo_name>', methods=['DELETE'])(deleted_repository_callback)
        self._flask_app.route(f'/repository/<repo_name>/entity', methods=['POST'])(changed_entities)
        self._flask_app.route(f'/repository/<repo_name>/entity', methods=['PUT'])(added_entities)
        self._flask_app.route(f'/repository/<repo_name>/entity', methods=['DELETE'])(removed_entities)
