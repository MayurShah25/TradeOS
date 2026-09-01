"""In-memory repository adapter for deterministic tests and early foundation work."""

from typing import Generic, TypeVar

from tradeos.infrastructure.repository import Repository


EntityT = TypeVar("EntityT")


class InMemoryRepository(Generic[EntityT], Repository[EntityT]):
    """Simple repository implementation with explicit replace semantics."""

    def __init__(self) -> None:
        self._items: dict[str, EntityT] = {}

    def get(self, entity_id: str) -> EntityT | None:
        return self._items.get(entity_id)

    def save(self, entity_id: str, entity: EntityT) -> None:
        self._items[entity_id] = entity

    def delete(self, entity_id: str) -> None:
        self._items.pop(entity_id, None)
