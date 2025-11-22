from abc import ABC, abstractmethod

from pciconcursos_service.domain.concursos.entity import Concurso


class ConcursoClient(ABC):
    @abstractmethod
    async def get_concursos_ativos(self) -> list[Concurso]:
        pass


class ConcursoRepository(ABC):
    @abstractmethod
    async def add_all(self, items: list[Concurso]) -> list[Concurso]:
        pass

    @abstractmethod
    async def get_by_region(self, region: str) -> list[Concurso]:
        pass
