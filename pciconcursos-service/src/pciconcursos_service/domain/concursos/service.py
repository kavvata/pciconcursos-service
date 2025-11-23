from abc import ABC, abstractmethod

import structlog

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoClient, ConcursoRepository
from pciconcursos_service.settings import PciConcursosRegion


class ConcursoService(ABC):
    @abstractmethod
    async def scrape_concursos(self, region: str) -> list[Concurso]:
        pass

    @abstractmethod
    async def get_concursos(self, region_list: list[PciConcursosRegion]) -> list[Concurso]:
        pass


class PciConcursosService(ConcursoService):
    def __init__(self, client: ConcursoClient, repository: ConcursoRepository) -> None:
        self.log = structlog.get_logger(__name__).bind(class_name=self.__class__.__name__)
        self.client = client
        self.repository = repository

    async def scrape_concursos(self, region: str = PciConcursosRegion.TODOS) -> list[Concurso]:
        scraped_items: list[Concurso] = await self.client.get_concursos_ativos(region)
        return await self.repository.add_all(scraped_items)

    async def get_concursos(self, region_list: list[PciConcursosRegion]) -> list[Concurso]:
        if not len(region_list):
            region_list = [PciConcursosRegion.TODOS]
        return await self.repository.get_by_region(region_list)
