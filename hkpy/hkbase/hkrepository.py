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

from typing import TypeVar, List, Dict, Union, Optional

import requests
import json
import copy
from abc import abstractmethod
from io import TextIOWrapper

from . import HKTransaction, generate_id, constants
from ..hklib import hkfy, HKEntity, HKContext
from ..oops import HKBError, HKpyError
from ..utils import response_validator

__all__  = ['HKRepository']

HKBase = TypeVar('HKBase')

class HKRepository(object):
    """ This class establishes a communication interface with a repository within a hkbase.
    """

    def __init__(self, base: HKBase, name: str):
        """ Initialize an instance of HKRepository class.
    
        Parameters
        ----------
        base: (HKBase) HKBase object in which the repository is located
        name: (str) Repository name
        """

        self.base = base
        self.name = name
        self._headers = base._headers

    def create_transaction(self, id_: Optional[str]=None) -> HKTransaction:
        """ Create a communication transaction with the repository.
        
        Parameters
        ----------
        entities : (Optional[str]) transaction id
        
        Returns
        -------
        (HKTransaction) A HKTransaction object
        """

        if id_ is not None:
            return HKTransaction(id_, self)

        return HKTransaction(id_=generate_id(self))

    def add_entities(self, entities: Union[HKEntity, List[HKEntity]], transaction: Optional[HKTransaction]=None) -> None:
        """ Add entities to repository.
        
        Parameters
        ----------
        entities : (Union[HKEntity, List[HKEntity]]) entity or list of entities
        transaction : (Optional[HKTransaction]) connection transaction
        """

        url = f'{self.base._repository_uri}/{self.name}/entity/'

        if not isinstance(entities, (list,tuple)):
            entities = [entities]
        
        if isinstance(entities[0], HKEntity):
            entities = [x.to_dict() for x in entities]
        elif isinstance(entities[0], dict):
            entities = list(map(hkfy, entities))
        else:
            raise ValueError

        headers = copy.deepcopy(self._headers)
        headers["Content-Type"] = "application/json"

        response = requests.put(url=url, data=json.dumps(entities), headers=headers, verify=False)
        response_validator(response=response)

    def get_entities(self, filter_: Union[str, Dict]) -> List[HKEntity]:
        """ Get entities filtered by a css filter or json filter.

        Parameters
        ----------
        filter : (Union[str, Dict]) retrieval filter

        Returns
        -------
        (List[HKEntity]) list of retrieved entities
        """

        url= f'{self.base._repository_uri}/{self.name}/entity'

        try:
            if isinstance(filter_, str):
                tmp_headers = copy.copy(self._headers)
                tmp_headers['Content-Type'] = 'text/plain'
                response = requests.post(url=url, data=filter_, headers=tmp_headers, params={})
            elif isinstance(filter_, dict):
                response = requests.post(url=url, data=json.dumps(filter_), headers=self._headers)
            else:
                raise HKpyError(message='Invalid filter type.')
                
            _, data = response_validator(response=response)
        except (HKBError, HKpyError) as err:
            raise err
        except Exception as err:
            raise HKpyError(message='Could not retrieve the entities.', error=err)
        
        return [hkfy(entity) for entity in data.values()]

    def delete_entities(self, ids: Union[str, List[str], HKEntity, List[HKEntity]], transaction: Optional[HKTransaction]=None) -> None:
        """ Delete entities from the repository using their ids.

        Parameters
        ----------
        ids : (Union[str, List[str], HKEntity, List[HKEntity]]) list of entities' ids or entities
        """

        url = f'{self.base._repository_uri}/{self.name}/entity/'

        if not isinstance(ids, (list,tuple)):
            ids = [ids]
        
        if isinstance(ids[0], HKEntity):
            ids = [x.id_ for x in ids]
            
        response = requests.delete(url=url, data=json.dumps(ids), headers=self._headers)
        response_validator(response=response)

    def update_entities(self, entities: Union[HKEntity, List[HKEntity]], transaction: Optional[HKTransaction]=None) -> None:
        """ Update entities in the repository.
        
        Parameters
        ----------
        entities : (Union[HKEntity, List[HKEntity]]) entity or list of entities
        transaction : Optional[HKTransaction] connection transaction
        """
        
        self.add_entities(entities, transaction)

    def import_data(self, fd: Union[str, TextIOWrapper], datatype: constants.ContentType, **options) -> None:
        """ Import data to the hkbase.

        Parameters
        ----------
        fd : (Union[str, TextIOWrapper]) file or data to be imported
        datatype : (constants.ContentType) data's type
        **options : additional options to hkbase
        """

        if isinstance(fd, TextIOWrapper):
            fd = fd.read()
        elif isinstance(fd, str):
            pass
        else:
            raise HKpyError(message='Data formaat not supported.')

        url = f'{self.base._repository_uri}/{self.name}/rdf'

        tmp_headers = copy.copy(self._headers)
        tmp_headers.update({
            'Content-Type': datatype,
            'Content-Length': str(len(fd.encode('utf-8')))
        })

        if 'context' in options:
            if isinstance(options['context'], HKContext):
                options['context'] = options['context'].id_

            tmp_headers['context-parent'] = options['context']

        response = requests.put(url=url, data=fd, params=options, headers=tmp_headers)
        response_validator(response)

    def clear(self) -> None:
        """ Delete all entities in the repository.
        """
        
        entities = self.get_entities(filter_={})
        self.delete_entities(ids=entities, transaction=None)
