from tradeos.infrastructure.in_memory_repository import InMemoryRepository


def test_save_and_get() -> None:
    repository: InMemoryRepository[str] = InMemoryRepository()
    repository.save("one", "value")

    assert repository.get("one") == "value"


def test_save_replaces_existing_entity() -> None:
    repository: InMemoryRepository[str] = InMemoryRepository()
    repository.save("one", "first")
    repository.save("one", "second")

    assert repository.get("one") == "second"


def test_delete_removes_entity() -> None:
    repository: InMemoryRepository[str] = InMemoryRepository()
    repository.save("one", "value")
    repository.delete("one")

    assert repository.get("one") is None


def test_delete_missing_entity_is_safe() -> None:
    repository: InMemoryRepository[str] = InMemoryRepository()

    repository.delete("missing")

    assert repository.get("missing") is None
