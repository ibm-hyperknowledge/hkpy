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

from typing import Dict, List

import time

from ..utils import HKType
from ..oops import HKpyError

from . import generate_id
from . import HKEntity
from . import HKContext
from . import HKConnector
from . import HKNode
from . import HKLink
from . import HKReferenceNode

__all__ = ['HKGraph']

class HKGraph(object):

    def __init__(self):
        self.HKNodes = {}
        self.HKContexts = {}
        self.HKLinks = {}
        self.HKConnectors = {}
        self.HKReferences = {}
        # self.trails = {}

        self.binds = {}
        self._HKConnector_HKLinks_map = {}
        self._HKReference_entity_map = {}
        self._HKContext_entities_map = {}
        # self.orphans = {}
        # self.relationless = {}

    def _dict2hk(self, entity):
        def _is_consistency(entity):
            return 'type' in entity
        
        def _fill_entity(entity):
            if 'id' not in entity:
                entity['id'] = generate_id(entity=entity)
            if 'parent' not in entity:
                entity['parent'] = None
            if 'properties' not in entity:
                entity['properties'] = {}
            if 'className' not in entity:
                entity['className'] = None
            if 'binds' not in entity:
                entity['binds'] = {}
            if 'ref' not in entity:
                entity['ref'] = None
            
            return entity

        if type(entity) is not dict or not _is_consistency(entity):
            raise HKpyError(message='Invalid entity.')

        entity = _fill_entity(entity)

        if entity['type'] == HKType.HKNode:      
            return HKNode(id_=entity['id'], parent=entity['parent'], properties=entity['properties'])

        elif entity['type'] == HKType.HKContext:
            return HKContext(id_=entity['id'], parent=entity['parent'], properties=entity['properties'])
            
        elif entity['type'] == HKType.HKLink:
            return HKLink(HKConnector=entity['HKConnector'], id_=entity['id'], binds=entity['binds'], parent=entity['parent'])
                
        elif entity['type'] == HKType.HKConnector:
            return HKConnector(id_=entity['id'], class_name=entity['className'])

        elif entity['type'] == HKType.REFERENCENODE:
            return HKReferenceNode(HKReference=entity['ref'], id_=entity['id'], parent=entity['parent'], properties=entity['properties'])
        
        else:
            raise HKpyError(message='Invalid entity type.')

    def get_entity(self, id_):
        for set_ in [self.HKNodes, self.HKContexts, self.HKLinks, self.HKConnectors, self.HKReferences]:
            if id_ in set_:
                return set_[id_]

        return None

    def add_entity(self, entity: [Dict, HKEntity]) -> List[HKEntity]:
        """ Add an entity to the Hyperknowledge graph.

        Parameters
        ----------
        entity : ([Dict, HKEntity]) the Hyperknowledge entity.

        Returns
        -------
        List of Hyperknowledge entities.
        """

        added_entities = []
        entity = entity if isinstance(entity, HKEntity) else self._dict2hk(entity)

        if entity.type_ == HKType.HKNode:
            self.HKNodes[entity.id_] = entity

        elif entity.type_ == HKType.HKContext:
            self.HKContexts[entity.id_] = entity

        elif entity.type_ == HKType.HKLink:
            
            if entity.id_ == None:
                entity.id_ = generate_id(entity=entity)

            self.HKLinks[entity.id_] = entity
            
            if entity.HKConnector not in self._HKConnector_HKLinks_map:
                self._HKConnector_HKLinks_map[entity.HKConnector] = {}
            self._HKConnector_HKLinks_map[entity.HKConnector][entity.id_] = entity

            for binds in entity.binds.values():
                for bind in binds.keys():
                    if bind in self.binds:
                        if entity.id_ not in self.binds[bind]:
                            self.binds[bind][entity.id_] = entity
                    else:
                        self.binds[bind] = {entity.id_: entity}

        elif entity.type_ == HKType.HKConnector:
            self.HKConnectors[entity.id_] = entity

        elif entity.type_ == HKType.HKReference:
            
            if entity.id_ == None:
                entity.id_ = generate_id(entity=entity)
            
            self.HKReferences[entity.id_] = entity

            if entity.id_ not in self._HKReference_entity_map:
                self._HKReference_entity_map[entity.id_] = {}
            self._HKReference_entity_map[entity.id_][entity.HKReference] = self.HKNodes[entity.HKReference]

        else:
            raise HKpyError(message='Invalid entity type.')

        added_entities.append(entity)
        
        # set HKContext
        if hasattr(entity, 'parent'):
            if entity.parent != None:
                if entity.parent not in self.HKContexts:
                    added_entities.append(self.add_entity(HKContext(id_=entity.parent)))
                if entity.parent not in self._HKContext_entities_map:
                    self._HKContext_entities_map[entity.parent] = {}
                self._HKContext_entities_map[entity.parent][entity.id_] = entity

        return added_entities

    def remove_entity(self, id_):
        
        def _remove_HKLinks(ids):
            for id_ in ids:
                del self.HKLinks[id_]

            for bind, lks in self.binds.items():
                for id_ in ids:
                    if id_ in lks:
                        del self.binds[bind][id_]

            for cnt, lks in self._HKConnector_HKLinks_map.items():
                for id_ in ids:
                    if id_ in lks:
                        del self._HKConnector_HKLinks_map[cnt][id_]

        entity = self.get_entity(id_=id_)
        
        if entity == None:
            return

        if entity.type_ == HKType.HKNode or entity.type_ == HKType.HKContext or entity.type_ == HKType.HKReference:

            # remove HKLinks
            if entity.id_ in self.binds:
                to_delete = []
                for lk in self.binds[entity.id_].keys():
                    to_delete.append(lk)

                _remove_HKLinks(ids=to_delete)

            # remove HKNode
            if entity.type_ == HKType.HKNode:
                del self.HKNodes[entity.id_]
            elif entity.type_ == HKType.HKContext:
                for e in self._HKContext_entities_map[entity.id_].keys():
                    self.remove_entity(e)
                del self.HKContexts[entity.id_]
                del self._HKContext_entities_map[entity.id_]
            else:
                del self.HKReferences[entity.id_]
                del self._HKReference_entity_map[entity.id_]

        elif entity.type_ == HKType.HKLink:
            
            # remove HKLinks
            _remove_HKLinks(ids=[entity.id_])

        elif entity.type_ == HKType.HKConnector:
            
            # remove HKLinks
            to_delete = self._HKConnector_HKLinks_map[entity.id_].keys()
            del self._HKConnector_HKLinks_map[entity.id_]
            _remove_HKLinks(ids=to_delete)

            del self.HKConnectors[entity.id_]

        else:
            return

    def to_graph(self, data: Dict) -> None:
        """ Convert a Hyperknowledge dictonary to a HKGraph instance.

        Parameters
        ----------
        data : (Dict) the Hyperknowledge dictonary
        """

        for id_ in data.keys():
            self.add_entity(data[id_])

    def __str__(self):
        return str(self.__dict__)