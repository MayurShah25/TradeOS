"""Persistence boundary for TradeOS domain objects."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


EntityT = TypeVar("EntityT")


class Repository(ABC, Generic[EntityT]):
    """Minimal persistence port; infrastructure owns the concrete storage adapter."""

    @abstractmethod
    def get(self, entity_id: str) -> EntityT | None:
        """Return an entity by identifier, or None when it does not exist."""
        raise NotImplementedError

    @abstractmethod
    def save(self, entity_id: str, entity: EntityT) -> None:
        """Persist an entity under its stable identifier."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: str) -> None:
        """Delete an entity when the domain lifecycle explicitly permits deletion."""
        raise NotImplementedError
