###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Union, Dict

from ..utils import constants, generate_id

from .anchor import HKAnchor
from .entity import HKEntity
from .connector import HKConnector
from .link import HKLink
from .node import HKNode, HKContext, HKReferenceNode, HKTrail, HKAnyNode, HKDataNode
from .graphbuilder import HKGraphBuilder

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
                hke = HKContext(id_=entity['id'], parent=entity.get('parent'))
            elif entity['type'] == constants.HKType.NODE:
                hke = HKNode(id_=entity['id'], parent=entity.get('parent'))
            elif entity['type'] == constants.HKType.REFERENCENODE:
                ref = entity['ref'] if 'ref' in entity else None
                hke = HKReferenceNode(id_=entity['id'], ref=ref, parent=entity.get('parent'))
            if 'interfaces' in entity:
                hke.interfaces = entity['interfaces']

        elif entity['type'] == constants.HKType.LINK:
            hke = HKLink(connector=entity['connector'], id_=entity['id'], binds=entity['binds'], parent=entity.get('parent'))

        elif entity['type'] == constants.HKType.ANCHOR:
            raise NotImplementedError
        elif entity['type'] == constants.HKType.GRAPH:
            hke = HKGraph()
            entities = []
            for entity_type, graph_entity in entity.items():
                if entity_type != 'type':
                    for eid, e in graph_entity.items():
                        entities.append(hkfy(e))
            hke.add_entities(entities)
        
        if 'properties' in entity:
            hke.add_properties(properties=entity['properties'])
        if 'metaproperties' in entity:
            hke.add_properties(properties=entity['metaproperties'])

        return hke

    # TODO: add a hkpyerror exection
    raise(Exception)


from .graph import HKGraph

__all__ = ['hkfy']