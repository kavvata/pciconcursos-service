from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoClient
from pciconcursos_service.settings import PciConcursosRegion


class ConcursoService(ABC):
    @abstractmethod
    async def get_concursos_ativos(self, region: str) -> list[Concurso]:
        pass


class PciConcursosService(ConcursoService):
    def __init__(self, client: ConcursoClient, session: AsyncSession) -> None:
        self.client = client
        self.session = session

    async def get_concursos_ativos(self, region: str = PciConcursosRegion.TODOS) -> list[Concurso]:
        return await self.client.get_concursos_ativos(region)
