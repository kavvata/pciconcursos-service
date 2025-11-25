from abc import ABC, abstractmethod

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.settings import PciConcursosRegion


class ConcursoClient(ABC):
    @abstractmethod
    async def get_concursos_ativos(self) -> list[Concurso]:
        pass


class ConcursoCache(ABC):
    @abstractmethod
    async def get(self, key: str) -> list[Concurso]:
        pass

    @abstractmethod
    async def set(self, key: str, value: list[Concurso], ex: int | None = None) -> list[Concurso]:
        pass


class ConcursoRepository(ABC):
    @abstractmethod
    async def add_new(self, items: list[Concurso]) -> list[Concurso]:
        pass

    @abstractmethod
    async def get_by_region(self, region_list: list[PciConcursosRegion]) -> list[Concurso]:
        pass

    @abstractmethod
    async def get_added_today(self, region_list: list[PciConcursosRegion]) -> list[Concurso]:
        pass
