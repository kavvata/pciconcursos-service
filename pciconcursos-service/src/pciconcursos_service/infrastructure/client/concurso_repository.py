from datetime import datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoRepository
from pciconcursos_service.infrastructure.db.models.concurso import ConcursoORM
from pciconcursos_service.settings import PciConcursosRegion


class AsyncConcursoRepository(ConcursoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.log = structlog.get_logger(__name__).bind(class_name=self.__class__.__name__)
        self.session = session

    async def add_new(self, items: list[Concurso]) -> list[Concurso]:
        if len(items) < 1:
            return []

        existing_urls = set(
            (
                await self.session.scalars(
                    select(ConcursoORM.url).where(
                        ConcursoORM.url.in_(
                            [c.url for c in items],
                        )
                    )
                )
            ).all()
        )

        filtered_items = filter(
            lambda c: c.url not in existing_urls,
            items,
        )

        instances_list: list[ConcursoORM] = [ConcursoORM(**c.model_dump()) for c in filtered_items]

        if len(instances_list) < 1:
            return []

        self.session.add_all(instances_list)
        await self.session.flush()

        new_concursos_list = [Concurso.model_validate(c) for c in instances_list]

        await self.session.commit()
        return new_concursos_list

    async def get_by_region(self, region_list: list[PciConcursosRegion]) -> list[Concurso]:
        stmt = select(ConcursoORM).where(
            ConcursoORM.inscricao_ate >= datetime.now(),
        )
        if PciConcursosRegion.TODOS not in region_list:
            stmt = stmt.where(
                ConcursoORM.regiao.in_([r.value for r in region_list]),
            )

        concursos = await self.session.scalars(
            stmt.order_by(
                ConcursoORM.regiao,
                ConcursoORM.salario_max.desc().nulls_last(),
                ConcursoORM.inscricao_ate,
            ),
        )

        return [Concurso.model_validate(c) for c in concursos]

    async def get_added_today(self, region_list: list[PciConcursosRegion]) -> list[Concurso]:
        now = datetime.now()
        stmt = select(ConcursoORM).where(
            ConcursoORM.inscricao_ate >= now,
            ConcursoORM.created_at >= now.replace(hour=0, minute=0, second=0, microsecond=0),
        )
        if PciConcursosRegion.TODOS not in region_list:
            stmt = stmt.where(
                ConcursoORM.regiao.in_([r.value for r in region_list]),
            )

        concursos = await self.session.scalars(
            stmt.order_by(
                ConcursoORM.regiao,
                ConcursoORM.salario_max.desc().nulls_last(),
                ConcursoORM.inscricao_ate,
            ),
        )

        return [Concurso.model_validate(c) for c in concursos]
