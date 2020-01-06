###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import requests
from abc import abstractmethod

from ..oops import HKBError, HKpyError
from ..utils import response_validator

__all__ = ['HKTransaction']

class HKTransaction(object):
    """ This class establishes a communication interface with a transaction within a hkbase.
    """

    def __init__(self, id_, repository):
        raise(NotImplementedError)
        self.id_ = id_
        self.repository = repository
    
    def __repr__(self):
        return f'{super().__repr__()}: {self.id_}'
    
    def commit(self) -> None:
        url = f'{self.repository.base.repository_url}/{self.repository.name}/transaction/commit/{self.id_}'
        
        response = requests.post(url=url, headers=self.repository.base.headers)
        response_validator(response=response)

    def rollback(self) -> None:
        url = f'{self.repository.base.repository_url}/{self.repository.name}/transaction/rollback/{self.id_}'
        
        response = requests.post(url=url, headers=self.repository.base.headers)
        response_validator(response=response)