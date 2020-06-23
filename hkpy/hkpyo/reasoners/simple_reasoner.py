###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from collections import defaultdict

from hkpy.hkpyo.model import HKOContext, HKOContextManager, HKOConcept, HKOSubConceptAxiom, HKOConjunctionExpression, \
    HKODisjunctionExpression, HKOConceptAssertion, HKOIndividual, HKOPropertyAssertion, HKOLiteral, Union, HKOAxiom, \
    HKOAssertion, HKOProperty


class HKAssertedContextReasoner:

    def __init__(self, context: HKOContext):
        self.mgr = HKOContextManager.get_global_context_manager()
        self.context = context
        self.reset_caches()

    def reset_caches(self):
        self.cache_axioms = []
        self.cache_assertions = []
        self.cache_individual_concept = defaultdict(lambda: {})
        self.cache_concept_individual = defaultdict(lambda: {})
        self.cache_individual_prop_value = defaultdict(lambda: defaultdict(lambda: {}))
        self.cache_value_prop_individual = defaultdict(lambda: defaultdict(lambda: {}))

        for e in self.context.elements:
            if isinstance(e, HKOConceptAssertion):
                self.cache_individual_concept[e.individual][e.concept] = True
                self.cache_concept_individual[e.concept][e.individual] = True
            elif isinstance(e, HKOPropertyAssertion):
                self.cache_individual_prop_value[e.arg1][e.property][e.arg2] = True
                self.cache_value_prop_individual[e.arg2][e.property][e.arg1] = True

            if isinstance(e, HKOAxiom):
                self.cache_axioms.append(e)
            elif isinstance(e, HKOAssertion):
                self.cache_assertions.append(e)

    def get_direct_sub_concepts_of(self, super_concept: HKOConcept) -> [HKOConcept]:
        print("Warning: incomplete implementation of get_direct_sub_concepts_of")
        sub_concepts = set()
        for e in self.cache_axioms:
            if isinstance(e, HKOSubConceptAxiom):
                if e.sup == super_concept:
                    sub_concepts.add(e.sub)
                # TODO: should look recursively into conjunctive expressions
                # elif isinstance(e.sub, HKOConjunctionExpression):
                #     # sub = (and c1 c2 super c3 ... cn)
                #     for exp in e.sub.concepts:
                #         if exp == super_concept:
                #             sub_concepts.add(e.sub)
        return list(sub_concepts)

    def get_direct_instances_of(self, concept: HKOConcept) -> [HKOIndividual]:
        print("Warning: incomplete implementation of get_direct_sub_concepts_of")
        return list(self.cache_concept_individual[concept].keys())

    def is_direct_instance_of(self, individual: HKOIndividual, concept: HKOConcept) -> bool:
        return self.cache_concept_individual[concept].get(individual, False)

    def is_instance_of(self, individual: HKOIndividual = None, concept: HKOConcept = None) -> bool:
        return self.is_direct_instance_of(individual=individual, concept=concept)

    def get_concept_assertion_pattern(self, concept: HKOConcept = None, individual: HKOIndividual = None) -> object:
        matched_assertions = set()
        for e in self.context.elements:
            if isinstance(e, HKOConceptAssertion):
                if concept is not None and e.concept != concept: continue
                if individual is not None and e.individual != individual: continue

                # match!
                matched_assertions.add(e)

        return list(matched_assertions)

    def get_related_values(self, property: HKOProperty, arg1: HKOIndividual) -> [Union[HKOIndividual, HKOLiteral]]:
        return list(self.cache_individual_prop_value.get(arg1, {}).get(property, {}).keys())

    def get_entities_relating_to(self, property: HKOProperty, arg2: HKOIndividual) -> [
        Union[HKOIndividual, HKOLiteral]]:
        return list(self.cache_value_prop_individual.get(arg2, {}).get(property, {}).keys())

    def get_related_value(self, property, arg1) -> Union[HKOIndividual, HKOLiteral]:
        lst = self.get_related_values(property, arg1)
        if len(lst) == 1:
            return lst[0]
        elif len(lst) == 0:
            return None
        else:
            raise Exception('Property returned more related values than expected.')

    def get_property_assertion_pattern(self, property=None, arg1=None, arg2=None) -> [HKOPropertyAssertion]:
        matched_assertions = set()
        for e in self.cache_assertions:
            if isinstance(e, HKOPropertyAssertion):
                if property is not None and e.property != property: continue
                if arg1 is not None and e.arg1 != arg1: continue
                if arg2 is not None and e.arg2 != arg2: continue

                # match!
                matched_assertions.add(e)

        return list(matched_assertions)
