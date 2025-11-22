from abc import ABC, abstractmethod

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoClient
from pciconcursos_service.infrastructure.db.models import ConcursoORM
from pciconcursos_service.settings import PciConcursosRegion


class ConcursoService(ABC):
    @abstractmethod
    async def scrape_concursos(self, region: str) -> list[Concurso]:
        pass

    @abstractmethod
    async def get_concursos(self, region: str) -> list[Concurso]:
        pass


class PciConcursosService(ConcursoService):
    def __init__(self, client: ConcursoClient, session: AsyncSession) -> None:
        self.log = structlog.get_logger(__name__).bind(class_name=self.__class__.__name__)
        self.client = client
        self.session = session

    async def scrape_concursos(self, region: str = PciConcursosRegion.TODOS) -> list[Concurso]:
        scraped_concursos: list[Concurso] = await self.client.get_concursos_ativos(region)
        existing_urls = set(
            (
                await self.session.scalars(
                    select(ConcursoORM.url).where(
                        ConcursoORM.url.in_(
                            [c.url for c in scraped_concursos],
                        )
                    )
                )
            ).all()
        )

        new_scraped_concursos = filter(
            lambda c: c.url not in existing_urls,
            scraped_concursos,
        )

        new_concursos: list[ConcursoORM] = [ConcursoORM(**c.model_dump()) for c in new_scraped_concursos]

        self.session.add_all(new_concursos)

        await self.session.commit()

        return [Concurso.model_validate(c) for c in new_concursos]

    async def get_concursos(self, region: str = PciConcursosRegion.TODOS) -> list[Concurso]:
        stmt = select(ConcursoORM)
        if region != PciConcursosRegion.TODOS:
            stmt.where(ConcursoORM.regiao == region)

        concursos = await self.session.scalars(stmt.order_by(ConcursoORM.inscricao_ate))

        return [Concurso.model_validate(c) for c in concursos]
