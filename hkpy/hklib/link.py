###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Union, Optional, Dict, List, TypeVar

from . import constants
from . import HKEntity
from . import HKParentedEntity
from . import HKAnchor
from . import HKConnector

__all__ = ['HKLink']

HKAnyNode = TypeVar('HKAnyNode')
HKContext = TypeVar('HKContext')

class HKLink(HKParentedEntity):
    """
    """
    
    def __init__(self,
                 connector: Union[str, HKConnector],
                 id_: Optional[str]=None,
                 parent: Optional[Union[str, HKContext]]=None,
                 properties: Optional[Dict]=None,
                 metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKLink class.
    
        Parameters
        ----------
        connector: (Union[str, HKConnector]) the connector associated to the link
        id_: (Optional[str]) the link's unique id
        parent: (Optional[Union[str, HKContext]]) the context in which the link is setted
        properties: (Optional[Dict]) any link's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """

        super().__init__(type_=constants.HKType.LINK, id_=id_, parent = parent, properties=properties, metaproperties=metaproperties)
        self.connector = connector
        self.binds = {}

    def add_bind(self, role: str, entity: Union[str, HKAnyNode], anchor: Optional[Union[str, HKAnchor]]=None) -> None:
        """ Add a bind to the link. If bind already exists, set list

        Parameters
        ----------
        role : (str) the entity's role in the link
        entity: (Union[str, HKAnyNode]) the entity related in the link
        anchor: (Optional[Union[str, HKAnchor]]) the entity's anchor associated in the bind
        """

        #TODO change: if we had access to the underlaying graph, we could retrieve the correct HKNode here
        if isinstance(entity, str): raise Exception('Ids not allowed')

        anchor = anchor if anchor is not None else constants.LAMBDA
        anchor = anchor.key if anchor is not None and isinstance(anchor, HKAnchor) else anchor

        #binds {role: {entity_id : {'entity': entity-object, 'anchor': [anchor]}
        if role in self.binds:
            if entity.id_ in self.binds[role]:
                #entity already binded, add anchor
                self.binds[role][entity.id_]['anchors'].append(anchor)
            else:
                self.binds[role][entity.id_] = {'entity': entity, 'anchors': [anchor]}
        else:
            self.binds[role] = {entity.id_: {'entity': entity, 'anchors': [anchor]}}



    #TODO: Fix to bind format
    def add_binds(self, binds: List[Dict]) -> None:
        """ Add binds to the link.

        Parameters
        ----------
        binds: (List[Dict]) the entity related in the link
        """

        if not isinstance(binds, (tuple, list)):
            binds = [binds]

        for bind in binds:
            for k,v in bind.items():
                self.binds[k] = v

    #TODO: REMOVE
    def get_bind_values_no_anchor(self, role: str) -> List[HKEntity]:
        """
        """
        
        if not self.binds[role]:
            return []

        result = []
        for nid, entity_and_anchor in self.binds[role].items():
            result.append(entity_and_anchor['entity'])

        return result

    #TODO: REMOVE
    def get_bind_value_no_anchor(self, role: str) -> List[HKEntity]:
        """ return first value
        """
        if not self.binds[role]:
            return None

        return self.get_bind_values_no_anchor(role)[0]

    #TODO: REMOVE
    def get_bind_anchor(self, role: str) -> str:
        """
        """

        return self.binds[role]

    def to_dict(self, buffer) -> Dict:
        """ Convert a HKEntity to a dict.

        Returns
        -------
        (Dict) The HKEntity's correspondent dict
        """

        jobj = super().to_dict(buffer)

        jobj['connector'] = self.connector

        jobj['binds'] = {}
        for role, values in self.binds.items():
            for entity_id, bind in values.items():
                if role not in jobj['binds']: jobj['binds'][role] = {}
                if entity_id not in buffer:
                    #convert (should not be recursive if not linking links)
                    bind['entity'].to_dict(buffer)
                jobj['binds'][role][entity_id] = bind['anchors']

        buffer[self.id_] = jobj

        return jobj