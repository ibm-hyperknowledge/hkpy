from hkpy.hkbase import HKBase

from hkb import hkbo_simple, load_HKOContext_from_hkb
from hkb.hkbo import HKOContextManagerHKB
from hkpyo.model import HKOContextManager



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

    print(hkctxFamilyContext)


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

    print(hkctxFamilyContext)

def test_load_from_hkb():
    hkbase = HKBase(url='http://localhost:3000')

    repo = hkbase.connect_repository('testhko')

    cm = HKOContextManagerHKB(repo)

    context = cm.readHKOContext('http://brl.ibm.com/hko/example1#FamilyContextA')

    print(context)

    context = cm.readHKOContext('http://brl.ibm.com/hko/example1#FamilyContextB')

    print(context)




print('Testing saving and loading from hkb:')
test_save_to_hkb_ctxA()
test_save_to_hkb_ctxB()
test_load_from_hkb()


