###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from hkpy.hklib import HKReferenceNode, HKContext, HKNode, HKEntity
from hkpy.hkpyo.model import HKOIndividual, HKOProperty, HKOConcept, IFI
import urllib

encode_uri_component = urllib.parse.quote
decode_uri_component = urllib.parse.unquote


def encode_ifi_as_hk_id(ifi : IFI) -> str:
    #return encode_uri_component(str(ifi.__str__()))
    return ifi.__str__()

def encode_contextualized_iri_concept_node(individual: HKOConcept, context: HKContext):
    if isinstance(context, HKContext):
        cid = context.id_
    else:
        cid = context

    if cid[0] == '<':
        cid = cid[1:-1]

    return cid + encode_uri_component('/<' + individual.iri + '>')


def decode_contextualized_iri_concept_node(node: HKReferenceNode) -> (str, str):
    iri = decode_uri_component(node.id_ if isinstance(node, HKEntity) else node)

    parts = iri.rsplit('/<')

    if len(parts) == 1: return iri, None

    return parts[1][:-1], parts[0]

def encode_contextualized_iri_property_node(individual: HKOProperty, context: HKContext):
    if isinstance(context, HKContext):
        cid = context.id_
    else:
        cid = context

    if cid[0] == '<':
        cid = cid[1:-1]

    return cid + encode_uri_component('/<' + individual.iri + '>')


def decode_contextualized_iri_property_node(node: HKReferenceNode) -> (str, str):
    iri = decode_uri_component(node.id_)

    parts = iri.rsplit('/<')

    if len(parts) == 1: return iri, None

    return parts[1][:-1], parts[0]


def encode_contextualized_iri_individual_node(individual: HKOIndividual, context: HKContext):
    if isinstance(context, HKContext):
        cid = context.id_
    else:
        cid = context

    if cid[0] == '<':
        cid = cid[1:-1]

    return cid + encode_uri_component('/<' + individual.iri + '>')

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
