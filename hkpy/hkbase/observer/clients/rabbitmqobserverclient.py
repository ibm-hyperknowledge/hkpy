###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import json
import logging
import time
import traceback
import os
import pika
import pika.exceptions
from threading import Thread

from hkpy.hkbase.observer.clients.configurableobserverclient import ConfigurableObserverClient as ObserverClient
from hkpy.hkbase.observer.clients.configurableobserverclient import HKBase


class RabbitMQObserverClient(ObserverClient):
    TYPE_KEY = 'rabbitmq'

    def __init__(self,
                 hkbase: HKBase,
                 info=None,
                 observer_options=None,
                 hkbase_options=None,
                 observer_service_params=None
                 ):
        super().__init__(hkbase, hkbase_options, observer_service_params)

        if observer_options is None:
            observer_options = {}
        if info is None:
            info = {}

        self._config = {
            'broker': info.get('broker', None),
            'brokerExternal': info.get('brokerExternal', None),
            'exchangeName': info.get('exchangeName', None),
            'exchangeOptions': info.get('exchangeOptions', {}),
            'certificate': info.get('certificate', observer_options.get('certificate', None)),
        }
        self._channel = None
        self._connection = None
        self._queue_name = None
        self._consumer_thread = None

    def init(self):
        try:
            logging.info("initializing RabbitMQ observer client")
            queue_name = ''
            if self.uses_specialized_observer():
                queue_name = self.register_observer()
            else:
                logging.info('registered as observer of hkbase')

            host, port = self._parse_config()
            connection_params = {}
            connection_params.update({'host': host})
            if port is not None:
                connection_params['port'] = port
            if self._config.get('certificate', False):
                connection_params['credentials'] = self._config['certificate']

            connection = pika.BlockingConnection(pika.ConnectionParameters(**connection_params))
            channel = connection.channel()
            result = channel.queue_declare(queue=queue_name, **self._config['exchangeOptions'])
            queue_name = result.method.queue
            channel.queue_bind(queue_name, exchange=self._config['exchangeName'])

            logging.info(f"Bound to exchange {self._config['exchangeName']}")

            observer_id = self._observer_id

            self._channel = channel
            self._queue_name = queue_name
            self._connection = connection

            def consumer():
                logging.info(f" [*] Waiting for messages in {self._queue_name}. To exit press CTRL+C")
                time.sleep(1)
                while self._queue_name is not None:
                    try:
                        try:
                            method, properties, body = channel.basic_get(queue=self._queue_name, auto_ack=True)
                        except pika.exceptions.DuplicateGetOkCallback:
                            continue
                        except (pika.exceptions.ConnectionWrongStateError, pika.exceptions.ChannelWrongStateError):
                            logging.info('stopping consumer')
                            return
                        if body is None:
                            continue
                        message = json.loads(body.decode('utf-8'))
                        if observer_id and message.get('observerId', '') == observer_id:
                            self.notify(message.get('notification', {}))
                        elif not observer_id:
                            self.notify(message)
                    except Exception as e:
                        traceback.print_exc()
                        logging.error(e)
                    time.sleep(1)
            self._consumer_thread = Thread(target=consumer)
            self._consumer_thread.start()

        except Exception as e:
            traceback.print_exc()
            logging.error(e)

    def deinit(self):
        logging.info("Deiniting observer")
        logging.info('canceled AMQP consumer')
        if self._observer_id is None:
            self._channel.queue_delete(self._queue_name)
            logging.info(f"removed queue {self._queue_name}")
            self._queue_name = None
        else:
            self.unregister_observer()
        self._channel.close()
        self._channel = None
        self._connection = None
        self._consumer_thread.join()
        self._consumer_thread = None

    def _parse_config(self):
        url_with_protocol = self._config['broker'].replace('amqp://', '')
        url_components = url_with_protocol.split(':')
        host = url_components[0]
        if len(url_components) == 2:
            port = url_components[1]
        else:
            port = None

        ping_result = os.system("ping -c 1 " + host)
        if ping_result != 0 and self._config.get('brokerExternal', False):
            url_with_protocol = self._config['brokerExternal'].replace('amqp://', '')
            url_components = url_with_protocol.split(':')
            host = url_components[0]
        return host, port
