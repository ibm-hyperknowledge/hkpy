from typing import Dict, Optional, List

__all__ = ['HKStoredQuery']


class HKStoredQuery:
    """Class model that represents an executable stored query"""

    def __init__(self, query_text: str, query_language: str, columns: List[str],
                 parameters: Optional[List[str]] = None, id_: Optional[str] = None,
                 label: Optional[str] = None):
        self.query_text = query_text
        self.query_language = query_language
        self.label = label
        self.columns = columns
        self.parameters = parameters
        self.id_ = id_

    @classmethod
    def from_dict(cls, dict_: Dict) -> 'HKStoredQuery':
        # required properties
        parameters = {
            'query_text': dict_['queryText'],
            'query_language': dict_['queryLanguage'],
            'columns': dict_['columns']
        }

        # optional properties
        if 'label' in dict_:
            parameters['label'] = dict_['label']
        if 'parameters' in dict_:
            parameters['parameters'] = dict_['parameters']
        if 'id' in dict_:
            parameters['id_'] = dict_['id']

        return cls(**parameters)

    def to_dict(self) -> Dict:
        dict_ = {
            'queryText': self.query_text,
            'queryLanguage': self.query_language,
            'columns': self.columns,
        }

        if self.label is not None:
            dict_['label'] = self.label

        if self.parameters is not None:
            dict_['parameters'] = self.parameters

        if self.id_ is not None:
            dict_['id'] = self.id_

        return dict_
