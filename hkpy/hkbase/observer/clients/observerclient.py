###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import TypeVar
from abc import ABC, abstractmethod
HKBase = TypeVar('HKBase')


class ObserverClient(ABC):
    """
    Abstract class with basic behaviour and API of an observer client
    """
    TYPE_KEY = 'default'

    def __init__(self, hkbase: HKBase):
        self._hkbase = hkbase
        self._handlers = []

    def get_type(self):
        """
        Retrieves client type

        Returns
        -------
        (str) client type
        """
        return self.TYPE_KEY

    @abstractmethod
    def init(self):
        """
        Initialize client and start calling handlers when notifications are received
        """
        pass

    @abstractmethod
    def deinit(self):
        """
        Deinitilize client and stop receiving notifications
        """
        pass

    def add_handler(self, callback):
        """
        Add handler function to be called when notifications are received
        Can be called more than once
        All added handlers are called for all notifications recieved

        Parameters
        ----------
        callback: (callable) handler function to be called when notifications are received
        """
        if callable(callback):
            self._handlers.append(callback)

    def notify(self, notification):
        """
        Calls every handler passing a notification as single parameter

        Parameters
        ----------
        notification: (Dict) notification received from HKBase or HKBase Observer Service
        """
        for handler in self._handlers:
            handler(notification)
