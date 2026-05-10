from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from django.db.models import Model


_Entity = TypeVar('_Entity')
_Model = TypeVar('_Model', bound=Model)


class BaseRepository(Generic[_Entity, _Model], ABC):
    def __init__(self, entity: type[_Entity], model: type[_Model]):
        self.entity = entity
        self.model = model

    @abstractmethod
    def _to_entity(self, model: type[_Model]) -> _Entity: ...
