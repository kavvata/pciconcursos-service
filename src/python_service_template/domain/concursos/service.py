from abc import ABC, abstractmethod

from python_service_template.domain.concursos.entity import Concurso
from python_service_template.domain.concursos.repository import ConcursoClient
from python_service_template.settings import PciConcursosRegion


class ConcursoService(ABC):
    @abstractmethod
    async def get_concursos_ativos(self, region: str) -> list[Concurso]:
        pass


class PciConcursosService(ConcursoService):
    def __init__(self, client: ConcursoClient) -> None:
        self.client = client

    async def get_concursos_ativos(self, region: str = PciConcursosRegion.TODOS) -> list[Concurso]:
        return await self.client.get_concursos_ativos(region)
