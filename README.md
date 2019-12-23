# hkpy: a Python Framework for Hyperknowledge

## Getting Started

### Connecting to a [Hyperknowledge Base](#)

```
from hkpy.hkbase import HKBase

hkbase = HKBase(url='foo.bar', auth='some_token')
```

### Creating a [Hyperknowledge Repository](#)

```
from hkpy.hkbase import HKBase, HKRepository

hkbase = HKBase(url='foo.bar', auth='some_token')
hkrepository = hkbase.create_repository(name='new_repository')
```

### Creating a [Context](#)

```
from hkpy.hklib import Context

new_context = Context(id_='new_context')
```

### Creating a [Node](#)

```
from hkpy.hklib import Node

new_node = Node(id_='new_node')
```

### Creating a [Connector](#)

```
from hkpy.hklib import Connector

new_connector = Connector(id_='new_connector', class_name='some_class')
```

### Creating a [Link](#)

```python
from hkpy.hklib import Link, Connector

new_connector = Connector(id_='new_connector', class_name='some_class')

new_link = Link(connector=new_connector)

# or new_link = Link(connector=new_connector.id_)

new_link.add_bind(entity='some_entity_1', role='some_role_1')
```

**Documentation under construction**.

For futher information please refer to the [tests/](#) for basic usage or [examples/](#) for concrete use cases.

**Requirements**

* Python 3.6+
* Dependencies on `requirements.txt`