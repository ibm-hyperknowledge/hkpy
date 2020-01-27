###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Union, List, Dict

import time

from ..oops import HKpyError

from . import generate_id
from . import HKEntity, HKContext
from . import constants
from . import hkfy

__all__ = ['HKGraph']

class HKGraph(object):

    def __init__(self):
        self.nodes = {}
        self.contexts = {}
        self.links = {}
        self.connectors = {}
        self.references = {}
        # self.trails = {}

        self.binds = {}
        self._connector_links_map = {}
        self.reference_entity_map = {}
        self._context_entities_map = {}
        # self.orphans = {}
        # self.relationless = {}

    def get_entity(self, id_):
        """
        """

        for set_ in [self.nodes, self.contexts, self.links, self.connectors, self.references]:
            if id_ in set_:
                return set_[id_]

        return None

    def add_entities(self, entities: Union[Dict, List[Dict], HKEntity, List[HKEntity]]) -> List[HKEntity]:
        """ Add an entity to the Hyperknowledge graph.

        Parameters
        ----------
        entities : Union[Dict, List[Dict], HKEntity, List[HKEntity]] the Hyperknowledge entities.

        Returns
        -------
        List of Hyperknowledge entities.
        """

        added_entities = []

        if not isinstance(entities, (tuple, list)):
            entities = [entities]
            
        for entity in entities:
            entity = entity if isinstance(entity, HKEntity) else hkfy(entity)

            if entity.type_ == constants.HKType.NODE:
                self.nodes[entity.id_] = entity

            elif entity.type_ == constants.HKType.CONTEXT:
                self.contexts[entity.id_] = entity

            elif entity.type_ == constants.HKType.LINK:
                
                if entity.id_ == None:
                    entity.id_ = generate_id(entity=entity)

                self.links[entity.id_] = entity
                
                if entity.connector not in self._connector_links_map:
                    self._connector_links_map[entity.connector] = {}
                self._connector_links_map[entity.connector][entity.id_] = entity

                for binds in entity.binds.values():
                    for bind in binds.keys():
                        if bind in self.binds:
                            if entity.id_ not in self.binds[bind]:
                                self.binds[bind][entity.id_] = entity
                        else:
                            self.binds[bind] = {entity.id_: entity}

            elif entity.type_ == constants.HKType.CONNECTOR:
                self.connectors[entity.id_] = entity

            elif entity.type_ == constants.HKType.REFERENCENODE:
                
                if entity.id_ == None:
                    entity.id_ = generate_id(entity=entity)
                
                self.references[entity.id_] = entity

                if entity.id_ not in self.reference_entity_map:
                    self.reference_entity_map[entity.id_] = {}
                self.reference_entity_map[entity.id_][entity.ref] = self.nodes[entity.ref]

            else:
                raise HKpyError(message='Invalid entity type.')

            added_entities.append(entity)
            
            # set context
            if hasattr(entity, 'parent'):
                if entity.parent != None:
                    if entity.parent not in self.contexts:
                        added_entities.append(self.add_entities(HKContext(id_=entity.parent)))
                    if entity.parent not in self._context_entities_map:
                        self._context_entities_map[entity.parent] = {}
                    self._context_entities_map[entity.parent][entity.id_] = entity

        return added_entities

    def remove_entities(self, ids: Union[str, List[str], HKEntity, List[HKEntity]]) -> None:
        """
        """

        def _remove_links(ids):
            for id_ in ids:
                del self.links[id_]

            for bind, lks in self.binds.items():
                for id_ in ids:
                    if id_ in lks:
                        del self.binds[bind][id_]

            for cnt, lks in self._connector_links_map.items():
                for id_ in ids:
                    if id_ in lks:
                        del self._connector_links_map[cnt][id_]

        if not isinstance(ids, (tuple, list)):
            ids = [ids]

        if isinstance(ids[0], HKEntity):
            ids = [x.id_ for x in ids]

        for id_ in ids:
            entity = self.get_entity(id_=id_)
            
            if entity is None:
                continue

            if entity.type_ in [constants.HKType.NODE, constants.HKType.CONTEXT, constants.HKType.REFERENCENODE]:

                # remove links
                if entity.id_ in self.binds:
                    to_delete = []
                    for lk in self.binds[entity.id_].keys():
                        to_delete.append(lk)

                    _remove_links(ids=to_delete)

                # remove node
                if entity.type_ == constants.HKType.NODE:
                    del self.nodes[entity.id_]
                elif entity.type_ == constants.HKType.CONTEXT:
                    for e in self._context_entities_map[entity.id_].keys():
                        self.remove_entities(e)
                    del self.contexts[entity.id_]
                    del self._context_entities_map[entity.id_]
                else:
                    del self.references[entity.id_]
                    del self.reference_entity_map[entity.id_]

            elif entity.type_ == constants.HKType.LINK:
                
                # remove links
                _remove_links(ids=[entity.id_])

            elif entity.type_ == constants.HKType.CONNECTOR:
                
                # remove links
                to_delete = self._connector_links_map[entity.id_].keys()
                del self._connector_links_map[entity.id_]
                _remove_links(ids=to_delete)

                del self.connectors[entity.id_]

            else:
                raise HKpyError(message='Entity of unkwown type.')

    def to_graph(self, data: Union[Dict, List[HKEntity]]) -> None:
        """ Convert a set of entities to a HKGraph instance.

        Parameters
        ----------
        data : (Union[Dict, List[HKEntity]]) a  dictonary of entities or list of entities
        """

        if isinstance(data, dict):
            for id_ in data.keys():
                self.add_entities(data[id_])
        elif isinstance(data, list):
            for entity in data:
                self.add_entities(entity)
        else:
            raise HKpyError(message='Invalid input format.')
        
    def __str__(self):
        return str(self.__dict__)