###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import json
import logging
import traceback
import os
import pika
import pika.exceptions
from threading import Thread

from hkpy.hkbase.observer.clients.configurableobserverclient import ConfigurableObserverClient
from hkpy.hkbase.observer.clients.configurableobserverclient import HKBase


class RabbitMQObserverClient(ConfigurableObserverClient):
    TYPE_KEY = 'rabbitmq'

    def __init__(self,
                 hkbase: HKBase,
                 info=None,
                 observer_options=None,
                 hkbase_options=None,
                 observer_service_params=None
                 ):
        """
        Parameters
        ----------
        hkbase: (HKBase) HKBase object that the client will observe
        info: (Dict) info observer info from hkbase
        info['broker']: (str) amqp broker default address
        info['brokerExternal']: (str) amqp broker external address to be used if default address is not accessible
        info['exchangeName']: (str) name of the RabbitMQ exchange where hkbase will publish messages
        info['exchangeOptions']: (Dict) additional options to be used when connecting to hkbase echange
        info['certificate']: (str) RabbitMQ connection certificate (if needed)
        observer_options: (Dict) observer initialization options
        observer_options['certificate']: (str) RabbitMQ connection certificate (if needed)
        hkbase_options: (Dict) options to be used when communicating with hkbase
        observer_service_params: (Dict) observer service parameters (if using specialized observer)
        """
        super().__init__(hkbase, hkbase_options, observer_service_params)

        if observer_options is None:
            observer_options = {}
        if info is None:
            info = {}

        self._config = {
            'broker': info.get('broker', None),
            'brokerExternal': info.get('brokerExternal', None),
            'exchangeName': info.get('exchangeName', None),
            'defaultExchangeName': info.get('exchangeName', None),
            'exchangeOptions': info.get('exchangeOptions', {}),
            'certificate': info.get('certificate', observer_options.get('certificate', None)),
        }
        self._channel = None
        self._connection = None
        self._consumer_id = None
        self._queue_name = None
        self._consumer_thread = None

    def init(self):
        try:
            logging.info("initializing RabbitMQ observer client")
            exchange_name = self._config.get('exchangeName', '')
            if self.uses_specialized_observer():
                exchange_name = self.register_observer()
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
            result = channel.queue_declare(queue='', **self._config['exchangeOptions'])
            queue_name = result.method.queue
            channel.queue_bind(queue_name, exchange=exchange_name)
            logging.info(f"Bound to exchange {exchange_name}")

            observer_id = self._observer_id

            def callback(ch, method, properties, body):
                try:
                    message = json.loads(body.decode('utf-8'))
                    if observer_id and message.get('observerId', '') == observer_id:
                        self.notify(message.get('notification', {}))
                    elif not observer_id:
                        self.notify(message)
                except Exception as e:
                    traceback.print_exc()
                    logging.error(e)

            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

            def consumer():
                logging.info(f" [*] Waiting for messages in {queue_name}. To exit press CTRL+C")
                try:
                    channel.start_consuming()
                except:
                    logging.info('stopping AMQP consumer')

            self._consumer_id = channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            self._channel = channel
            self._queue_name = queue_name
            self._connection = connection
            self._config['exchangeName'] = exchange_name
            self._consumer_thread = Thread(target=consumer)
            self._consumer_thread.start()
        except Exception as e:
            traceback.print_exc()
            logging.error(e)

    def deinit(self):
        logging.info("Deiniting observer")
        if self._channel is None:
            logging.info("Observer already deinited")
            return
        try:
            self._channel.basic_cancel(self._consumer_id)
        except pika.exceptions.StreamLostError as e:
            logging.warning(e)
        logging.info('canceled AMQP consumer')
        if self._observer_id is not None:
            self.unregister_observer()
        try:
            self._channel.queue_delete(self._queue_name)
        except pika.exceptions.ChannelWrongStateError as e:
            logging.warning(e)
        logging.info(f"removed queue {self._queue_name}")
        self._queue_name = None
        self._config['exchangeName'] = self._config['defaultExchangeName']
        self._consumer_id = None

        try:
            self._channel.close()
        except pika.exceptions.ChannelWrongStateError as e:
            logging.warning(e)
        self._channel = None
        try:
            self._connection.close()
        except pika.exceptions.ConnectionWrongStateError as e:
            logging.warning(e)
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

