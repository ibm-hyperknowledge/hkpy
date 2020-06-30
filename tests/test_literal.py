###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from hkpy.hkpyo.model import *


def test_save_to_file():
    cm = HKOContextManager()

    hkctxSomeContext = cm.createHKOContext("http://brl.ibm.com/hko/example1#SomeContext")

    cb = cm.getHKOContextBuilder(hkctxSomeContext)

    indiv = cb.getHKOIndividual("http://brl.ibm.com/hko/example1#john")
    prop = cb.getHKOProperty("http://brl.ibm.com/hko/example1#hasAge")
    assertion = cb.getHKOPropertyAssertion(prop, indiv, 42)

    cm.addAssertion(hkctxSomeContext, assertion)

    cm.saveHKOContextToFile(hkctxSomeContext,'test.json')

    print(hkctxSomeContext)

def test_load_from_file():
    cm = HKOContextManager()

    context = cm.readHKOContextFromFile('http://brl.ibm.com/hko/example1#SomeContext', 'test.json')

    print(context)

test_save_to_file()
test_load_from_file()