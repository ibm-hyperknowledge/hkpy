###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from hkpy.hklib import HKReferenceNode, HKContext, HKNode, HKEntity
from hkpy.hkpyo.model import HKOIndividual, HKOProperty
import urllib

encode_uri_component = urllib.parse.quote
decode_uri_component = urllib.parse.unquote


def encode_contextualized_iri_property_node(individual: HKOProperty, context: HKContext):
    return context.id_ if isinstance(context, HKContext) else context + encode_uri_component(
        '/<' + individual.iri + '>')


def decode_contextualized_iri_property_node(node: HKReferenceNode) -> (str, str):
    iri = decode_uri_component(node.id_)

    parts = iri.rsplit('/<')

    if len(parts) == 1: return iri, None

    return parts[1][:-1], parts[0]


def encode_contextualized_iri_individual_node(individual: HKOIndividual, context: HKContext):
    return context.id_ + encode_uri_component('/<' + individual.iri + '>')


def decode_contextualized_iri_individual_node(node: HKReferenceNode) -> (str, str):
    iri = decode_uri_component(node.id_ if isinstance(node, HKEntity) else node)

    parts = iri.rsplit('/<')

    if len(parts) == 1: return iri, None

    return parts[1][:-1], parts[0]


def encode_iri(iri: str) -> str:
    return '<' + iri + '>'


def decode_iri(iri: str) -> str:
    if iri is None:
        return iri
    if len(iri) >= 2 and iri[0] == '<':
        return iri[1:-1]
    else:
        raise Exception(iri + ' is not an encoded hkb-iri (no enclosing diamonds)')
