###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from hkpy import HKBase


class ObserverClient:
    TYPE_KEY = 'default'

    def __init__(self, hkbase: HKBase):
        self._hkbase = hkbase
        self._handlers = []

    def get_type(self):
        return self.TYPE_KEY

    def init(self):
        pass

    def add_handler(self, callback):
        if callable(callback):
            self._handlers.append(callback)

    def notify(self, notification):
        for handler in self._handlers:
            handler(notification)
