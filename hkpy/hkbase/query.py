from typing import Dict, Union, Any


__all__ = ['SPARQLResultSet', 'SPARQLResultRow', 'SPARQLCell']


class SPARQLResultSet(object):
    def __init__(self, result):
        self._result = result

    def __iter__(self):
        return SPARQLResultSetIterator(self._result)

    def __len__(self):
        return len(self._result['results']['bindings'])


class SPARQLResultSetIterator(object):
    def __init__(self, result):
        self._result = result
        self._index = 0

    def __next__(self):
        if self._index < len(self._result['results']['bindings']):
            result = SPARQLResultRow(self._result['results']['bindings'][self._index], self._result['head'])
            self._index += 1
            return result
        raise StopIteration


class SPARQLResultRow(object):
    def __init__(self, bindings, head: Dict):
        self._bindings = bindings
        self._head = head

    def __getitem__(self, key: Union[str, int]) -> Union[None, Any]:
        if isinstance(key, int):
            key = self._head['vars'][key]
        bind = self._bindings.get(key)
        return SPARQLCell(bind)

    def __len__(self):
        return len(self._bindings)


class SPARQLCell(object):
    def __init__(self, dict_: Dict):
        self.value = None
        self.type_ = None
        self.datatype = None
        if dict_ is not None:
            self.value = dict_.get('value', None)
            self.type_ = dict_.get('type', None)
            self.datatype = dict_.get('datatype', None)

    def __str__(self):
        return self.value

    def __contains__(self, item: str):
        if self.value is None:
            return item is None
        return item in self.value

    def __eq__(self, other):
        if other is None and self.value is None:
            return True
        else:
            return other.value == self.value
