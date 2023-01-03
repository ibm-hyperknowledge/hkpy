###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import Optional, Union, List, Dict
from io import TextIOWrapper, BufferedReader, BufferedIOBase, BytesIO

import os
import datetime
import mimetypes

from hkpy.hklib.entity import HKParentedEntity
from . import HKEntity
from . import constants
from . import HKConnector
from . import HKLink
from . import HKAnchor

__all__ = ['HKContext', 'HKNode', 'HKReferenceNode', 'HKTrail', 'HKAnyNode', 'HKDataNode']

class HKAnyNode(HKParentedEntity):
    def __init__(self, type_, id_, parent, properties, metaproperties):
        super().__init__(type_, id_, properties=properties, metaproperties=metaproperties)
        self.parent = parent.id_ if isinstance(parent, HKContext) else parent
        self.interfaces = {}

    def add_anchors(self, anchors: Union[HKAnchor, List[HKAnchor]]) -> None:
        """ Add anchors to the node.

        Parameters
        ----------
        anchors: (Union[HKAnchor, List[HKAnchor]]) the anchor or list of anchors
        """

        if not isinstance(anchors, (tuple, list)):
            anchors = [anchors]

        for anchor in anchors:
            interface = {
                'type' : anchor.type_
            }
            if anchor.properties:
                interface['properties'] = anchor.properties

            if anchor.metaproperties:
                interface['metaproperties'] = anchor.metaproperties
            
            self.interfaces[anchor.key] = interface
    
    def to_dict(self) -> Dict:
        """ Convert a HKAnyNode to a dict.

        Returns
        -------
        (Dict) The HKAnyNode's correspondent dict
        """

        jobj = super().to_dict()

        jobj['interfaces'] = self.interfaces

        return jobj

