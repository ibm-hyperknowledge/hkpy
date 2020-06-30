###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from hkpy.hkbase import HKBase

from hkpy.hkpyo.hkb import hkbo_simple, load_HKOContext_from_hkb
from hkpy.hkpyo.hkb.hkbo import HKOContextManagerHKB
from hkpy.hkpyo.model import HKOContextManager


def test_save_to_file():
    cm = HKOContextManager()

    hkctxFamilyContext = cm.createHKOContext("http://brl.ibm.com/hko/example1#FamilyContext")

    cb = cm.getHKOContextBuilder(hkctxFamilyContext)

    hkcFather = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Father")
    hkcMan = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Man")
    hkcPerson = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Person")
    hkpHasChild = cb.getHKOProperty("http://brl.ibm.com/hko/example1#hasChild")

    exp1 = cb.getHKOExistsExpression(hkpHasChild, hkcPerson)
    exp2 = cb.getHKOConjunctionExpression(hkcMan, exp1)
    hkaxFatherDef = cb.getHKOSubConceptAxiom(hkcFather, exp2)

    cm.addAxiom(hkctxFamilyContext, hkaxFatherDef)

    cm.saveHKOContextToFile(hkctxFamilyContext,'test.json')

    print(hkctxFamilyContext)

def test_load_from_file():
    cm = HKOContextManager()

    context = cm.readHKOContextFromFile('http://brl.ibm.com/hko/example1#FamilyContext', 'test.json')

    print(context)


def test_save_to_hkb():
    hkbase = HKBase(url='http://localhost:3000')

    repo = hkbase.delete_create_repository('testhko')

    cm = HKOContextManagerHKB(repo)

    hkctxFamilyContext = cm.createHKOContext("http://brl.ibm.com/hko/example1#FamilyContext")

    cb = cm.getHKOContextBuilder(hkctxFamilyContext)

    hkcFather = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Father")
    hkcMan = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Man")
    hkcPerson = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Person")
    hkpHasChild = cb.getHKOProperty("http://brl.ibm.com/hko/example1#hasChild")

    exp1 = cb.getHKOExistsExpression(hkpHasChild, hkcPerson)
    exp2 = cb.getHKOConjunctionExpression(hkcMan, exp1)
    hkaxFatherDef = cb.getHKOSubConceptAxiom(hkcFather, exp2)

    cm.addAxiom(hkctxFamilyContext, hkaxFatherDef)

    cm.commitHKOContext(hkctxFamilyContext)

    print(hkctxFamilyContext)

def test_load_from_hkb():
    hkbase = HKBase(url='http://localhost:3000')

    repo = hkbase.connect_repository('testhko')

    cm = HKOContextManagerHKB(repo)

    context = cm.readHKOContext('http://brl.ibm.com/hko/example1#FamilyContext')

    print(context)


def test_save_to_hkb_simple():


    cm = HKOContextManager()

    hkctxFamilyContext = cm.createHKOContext("http://brl.ibm.com/hko/example1#FamilyContext")

    cb = cm.getHKOContextBuilder(hkctxFamilyContext)

    hkcFather = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Father")
    hkcMan = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Man")
    hkcPerson = cb.getHKOConcept("http://brl.ibm.com/hko/example1#Person")
    hkpHasChild = cb.getHKOProperty("http://brl.ibm.com/hko/example1#hasChild")

    exp1 = cb.getHKOExistsExpression(hkpHasChild, hkcPerson)
    exp2 = cb.getHKOConjunctionExpression(hkcMan, exp1)
    hkaxFatherDef = cb.getHKOSubConceptAxiom(hkcFather, exp2)

    cm.addAxiom(hkctxFamilyContext, hkaxFatherDef)

    hkbase = HKBase(url='http://localhost:3000')
    repo = hkbase.delete_create_repository('testhko')

    hkbo_simple.save_HKOContext_to_hkb(hkctxFamilyContext, repo)

    print(hkctxFamilyContext)


def test_load_from_hkb_simple():
    hkbase = HKBase(url='http://localhost:3000')

    repo = hkbase.connect_repository('testhko')

    context = load_HKOContext_from_hkb('http://brl.ibm.com/hko/example1#FamilyContext', repo)

    print(context)

print('Testing saving and loading from file:')
test_save_to_file()
test_load_from_file()

print()

print('Testing saving and loading from hkb:')
test_save_to_hkb()
test_load_from_hkb()

print()

print('Testing saving and loading from hkb:')
test_save_to_hkb_simple()
test_load_from_hkb_simple()

print()
