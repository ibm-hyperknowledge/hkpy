###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Optional, Dict, Tuple

from . import HKEntity
from . import constants

__all__ = ['HKConnector']

class HKConnector(HKEntity):
    def __init__(self,
                 id_: str,
                 class_name: constants.ConnectorType,
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

    def add_roles(self, **roles) -> None:
        """ Add roles to the connector.

        Parameters
        ----------
        **roles: keys and values, which the keys are the roles' names and the values are the roles' types
        """
        
        if 'roles' in roles:
            roles = roles['roles']
            
            if not isinstance(roles, (tuple, list)):
                roles = [roles]
            for r in roles:
                self.roles.update(r)

        else:
            for name, type_ in roles.items():
                self.roles[name] = type_