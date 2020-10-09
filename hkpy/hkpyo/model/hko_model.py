###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import json
from collections import Counter
from typing import TypeVar, Union, Dict, List, Set

from hkpy.hkpyo.model.ifi import IFI, IRI

CONCEPT_IRI = "http://brl.ibm.com/ontologies/hko#Concept"
PROPERTY_IRI = "http://brl.ibm.com/ontologies/hko#Property"
INDIVIDUAL_IRI = "http://brl.ibm.com/ontologies/hko#Individual"


TOP_CONCEPT_IRI = "http://brl.ibm.com/ontologies/hko#Entity"
TOP_PROPERTY_IRI = "http://brl.ibm.com/ontologies/hko#property"


HKOContext = TypeVar('HKOContext')
HKOProperty = TypeVar('HKOProperty')
HKONamedElement = TypeVar('HKONamedElement')

HKOLiteral = TypeVar('Union[str,int,float]')

HKO_NUMBER_DATATYPE = "http://brl.ibm.com/ontologies/hko#Number"
HKO_STRING_DATATYPE = "http://brl.ibm.com/ontologies/hko#String"


class HKOElement:
    """Any syntactic element should extend this class"""

    def __init__(self):
        pass


class HKOContextElement(HKOElement):

    def __init__(self, context: HKOContext) -> None:
        super().__init__()
        if context is None: raise Exception('Context cannot be None. Use top context instead.')
        self.context = context


class HKONamedElement(HKOContextElement):
    """All named elements are contextualized. IRIs are used to identify named elements, while IFI is used to identify
    the element in context, so that, in general ifi = context.iri # iri

    """

    def __init__(self, iri: str, context: HKOContext) -> None:
        self.iri = IRI(iri)
        from hkpy.hkpyo.model.base_entities import TOP_CONTEXT_IRI
        if iri == TOP_CONTEXT_IRI:
            #top concept is treated differently, as it has no parent context
            self.ifi = IFI(f"<{self.iri.__str__()}>")
            self.context = None
        else:
            super().__init__(context=context)
            iri = self.iri.__str__() if self.iri[0] == '<' and self.iri[-1] == '>' else f"<{self.iri.__str__()}>"
            self.ifi = IFI(context.ifi, iri)

    def __str__(self) -> str:
        return str(self.ifi)


    #do not add hash and eq.


class HKOConceptExpression(HKOElement):
    pass


class HKOConcept(HKOConceptExpression, HKONamedElement):

    def __init__(self, iri: str, context: HKOContext):
        HKONamedElement.__init__(self, iri, context)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, HKOConcept):
            #it might happen that the same iri can identify concepts/properties and individuals
            return self.ifi == o.ifi
        else:
            return super().__eq__(o)

    def __hash__(self) -> int:
        return hash(str(HKOConcept)+str(self.ifi))


class HKOExistsExpression(HKOConceptExpression):

    def __init__(self, property: HKOProperty, concept: HKOConceptExpression):
        super().__init__()
        self.property = property
        self.concept = concept

    def __str__(self) -> str:
        return f"""(exists {self.property} {self.concept})"""

    def __eq__(self, o: object) -> bool:
        return isinstance(o, HKOExistsExpression) and o.concept == self.concept and o.property == self.property

    def __hash__(self) -> int:
        return hash(hash(HKOExistsExpression) + self.property.__hash__() + self.concept.__hash__())


class HKOForallExpression(HKOConceptExpression):

    def __init__(self, property: HKOProperty, concept: HKOConceptExpression):
        super().__init__()
        self.property = property
        self.concept = concept

    def __str__(self) -> str:
        return f"""(forall {self.property} {self.concept})"""

    def __eq__(self, o: object) -> bool:
        return isinstance(o, HKOForallExpression) and o.concept == self.concept and o.property == self.property

    def __hash__(self) -> int:
        return hash(hash(HKOForallExpression) + self.property.__hash__() + self.concept.__hash__())

