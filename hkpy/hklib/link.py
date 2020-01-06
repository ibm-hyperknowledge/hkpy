###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Union, Optional, Dict, List

from . import constants
from . import HKEntity, HKConnector, HKNode, HKContext, HKReferenceNode

__all__ = ['HKLink']

class HKLink(HKEntity):
    """
    """
    
    def __init__(self,
                 connector: Union[str, HKConnector],
                 id_: Optional[str]=None,
                 parent: Optional[Union[str, HKContext]]=None,
                 binds: Optional[Dict]=None,
                 properties: Optional[Dict]=None,
                 metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKLink class.
    
        Parameters
        ----------
        connector: (Union[str, HKConnector]) the connector associated to the link
        id_: (Optional[str]) the link's unique id
        parent: (Optional[Union[str, HKContext]]) the context in which the link is setted
        binds: (Optional[Dict]) the entities binded with this link
        properties: (Optional[Dict]) any link's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """

        super().__init__(type_=constants.HKType.LINK, id_=id_, properties=properties, metaproperties=metaproperties)
        self.connector = connector.id_ if isinstance(connector, HKEntity) else connector
        self.binds = {} if binds is None else binds
        self.parent = parent.id_ if isinstance(parent, HKEntity) else parent
    
    def add_bind(self, role: str, entity: Union[str, HKNode, HKContext, HKReferenceNode]) -> None:
        """ Add a bind to the link.

        Parameters
        ----------
        role : (str) the entity's role in the link
        entity: (Union[str, HKNode, HKContext, HKReferenceNode]) the entity related in the link
        """

        bind = {entity[0] : [entity[1]]} if(type(entity) is tuple) else {entity : [constants.LAMBDA]}
        if role in self.binds:
            self.binds[role].update(bind)
        else:
            self.binds[role] = bind

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
    def get_bind_values_no_anchor(self, role: str) -> List[str]:
        """
        """
        
        if not self.binds[role]:
            return []
        
        return list(self.binds[role].keys())

    #TODO: REMOVE
    def get_bind_value_no_anchor(self, role: str) -> str:
        """ return first value
        """
        if not self.binds[role]:
            return None

        return list(self.binds[role].keys())[0]

    #TODO: REMOVE
    def get_bind_anchor(self, role: str) -> str:
        """
        """

        return self.binds[role]