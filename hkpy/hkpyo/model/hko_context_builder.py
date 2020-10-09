from hkpy.hkpyo.model.hko_model import *

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

    def getHKOImportContextAssertion(self, sub: HKOContext, sup: HKOContext):
        return HKOImportContextAssertion(self.context, sub, sup)