###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Optional, Dict

from . import HKEntity
from . import constants

__all__ = ['HKAnchor']

class HKAnchor(HKEntity):
    """
    """

    def __init__(self,
                 type_: constants.AnchorType,
                 id_: str,
                 properties: Optional[Dict]=None,
                 metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKAnchor class.
    
        Parameters
        ----------
        type_: (constants.AnchorType) the anchor's type
        id_: (str) the anchor's unique id
        properties: (Optional[Dict]) any anchor's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """

        super().__init__(type_=type_, id_=id_, properties=properties, metaproperties=properties)
