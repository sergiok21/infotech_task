from abc import ABC
from typing import TypeVar, Generic


from repositories.base import BaseRepository


_Entity = TypeVar('_Entity')
_Repository = TypeVar('_Repository', bound=BaseRepository)


class BaseService(Generic[_Entity, _Repository], ABC):
    def __init__(self, entity: type[_Entity], repository: _Repository) -> None:
        self.entity = entity
        self.repository = repository
