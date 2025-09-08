from typing import Any, Callable


class Container:
    _providers: dict[str, Callable[[], Any]] = {}
    _cache: dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[[], Any]):
        cls._providers[name] = factory

    @classmethod
    def get(cls, name: str) -> Any:
        if name not in cls._cache:
            cls._cache[name] = cls._providers[name]()
        return cls._cache[name]

    @classmethod
    def invalidate(cls, name: str):
        cls._cache.pop(name, None)


di = Container()
