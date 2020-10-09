###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import uuid
from queue import SimpleQueue
from typing import Dict, Set

from hkpy.hklib import HKEntity, HKNode, HKLink, HKContext, HKConnector, HKReferenceNode
from hkpy.hklib import HKAnyNode
from hkpy.utils import ConnectorType, RoleType

from hkpy.hkpyo.converters.utils import encode_contextualized_iri_individual_node, \
    encode_contextualized_iri_property_node, encode_iri, \
    decode_iri, encode_contextualized_iri_concept_node, encode_ifi_as_hk_id

from hkpy.hkpyo.converters.constants import *
from hkpy.hkpyo.model import *

HKOCONCEPT_NODE = HKNode(id_=encode_iri(CONCEPT_IRI))
HKOPROPERTY_NODE = HKNode(id_=encode_iri(PROPERTY_IRI))
HKOINDIVIDUAL_NODE = HKNode(id_=encode_iri(INDIVIDUAL_IRI))


#HKO_TOP_NODE = HKI(id_=encode_iri(TOP_CONCEPT_IRI))


class SerializingKit:

    def __init__(self):

        self.writtenHkG: [HKEntity] = []
        self.writtenHkO: Set[HKEntity] = set()
        self.writtenNamedElements: Set[HKEntity] = set()
        self.mapConceptExpressionToHkg: Dict[HKOConceptExpression, HKEntity] = {}
        self.mapPropertyToHkg: Dict[HKOProperty, HKEntity] = {}
        self.mapIndividualToHkg: Dict[HKOIndividual, HKEntity] = {}
        self.mapContextToHkg: Dict[HKOContext, HKEntity] = {}
        self.context_stack = [HKOContext]
        self.contexts_to_write:  SimpleQueue = SimpleQueue()

