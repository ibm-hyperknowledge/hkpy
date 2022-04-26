###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from hkpy.hkbase import HKRepository
from hkpy.hklib import HKContext, HKConnector, HKEntity

from hkpy.hkpyo.converters.HKOWriterHKG import HKOWriterHKG
from hkpy.hkpyo.converters.HKOReaderHKG import HKOContextExpandable, HKOReaderHKG
from hkpy.hkpyo.model import *
from hkpy.hkpyo.converters.utils import encode_iri, decode_iri


def load_HKOContext_from_hkb(iri: str, repo : HKRepository) -> HKOContext:

    mgr = HKOContextManager.get_global_context_manager()

    if iri is None:
        hkg_contexts = repo.filter_entities(f"""[id=null]""")
    else:
        hkg_contexts = repo.filter_entities(f"""[id="{encode_iri(iri)}"]""")

    if len(hkg_contexts) == 0:
        raise Exception("Context IRI not found.")
    elif len(hkg_contexts) != 1:
        raise Exception(f"""Error retrieving HKBcontext {encode_iri(iri)}.""")

    hkg_context = hkg_contexts[0]

    hko_pcontext = mgr.createHKOContext(decode_iri(hkg_context.id_), HKOContextExpandable(iri=hkg_context.parent))

    hkg_context_graph = repo.filter_entities(f"""[parent="{encode_iri(iri)}"]""")
    print("Loading ", len(hkg_context_graph), " entities from HKB")

    #
    # cb = self.getHKOContextBuilder(hko_pcontext)

    reader = HKOReaderHKG()
    reader.readHKOintoContext(hkg_context_graph, mgr.getHKOContextBuilder(hko_pcontext))

    return hko_pcontext


def save_HKOContext_to_hkb(context : HKOContext, repo : HKRepository):
    writer = HKOWriterHKG()
    buffer = writer.writeHKOContext(context)

    n_conntext = len(list(filter(lambda x: isinstance(x, HKConnector) or isinstance(x, HKContext), buffer)))

    print("Sending ", len(buffer), "entities to HKB. Nodes and links: ",len(buffer)-n_conntext, ". Connectors and contexts:", n_conntext)
    repo.add_entities(buffer)


def generate_hkentities_for_HKOContext(context : HKOContext) -> [HKEntity]:
    writer = HKOWriterHKG()
    buffer = writer.writeHKOContext(context)

    n_conntext = len(list(filter(lambda x: isinstance(x, HKConnector) or isinstance(x, HKContext), buffer)))

    print("Generating ", len(buffer), "entities to HKB. Nodes and links: ",len(buffer)-n_conntext, ". Connectors and contexts:", n_conntext)

    return buffer
