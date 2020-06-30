###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###


from hkpy.hkbase import HKBase

from hkpy.hkpyo.hkb import hkbo_simple, load_HKOContext_from_hkb
from hkpy.hkpyo.hkb.hkbo import HKOContextManagerHKB
from hkpy.hkpyo.model import HKOContextManager



def test_save_to_hkb_ctxA():
    hkbase = HKBase(url='http://localhost:3000')

    repo = hkbase.delete_create_repository('testhko')

    cm = HKOContextManagerHKB(repo)

    hkctxFamilyContext = cm.createHKOContext("http://brl.ibm.com/hko/example1#FamilyContextA")

    cb = cm.getHKOContextBuilder(hkctxFamilyContext)

    hkcFather = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Father")
    hkcMan = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Man")
    hkcPerson = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Person")
    hkpHasChild = cb.getHKOProperty("http://brl.ibm.com/hko/example1#hasChild")


    exp1 = cb.getHKOExistsExpression(hkpHasChild, hkcPerson)
    exp2 = cb.getHKOConjunctionExpression(hkcMan, exp1)
    hkaxFatherDef = cb.getHKOSubConceptAxiom(hkcFather, exp2)

    cm.addAxiom(hkctxFamilyContext, hkaxFatherDef)

    indiv = cb.getHKOIndividual("http://brl.ibm.com/hko/example1#john")
    prop = cb.getHKOProperty("http://brl.ibm.com/hko/example1#hasAge")
    assertion = cb.getHKOPropertyAssertion(prop, indiv, 42)

    cm.addAssertion(hkctxFamilyContext, assertion)

    cm.commitHKOContext(hkctxFamilyContext)

    return hkctxFamilyContext

def test_save_to_hkb_ctxB():
    hkbase = HKBase(url='http://localhost:3000')

    repo = hkbase.connect_repository('testhko')

    cm = HKOContextManagerHKB(repo)

    hkctxFamilyContext = cm.createHKOContext("http://brl.ibm.com/hko/example1#FamilyContextB")

    cb = cm.getHKOContextBuilder(hkctxFamilyContext)

    hkcFather = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Father")
    hkcMan = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Man")
    hkcPerson = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Person")
    hkpHasChild = cb.getHKOProperty("http://brl.ibm.com/hko/example1#hasChild")

    exp1 = cb.getHKOExistsExpression(hkpHasChild, hkcPerson)
    exp2 = cb.getHKOConjunctionExpression(hkcMan, exp1)
    hkaxFatherDef = cb.getHKOSubConceptAxiom(hkcFather, exp2)

    cm.addAxiom(hkctxFamilyContext, hkaxFatherDef)

    indiv = cb.getHKOIndividual("http://brl.ibm.com/hko/example1#john")
    prop = cb.getHKOProperty("http://brl.ibm.com/hko/example1#hasAge")
    assertion = cb.getHKOPropertyAssertion(prop, indiv, 43)

    cm.addAssertion(hkctxFamilyContext, assertion)

    cm.commitHKOContext(hkctxFamilyContext)

    return hkctxFamilyContext

def test_load_from_hkb():
    hkbase = HKBase(url='http://localhost:3000')

    repo = hkbase.connect_repository('testhko')

    cm = HKOContextManagerHKB(repo)

    contextA = cm.readHKOContext('http://brl.ibm.com/hko/example1#FamilyContextA')

    contextB = cm.readHKOContext('http://brl.ibm.com/hko/example1#FamilyContextB')

    return contextA, contextB


print('Testing saving and loading from hkb:')
print('Generate and save:')
saved_ctxA = test_save_to_hkb_ctxA()
saved_ctxB = test_save_to_hkb_ctxB()

print(saved_ctxA)
print(saved_ctxB)

print('Loaded:')
loaded_ctxA, loaded_ctxB = test_load_from_hkb()

print(loaded_ctxA)
print(loaded_ctxB)

assert set(saved_ctxA.elements) == set(loaded_ctxA.elements)
assert set(saved_ctxB.elements) == set(loaded_ctxB.elements)