class HKOWriterHKG:
    #  context: HKContext | null= null

    # mapNodesToHKElements = new Map<HKGElement,HKElement>()

    #  setContext(context: HKContext) :
    #     self.context = context

    def create_instaceof_link(self, individual: HKNode, concept: HKNode, parent: str = None) -> HKLink:


        hk_link = HKLink(
            id_=INSTANCEOF_CONNECTOR + '-' + str(uuid.uuid4()),
            connector=encode_iri(INSTANCEOF_CONNECTOR),
            parent=parent)

        hk_link.add_bind('subject', individual.id_)
        hk_link.add_bind('object', concept.id_)

        return hk_link

    def fix_connectors(self, entities) -> None:
        connectors = {}

        # fix meta
        connectors[INSTANCEOF_CONNECTOR] = HKConnector(id_=encode_iri(INSTANCEOF_CONNECTOR), class_name=ConnectorType.HIERARCHY,
                                                       roles={"subject": RoleType.CHILD,
                                                              'object': RoleType.PARENT})
        connectors[SUBCONCEPTOF_CONNECTOR] = HKConnector(id_=SUBCONCEPTOF_CONNECTOR, class_name=ConnectorType.HIERARCHY,
                                                         roles={"sub": RoleType.CHILD,
                                                                'sup': RoleType.PARENT})
        connectors[EQCONCEPT_CONNECTOR] = HKConnector(id_=EQCONCEPT_CONNECTOR, class_name=ConnectorType.FACTS,
                                                      roles={"ConceptA": RoleType.SUBJECT,
                                                             'ConceptB': RoleType.OBJECT})
        connectors[EXISTS_CONNECTOR] = HKConnector(id_=EXISTS_CONNECTOR, class_name=ConnectorType.FACTS,
                                                   roles={"head_concept": RoleType.SUBJECT,
                                                          'property': RoleType.OBJECT,
                                                          'concept': RoleType.OBJECT})
        connectors[FORALL_CONNECTOR] = HKConnector(id_=FORALL_CONNECTOR, class_name=ConnectorType.FACTS,
                                                   roles={"head_concept": RoleType.SUBJECT,
                                                          'property': RoleType.OBJECT,
                                                          'concept': RoleType.OBJECT})
        connectors[CONJUNCTION_CONNECTOR] = HKConnector(id_=CONJUNCTION_CONNECTOR, class_name=ConnectorType.FACTS,
                                                        roles={"head_concept": RoleType.SUBJECT,
                                                               'concepts': RoleType.OBJECT})
        connectors[DISJUNCTION_CONNECTOR] = HKConnector(id_=DISJUNCTION_CONNECTOR, class_name=ConnectorType.FACTS,
                                                        roles={"head_concept": RoleType.SUBJECT,
                                                               'concepts': RoleType.OBJECT})
        connectors[CONTEXT_IMPORT_CONNECTOR] = HKConnector(id_=CONTEXT_IMPORT_CONNECTOR, class_name=ConnectorType.FACTS,
                                                        roles={"sub": RoleType.SUBJECT,
                                                               'sup': RoleType.OBJECT})

        # connectors[NOT_CONNECTOR] = HKConnector(id_=NOT_CONNECTOR, class_name=ConnectorType.FACTS,
        #                                                 roles={"head_concept": RoleType.SUBJECT,
        #                                                        'concepts': RoleType.OBJECT})


        # for e in entities:
        #     if isinstance(e, HKLink) and e.connector  not in connectors:
        #         hkg_connector = HKConnector(id_=e.connector if isinstance(e.connector, str) else e.connector.id_,
        #                                     class_name=ConnectorType.FACTS,
        #                                     roles={})
        #
        #         connectors[hkg_connector.id_] = hkg_connector

        entities += list(connectors.values())

    def _writeHKOConcept(self, e: HKOConcept, serializing_kit) -> None:
        if e in serializing_kit.writtenNamedElements:
            return # already written

        self._writeRouter(e.context, serializing_kit)
        econtext = serializing_kit.mapContextToHkg.get(e.context)

        hkg: HKNode = HKNode(
            id_=encode_iri(e.iri)
        )

        hkg_ref = HKReferenceNode(
            # id_=encode_iri(encode_contextualized_iri_concept_node(e, econtext.id_)),
            id_=encode_ifi_as_hk_id(e.ifi),
            ref=encode_ifi_as_hk_id(e.ifi.fragment),
            parent=encode_ifi_as_hk_id(e.ifi.artifact)
        )

        hkg_meta_link = self.create_instaceof_link(hkg, HKOCONCEPT_NODE, econtext.id_)
        hkg_meta_link_ref = self.create_instaceof_link(hkg_ref, HKOCONCEPT_NODE, econtext.id_)

        serializing_kit.mapConceptExpressionToHkg[e] = hkg

        serializing_kit.writtenHkG += [hkg, hkg_ref, hkg_meta_link, HKOCONCEPT_NODE, hkg_meta_link_ref]
        serializing_kit.writtenNamedElements.add(e)

    def _writeHKOProperty(self, e: HKOProperty, serializing_kit) -> None:
        if e in serializing_kit.writtenNamedElements:
            return  # already written

        self._writeRouter(e.context, serializing_kit)
        econtext = serializing_kit.mapContextToHkg.get(e.context)

        hkg: HKNode = HKNode(
            id_=encode_iri(e.iri)
        )

        hkg_ref = HKReferenceNode(
            id_=encode_iri(encode_contextualized_iri_property_node(e, decode_iri(econtext.id_))),
            ref=encode_iri(e.iri),
            parent=econtext.id_,
        )

        hkg_meta_link = self.create_instaceof_link(hkg, HKOPROPERTY_NODE, econtext.id_)
        hkg_meta_link_ref = self.create_instaceof_link(hkg_ref, HKOPROPERTY_NODE, econtext.id_)

        serializing_kit.mapPropertyToHkg[e] = hkg_ref

        serializing_kit.writtenHkG += [hkg_ref, hkg_meta_link, hkg_meta_link_ref, HKOPROPERTY_NODE]
        serializing_kit.writtenNamedElements.add(e)

    def _writeHKOIndividual(self, e: HKOIndividual, serializing_kit: SerializingKit) -> None:
        if e in serializing_kit.writtenNamedElements:
            return  # already written

        self._writeRouter(e.context, serializing_kit)
        econtext = serializing_kit.mapContextToHkg.get(e.context)

        hkg: HKNode = HKNode(
            id_=encode_iri(e.iri)
        )

        hkg_ref: HKReferenceNode = HKReferenceNode(
            id_=encode_iri(encode_contextualized_iri_individual_node(e, decode_iri(econtext.id_))),
            ref = encode_iri(e.iri),
            parent=econtext.id_
        )

        hkg_meta_link = self.create_instaceof_link(hkg, HKOINDIVIDUAL_NODE, econtext.id_)
        hkg_meta_link_ref = self.create_instaceof_link(hkg_ref, HKOINDIVIDUAL_NODE, econtext.id_)

        serializing_kit.mapIndividualToHkg[e] = hkg_meta_link_ref

        serializing_kit.writtenHkG += [hkg, hkg_meta_link, hkg_meta_link_ref, HKOINDIVIDUAL_NODE]
        serializing_kit.writtenNamedElements.add(e)

    def _writeHKOExistsExpression(self, e: HKOExistsExpression, serializing_kit : SerializingKit) -> None:
        if e in serializing_kit.writtenHkO:
            return None  # already written

        self._writeRouter(e.property, serializing_kit)
        self._writeRouter(e.concept, serializing_kit)

        econtext = serializing_kit.mapContextToHkg.get(serializing_kit.context_stack[-1])

        property_g = serializing_kit.mapPropertyToHkg.get(e.property)
        concept_g = serializing_kit.mapConceptExpressionToHkg.get(e.concept)

        blank_node_id = str(uuid.uuid4())

        hkg_node: HKNode = HKNode(
            id_="_:" + blank_node_id,
            parent=econtext.id_,
        )

        hkg_link: HKLink = HKLink(
            id_=EXISTS_CONNECTOR + '-' + blank_node_id,
            connector=EXISTS_CONNECTOR,
            parent=econtext.id_,
        )

        hkg_link.add_bind('head_concept', hkg_node.id_)
        hkg_link.add_bind('property', property_g.id_)
        hkg_link.add_bind('concept', concept_g.id_)

        serializing_kit.mapConceptExpressionToHkg[e] = hkg_node

        serializing_kit.writtenHkG.append(hkg_node)
        serializing_kit.writtenHkG.append(hkg_link)
        serializing_kit.writtenHkO.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _writeHKOConjunctionExpression(self, e: HKOConjunctionExpression, serializing_kit) -> None:
        if e in serializing_kit.writtenHkO:
            return None  # already written

        for c in e.concepts:
            self._writeRouter(c, serializing_kit)

        econtext = serializing_kit.mapContextToHkg.get(serializing_kit.context_stack[-1])

        concepts_g: [HKNode] = []
        for c in e.concepts:
            concepts_g.append(serializing_kit.mapConceptExpressionToHkg.get(c))

        blank_node_id = "conjunction-" + str(uuid.uuid4())

        hkg_node: HKNode = HKNode(
            id_="_:" + blank_node_id,
            parent=econtext.id_,
        )

        hkg_link: HKLink = HKLink(
            id_= "_:" + blank_node_id,
            connector=CONJUNCTION_CONNECTOR,
            parent=econtext.id_,
        )

        hkg_link.add_bind('head_concept', hkg_node.id_)

        for c in concepts_g:
            hkg_link.add_bind('concepts', c.id_)

        serializing_kit.mapConceptExpressionToHkg[e] = hkg_node

        serializing_kit.writtenHkG.append(hkg_node)
        serializing_kit.writtenHkG.append(hkg_link)
        serializing_kit.writtenHkO.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _writeHKODisjunctionExpression(self, e: HKODisjunctionExpression, serializing_kit : SerializingKit) -> None:
        if e in serializing_kit.writtenHkO:
            return None  # already written

        for c in e.concepts:
            self._writeRouter(c, serializing_kit)

        econtext = serializing_kit.mapContextToHkg.get(serializing_kit.context_stack[-1])

        concepts_g: [HKNode] = []
        for c in e.concepts:
            concepts_g.append(serializing_kit.mapConceptExpressionToHkg.get(c))

        blank_node_id = "disjunction-" + str(uuid.uuid4())

        hkg_node: HKNode = HKNode(
            id_="_:" + blank_node_id,
            parent=econtext.id_,
        )

        hkg_link: HKLink = HKLink(
            id_="_:" + blank_node_id,
            connector=DISJUNCTION_CONNECTOR,
            parent=econtext.id_,
        )

        hkg_link.add_bind('head_concept', hkg_node.id)

        for c in concepts_g:
            hkg_link.add_bind('concepts', c)

        serializing_kit.mapConceptExpressionToHkg[e] = hkg_node

        serializing_kit.writtenHkG.append(hkg_node)
        serializing_kit.writtenHkG.append(hkg_link)
        serializing_kit.writtenHkO.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _writeHKOSubConceptAxiom(self, e: HKOSubConceptAxiom, serializing_kit : SerializingKit) -> None:
        if e in serializing_kit.writtenHkO:
            return None  # already written

        self._writeRouter(e.sub, serializing_kit)
        self._writeRouter(e.sup, serializing_kit)

        esub = serializing_kit.mapConceptExpressionToHkg.get(e.sub)
        esup = serializing_kit.mapConceptExpressionToHkg.get(e.sup)
        econtext = serializing_kit.mapContextToHkg.get(e.context)

        hkg_link: HKLink = HKLink(
            id_=SUBCONCEPTOF_CONNECTOR + '-' + str(uuid.uuid4()),
            connector=SUBCONCEPTOF_CONNECTOR,
            parent=econtext.id_,
        )

        hkg_link.add_bind('sub', esub.id_)
        hkg_link.add_bind('sup', esup.id_)

        serializing_kit.writtenHkG.append(hkg_link)
        serializing_kit.writtenHkO.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _writeHKOEquivalentConceptAxiom(self, e: HKOEquivalentConceptAxiom, serializing_kit) -> None:
        if e in serializing_kit.writtenHkO:
            return None  # already written

        self._writeRouter(e.conceptA, serializing_kit)
        self._writeRouter(e.conceptB, serializing_kit)

        ecA = serializing_kit.mapConceptExpressionToHkg.get(e.conceptA)
        ecB = serializing_kit.mapConceptExpressionToHkg.get(e.conceptB)
        econtext = serializing_kit.mapConceptExpressionToHkg.get(e.context)

        hkg_link: HKLink = HKLink(
            id_=EQCONCEPT_CONNECTOR + '-' + str(uuid.uuid4()),
            connector=EQCONCEPT_CONNECTOR,
            parent=econtext.id_,
        )

        hkg_link.add_bind('left', ecA.id_)
        hkg_link.add_bind('right', ecB.id_)

        serializing_kit.writtenHkG.append(hkg_link)
        serializing_kit.writtenHkO.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _writeHKOConceptAssertion(self, e: HKOConceptAssertion, serializing_kit) -> None:
        if e in serializing_kit.writtenHkO:
            return None  # already written


        self._writeRouter(e.concept, serializing_kit)
        self._writeRouter(e.individual, serializing_kit)

        hkg_concept = serializing_kit.mapConceptExpressionToHkg.get(e.concept)
        hkg_individual = serializing_kit.mapIndividualToHkg.get(e.individual)
        econtext = serializing_kit.mapContextToHkg.get(e.context)

        hkg_link: HKLink = HKLink(
            id_=INSTANCEOF_CONNECTOR + '-' + str(uuid.uuid4()),
            connector=encode_iri(INSTANCEOF_CONNECTOR),
            parent=econtext.id_,
        )

        hkg_link.add_bind('object', hkg_concept.id_)
        hkg_link.add_bind('subject', hkg_individual.id_)

        serializing_kit.writtenHkG.append(hkg_link)
        serializing_kit.writtenHkO.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _writeHKOPropertyAssertion(self, e: HKOPropertyAssertion, serializing_kit) -> None:
        if e in serializing_kit.writtenHkO:
            return None  # already written


        self._writeRouter(e.property, serializing_kit)
        self._writeRouter(e.arg1, serializing_kit)

        if isinstance(e.arg2, HKOIndividual):
            self._writeRouter(e.arg2, serializing_kit)

            # self.state_stack.pop()

            hkg_arg1 = serializing_kit.mapIndividualToHkg.get(e.arg1)
            hkg_arg2 = serializing_kit.mapIndividualToHkg.get(e.arg2)
            econtext = serializing_kit.mapContextToHkg.get(e.context)

            hkg_connector = HKConnector(id_=encode_iri(e.property.iri), class_name=ConnectorType.FACTS,
                                                roles={HK_BIND_ARG_1: RoleType.SUBJECT,
                                                       HK_BIND_ARG_2: RoleType.OBJECT})

            hkg_link: HKLink = HKLink(
                id_=encode_iri(e.property.iri + '-' + str(uuid.uuid4())),
                connector=encode_iri(e.property.iri),
                parent=econtext.id_,
            )

            hkg_link.add_bind(HK_BIND_ARG_1, hkg_arg1.id_)
            hkg_link.add_bind(HK_BIND_ARG_2, hkg_arg2.id_)

            serializing_kit.writtenHkG.append(hkg_connector)
            serializing_kit.writtenHkG.append(hkg_link)

        elif isinstance(e.arg2, str) or isinstance(e.arg2, int) or isinstance(e.arg2, float):
            #literals as properties
            hkg_arg1 = serializing_kit.mapIndividualToHkg.get(e.arg1)
            hkg_arg1.properties[encode_iri(e.property.iri)] = str(e.arg2)
        else:
            raise Exception("Cannot convert property ")

        serializing_kit.writtenHkO.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _writeHKOImportContextAssertion(self, e: HKOImportContextAssertion, serializing_kit) -> None:
        if e in serializing_kit.writtenHkO:
            return None  # already written


        self._writeRouter(e.sub, serializing_kit)
        self._writeRouter(e.sup, serializing_kit)

        # self.state_stack.pop()

        hkg_sub = serializing_kit.mapIndividualToHkg.get(e.sub)
        hkg_sup = serializing_kit.mapIndividualToHkg.get(e.sup)
        econtext = serializing_kit.mapContextToHkg.get(e.context)


        hkg_link: HKLink = HKLink(
            id_=encode_iri(CONTEXT_IMPORT_CONNECTOR + '-' + str(uuid.uuid4())),
            connector=encode_iri(CONTEXT_IMPORT_CONNECTOR),
            parent=econtext.id_,
        )

        hkg_link.add_bind('sub', hkg_sub.id_)
        hkg_link.add_bind('sup', hkg_sup.id_)

        serializing_kit.writtenHkG.append(hkg_link)

        serializing_kit.writtenHkO.add(e)

    def _writeHKOContext(self, e: HKOContext, serializing_kit) -> HKOContext:
        if e in serializing_kit.writtenNamedElements:
            return None  # already written

        # writer don't serialize up the parent hierarchy
        if e.context is not None and e.context.iri is not 'null':
            parent_id = encode_iri(e.context.iri) if e.context.iri is not None else None
        else:
            parent_id = None

        hkg: HKContext = HKContext(
            id_=encode_iri(e.iri),
            parent=parent_id,
        )

        serializing_kit.contexts_to_write.put_nowait(e)

        serializing_kit.writtenHkG.append(hkg)
        serializing_kit.writtenNamedElements.add(e)

        serializing_kit.mapContextToHkg[e] = hkg



    def _write_context_elements(self, serializing_kit : SerializingKit) -> None:

        while not serializing_kit.contexts_to_write.empty():
            e = serializing_kit.contexts_to_write.get_nowait()

            # push context
            currentContext = serializing_kit.context_stack.append(e)

            for entity in e.elements:
                self._writeRouter(entity, serializing_kit)

            #pop context
            serializing_kit.context_stack.pop()

    def _writeRouter(self, e: HKOElement, serializing_kit):
        if isinstance(e, HKOConcept):
            self._writeHKOConcept(e, serializing_kit)
        elif isinstance(e, HKOProperty):
            self._writeHKOProperty(e, serializing_kit)
        elif isinstance(e, HKOIndividual):
            self._writeHKOIndividual(e, serializing_kit)
        elif isinstance(e, HKOProperty):
            self._writeHKOProperty(e, serializing_kit)
        elif isinstance(e, HKOExistsExpression):
            self._writeHKOExistsExpression(e, serializing_kit)
        elif isinstance(e, HKOConjunctionExpression):
            self._writeHKOConjunctionExpression(e, serializing_kit)
        elif isinstance(e, HKODisjunctionExpression):
            self._writeHKODisjunctionExpression(e, serializing_kit)
        elif isinstance(e, HKOSubConceptAxiom):
            self._writeHKOSubConceptAxiom(e, serializing_kit)
        elif isinstance(e, HKOEquivalentConceptAxiom):
            self._writeHKOEquivalentConceptAxiom(e, serializing_kit)
        elif isinstance(e, HKOConceptAssertion):
            self._writeHKOConceptAssertion(e, serializing_kit)
        elif isinstance(e, HKOPropertyAssertion):
            self._writeHKOPropertyAssertion(e, serializing_kit)
        elif isinstance(e, HKOImportContextAssertion):
            self._writeHKOImportContextAssertion(e, serializing_kit)
        elif isinstance(e, HKOContext):
            self._writeHKOContext(e, serializing_kit)
        else:
            raise Exception("Entity ", e, " is not valid HKO.")

    def writeHKOContext(self, baseContext: HKOContext) -> [HKEntity]:

        serializing_kit = SerializingKit()

        self._writeHKOContext(baseContext, serializing_kit)
        self._write_context_elements(serializing_kit)

        self.fix_connectors(serializing_kit.writtenHkG)

        return serializing_kit.writtenHkG
