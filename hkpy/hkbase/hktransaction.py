# MIT License

# Copyright (c) 2019 IBM Hyperlinked Knowledge Graph

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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