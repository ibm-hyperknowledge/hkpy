###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import TypeVar

from hkpy.hkbase import HKRepository

from hkpy.hkpyo.converters.HKOReaderHKG import HKOContextExpandable
from hkpy.hkpyo.converters.utils import encode_iri, decode_iri

from hkpy.hkpyo.model import *

HKOContextManagerHKB = TypeVar('HKOContextManagerHKB')


class HKOContextHKB(HKOContext):

    def __init__(self, iri: str, context: HKOContext, *elements: HKOElement):
        super().__init__(iri, context)
        self.elements: [HKOAxiom] = elements

    def addAxiom(self, axiom: HKOAxiom):
        self.elements.append(axiom)

    def axioms(self):
        return self.elements





class HKOContextBuilderHKB(HKOContextBuilder):

    def __init__(self, context, context_manager: HKOContextManagerHKB):
        self.context = context
        self.context_manager = context_manager


class HKOContextManagerHKB(HKOContextManager):
    """ Context-centric model loader"""

    def __init__(self, repo : HKRepository):
        super().__init__()
        self.repo = repo

    def readHKOContext(self, iri: str) -> HKOContext:

        if iri is None:
            hkg_contexts = self.repo.filter_entities(f"""[id=null]""")
        else:
            hkg_contexts = self.repo.filter_entities(f"""[id="{encode_iri(iri)}"]""")

        if len(hkg_contexts) == 0:
            raise Exception("Context IRI not found.")
        elif len(hkg_contexts) != 1:
            raise Exception(f"""Error retrieving HKBcontext {iri}.""")

        hkg_context = hkg_contexts[0]

        hko_pcontext = HKOContext(decode_iri(hkg_context.id_), HKOContextExpandable(iri=decode_iri(hkg_context.parent)))

        hkg_context_graph = self.repo.filter_entities(f"""[parent="{encode_iri(iri)}"]""")

        #
        # cb = self.getHKOContextBuilder(hko_pcontext)

        from hkpy.hkpyo.converters.HKOReaderHKG import HKOReaderHKG
        reader = HKOReaderHKG()
        reader.readHKOintoContext(hkg_context_graph, self.getHKOContextBuilder(hko_pcontext))

        self.loaded_contexts[hko_pcontext.iri] = hko_pcontext

        return hko_pcontext

    def getHKOContextBuilder(self, context=TOP_CONTEXT):
        return HKOContextBuilderHKB(context=context, context_manager=self)

    def addAxiom(self, context: HKOContext, axiom: HKOAxiom) -> None:
        axiom.context = context
        context.elements.append(axiom)

    def commitHKOContext(self, context : HKOContext):
        from hkpy.hkpyo.converters.HKOWriterHKG import HKOWriterHKG
        writer = HKOWriterHKG()
        buffer = writer.writeHKOContext(context)
        self.repo.add_entities(buffer)







