###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Union, Dict

from ..utils import constants, generate_id

from .anchor import HKAnchor
from .entity import HKEntity, HKParentedEntity
from .connector import HKConnector
from .link import HKLink
from .node import HKAnyNode, HKNode, HKContext, HKReferenceNode, HKTrail

def hkfy(entities: [Dict]) -> [HKEntity]:
    """ Convert an entity in string or dict format to a HKEntity object.

    Parameters
    ----------
    entity : (Union[str, Dict]) an entity in string or dict format

    Returns
    -------
    (HKEntity) The entity's correspondent HKEntity object
    """

    # TODO: check_consistency
    if isinstance(entities, HKEntity):
        return entities

    # TODO: add a hkpyerror exection
    #if not isinstance(entities, [dict]): raise (Exception)


    # _check_consistency()

    #process non-links first
    nodes_buffer = {}
    for entity in entities:
        if not isinstance(entity, dict): raise Exception("Wrong json format.")
        if entity['type'] == constants.HKType.LINK: continue


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

        elif entity['type'] == constants.HKType.ANCHOR:
            raise NotImplementedError

        if 'properties' in entity:
            hke.add_properties(properties=entity['properties'])
        if 'metaproperties' in entity:
            hke.add_properties(properties=entity['metaproperties'])

        nodes_buffer[hke.id_] = hke

    links_buffer = []
    for entity in entities:
        if entity['type'] != constants.HKType.LINK: continue

        hke = HKLink(connector=entity['connector'], id_=entity['id'], parent=entity['parent'])

        if 'binds'in entity:
            for role, nodes in entity['binds'].items():
                for id_, anchors in nodes.items():
                    for anchor in anchors:
                        if id_ in nodes_buffer:
                            binded_node = nodes_buffer[id_]
                        else:
                            #TODO: weak instantiation of node using only id
                            binded_node = HKNode(id_=id_)
                            nodes_buffer[binded_node.id_] = binded_node
                        hke.add_bind(role, binded_node, anchor)

        if 'properties' in entity:
            hke.add_properties(properties=entity['properties'])
        if 'metaproperties' in entity:
            hke.add_properties(properties=entity['metaproperties'])

        links_buffer.append(hke)

    return list(nodes_buffer.values()) + links_buffer




from .graph import HKGraph

__all__ = ['hkfy']