class HKOConjunctionExpression(HKOConceptExpression):

    def __init__(self, *concepts: HKOConceptExpression):
        super().__init__()
        self.concepts = tuple(concepts)

    def __str__(self) -> str:
        return f"""(and {' '.join(map(lambda x : str(x), self.concepts))})"""


    def __eq__(self, o: object) -> bool:
        return isinstance(o, HKOConjunctionExpression) and Counter(o.concepts) == Counter(self.concepts)


    def __hash__(self) -> int:
        #TODO: check if self.concepts should be changed to a set implementation
        return hash(hash(HKOConjunctionExpression) + sum(hash(e) for e in self.concepts))


class HKODisjunctionExpression(HKOConceptExpression):

    def __init__(self, *concepts: HKOConceptExpression):
        super().__init__()
        self.concepts = concepts

    def __str__(self) -> str:
        return f"""(or {' '.join(map(lambda x : str(x), self.concepts))})"""

    def __eq__(self, o: object) -> bool:
        return isinstance(o, HKODisjunctionExpression) and Counter(o.concepts) == Counter(self.concepts)


    def __hash__(self) -> int:
        #TODO: check if self.concepts should be changed to a set implementation
        return hash(hash(HKODisjunctionExpression) + sum(hash(e) for e in self.concepts))

class HKOConceptNegationExpression(HKOConceptExpression):

    def __init__(self, concept_expr: HKOConceptExpression):
        super().__init__()
        self.concept_expr = concept_expr

    def __str__(self) -> str:
        return f"""(not {self.concept_expr})"""


# class HKOPropertyExpression(HKOElement):
#     context: HKOContext
#
#     def __init__(self, context: HKOContext):
#         super().__init__()
#         self.context = context


class HKOIndividual(HKONamedElement):

    def __init__(self, iri: str, context: HKOContext):
        HKONamedElement.__init__(self, iri, context)

    def __str__(self) -> str:
        return self.iri

    def __eq__(self, o: object) -> bool:
        if isinstance(o, HKOIndividual):
            #it might happen that the same iri can identify concepts/properties and individuals
            return self.ifi == o.ifi
        else:
            return super().__eq__(o)

    def __hash__(self) -> int:
        return hash(str(HKOIndividual)+self.ifi)


class HKOProperty(HKONamedElement):

    def __init__(self, iri: str, context: HKOContext):
        HKONamedElement.__init__(self, iri, context)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, HKOProperty):
            #it might happen that the same iri can identify concepts/properties and individuals
            return self.ifi == o.ifi
        else:
            return super().__eq__(o)

    def __hash__(self) -> int:
        return hash(str(HKOProperty)+str(self.ifi))


# class HKORoleExpression(HKOPropertyExpression) :
#     property: HKOProperty
#     //role: HKORole
#     concept: HKOConceptExpression
#
#     constructor(iri: string, context: HKOContext, property: HKOProperty, concept: HKOConcept)
#         super(context)
#         self.property = property
#         //self.role = role
#         self.concept = concept
#
#

class HKOAxiom(HKOContextElement):
    def __init__(self, context: HKOContext):
        super().__init__(context=context)


class HKOSubConceptAxiom(HKOAxiom):

    def __init__(self, context: HKOContext, sub: HKOConceptExpression, sup: HKOConceptExpression):
        assert(isinstance(context, HKOContext))
        assert(isinstance(sub, HKOConceptExpression))
        assert(isinstance(sup, HKOConceptExpression))

        super().__init__(context)
        self.sub = sub
        self.sup = sup

    def __str__(self) -> str:
        return f"""(subconcept {self.sub} {self.sup})"""

    def __eq__(self, o: object) -> bool:
        return isinstance(o, HKOSubConceptAxiom) and o.context == self.context and o.sub == self.sub and o.sup == self.sup

    def __hash__(self) -> int:
        return hash(hash(HKOSubConceptAxiom) + hash(self.context) + hash(self.sub)+ hash(self.sup))

class HKOEquivalentConceptAxiom(HKOAxiom):

    def __init__(self, context: HKOContext, conceptA: HKOConceptExpression, conceptB: HKOConceptExpression):
        assert(isinstance(context, HKOContext))
        assert(isinstance(conceptA, HKOConceptExpression))
        assert(isinstance(conceptB, HKOConceptExpression))

        super().__init__(context)
        self.conceptA = conceptA
        self.conceptB = conceptB

    def __str__(self) -> str:
        return f"""(eqconcept {self.conceptA} {self.conceptB})"""

    def __eq__(self, o: object) -> bool:
        return isinstance(o, HKOEquivalentConceptAxiom) and o.context == self.context and o.conceptA == self.conceptA and o.conceptB == self.conceptB

    def __hash__(self) -> int:
        return hash(str(HKOEquivalentConceptAxiom) + hash(self.context) + hash(self.conceptA)+ hash(self.conceptB))

