###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Optional, Dict

from . import constants

__all__ = ['HKAnchor']

class HKAnchor(object):
    """
    """

    def __init__(self,
                 key: str,
                 type_: constants.AnchorType,
                 properties: Optional[Dict]=None,
                 metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKAnchor class.
    
        Parameters
        ----------
        key: (str) the anchor's unique key
        type_: (constants.AnchorType) the anchor's type
        properties: (Optional[Dict]) any anchor's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """

        self.key = key
        self.type_ = type_
        self.properties = {} if properties is None else properties
        self.metaproperties = {} if metaproperties is None else metaproperties

    def add_properties(self, **kwargs) -> None:
        """ Add properties in the HKAnchor.

        Parameters
        ----------
        kwargs : keyword argument as property and property's value
        """

        if len(kwargs.keys()) == 1 and 'properties' in kwargs:
            self.properties.update(kwargs['properties'])
        else:
            self.properties.update(kwargs)

    def add_metaproperties(self, **kwargs) -> None:
        """ Add metaproperties in the HKAnchor.

        Parameters
        ----------
        kwargs : keyword argument as metaproperty and metaproperty's value
        """

        if len(kwargs.keys()) == 1 and 'metaproperties' in kwargs:
            self.metaproperties.update(kwargs['metaProperties'])
        else:
            self.metaproperties.update(kwargs)