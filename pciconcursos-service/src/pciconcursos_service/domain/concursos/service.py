from abc import ABC, abstractmethod

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoClient
from pciconcursos_service.settings import PciConcursosRegion


class ConcursoService(ABC):
    @abstractmethod
    async def get_concursos_ativos(self, region: str) -> list[Concurso]:
        pass


class PciConcursosService(ConcursoService):
    def __init__(self, client: ConcursoClient) -> None:
        self.client = client

    async def get_concursos_ativos(self, region: str = PciConcursosRegion.TODOS) -> list[Concurso]:
        return await self.client.get_concursos_ativos(region)
