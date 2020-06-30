###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import json
from collections import Counter
from typing import TypeVar, Union, Dict

from hkpy import hkfy


CONCEPT_IRI = "http://brl.ibm.com/ontologies/hko#Concept"
PROPERTY_IRI = "http://brl.ibm.com/ontologies/hko#Property"
INDIVIDUAL_IRI = "http://brl.ibm.com/ontologies/hko#Individual"


#TOP_CONTEXT_IRI = "http://brl.ibm.com/ontology/hko$Everything"
TOP_CONTEXT_IRI = None
TOP_CONCEPT_IRI = "http://brl.ibm.com/ontologies/hko#Entity"
TOP_PROPERTY_IRI = "http://brl.ibm.com/ontologies/hko#property"

HKOContext = TypeVar('HKOContext')
HKOProperty = TypeVar('HKOProperty')
HKOContextManager = TypeVar("HKOContextManager")

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
        self.context = context


class HKONamedElement(HKOContextElement):
    """All named elements are contextualized """

    def __init__(self, iri: str, context: HKOContext) -> None:
        super().__init__(context=context)
        self.iri = iri

    def __str__(self) -> str:
        return self.iri

    #do not add hash and eq.


class HKOConceptExpression(HKOElement):
    pass


class HKOConcept(HKOConceptExpression, HKONamedElement):

    def __init__(self, iri: str, context: HKOContext):
        HKONamedElement.__init__(self, iri, context)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, HKOConcept):
            #it might happen that the same iri can identify concepts/properties and individuals
            return self.iri == o.iri
        else:
            return super().__eq__(o)

    def __hash__(self) -> int:
        return hash(str(HKOConcept)+self.iri)


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
            return self.iri == o.iri
        else:
            return super().__eq__(o)

    def __hash__(self) -> int:
        return hash(str(HKOIndividual)+self.iri)


class HKOProperty(HKONamedElement):

    def __init__(self, iri: str, context: HKOContext):
        HKONamedElement.__init__(self, iri, context)

    def __str__(self) -> str:
        return self.iri

    def __eq__(self, o: object) -> bool:
        if isinstance(o, HKOProperty):
            #it might happen that the same iri can identify concepts/properties and individuals
            return self.iri == o.iri
        else:
            return super().__eq__(o)

    def __hash__(self) -> int:
        return hash(str(HKOProperty)+self.iri)


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


class HKOContext(HKONamedElement):

    def __init__(self, iri: str, context: HKOContext, *elements: HKOElement):
        super().__init__(iri, context)
        self.elements = list(elements)

    def __eq__(self, o: object) -> bool:
        #simple implementation
        return isinstance(o, HKOContext) and o.iri == self.iri

    def __hash__(self) -> int:
        return hash(str(HKOContext) + self.iri)

    def addAxiom(self, axiom: HKOAxiom):
        self.elements.append(axiom)

    def axioms(self):
        return self.elements

    def addAssertion(self, assertion: HKOAxiom):
        self.elements.append(assertion)

    def __str__(self) -> str:
        str_elements = ',\n'.join(map(lambda x : str(x), self.elements))
        return f"""{self.iri}:[ {str_elements} ]"""

TOP_CONTEXT: HKOContext = HKOContext(TOP_CONTEXT_IRI, None)

