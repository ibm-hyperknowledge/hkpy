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

from typing import Union, Dict

from ..utils import constants, generate_id

from .entity import HKEntity
from .connector import HKConnector
from .anchor import HKAnchor
from .node import HKNode, HKContext, HKReferenceNode
from .link import HKLink

def hkfy(entity: Union[str, Dict]) -> HKEntity:
    """ Convert an entity in string or dict format to a HKEntity object.

        Parameters
        ----------
        entity : (Union[str, Dict]) an entity in string or dict format

        Returns
        -------
        (HKEntity) The entity's correspondent HKEntity object
    """

    # TODO: check_consistency
    if isinstance(entity, HKEntity):
        return entity
        
    if isinstance(entity, dict):
        
        # _check_consistancy()
        hke = None
        if entity['type'] == constants.HKType.CONNECTOR:
            hke = HKConnector(id_=entity['id'], class_name=entity['className'], roles=entity['roles'])
        
        elif entity['type'] in ['context', 'node', 'ref']:
            if entity['type'] == constants.HKType.CONTEXT:
                hke = HKContext(id_=entity['id'], parent=entity['parent'])
            elif entity['type'] == constants.HKType.NODE:
                hke = HKNode(id_=entity['id'], parent=entity['parent'])
            elif entity['type'] == constants.HKType.REFERENCENODE:
                ref = entity['ref'] if 'ref' in entity else None
                hke = HKReferenceNode(id_=entity['id'], ref=ref, parent=entity['parent'])       
            if 'interfaces' in entity:
                hke.interfaces = entity['interfaces']

        elif entity['type'] == 'link':
            hke = HKLink(connector=entity['connector'], id_=entity['id'], binds=entity['binds'], parent=entity['parent'])

        if 'properties' in entity:
            hke.add_properties(properties=entity['properties'])
        if 'metaproperties' in entity:
            hke.add_properties(properties=entity['metaproperties'])

        return hke

    # TODO: add a hkpyerror exection
    raise(Exception)


from .graph import HKGraph

__all__ = ['hkfy']