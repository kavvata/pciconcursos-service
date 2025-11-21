from abc import ABC, abstractmethod

from pciconcursos_service.domain.concursos.entity import Concurso


class ConcursoClient(ABC):
    @abstractmethod
    async def get_concursos_ativos(self) -> list[Concurso]:
        pass
