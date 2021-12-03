###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

__all__ = ['NotificationObjects', 'NotificationActions', 'HTTPMethodByNotificationAction']


from enum import Enum, unique


@unique
class NotificationObjects(Enum):
    REPOSITORY = 'repository'
    ENTITIES = 'entities'


@unique
class NotificationActions(Enum):
    CREATE = 'create'
    DELETE = 'dele'
    UPDATE = 'update'


HTTPMethodByNotificationAction = {
    NotificationActions.CREATE: 'POST',
    NotificationActions.DELETE: 'DELETE',
    NotificationActions.UPDATE: 'PUT'
}
