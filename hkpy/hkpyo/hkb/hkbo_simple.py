""" HKB-based HKO store

    - Can load a single context without subcontexts
    - Deals with supercontext chains by using HKOContextExpandable as a placeholder for super contexts

    TODO: implement full support for refering to nodes in other contexts
    TODO: implement full support to load child contexts
    TODO: many other things

"""
from hkpy.hkbase import HKRepository
from hkpy.hklib import HKContext, HKConnector

from hkpyo.converters.HKOWriterHKG import HKOWriterHKG
from hkpyo.converters.HKOReaderHKG import HKOContextExpandable, HKOReaderHKG
from hkpyo.model import *
from hkpyo.converters.utils import encode_iri, decode_iri

def load_HKOContext_from_hkb(iri: str, repo : HKRepository) -> HKOContext:

    mgr = HKOContextManager.get_global_context_manager()

    if iri is None:
        hkg_contexts = repo.get_entities(f"""[id=null]""")
    else:
        hkg_contexts = repo.get_entities(f"""[id="{encode_iri(iri)}"]""")

    if len(hkg_contexts) == 0:
        raise Exception("Context IRI not found.")
    elif len(hkg_contexts) != 1:
        raise Exception(f"""Error retrieving HKBcontext {encode_iri(iri)}.""")

    hkg_context = hkg_contexts[0]

    hko_pcontext = mgr.createHKOContext(decode_iri(hkg_context.id_), HKOContextExpandable(iri=hkg_context.parent))

    hkg_context_graph = repo.get_entities(f"""[parent="{encode_iri(iri)}"]""")
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