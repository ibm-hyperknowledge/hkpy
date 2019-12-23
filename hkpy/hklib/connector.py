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

from typing import Optional, Dict

from . import HKEntity
from . import constants

__all__ = ['HKConnector']

class HKConnector(HKEntity):
    def __init__(self,
                 id_: str,
                 class_name: str,
                 roles: Optional[Dict]=None,
                 properties: Optional[Dict]=None,
                 metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKConnector class.
    
        Parameters
        ----------
        id_: (str) the connector's unique id
        class_name: (str) the connector's class
        roles: (Optional[Dict]) each role of the connector
        properties: (Optional[Dict]) any connector's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """

        super().__init__(type_=constants.HKType.CONNECTOR, id_=id_, properties=properties, metaproperties=metaproperties)
        self.class_name = class_name
        self.roles = {} if roles is None else roles

    def add_roles(self, roles: Dict) -> None:
        """ Add roles to the connector.

        Parameters
        ----------
        roles : (Dict) dictionary of roles and roles' abbreviations
        """
        
        if not isinstance(roles, (tuple, list)):
            roles = [roles]
        
        for r in roles:
            self.roles.update(r)