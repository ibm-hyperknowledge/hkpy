from typing import Optional, Dict, Union, List

from hkpy.hklib import HKNode, HKLink, HKConnector, HKContext, HKAnchor
from hkpy.hklib.fi.fi import FI
from hkpy.hklib.fi.fianchor import FIAnchor
from hkpy.utils import LAMBDA


class HKGraphBuilder:

    @staticmethod
    def create_hknode(id_, parent=None):
        return HKNode(id_, parent);

    @staticmethod
    def createDataNode(id_, mimeType, data, parent=None):
        return HKNode(id_, parent);

    @staticmethod
    def create_hklink(connector: Union[str, HKConnector],
                      id_: Optional[str] = None,
                      parent: Optional[Union[str, HKContext]] = None,
                      binds: Optional[Dict] = None,
                      properties: Optional[Dict] = None,
                      metaproperties: Optional[Dict] = None) -> HKLink:
        return HKLink(connector=connector,
                      id_=id_,
                      parent=parent,
                      binds=binds,
                      properties=properties,
                      metaproperties=metaproperties)

    @staticmethod
    def create_spo_hklink(connector: Union[str, HKConnector],
                          subject: Union[str, HKNode,  List[Union[str, HKNode]]],
                          object: Union[str, HKNode, List[Union[str, HKNode]]],
                          parent: Optional[Union[str, HKContext]] = None,
                          id_: Optional[str] = None, ):
        link = HKGraphBuilder.create_anchored_spo_hklink(connector, subject, LAMBDA, object, LAMBDA,
                                                    parent=parent, id_=id_)

        return link

    @staticmethod
    def create_anchored_spo_hklink(connector: Union[str, HKConnector],
                                   subject: Union[str, HKNode,  List[Union[str, HKNode]]],
                                   subject_anchor: Union[str, HKAnchor, FIAnchor],
                                   object: Union[str, HKNode,  List[Union[str, HKNode]]],
                                   object_anchor: Union[str, HKAnchor, FIAnchor],
                                   parent: Optional[Union[str, HKContext]] = None,
                                   id_: Optional[str] = None, ):
        link = HKGraphBuilder.create_hklink(connector=connector, parent=parent, id_=id_)

        sa = subject_anchor.__str__() if subject_anchor else None
        oa = object_anchor.__str__() if object_anchor else None

        link.add_bind('subject', subject.__str__(), sa)
        link.add_bind('object', object.__str__(), oa)

        return link

    @staticmethod
    def create_ifi_spo_hklink(connector: Union[str, HKConnector],
                              subject: FI,
                              object: FI,
                              parent: Optional[Union[str, HKContext]] = None,
                              id_: Optional[str] = None):
        link = HKGraphBuilder.create_anchored_spo_hklink(connector, subject.artifact, subject.anchor, object.artifact,
                                                    object.anchor,
                                                    parent=parent, id_=id_)
        return link

    @staticmethod
    def create_subconceptof_link(sub, sup, parent = None):
        return HKGraphBuilder.create_ifi_spo_hklink('subConceptOf', sub, sup, parent)

    @staticmethod
    def create_instanceof_link(instance, concept, parent = None):
        return HKGraphBuilder.create_ifi_spo_hklink('instanceOf', instance, concept, parent)