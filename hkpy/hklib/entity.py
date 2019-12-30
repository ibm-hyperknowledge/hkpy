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

from typing import Optional, Union, List, Dict

import json
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
        for k, v in self.__dict__.items():
            if (not v and k not in ['parent', 'children']):
                continue
            if (k == 'id_'):
                jobj['id'] = v
            elif (k == 'type_'):
                jobj['type'] = v.value
            elif (k == 'class_name'):
                jobj['className'] = v
            elif (k == 'metaproperties'):
                jobj['metaProperties'] = v
            else:
                jobj[k] = v

        jobj['properties'] = jobj['properties'] if 'properties' in jobj else {}
        jobj['metaProperties'] = jobj['metaProperties'] if 'metaProperties' in jobj else {}

        return jobj