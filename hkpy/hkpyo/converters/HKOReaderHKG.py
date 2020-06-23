###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from hkpy.hklib import HKLink, HKEntity, HKNode, HKContext, HKReferenceNode, HKConnector

from hkpy.hkpyo.converters.utils import decode_contextualized_iri_individual_node, decode_contextualized_iri_property_node, decode_iri, \
    encode_iri
from hkpy.hkpyo.converters.constants import *
from hkpy.hkpyo.model import *

HKOCONCEPT_NODE = HKNode(id_=encode_iri(CONCEPT_IRI))
HKOPROPERTY_NODE = HKNode(id_=encode_iri(PROPERTY_IRI))


EXCLUDE_META = True #exclude meta axioms


class HKOContextExpandable(HKOContext):

    def __init__(self, iri: str):
        super().__init__(iri, None)


class HKOReaderHKG:

    def _preprocess(self, parsing_kit):
        # preprocess non axioms

        to_remove = set()
        for e in parsing_kit.hkg_entities:
            if isinstance(e, HKLink) and e.connector == encode_iri(INSTANCEOF_CONNECTOR):
                #separate meta entities

                cnode = parsing_kit.get_HKNode(e.get_bind_value_no_anchor('object'))
                inode = parsing_kit.get_HKNode(e.get_bind_value_no_anchor('subject'))


                # if cnode.id_ not in parsing_kit.tbox:
                #     # if not, ignore_hko_entities:
                #     hko_meta_concept = parsing_kit.cb.getHKOConcept(cnode.id_)
                #     parsing_kit.tbox[hko_meta_concept.iri] = hko_meta_concept

                if cnode.id_ == HKOCONCEPT_NODE.id_:
                    hko_concept = parsing_kit.cb.getHKOConcept(decode_iri(inode.id_))
                    parsing_kit.tbox[hko_concept.iri] = hko_concept
                    to_remove.add(e)
                elif cnode.id_ == HKOPROPERTY_NODE.id_:
                    hko_property = parsing_kit.cb.getHKOProperty(decode_iri(inode.id_))
                    parsing_kit.tbox[hko_property.iri] = hko_property
                    to_remove.add(e)

                # else:
                #     # this should allow punning
                #     hko_individual = parsing_kit.cb.getHKOIndividual(inode.id_)
                #     parsing_kit.abox[hko_individual.iri] = hko_individual

            #process expressions
            elif isinstance(e, HKLink) and (
                    e.connector == CONJUNCTION_CONNECTOR
                    or e.connector == DISJUNCTION_CONNECTOR
                    or e.connector == EXISTS_CONNECTOR
                    or e.connector == FORALL_CONNECTOR
                    or e.connector == NOT_CONNECTOR):
                head_node = parsing_kit.get_HKNode(e.get_bind_value_no_anchor('head_concept'))
                parsing_kit.expressions[head_node.id_] = e
            elif isinstance(e, HKContext):
                print("Ignoring HKContext in json file")

        #TODO: this is potentially slow. Improve with a set or change the previous code to get indexes
        for e in to_remove:
            parsing_kit.hkg_entities.remove(e)

        parsing_kit.preprocessed = True


    def _readHKOConceptExpressionNode(self, e: HKNode, parsing_kit) -> HKOConceptExpression:
        if e.id_ in parsing_kit.expressions:
            return self._readRouter(parsing_kit.expressions[e.id_], parsing_kit)
        else:
            return self._readHKONamedConcept(e, parsing_kit)

    def _readHKONamedConcept(self, e: HKNode, parsing_kit):
        if e.id_ in parsing_kit.tbox:
            return parsing_kit.tbox[e.id_]
        else:
            hkoc_concept = parsing_kit.cb.getHKOConcept(decode_iri(e.id_))
            parsing_kit.tbox[e.id_] = hkoc_concept
            return hkoc_concept

    def _readHKOProperty(self, e: HKReferenceNode, parsing_kit):
        if e.id_ in parsing_kit.tbox:
            return parsing_kit.tbox[e.id_]
        else:
            clean_id_, id_context = decode_contextualized_iri_individual_node(decode_iri(e.id_))
            hkop_property = parsing_kit.cb.getHKOProperty(clean_id_)
            parsing_kit.tbox[e.id_] = hkop_property
            return hkop_property

    def _readHKOPropertyConnector(self, e: HKConnector, parsing_kit):
        id = decode_iri(e if isinstance(e, str) else e.id_)
        if id in parsing_kit.tbox:
            return parsing_kit.tbox[id]
        else:
            hkop_property = parsing_kit.cb.getHKOProperty(id)
            parsing_kit.tbox[id] = hkop_property
            return hkop_property


    def _readHKOIndividual(self, e: HKReferenceNode, parsing_kit):
        if e.id_ in parsing_kit.abox:
            return parsing_kit.abox[e.id_]
        else:
            clean_id_, id_context = decode_contextualized_iri_individual_node(decode_iri(e.id_))
            hkoi_indiv = parsing_kit.cb.getHKOIndividual(clean_id_)
            parsing_kit.abox[e.id_] = hkoi_indiv
            return hkoi_indiv

    def _readHKOExistsExpression(self, e: HKLink, parsing_kit) -> HKOExistsExpression:

        parsing_kit.state_stack.append({'expecting_tbox_nodes':True})
        hko_property = self._readHKOProperty(parsing_kit.get_HKNode(e.get_bind_value_no_anchor('property')), parsing_kit)
        hko_concept = self._readHKOConceptExpressionNode(parsing_kit.get_HKNode(e.get_bind_value_no_anchor('concept')), parsing_kit)
        parsing_kit.state_stack.pop()

        hko_expression = parsing_kit.cb.getHKOExistsExpression(property=hko_property, concept=hko_concept)

        return hko_expression

    def _readHKOConjunctionExpression(self, e: HKLink, parsing_kit) -> HKOConjunctionExpression:
        # if e in self.writtenHk:
        #     return None  # already written

        hkg_concepts = list(parsing_kit.get_HKNode(x) for x in e.get_bind_values_no_anchor('concepts'))

        hko_concepts = []
        parsing_kit.state_stack.append({'expecting_box':'tbox'})
        for c in hkg_concepts:
            hko_concepts.append(self._readHKOConceptExpressionNode(c, parsing_kit))
        parsing_kit.state_stack.pop()

        hkbo_expression = parsing_kit.cb.getHKOConjunctionExpression(*hko_concepts)

        return hkbo_expression

        # self.mapNodesToHKElements.set(hkg, e)


    def _readHKODisjunctionExpression(self, e: HKLink, parsing_kit) -> HKODisjunctionExpression:
        # if e in self.writtenHk:
        #     return None  # already written

        hkg_concepts = list(parsing_kit.get_HKNode(x) for x in e.get_bind_values_no_anchor('concepts'))

        hko_concepts = []
        parsing_kit.state_stack.append({'expecting_box':'tbox'})
        for c in hkg_concepts:
            hko_concepts.append(self._readHKOConceptExpressionNode(c, parsing_kit))
        parsing_kit.state_stack.pop()

        hkbo_expression = parsing_kit.cb.getHKODisjunctionExpression(*hko_concepts)

        return hkbo_expression

        # self.mapNodesToHKElements.set(hkg, e)

    def _readHKOSubClassOfAxiom(self, e: HKLink, parsing_kit):
        # if e in self.writtenHk:
        #     return None  # already written

        # Assuming e.context = cb.context
        assert (decode_iri(e.parent) == parsing_kit.cb.context.iri)

        osub = self._readHKOConceptExpressionNode(parsing_kit.get_HKNode(e.get_bind_value_no_anchor('sub')), parsing_kit)
        osup = self._readHKOConceptExpressionNode(parsing_kit.get_HKNode(e.get_bind_value_no_anchor('sup')), parsing_kit)

        hkoax_subconcept = parsing_kit.cb.getHKOSubConceptAxiom(sub=osub, sup=osup)
        parsing_kit.cb.context.addAxiom(hkoax_subconcept)

        parsing_kit.loaded_axioms.append(hkoax_subconcept)
        # self.writtenHk.add(e)
        # self.mapNodesToHKElements.set(hkg, e)


    def _readHKOEquivalentConceptAxiom(self, e: HKLink, parsing_kit):
        # if e in self.writtenHk:
        #     return None  # already written

        # Assuming e.context = cb.context
        assert (decode_iri(e.parent) == parsing_kit.cb.context.iri)

        osub = self._readHKOConceptExpressionNode(parsing_kit.get_HKNode(e.get_bind_value_no_anchor('left')), parsing_kit)
        osup = self._readHKOConceptExpressionNode(parsing_kit.get_HKNode(e.get_bind_value_no_anchor('right')), parsing_kit)

        hkoax_subconcept = parsing_kit.cb.getHKOEquivalentConceptAxiom(sub=osub, sup=osup)
        parsing_kit.cb.context.addAxiom(hkoax_subconcept)

        parsing_kit.loaded_axioms.append(hkoax_subconcept)
        # self.writtenHk.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _readHKOConceptAssertion(self, e: HKLink, parsing_kit):
        # if e in self.writtenHk:
        #     return None  # already written

        # Assuming e.context = cb.context
        assert (decode_iri(e.parent) == parsing_kit.cb.context.iri)


        hkgn_concept = parsing_kit.get_HKNode(e.get_bind_value_no_anchor('object'))
        hkgn_instance = parsing_kit.get_HKNode(e.get_bind_value_no_anchor('subject'))

        parsing_kit.state_stack.append({'expecting_box':'tbox'})
        hkoc_concept = self._readHKOConceptExpressionNode(hkgn_concept,parsing_kit)
        parsing_kit.state_stack.pop()


        parsing_kit.state_stack.append({'expecting_box':'abox'})
        hkoi_individual = self._readHKOIndividual(hkgn_instance,parsing_kit)
        parsing_kit.state_stack.pop()


        hkocas_concept = parsing_kit.cb.getHKOConceptAssertion(concept=hkoc_concept, individual=hkoi_individual)
        parsing_kit.cb.context.addAxiom(hkocas_concept)

        parsing_kit.loaded_axioms.append(hkocas_concept)
        # self.writtenHk.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _readHKOPropertyAssertion(self, e: HKLink, parsing_kit):
        # if e in self.writtenHk:
        #     return None  # already written

        # Assuming e.context = cb.context
        assert (decode_iri(e.parent) == parsing_kit.cb.context.iri)

        # parsing_kit.state_stack.append({'expecting_box':'abox'})
        # osub = self._readRouter(e.get_bind_value_no_anchor('sub'), parsing_kit)
        # osup = self._readRouter(e.get_bind_value_no_anchor('sup'), parsing_kit)
        # parsing_kit.state_stack.pop()

        hkgn_property = e.connector
        hkgn_arg1 = parsing_kit.get_HKNode(e.get_bind_value_no_anchor(HK_BIND_ARG_1))
        hkgn_arg2 = parsing_kit.get_HKNode(e.get_bind_value_no_anchor(HK_BIND_ARG_2))

        parsing_kit.state_stack.append({'expecting_box': 'tbox'})
        hkop_property = self._readHKOPropertyConnector(hkgn_property, parsing_kit)
        parsing_kit.state_stack.pop()

        parsing_kit.state_stack.append({'expecting_box': 'abox'})
        hkoi_arg1 = self._readHKOIndividual(hkgn_arg1, parsing_kit)
        hkoi_arg2 = self._readHKOIndividual(hkgn_arg2, parsing_kit)
        parsing_kit.state_stack.pop()

        hkopas_property = parsing_kit.cb.getHKOPropertyAssertion(property=hkop_property, arg1=hkoi_arg1, arg2=hkoi_arg2)
        parsing_kit.cb.context.addAxiom(hkopas_property)

        parsing_kit.loaded_axioms.append(hkopas_property)
        # self.writtenHk.add(e)
        # self.mapNodesToHKElements.set(hkg, e)

    def _readHKOPropertyAssertionsInNode(self, e: HKNode, parsing_kit):
        # if e in self.writtenHk:
        #     return None  # already written

        # Assuming e.context = cb.context
        assert (decode_iri(e.parent) == parsing_kit.cb.context.iri)

        for p in e.properties:
            property_value = e.properties[p]

            #fix types in _readHKOPropertyConnector
            hkop_property = self._readHKOPropertyConnector(str(p), parsing_kit)
            hkoi_arg1 = self._readHKOIndividual(e, parsing_kit)

            hkoi_arg2 = str(property_value)

            hkopas_property = parsing_kit.cb.getHKOPropertyAssertion(property=hkop_property,
                                                                     arg1=hkoi_arg1,
                                                                     arg2=hkoi_arg2)
            parsing_kit.cb.context.addAxiom(hkopas_property)

            parsing_kit.loaded_axioms.append(hkopas_property)


    def _readRouter(self, e, parsing_kit) -> HKOElement:

        assert(parsing_kit.preprocessed) #cannot proceed if not preprocessed

        if isinstance(e, HKNode) or isinstance(e, HKReferenceNode):
            if len(e.properties) > 0:
                return self._readHKOPropertyAssertionsInNode(e, parsing_kit)
        elif isinstance(e, HKLink) and e.connector == CONJUNCTION_CONNECTOR:
            return self._readHKOConjunctionExpression(e, parsing_kit)
        elif isinstance(e, HKLink) and e.connector == DISJUNCTION_CONNECTOR:
            return self._readHKODisjunctionExpression(e, parsing_kit)
        elif isinstance(e, HKLink) and e.connector == SUBCONCEPTOF_CONNECTOR:
            return self._readHKOSubClassOfAxiom(e, parsing_kit)
        elif isinstance(e, HKLink) and e.connector == EQCONCEPT_CONNECTOR:
            return self._readHKOEquivalentConceptAxiom(e, parsing_kit)
        elif isinstance(e, HKLink) and e.connector == EXISTS_CONNECTOR:
            return self._readHKOExistsExpression(e, parsing_kit)
        elif isinstance(e, HKLink) and e.connector == encode_iri(INSTANCEOF_CONNECTOR):
            return self._readHKOConceptAssertion(e, parsing_kit)
        elif isinstance(e, HKLink) and HK_BIND_ARG_1 in e.binds and HK_BIND_ARG_2 in e.binds:
            #TODO: any other FACT link should be a property assertion
            return self._readHKOPropertyAssertion(e, parsing_kit)
        elif e.id_ in parsing_kit.abox or e.id_ in parsing_kit.tbox or e.id_ in parsing_kit.expressions:
            #do nothing, should be captured by previous
            pass
        else:
            #print("The entity ", e, " is not valid HKO. Ignoring...")
            pass

    def _loadContextGraph(self, parsing_kit):
        self._preprocess(parsing_kit)

        #TODO: call this only on axioms and assertion items. Change preprocess to separate these.
        for e in parsing_kit.hkg_entities:
            self._readRouter(e, parsing_kit)


    def readHKOintoContextFromHKGJson(self, json_entities : [Dict], context_builder: HKOContextBuilder):
        hkentities = list(hkfy(e) for e in json_entities)
        self.readHKOintoContext(hkentities, context_builder)

    def readHKOintoContext(self, hkg_context_graph: [HKEntity], context_builder: HKOContextBuilder):
        """

        Parses HK graph into an HKO model. It is a two-passes algorithm. First, it preprocesses the graph indexing
        concept expressions, then proceed to process tbox axioms and abox assertions. Any link that has arg1 and arg2 will
        be considered a property assertion.

        :param hkg_context_graph:
        :param context_builder:
        :return:
        """

        index_hkg_entities = {}

        for e in hkg_context_graph:
            index_hkg_entities[e.id_] = e

        # parsing kit object to pass along parsing functions. It is also called parsing context in some implementations
        class ParsinKit:

            def __init__(self):
                self.cb: HKOContextBuilder = None
                self.hkg_entities = {}
                self.loaded_axioms = []
                self.hke_index = {}
                self.tbox: Dict[str, HKOElement] = {}
                self.abox: Dict[str, HKOElement] = {}
                self.expressions: Dict[str, HKLink] = {} # map blank node -> concept expressions
                self.expecting_tbox_nodes = False # control for punning
                self.state_stack = []

            def get_HKNode(self, id_):
                return self.hke_index.get(id_, HKNode(id_))



        parsing_kit = ParsinKit()
        parsing_kit.cb = context_builder
        parsing_kit.hkg_entities = hkg_context_graph
        parsing_kit.hke_index = index_hkg_entities
        parsing_kit.loaded_axioms = []
        parsing_kit.tbox: Dict[str, HKOElement] = {}
        parsing_kit.abox: Dict[str, HKOElement] = {}
        parsing_kit.expressions: Dict[str, HKLink] = {}  # map blank node -> concept expressions
        parsing_kit.expecting_tbox_nodes = False  # control for punning
        parsing_kit.state_stack = []


        # load axioms
        self._loadContextGraph(parsing_kit)
