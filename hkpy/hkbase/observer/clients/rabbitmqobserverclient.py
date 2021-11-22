###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import json
import logging
import traceback

import pika

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
            'exchangeName': info.get('exchangeName', None),
            'exchangeOptions': info.get('exchangeOptions', {}),
            'certificate': info.get('certificate', observer_options.get('certificate', None)),
        }

    def init(self):
        try:
            queue_name = ''

            if self.uses_specialized_observer():
                logging.info('registering as observer of hkbase observer service')
                queue_name = self.register_observer()
            else:
                logging.info('registering as observer of hkbase')

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

            def callback(ch, method, properties, body):
                try:
                    notification = json.loads(body.decode('utf-8'))
                    self.notify(notification)
                except Exception as e:
                    traceback.print_exc()
                    logging.error(e)

            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

            logging.info(f" [*] Waiting for messages in {queue_name}. To exit press CTRL+C")
            channel.start_consuming()
        except Exception as e:
            traceback.print_exc()
            logging.error(e)

    def _parse_config(self):
        url_with_protocol = self._config['broker'].replace('amqp://', '')
        url_components = url_with_protocol.split(':')
        host = url_components[0]
        if len(url_components) == 2:
            port = url_components[1]
        else:
            port = None
        return host, port
