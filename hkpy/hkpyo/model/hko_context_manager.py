import json
from typing import TypeVar, Union

from hkpy.hkpyo import IFI, HKOContext, HKOAxiom
from hkpy.hkpyo.model.hko_context_builder import HKOContextBuilder
from hkpy.hkpyo.model.base_entities import TOP_CONTEXT
from hkpy.hklib import hkfy

HKOContextManager = TypeVar("HKOContextManager")

class HKOContextManager:

    _manager_singleton : HKOContextManager = None

    def __init__(self):
        self.loaded_contexts: Dict[IFI, HKOContext] = {}

    @classmethod
    def get_global_context_manager(cls) -> HKOContextManager:
        if not HKOContextManager._manager_singleton:
            HKOContextManager._manager = HKOContextManager()
        return HKOContextManager._manager

    def getHKOContext(self, iri: str, parent: Union[str,HKOContext] = TOP_CONTEXT) -> HKOContext:
        ifi = IFI(parent.ifi, iri)
        if ifi not in self.loaded_contexts:
            return HKOContext(iri, parent)
            self.loaded_contexts[ifi] = context


        context = HKOContext(iri, parent)
        return context

    def createHKOContext(self, iri: str, parent: Union[str,HKOContext] = TOP_CONTEXT) -> HKOContext:
        ifi = IFI(parent.ifi, iri)
        if ifi in self.loaded_contexts:
            raise Exception('Existing context already loaded.')

        return self.getHKOContext(iri, parent)

    def getHKOContextBuilder(self, context=TOP_CONTEXT) -> HKOContextBuilder:
        return HKOContextBuilder(context=context)

    def addAxiom(self, context: HKOContext, *axioms: HKOAxiom) -> None:
        for axiom in axioms : axiom.context = context
        context.elements.update(axioms)

    def addAssertion(self, context: HKOContext, *assertions: HKOAxiom) -> None:
        for assertion in assertions: assertion.context = context
        context.elements.update(assertions)

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
            hko_pcontext = HKOContext(hkg_context.id_[1:-1], HKOContextExpandable(iri=hkg_context.parent[1:-1]))

            from hkpy.hkpyo.converters.HKOReaderHKG import HKOReaderHKG
            reader = HKOReaderHKG()
            reader.readHKOintoContextFromHKGJson(file_data_json, hko_pcontext)

            return hko_pcontext