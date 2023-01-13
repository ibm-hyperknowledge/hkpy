###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Optional, Union, List, Dict

import json

from hkpy.utils import HKType
from . import constants

__all__ = ['HKEntity']

class HKEntity(object):
    """
    """

    def __init__(self,
                 type_: Union[constants.HKType, constants.AnchorType],
                 id_: str,
                 properties: Optional[Dict] = {},
                 metaproperties: Optional[Dict] = {}) -> None:
        """ Initialize an instance of HKAnchor class.
    
        Parameters
        ----------
        type_: (Union[constants.HKType, constants.AnchorType]) the entity's type
        id_: (str) the entity's unique id
        properties: (Optional[Dict]) any entity's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """

        self.type_ = type_
        self.id_ = id_
        self.properties = {} if properties is None else properties
        self.metaproperties = {} if metaproperties is None else metaproperties

    def __repr__(self):
        return f'{super().__repr__()}: {self.id_}'
    
    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

    def add_properties(self, **kwargs) -> None:
        """ Add properties in the HKEntity.

        Parameters
        ----------
        kwargs : keyword argument as property and property's value
        """

        if len(kwargs.keys()) == 1 and 'properties' in kwargs:
            self.properties.update(kwargs['properties'])
        else:
            self.properties.update(kwargs)

    def set_property(self, property, value):
        self.properties[property] = value

    def get_property(self, key):
        return self.properties.get(key)

    def has_property(self, key):
        return key in self.properties

    def add_metaproperties(self, **kwargs) -> None:
        """ Add metaproperties in the HKEntity.

        Parameters
        ----------
        kwargs : keyword argument as metaproperty and metaproperty's value
        """

        if len(kwargs.keys()) == 1 and 'metaproperties' in kwargs:
            self.metaproperties.update(kwargs['metaProperties'])
        else:
            self.metaproperties.update(kwargs)

    def to_dict(self) -> Dict:
        """ Convert a HKEntity to a dict.

        Returns
        -------
        (Dict) The HKEntity's correspondent dict
        """

        jobj = {}
        
        jobj['id'] = self.id_
        jobj['type'] = self.type_.value if isinstance(self.type_, HKType) else self.type_
        jobj['properties'] = self.properties
        jobj['metaProperties'] = self.metaproperties

        return jobj

class HKParentedEntity(HKEntity):

    def __init__(self,
                 type_: Union[constants.HKType, constants.AnchorType],
                 id_: str,
                 parent: Optional[str]=None,
                 properties: Optional[Dict] = {},
                 metaproperties: Optional[Dict] = {}):
        from hkpy.hklib import HKContext

        super().__init__(type_, id_, properties=properties, metaproperties=metaproperties)
        self.parent = parent

    def to_dict(self) -> Dict:
        jobj = super().to_dict()

        jobj['parent'] = self.parent

        return jobj