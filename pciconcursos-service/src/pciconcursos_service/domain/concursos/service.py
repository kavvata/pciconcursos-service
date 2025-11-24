from abc import ABC, abstractmethod
from datetime import date
from hashlib import md5

import structlog

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoCache, ConcursoClient, ConcursoRepository
from pciconcursos_service.settings import PciConcursosRegion


class ConcursoService(ABC):
    @abstractmethod
    async def scrape_concursos(self, region: str) -> list[Concurso]:
        pass

    @abstractmethod
    async def get_concursos(self, region_list: list[PciConcursosRegion]) -> list[Concurso]:
        pass


class PciConcursosService(ConcursoService):
    def __init__(self, client: ConcursoClient, repository: ConcursoRepository, cache: ConcursoCache) -> None:
        self.log = structlog.get_logger(__name__).bind(class_name=self.__class__.__name__)
        self.client = client
        self.repository = repository
        self.cache = cache

    async def scrape_concursos(self, region: str = PciConcursosRegion.TODOS) -> list[Concurso]:
        cache_key = f"scraped_items:{str(date.today()).replace('-', '')}"
        scraped_items = await self.cache.get(cache_key)

        if not scraped_items:
            scraped_items: list[Concurso] = await self.client.get_concursos_ativos(region)
            await self.cache.set(
                cache_key,
                scraped_items,
                ex=60 * 60 * 24,  # 24 hours
            )

        return await self.repository.add_all(scraped_items)

    async def get_concursos(self, region_list: list[PciConcursosRegion]) -> list[Concurso]:
        if not region_list:
            region_list = [PciConcursosRegion.TODOS]

        region_values = ",".join([r.value for r in region_list])
        hashed_regions = md5(region_values.encode()).hexdigest()
        cache_key = f"concursos:{hashed_regions}"

        concursos = await self.cache.get(cache_key)
        if concursos is not None:
            return concursos

        concursos = await self.repository.get_by_region(region_list)
        await self.cache.set(cache_key, concursos, ex=60 * 5)
        return concursos