class HKOAssertion(HKOContextElement):
    def __init__(self, context: HKOContext):
        super().__init__(context=context)


class HKOConceptAssertion(HKOAssertion):

    def __init__(self, context: HKOContext, concept: HKOConceptExpression, individual: HKOIndividual):
        super().__init__(context)
        assert(isinstance(concept,HKOConceptExpression))
        assert(isinstance(individual,HKOIndividual))
        self.concept = concept
        self.individual = individual

    def __str__(self) -> str:
        return f"""({self.concept} {self.individual})"""

    def __eq__(self, o: object) -> bool:
        return isinstance(o, HKOConceptAssertion) \
            and o.context == self.context \
                and o.concept == self.concept \
                and o.individual == self.individual

    def __hash__(self) -> int:
        return hash(hash(HKOConceptAssertion) +
                    self.context.__hash__()
                    + self.concept.__hash__()
                    + self.individual.__hash__())

class HKOPropertyAssertion(HKOAssertion):

    def __init__(self, context: HKOContext, property: HKOProperty, arg1: HKOIndividual, arg2: Union[HKOIndividual, str, int, float]):
        assert(isinstance(property,HKOProperty))
        assert(isinstance(arg1,HKOIndividual))
        assert(isinstance(arg2,HKOIndividual) or isinstance(arg2,str) or isinstance(arg2,int) or isinstance(arg2,float))
        super().__init__(context)
        self.property = property
        self.arg1 = arg1
        #self.arg2 = arg2
        self.arg2 = arg2 if isinstance(arg2, HKOIndividual) else str(arg2)

    def __str__(self) -> str:
        if isinstance(self.arg2, HKOIndividual):
            return f"""({self.property} {self.arg1} {self.arg2})"""
        else:
            return f"""({self.property} {self.arg1} "{str(self.arg2)}")"""

    def __eq__(self, o: object) -> bool:
        return isinstance(o, HKOPropertyAssertion) \
            and o.context == self.context \
            and o.property == self.property \
                and o.arg1 == self.arg1 \
                and o.arg2 == self.arg2

    def __hash__(self) -> int:
        return hash(hash(HKOConceptAssertion)
                    + self.context.__hash__()
                    + self.property.__hash__()
                    + self.arg1.__hash__()
                    + self.arg2.__hash__())

class HKOImportContextAssertion(HKOAxiom):

    def __init__(self, context: HKOContext, sub: HKOContext, sup: HKOContext):
        super().__init__(context)
        self.sub = sub
        self.sup = sup

    def __str__(self) -> str:
        return f"""(import {self.sub} {self.sup})"""

    def __eq__(self, o: object) -> bool:
        return isinstance(o, HKOImportContextAssertion) and o.context == self.context and o.sub == self.sub and o.sup == self.sup

    def __hash__(self) -> int:
        return hash(hash(HKOImportContextAssertion) + hash(self.context) + hash(self.sub)+ hash(self.sup))


class HKOContext(HKONamedElement):

    def __init__(self, iri: IFI, context: HKOContext, children_contexts : Set[HKOElement] = None,  *elements: HKOElement):
        super().__init__(iri, context)
        self._elements = set(elements)

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, v : Set[HKOElement]):
        if not isinstance(v, set) : raise TypeError()
        self._elements = v

    def add_axiom(self, axiom : HKOAxiom):
        self._elements.add(axiom)

    def add_assertion(self, assertion : HKOAssertion):
        self._elements.add(assertion)

    def __eq__(self, o: object) -> bool:
        #simple implementation
        return isinstance(o, HKOContext) and o.ifi == self.ifi

    def __hash__(self) -> int:
        return hash(str(HKOContext) + str(self.ifi))

    def __str__(self) -> str:
        str_elements = ',\n'.join(map(lambda x : str(x), self.elements))
        return f"""{self.ifi}:[ {str_elements} ]"""



