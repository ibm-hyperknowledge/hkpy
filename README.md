# HKPy: a Python Framework for Hyperknowledge

## Getting Started

### Install

To use HKPy in your project, you can install using:
```
pip install hkpy
```

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

### Querying data

#### HyQL

WIP

#### SPARQL
Connect to a HKBase repository
```
from hkpy.hkbase import HKBase, HKRepository

hkbase = HKBase(url='foo.bar', auth='some_token')
hkrepository = hkbase.create_repository(name='new_repository')
```

```
sparql_query = ('select ?s ?p ?o ?g {\n'
                '   ?s ?p ?o\n'
                '}')
result_set = hkrepository.sparql(sparql_query)
```

You can consume the result_set in different ways:
```
# iterate over rows
for row in result_set: 
    # access via position in select
    print(f's: {row[0].value}')
    
    # access via variable name in select
    print(f'p: {row["p"].value}')
    
    # an empty variable returns none
    print(f'g: {row["g"].value}')
```

```
# splitting results_set's rows into variables
for s, p, o in result_set:
    print(f's: {s.value} p: {p.value} o:{o.value}')
```

```
# Aside from its value, a row component also has some relevant metadata
for s, p, o in result_set: 
    print((f's value: {s.value}\n'
           f's type: {s.type_}\n'
           f's datatype: {s.datatype}'))
```

**Optional parameters** 
- `reasoning: bool`
- `by_pass: bool` 
--- 
**Documentation under construction**.

For futher information please refer to the [tests/](#) for basic usage or [examples/](#) for concrete use cases.

**Requirements**

* Python 3.6+
* Dependencies on `requirements.txt`