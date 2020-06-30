###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from pprint import pprint

from hkpy.hkpyo.model import *
from hkpy.hkpyo.reasoners import HKAssertedContextReasoner


def test_simple_reasoner():

    cm = HKOContextManager.get_global_context_manager()

    hkctx_test = cm.createHKOContext("http://brl.ibm.com/hko/example1#TestContext")

    cb = cm.getHKOContextBuilder(hkctx_test)

    c1 = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Entity1")
    c1_1 = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Entity1-1")
    c1_2 = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Entity1-2")
    c1_1_1 = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Entity1-1-1")
    c1_1_2 = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Entity1-1-2")


    cm.addAxiom(hkctx_test, cb.getHKOSubConceptAxiom(c1_1,c1))
    cm.addAxiom(hkctx_test, cb.getHKOSubConceptAxiom(c1_2,c1))
    cm.addAxiom(hkctx_test, cb.getHKOSubConceptAxiom(c1_1_1,c1_1))
    cm.addAxiom(hkctx_test, cb.getHKOSubConceptAxiom(c1_1_2,c1_1))


    e1_a = cb.getHKOIndividual("http://brl.ibm.com/hko/example1#e1-a")
    e1_b = cb.getHKOIndividual("http://brl.ibm.com/hko/example1#e1-b")
    e1_1_a = cb.getHKOIndividual("http://brl.ibm.com/hko/example1#e1_1-a")
    e1_1_b = cb.getHKOIndividual("http://brl.ibm.com/hko/example1#e1_1-b")
    e1_1_1_a = cb.getHKOIndividual("http://brl.ibm.com/hko/example1#e1_1_1-a")
    e1_1_1_b = cb.getHKOIndividual("http://brl.ibm.com/hko/example1#e1_1_1-b")

    cm.addAssertion(hkctx_test, cb.getHKOConceptAssertion(c1,e1_a))
    cm.addAssertion(hkctx_test, cb.getHKOConceptAssertion(c1,e1_b))
    cm.addAssertion(hkctx_test, cb.getHKOConceptAssertion(c1_1,e1_1_a))
    cm.addAssertion(hkctx_test, cb.getHKOConceptAssertion(c1_1,e1_1_b))
    cm.addAssertion(hkctx_test, cb.getHKOConceptAssertion(c1_1_1,e1_1_1_a))
    cm.addAssertion(hkctx_test, cb.getHKOConceptAssertion(c1_1_1,e1_1_1_b))


    p = cb.getHKOProperty("http://brl.ibm.com/hko/example1#associatedWith")

    #create relationships between brothers
    cm.addAssertion(hkctx_test, cb.getHKOPropertyAssertion(p, e1_a, e1_b))
    cm.addAssertion(hkctx_test, cb.getHKOPropertyAssertion(p, e1_1_a, e1_1_b))
    cm.addAssertion(hkctx_test, cb.getHKOPropertyAssertion(p, e1_1_1_a, e1_1_1_b))


    reasoner = HKAssertedContextReasoner(hkctx_test)

    print("Testing get_direct_sub_concepts_of")
    print("Direct sub-concepts of ", c1)
    print([str(e) for e in reasoner.get_direct_sub_concepts_of(c1)])

    print("Direct sub-concepts of ", c1_1)
    print([str(e) for e in reasoner.get_direct_sub_concepts_of(c1_1)])

    print("Direct sub-concepts of ", c1_1_1)
    print([str(e) for e in reasoner.get_direct_sub_concepts_of(c1_1_1)])

    print("\nTesting get_direct_instances_of")
    print("Direct instances of c1")
    print([str(e) for e in reasoner.get_direct_instances_of(c1)])

    print("Direct instances of c1_1")
    print([str(e) for e in reasoner.get_direct_instances_of(c1_1)])

    print("Direct instances of c1_1_1")
    print([str(e) for e in reasoner.get_direct_instances_of(c1_1_1)])

    print("\nTesting get_property_assertion_pattern")
    print("Assertions with patterh p,none,none")
    pprint([str(e) for e in reasoner.get_property_assertion_pattern(p, None, None)])

    print("Assertions with patterh p,e1_a,none")
    pprint([str(e) for e in reasoner.get_property_assertion_pattern(p, e1_a, None)])

    print("Assertions with patterh p, none, e1_a")
    pprint([str(e) for e in reasoner.get_property_assertion_pattern(p, None, e1_a)])

    print("Assertions with patterh none,none,none")
    pprint([str(e) for e in reasoner.get_property_assertion_pattern(None, None, None)])


test_simple_reasoner()