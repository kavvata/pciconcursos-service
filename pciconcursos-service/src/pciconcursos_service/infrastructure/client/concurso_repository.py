from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoRepository
from pciconcursos_service.infrastructure.db.models.concurso import ConcursoORM
from pciconcursos_service.settings import PciConcursosRegion


class AsyncConcursoRepository(ConcursoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_all(self, items: list[Concurso]) -> list[Concurso]:
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

        items = filter(
            lambda c: c.url not in existing_urls,
            items,
        )

        instances_list: list[ConcursoORM] = [ConcursoORM(**c.model_dump()) for c in items]

        if len(instances_list) < 1:
            return []

        self.session.add_all(instances_list)
        await self.session.flush()

        new_concursos_list = [Concurso.model_validate(c) for c in instances_list]

        await self.session.commit()
        return new_concursos_list

    async def get_by_region(self, region: str = PciConcursosRegion.TODOS) -> list[Concurso]:
        stmt = select(ConcursoORM)
        if region != PciConcursosRegion.TODOS:
            stmt.where(ConcursoORM.regiao == region, ConcursoORM.inscricao_ate <= datetime.now())

        concursos = await self.session.scalars(
            stmt.order_by(ConcursoORM.salario_max.desc().nulls_last(), ConcursoORM.inscricao_ate),
        )

        return [Concurso.model_validate(c) for c in concursos]
