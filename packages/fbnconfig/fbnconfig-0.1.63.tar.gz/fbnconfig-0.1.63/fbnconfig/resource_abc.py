from abc import ABC, abstractmethod
from types import SimpleNamespace
from typing import Any, Dict, Optional, Sequence, Union

from httpx import Client as httpxClient
from pydantic import AliasGenerator, ConfigDict, alias_generators

alias_generator = ConfigDict(
    alias_generator=AliasGenerator(
        serialization_alias=lambda field_name: alias_generators.to_camel(field_name)
    )
)


class Ref(ABC):
    id: str

    @abstractmethod
    def attach(self, client: httpxClient) -> None:
        pass

    def deps(self):
        return []


class Resource(ABC):
    model_config = alias_generator

    id: str

    @abstractmethod
    def read(self, client: httpxClient, old_state: SimpleNamespace) -> None | Dict[str, Any]:
        pass

    @abstractmethod
    def create(self, client: httpxClient) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def update(self, client: httpxClient, old_state) -> Union[None, Dict[str, Any]]:
        pass

    @staticmethod
    @abstractmethod
    def delete(client: httpxClient, old_state) -> None:
        pass

    @abstractmethod
    def deps(self) -> Sequence["Resource|Ref"]:
        pass


class CamelAlias(ABC):
    model_config = alias_generator