class HKOContextBuilder:

    def __init__(self, context):
        self.context = context

    def getHKOConcept(self, iri: str) -> HKOConcept:
        return HKOConcept(iri, self.context)

    def getHKOProperty(self, iri: str) -> HKOProperty:
        return HKOProperty(iri, self.context)

    def getHKOExistsExpression(self, property: HKOProperty, concept: HKOConceptExpression) -> HKOExistsExpression:
        return HKOExistsExpression(property, concept)

    def getHKOForallExpression(self, property: HKOProperty, concept: HKOConceptExpression) -> HKOExistsExpression:
        return HKOForallExpression(property, concept)

    def getHKOConjunctionExpression(self, *concepts: HKOConceptExpression) -> HKOConjunctionExpression:
        return HKOConjunctionExpression(*concepts)

    def getHKODisjunctionExpression(self, *concepts: HKOConceptExpression) -> HKODisjunctionExpression:
        return HKODisjunctionExpression(*concepts)

    def getHKOConceptNegationExpression(self, concept: HKOConceptExpression) -> HKOConceptNegationExpression:
        return HKOConceptNegationExpression(concept)

    def getHKOSubConceptAxiom(self, sub: HKOConcept, sup: HKOConceptExpression) -> HKOSubConceptAxiom:
        return HKOSubConceptAxiom(self.context, sub, sup)

    def getHKOEquivalentConceptAxiom(self, conceptA: HKOConcept,
                                    conceptB: HKOConceptExpression) -> HKOEquivalentConceptAxiom:
        return HKOEquivalentConceptAxiom(self.context, conceptA, conceptB)

    def getHKOIndividual(self, iri) -> HKOIndividual:
        return HKOIndividual(iri, self.context)

    def getHKOConceptAssertion(self, concept : HKOConceptExpression, individual : HKOIndividual) -> HKOConceptAssertion:
        return HKOConceptAssertion(self.context, concept, individual)

    def getHKOPropertyAssertion(self, property: HKOProperty, arg1: HKOIndividual, arg2: Union[HKOIndividual, str, int, float]):
        return HKOPropertyAssertion(self.context, property, arg1, arg2)



class HKOContextManager:

    _manager_singleton : HKOContextManager = None

    def __init__(self):
        self.loaded_contexts: Dict[str, HKOContext] = {}


    def get_global_context_manager() -> HKOContextManager:
        if not HKOContextManager._manager_singleton:
            HKOContextManager._manager = HKOContextManager()
        return HKOContextManager._manager

    def getHKOContext(self, iri: str, parent: Union[str,HKOContext] = TOP_CONTEXT) -> HKOContext:
        if iri not in self.loaded_contexts:
            return None

        context = HKOContext(iri, parent)
        return context

    def createHKOContext(self, iri: str, parent: Union[str,HKOContext] = TOP_CONTEXT) -> HKOContext:
        if iri in self.loaded_contexts:
            raise Exception('Existing context already loaded.')

        context = HKOContext(iri, parent)
        self.loaded_contexts[iri] = context
        return context

    def getHKOContextBuilder(self, context=TOP_CONTEXT) -> HKOContextBuilder:
        return HKOContextBuilder(context=context)

    def addAxiom(self, context: HKOContext, *axioms: HKOAxiom) -> None:
        for axiom in axioms : axiom.context = context
        context.elements.extend(axioms)

    def addAssertion(self, context: HKOContext, *assertions: HKOAxiom) -> None:
        for assertion in assertions: assertion.context = context
        context.elements.extend(assertions)

    def saveHKOContextToFile(self, context : HKOContext, file_path : str):
        with open(file_path, mode="w") as f:
            from hkpy.hkpyo.converters.HKOWriterHKG import HKOWriterHKG
            writer = HKOWriterHKG()
            entities = writer.writeHKOContext(context)
            buffer = {}
            for x in entities:
                buffer[x.id_] = x.to_dict()
            json_entities = list(buffer.values())
            f.write(json.dumps(json_entities))

    def readHKOContextFromFile(self, context_iri : str, file_path : str) -> HKOContext:
        with open(file_path, mode="r") as f:
            file_data = f.read()
            file_data_json = json.loads(file_data)

            hkg_graph = {}
            for e in file_data_json:
                hke = hkfy(e)
                hkg_graph[hke.id_] = hke

            hkg_context = hkg_graph.get('<' + context_iri + '>', None)
            del hkg_graph[hkg_context.id_]

            if hkg_context is None:
                raise Exception('Context iri is not present in the file.')

            from hkpy.hkpyo.converters.HKOReaderHKG import HKOContextExpandable
            hko_pcontext = HKOContext(hkg_context.id_[1:-1], HKOContextExpandable(iri=hkg_context.parent))

            from hkpy.hkpyo.converters.HKOReaderHKG import HKOReaderHKG
            reader = HKOReaderHKG()
            reader.readHKOintoContextFromHKGJson(file_data_json, self.getHKOContextBuilder(hko_pcontext))

            return hko_pcontext