class HKContext(HKAnyNode):
    """
    """

    def __init__(self,
                 id_: str,
                 parent: Optional[Union[str, HKEntity]]=None,
                 properties: Optional[Dict]=None,
                 metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKContext class.
    
        Parameters
        ----------
        id_: (str) the context's unique id
        parent: (Optional[Union[str, HKEntity]]) the context in which the context is setted
        properties: (Optional[Dict]) any context's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """

        super().__init__(type_=constants.HKType.CONTEXT, id_=id_, parent=parent, properties=properties, metaproperties=metaproperties)

class HKNode(HKAnyNode):
    """
    """

    def __init__(self,
                 id_: str,
                 parent: Optional[Union[str, HKContext]]=None,
                 properties: Optional[Dict]=None,
                 metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKNode class.
    
        Parameters
        ----------
        id_: (str) the node's unique id
        parent: (Optional[Union[str, HKContext]]) the context in which the node is setted
        properties: (Optional[Dict]) any link's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """

        super().__init__(type_=constants.HKType.NODE, id_=id_, parent=parent, properties=properties, metaproperties=metaproperties)
               
class HKReferenceNode(HKAnyNode):
    """
    """

    def __init__(self,
                 ref: Optional[Union[str, HKEntity]]=None,
                 id_: Optional[str]=None,
                 parent: Optional[Union[str, HKContext]]=None,
                 properties: Optional[Dict]=None,
                 metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKReferenceNode class.
    
        Parameters
        ----------
        ref: (Optional[Union[str, HKEntity]]) the entity that the reference node make referece
        id_: (Optional[str]) the reference node's unique id
        parent: (Optional[Union[str, HKContext]]) the context in which the reference node is setted
        properties: (Optional[Dict]) any reference node's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """

        super().__init__(type_=constants.HKType.REFERENCENODE, id_=id_, parent=parent, properties=properties, metaproperties=metaproperties)
        self.ref = ref.id_ if isinstance(ref, HKEntity) else ref

    def to_dict(self) -> Dict:
        """ Convert a HKReferenceNode to a dict.

        Returns
        -------
        (Dict) The HKReferenceNode's correspondent dict
        """

        jobj = super().to_dict()

        jobj['ref'] = self.ref

        return jobj


class HKDataNode(HKAnyNode):  
    """
    A HKDataNode is a HKNode that carries media information, together with it mimetype. It is akin to a general Content Node.
    """

    def __init__(self, raw_data: any, mimeType: Optional[str]=None, id_: Optional[str]=None, parent: Optional[Union[str, HKContext]]=None, 
                 properties: Optional[Dict]=None, metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKDataNode class.
    
        Parameters
        ----------
        raw_data: (Optional[Union[str, HKEntity]]) The data which this entities represents
        mimeType: Optional[str]: String specifying the data type.
        id_: (Optional[str]) the reference node's unique id
        parent: (Optional[Union[str, HKContext]]) the context in which the reference node is setted
        properties: (Optional[Dict]) any reference node's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """  

        if isinstance(raw_data, (TextIOWrapper, BufferedReader, BufferedIOBase)):
            filename = os.path.basename(raw_data.name)
            raw_data = raw_data.buffer.read()
        elif isinstance(raw_data, str) and os.path.isfile(raw_data):
            filename = os.path.basename(raw_data)
            raw_data = open(filename,'rb').read()
        elif isinstance(raw_data, bytes): 
            if not id_:
                raise HKpyError(message='You should provide a node id.')
            filename = id_

        if not id_:
            id_ = filename

        if not properties:
            properties = {}

        if mimeType:
            properties['mimeType'] = mimeType
        else:
            if 'mimeType' in properties:
                mimeType = properties['mimeType']
            else:
                mimeType = mimetypes.guess_type(filename)[0]
                properties['mimeType'] = mimeType

        super().__init__(type_=constants.HKType.NODE, id_=id_, parent=parent, properties=properties, metaproperties=metaproperties)
        self.raw_data = raw_data

    def to_dict(self) -> Dict:
        """ Convert a HKDataNode to a dict.
        
        Returns
        -------
        (Dict) The HKDataNode's correspondent dict
        """
        jobj = super().to_dict()
        
        jobj['raw_data'] = self.raw_data
        return jobj

class HKTrail(HKAnyNode):
    """
    """

    def __init__(self,
                 id_: Optional[str]=None,
                 parent: Optional[Union[str, HKContext]]=None,
                 properties: Optional[Dict]=None,
                 metaproperties: Optional[Dict]=None):
        """ Initialize an instance of HKTrail class.
    
        Parameters
        ----------
        id_: (str) the node's unique id
        parent: (Optional[Union[str, HKContext]]) the context in which the node is setted
        properties: (Optional[Dict]) any link's property and its value
        metaproperties: (Optional[Dict]) the type of any property
        """
        super().__init__(type_=constants.HKType.TRAIL, id_=id_, parent=parent, properties=properties, metaproperties=metaproperties)
        self.steps = []        

    def add_step(self, key: str, properties: Optional[Dict]=None) -> None:
        """ Add a step to the trail.

        Parameters
        ----------
        key: (str) the anchor's unique key
        properties: (Optional[Dict]) any link's property and its value
        """

        ts = properties['begin'] if 'begin' in properties else str(datetime.datetime.now())

        if len(self.steps) > 0:
            last_step = self.steps[-1]
            if 'end' not in self.interfaces[last_step].properties:
                self.interfaces[last_step].properties['end'] = ts
        
        new_step = {
            'key': key,
            'begin': ts
        }

        self.steps.append(new_step)
        self.add_anchors(HKAnchor(key=key, type_=constants.AnchorType.TEMPORAL, properties=properties))

    def create_links_from_steps(self) -> List[HKEntity]:
        """ Add a step to the trail.

        Returns
        -------
        (List[HKEntity]) list of created entities
        """

        cnt_occurs = HKConnector(id_='occurs', class_name=constants.ConnectorType.FACTS)
        cnt_occurs.add_roles(subject=constants.RoleType.SUBJECT, object=constants.RoleType.OBJECT)

        virtual_entities = [cnt_occurs]

        for ikey, ivalues in self.interfaces.items():
            interProp = ivalues.properties
            if interProp == {}:
                continue
            
            if 'obj' in interProp:
                
                lk = HKLink(connector=cnt_occurs.id_, parent=self.parent)

                anchor = None
                if 'objInterface' in interProp:
                    anchor = interProp['objInterface']
                lk.add_bind(role='subject', entity=interProp['obj'], anchor=anchor)
                lk.add_bind(role='object', entity=self.id_)
                virtual_entities.append(lk)

        return virtual_entities