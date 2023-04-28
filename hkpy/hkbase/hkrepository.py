###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###
import urllib
from typing import TypeVar, List, Dict, Union, Optional, Any, cast, Tuple

import os
import copy
import json
import requests
from urllib.parse import quote
from io import TextIOWrapper, BufferedReader, BufferedIOBase, BytesIO

from . import HKTransaction, generate_id, constants
from ..hklib import hkfy, HKEntity, HKContext
from ..hklib.fi.fi import FI
from ..hklib.node import HKDataNode
from ..oops import HKBError, HKpyError
from ..utils import response_validator
from ..common.result_set import ResultSet
from .query import SPARQLResultSet
from .query_management import HKStoredQuery

__all__  = ['HKRepository']

HKBase = TypeVar('HKBase')
HKEntityResultSet = ResultSet[HKEntity]


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

    def __repr__(self):
        return f'{super().__repr__()}: {self.name}'

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

        filtered_data_objects = []

        if not isinstance(entities, (list,tuple)):
            entities = [entities]

        if isinstance(entities[0], HKEntity):
            entities = [x.to_dict() for x in entities]
        elif isinstance(entities[0], dict):
            pass
        else:
            raise ValueError

        data_entities, entities = self.filter_data_entities(entities)
        if data_entities:
            self.add_data_entities(data_entities)

        headers = copy.deepcopy(self._headers)
        headers['Content-Type'] = 'application/json'

        response = requests.put(url=url, data=json.dumps(entities), headers=headers)
        response_validator(response=response)

    def add_entities_bulk(self, entities: Union[HKEntity, List[HKEntity]], transaction: Optional[HKTransaction] = None) -> None:
        """ Add entities to repository.

        Parameters
        ----------
        entities : (Union[HKEntity, List[HKEntity]]) entity or list of entities
        transaction : (Optional[HKTransaction]) connection transaction
        """

        url = f'{self.base._repository_uri}/{self.name}/entity/bulk'

        if not isinstance(entities, (list,tuple)):
            entities = [entities]

        if isinstance(entities[0], HKEntity):
            entities = [x.to_dict() for x in entities]
        elif isinstance(entities[0], dict):
            pass
            # entities = list(map(hkfy, entities))
        else:
            raise ValueError

        headers = copy.deepcopy(self._headers)
        headers['Content-Type'] = 'application/octet-stream'

        response = requests.put(url=url, data=BufferedReader(BytesIO(json.dumps(entities).encode())), headers=headers)
        response_validator(response=response)

    def filter_data_entities(self, entities: Union[HKEntity, List[HKEntity]]):
        """ filter the entities with raw data.
        Return two lists:
            dataentities: entities with raw data.
            nondataentites: entities without raw data.

        Parameters
        ----------
        entities : (Union[HKDataNode, List[HKDataNode]]) entity or list of entities
        transaction : (Optional[HKTransaction]) connection transaction

        Returns
        -------
        dataentities: (List[HKEntity]) list of entities with raw data
        nondataentites: (List[HKEntity]) list of entities without raw data
        """

        dataentities = []
        nondataentites = []
        for entity in entities:
            if 'raw_data' in entity:
                dataentities.append(entity)
            else:
                nondataentites.append(entity)
        return dataentities, nondataentites

    def add_data_entities(self, dataentities: Union[HKDataNode, List[HKDataNode]], transaction: Optional[HKTransaction]=None) -> None:
        """ Add entities with raw data to repository.

        Parameters
        ----------
        entities : (Union[HKDataNode, List[HKDataNode]]) data node or list of data nodes
        transaction : (Optional[HKTransaction]) connection transaction
        """

        url = f'{self.base._repository_uri}/{self.name}/entity/'

        if not dataentities:
            return

        if not isinstance(dataentities, (list,tuple)):
            dataentities = [dataentities]

        if isinstance(dataentities[0], HKEntity):
            dataentities = [x.to_dict() for x in entities]
        elif isinstance(dataentities[0], dict):
            pass
        else:
            raise ValueError

        files = {}
        data = {}
        for entity in dataentities:
            file = entity.pop('raw_data')
            files[entity['id']] = (entity['id'], file, entity['properties']['mimeType'])
            data[entity['id']] = json.dumps(entity)

        response = requests.put(url=url, data=data, files=files)
        response_validator(response=response)


    def filter_entities(self, filter_: Union[str, Dict], bring_raw_data: Optional[bool]=False) -> List[HKEntity]:
        """ Get entities filtered by a css filter or json filter.

        Parameters
        ----------
        filter_ : (Union[str, Dict]) retrieval filter
        bring_raw_data: Optional[bool] flag to define whether raw data should be fetched or not

        Returns
        -------
        (List[HKEntity]) list of retrieved entities
        """

        url = f'{self.base._repository_uri}/{self.name}/entity/filter'

        try:
            if isinstance(filter_, str):
                tmp_headers = copy.deepcopy(self._headers)
                tmp_headers['Content-Type'] = 'text/plain'
                response = requests.post(url=url, data=filter_, headers=tmp_headers, params={})
            elif isinstance(filter_, dict):
                response = requests.post(url=url, data=json.dumps(filter_), headers=self._headers)
            elif isinstance(filter_, list):
                def check_list(the_filter, depth=0):
                    max_depth = 2
                    if depth <= max_depth:
                        if isinstance(the_filter, str):
                            return True
                        elif isinstance(the_filter, dict):
                            return True
                        elif isinstance(the_filter, list):
                            if all([check_list(i, depth+1) for i in the_filter]):
                                return True
                    raise HKpyError(message='Invalid filter type.')

                check_list(filter_)
                response = requests.post(url=url, data=json.dumps(filter_), headers=self._headers)
            else:
                raise HKpyError(message='Invalid filter type.')

            _, data = response_validator(response=response)
        except (HKBError, HKpyError) as err:
            raise err
        except Exception as err:
            raise HKBError(message='Could not retrieve the entities.', error=err)

        entities = [hkfy(entity) for entity in data.values()]
        if bring_raw_data:
            entities = self.retrieve_raw_data_from_data_entities(entities)

        return entities

    def get_entities(self, ids: List[Union[str, Dict]], bring_raw_data: Optional[bool]=False) -> List[HKEntity]:
        """ Get entities by an array of ids, where the id can be a string or an object containing remote information of
         virtual entities.

        Parameters
        ----------
        ids : List[Union[str, Dict]] entities identifiers
        bring_raw_data: Optional[bool] flag to define whether raw data should be fetched or not

        Returns
        -------
        (List[HKEntity]) list of retrieved entities
        """
        url = f'{self.base._repository_uri}/{self.name}/entity'

        try:
            if isinstance(ids, list):
                response = requests.post(url=url, data=json.dumps(ids), headers=self._headers)
            else:
                raise HKpyError(message='Invalid id type .')

            _, data = response_validator(response=response)
        except (HKBError, HKpyError) as err:
            raise err
        except Exception as err:
            raise HKBError(message='Could not retrieve the entities.', error=err)

        entities = [hkfy(entity) for entity in data.values()]
        if bring_raw_data:
            entities = self.retrieve_raw_data_from_data_entities(entities)

        return entities

    def retrieve_raw_data_from_data_entities(self, entities: List[HKEntity]) -> List[HKEntity]:
        """ Retrive data from storage from data entities

        Obs.: This is probably temporary. Probably the data will come from hkbase directly

        Parameters
        ----------
        ids : List[HKEntity] entities

        Returns
        -------
        (List[HKEntity]) list of data entities filled with their raw data
        """

        for i in range(len(entities)):
            if 'mimeType' in entities[i].properties:
                raw_data = self.get_object(entities[i].id_)
                entities[i] = HKDataNode(raw_data, id_=entities[i].id_, parent=entities[i].parent, properties=entities[i].properties, metaproperties=entities[i].metaproperties)

        return entities

    def delete_entities(self, ids: Optional[Union[str, List[str], HKEntity, List[HKEntity]]] = None, transaction: Optional[HKTransaction]=None) -> None:
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

        if 'as_hk' in options and options['as_hk'] == True:
            entities = json.loads(fd)
            entities = list(map(hkfy, entities.values()))
            self.add_entities(list(entities))

        else:
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

        tmp_headers = copy.copy(self._headers)
        tmp_headers.update({
            'Content-Type': 'text/plain'
        })

        url = f'{self.base._repository_uri}/{self.name}/entity'

        response = requests.delete(url=url, data='*', headers=tmp_headers)
        response_validator(response)

    def hyql(self, query: str, transitivity: Optional[bool] = False) -> HKEntityResultSet:
        """ Performs a HyQL query on the repository and retrive its results.

        Parameters
        ----------
        query : (str) the HyQL query
        transitivity: (Optional[bool]): Hierarchical links will be evaluated as transitive

        Returns
        -------
        HKEntityResultSet: A result set containing HKEntity objects
        """

        url = f'{self.base._repository_uri}/{self.name}/query/'

        headers = copy.deepcopy(self._headers)
        headers['Content-Type'] = 'text/plain'

        params = {}

        if transitivity:
            params['transitivity'] = 'true'

        response = requests.post(url=url, data=query, params=params, headers=headers)
        _, data = response_validator(response=response)

        return self._build_hyql_result(data)

    def sparql(self, query: str, reasoning: Optional[bool] = None, by_pass: Optional[bool] = None) -> SPARQLResultSet:
        url = f'{self.base._repository_uri}/{self.name}/sparql/'

        headers = copy.deepcopy(self._headers)
        headers['Content-Type'] = 'text/plain'

        params = {}

        if reasoning is not None:
            params['reasoning'] = 'true' if reasoning else 'false'

        if by_pass is not None:
            params['bypass'] = 'true' if by_pass else 'false'

        response = requests.post(url=url, data=query, params=params, headers=headers)
        _, data = response_validator(response=response)

        return self._build_sparql_result(data)

    def list_objects(self) -> List[str]:
        """
        """

        url = f'{self.base._repository_uri}/{self.name}/storage'

        response = requests.get(url=url, headers=self._headers)
        _, data = response_validator(response=response)

        return data

    def add_object(self, object_: [str, TextIOWrapper, BufferedReader, BufferedIOBase], mimetype: str,
                   id_: Optional[str] = None) -> str:
        """
        """

        url = f'{self.base._repository_uri}/{self.name}/storage/object'

        if id_ is not None:
            url = f'{url}/{urllib.parse.quote_plus(id_)}'

        if isinstance(object_, (TextIOWrapper, BufferedReader, BufferedIOBase)):
            object_ = object_.read()
        elif isinstance(object_, str) and os.path.isfile(object_):
            with open(object_ ,'rb') as f:
                object_ = f.read()
        elif isinstance(object_, str):
            pass # do nothing
        elif isinstance(object_, bytes):
            pass # do nothing
        else:
            raise HKpyError(message='Object not valid.')

        headers = copy.deepcopy(self._headers)
        headers['Content-Type'] = mimetype

        response = requests.put(url=url, data=object_, headers=headers)
        _, data = response_validator(response=response)

        return data['objectId'] if 'objectId' in data else data

    def delete_object(self, id_: str) -> None:
        """
        """

        url = f'{self.base._repository_uri}/{self.name}/storage/object/{urllib.parse.quote_plus(id_)}'

        response = requests.delete(url=url, headers=self._headers)
        response_validator(response=response)

    def get_object(self, id_: str) -> bytes:
        """
        """

        url = f'{self.base._repository_uri}/{self.name}/storage/object/{urllib.parse.quote_plus(id_)}'

        response = requests.get(url=url, headers=self._headers)
        _, data = response_validator(response=response, content='.')

        return data

    def get_all_stored_queries(self, transaction_id: Optional[str] = None) -> List[HKStoredQuery]:
        url = f'{self.base._repository_uri}/{self.name}/stored-query'

        headers = {**self._headers,
                   "Content-type": "application/json"}

        if transaction_id is not None:
            headers['transactionId'] = transaction_id

        response = requests.get(url=url, headers=headers)
        _, data = response_validator(response=response)

        return [HKStoredQuery.from_dict(q) for q in data]

    def get_stored_query(self, query_id: str, transaction_id: Optional[str] = None) -> HKStoredQuery:
        url = f'{self.base._repository_uri}/{self.name}/stored-query/{query_id}'

        headers = {**self._headers,
                   "Content-type": "application/json"}

        if transaction_id is not None:
            headers['transactionId'] = transaction_id

        response = requests.get(url=url, headers=headers)
        _, data = response_validator(response=response)

        return HKStoredQuery.from_dict(data)

    def deleted_stored_query(self, query_id: str, transaction_id: Optional[str] = None) -> HKStoredQuery:
        url = f'{self.base._repository_uri}/{self.name}/stored-query/{query_id}'

        headers = {**self._headers,
                   "Content-type": "application/json"}

        if transaction_id is not None:
            headers['transactionId'] = transaction_id

        response = requests.delete(url=url, headers=headers)
        _, data = response_validator(response=response)

        return HKStoredQuery.from_dict(data)

    def store_query(self, stored_query: Union[Dict, HKStoredQuery],
                    transaction_id: Optional[str] = None) -> HKStoredQuery:
        url = f'{self.base._repository_uri}/{self.name}/stored-query'

        if isinstance(stored_query, HKStoredQuery):
            stored_query = stored_query.to_dict()
        elif not isinstance(stored_query, dict):
            raise HKpyError(f"Trying to store query object of unknown type {type(stored_query)}")

        headers = {**self._headers,
                   "Content-type": "application/json"}

        if transaction_id is not None:
            headers['transactionId'] = transaction_id

        response = requests.post(url=url, headers=headers, json=stored_query)
        _, data = response_validator(response=response)

        return HKStoredQuery.from_dict(data)

    def run_stored_query(self, query_id: str, parameters: Optional[Dict[str, Union[str, float, int]]] = None,
                         run_options: Optional[Dict] = None, transaction_id: Optional[str] = None,
                         mime_type: Optional[str] = None, proxy: Optional[bool] = False) -> Union[HKEntityResultSet,
                                                                                                  SPARQLResultSet]:
        run_configuration = dict()
        if parameters is not None:
            run_configuration['parameters'] = parameters
        if run_options is not None:
            run_configuration['options'] = run_options

        if mime_type is not None:
            options = run_configuration.get('options', {})
            options['mimeType'] = mime_type

        headers = {**self._headers, "Content-type": "application/json"}

        if transaction_id is not None:
            headers['transactionId'] = transaction_id

        url = f'{self.base._repository_uri}/{self.name}/stored-query/{query_id}/run'

        response = requests.post(url=url, json=run_configuration, headers=headers)
        _, data = response_validator(response=response)
        if proxy:
            return data
        try:
            return self._build_hyql_result(data)
        except HKpyError as e:
            return self._build_sparql_result(data)

    def _build_hyql_result(self, data: Union[List[dict], List[List[dict]], List[Any]]) -> HKEntityResultSet:
        # validate if data is of the correct type
        if not isinstance(data, list):
            raise HKpyError(f'The given data is not of the expected format')

        row_matrix = list()
        for entry in data:
            if isinstance(entry, dict):
                entry = [entry]
            if isinstance(entry, list):
                row = []
                for e in entry:
                    if isinstance(e, dict):
                        row.append(hkfy(e))
                    else:
                        row.append(e)
            else:
                row = entry
            row_matrix.append(row)

        return HKEntityResultSet.build(row_matrix=row_matrix)

    def _build_sparql_result(self, data) -> Union[SPARQLResultSet, bool]:
        if 'head' in data and 'boolean' in data:
            return data['boolean']
        # validate if data is of the correct format
        if not ('results' in data and 'bindings' in data['results'] and 'head' in data):
            raise HKpyError(f'The given data is not of the expected format')
        return SPARQLResultSet(data)

    def resolve_fi(self, fi: FI, raw: bool = False, output_mimetype: bool = False) -> Union[HKEntity, Tuple[Any, str]]:
        """
        Resolve a full FI. Set raw to True in order to get raw output. Otherwise the function will try to
        interpret the response (i.e. into hk objects)
        """
        quoted_fi = quote(fi.__str__(), safe="");
        url = f'{self.base._repository_uri}/{self.name}/fi/{quoted_fi}'

        response = requests.get(url=url, headers=self._headers)
        _, data = response_validator(response=response, content='.')

        content_type = response.headers['Content-Type']
        if raw:
            if output_mimetype:
                return data, content_type
            else:
                return data

        # some extra response data converter
        if content_type.startswith('hyperknowledge/graph'):
            return hkfy(response.json())
        elif content_type.startswith('hyperknowledge/node'):
            return hkfy(response.json())
        elif content_type.startswith('text'):
            return response.content.decode()
        else:
            return data

    def persist_fi(self, fi):

        quoted_fi = quote(fi.__str__(), safe="");
        url = f'{self.base._repository_uri}/{self.name}/fi/{quoted_fi}'

        response = requests.put(url=url, headers=self._headers)
        response_validator(response=response)