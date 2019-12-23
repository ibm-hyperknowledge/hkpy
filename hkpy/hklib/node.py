# MIT License

# Copyright (c) 2019 IBM Hyperlinked Knowledge Graph

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Optional, Union, List, Dict

from . import HKEntity
from . import constants
from . import HKAnchor

__all__ = ['HKContext', 'HKNode', 'HKReferenceNode']

class HKContext(HKEntity):
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

        super().__init__(type_=constants.HKType.CONTEXT, id_=id_, properties=properties, metaproperties=metaproperties)
        self.parent = parent.id_ if isinstance(parent, HKEntity) else parent


class HKNode(HKEntity):
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

        super().__init__(type_=constants.HKType.NODE, id_=id_, properties=properties, metaproperties=metaproperties)
        self.parent = parent.id_ if isinstance(parent, HKContext) else parent
        self.interfaces = {}
    
    def add_anchors(self, anchors: Union[HKAnchor, List[HKAnchor]]) -> None:
        """
        """

        if not isinstance(anchors, (tuple, list)):
            anchors = [anchors]

        for a in anchors:
            interface = {
                "type" : a.type_
            }
            if(a.properties):
                interface['properties'] = a.properties
            
            self.interfaces[a.id_] = interface
          
class HKReferenceNode(HKEntity):
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

        super().__init__(type_=constants.HKType.REFERENCENODE, id_=id_, properties=properties, metaproperties=metaproperties)
        self.ref = ref.id_ if isinstance(ref, HKEntity) else ref
        self.parent = parent.id_ if isinstance(parent, HKContext) else parent