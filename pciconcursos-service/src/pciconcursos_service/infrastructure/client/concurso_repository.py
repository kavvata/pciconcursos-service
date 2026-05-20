from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import or_

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoRepository
from pciconcursos_service.infrastructure.db.models.concurso import (
    AreaAtuacaoORM,
    ConcursoORM,
    NivelEscolaridadeORM,
)
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

        filtered_items = list(
            filter(
                lambda c: c.url not in existing_urls,
                items,
            )
        )

        all_areas = {a.descricao for c in filtered_items for a in c.areas_atuacao}
        all_niveis = {n.descricao for c in filtered_items for n in c.niveis_escolaridade}

        existing_areas = {
            a.descricao: a
            for a in (
                await self.session.scalars(
                    select(AreaAtuacaoORM).where(AreaAtuacaoORM.descricao.in_(all_areas)),
                )
            ).all()
        }
        existing_niveis = {
            n.descricao: n
            for n in (
                await self.session.scalars(
                    select(NivelEscolaridadeORM).where(NivelEscolaridadeORM.descricao.in_(all_niveis)),
                )
            ).all()
        }

        instances_list = []

        for c in filtered_items:
            orm = ConcursoORM(
                **c.model_dump(exclude={"niveis_escolaridade", "areas_atuacao"}),
            )

            orm.areas_atuacao = []
            for a in c.areas_atuacao:
                area = existing_areas.get(a.descricao)
                if not area:
                    area = AreaAtuacaoORM(descricao=a.descricao)
                    existing_areas[a.descricao] = area
                if area not in orm.areas_atuacao:
                    orm.areas_atuacao.append(area)

            orm.niveis_escolaridade = []
            for n in c.niveis_escolaridade:
                nivel = existing_niveis.get(n.descricao)
                if not nivel:
                    nivel = NivelEscolaridadeORM(descricao=n.descricao)
                    existing_niveis[n.descricao] = nivel
                if nivel not in orm.niveis_escolaridade:
                    orm.niveis_escolaridade.append(nivel)

            instances_list.append(orm)

        if len(instances_list) < 1:
            return []

        self.session.add_all(instances_list)
        await self.session.flush()

        new_concursos_list = [Concurso.model_validate(c) for c in instances_list]

        await self.session.commit()
        return new_concursos_list

    async def update_all(self, items: list[Concurso]):
        if len(items) < 1:
            return []

        all_areas = {a.descricao for c in items for a in c.areas_atuacao}
        all_niveis = {n.descricao for c in items for n in c.niveis_escolaridade}

        existing_areas = {
            a.descricao: a
            for a in (
                await self.session.scalars(
                    select(AreaAtuacaoORM).where(AreaAtuacaoORM.descricao.in_(all_areas)),
                )
            ).all()
        }
        existing_niveis = {
            n.descricao: n
            for n in (
                await self.session.scalars(
                    select(NivelEscolaridadeORM).where(NivelEscolaridadeORM.descricao.in_(all_niveis)),
                )
            ).all()
        }

        instances_list = []

        for c in items:
            orm = (
                await self.session.scalars(
                    select(ConcursoORM)
                    .options(
                        selectinload(ConcursoORM.areas_atuacao),
                        selectinload(ConcursoORM.niveis_escolaridade),
                    )
                    .where(ConcursoORM.url == c.url)
                )
            ).first()

            if not orm:
                continue

            orm.nome = c.nome
            orm.regiao = c.regiao
            orm.inscricao_ate = c.inscricao_ate
            orm.edital_pdf_url = c.edital_pdf_url

            orm.areas_atuacao = []
            for a in c.areas_atuacao:
                area = existing_areas.get(a.descricao)
                if not area:
                    area = AreaAtuacaoORM(descricao=a.descricao)
                    existing_areas[a.descricao] = area
                if area not in orm.areas_atuacao:
                    orm.areas_atuacao.append(area)

            orm.niveis_escolaridade = []
            for n in c.niveis_escolaridade:
                nivel = existing_niveis.get(n.descricao)
                if not nivel:
                    nivel = NivelEscolaridadeORM(descricao=n.descricao)
                    existing_niveis[n.descricao] = nivel
                if nivel not in orm.niveis_escolaridade:
                    orm.niveis_escolaridade.append(nivel)

            instances_list.append(orm)

        updated_instances = [Concurso.model_validate(c) for c in instances_list]

        await self.session.commit()
        return updated_instances

    async def get(
        self,
        region_list: list[PciConcursosRegion] | None = None,
        area_atuacao_list: list[str] | None = None,
        nome_q: str | None = None,
        id: int | None = None,
    ) -> list[Concurso]:
        stmt = select(ConcursoORM).where(
            ConcursoORM.inscricao_ate >= datetime.now(),
        )

        if id:
            stmt = stmt.where(ConcursoORM.id == id)
            concursos = await self.session.scalars(
                stmt.options(
                    selectinload(ConcursoORM.niveis_escolaridade),
                    selectinload(ConcursoORM.areas_atuacao),
                )
            )
            return [Concurso.model_validate(c) for c in concursos]

        if region_list:
            if PciConcursosRegion.TODOS not in region_list:
                stmt = stmt.where(
                    ConcursoORM.regiao.in_([r.value for r in region_list]),
                )

        if area_atuacao_list:
            areas_conditions = or_(
                *[ConcursoORM.areas_atuacao.any(AreaAtuacaoORM.descricao.ilike(f"%{a}%")) for a in area_atuacao_list]
            )
            stmt = stmt.where(
                ConcursoORM.areas_atuacao.any(
                    areas_conditions,
                ),
            )

        if nome_q:
            stmt = stmt.where(
                ConcursoORM.nome.ilike(f"%{nome_q}%"),
            )

        concursos = await self.session.scalars(
            stmt.options(
                selectinload(ConcursoORM.niveis_escolaridade),
                selectinload(ConcursoORM.areas_atuacao),
            ).order_by(
                ConcursoORM.regiao,
                ConcursoORM.salario_max.desc().nulls_last(),
                ConcursoORM.inscricao_ate,
            ),
        )

        return [Concurso.model_validate(c) for c in concursos]

    async def get_by_region(self, region_list: list[PciConcursosRegion]) -> list[Concurso]:
        stmt = select(ConcursoORM).where(
            ConcursoORM.inscricao_ate >= datetime.now(),
        )
        if PciConcursosRegion.TODOS not in region_list:
            stmt = stmt.where(
                ConcursoORM.regiao.in_([r.value for r in region_list]),
            )

        concursos = await self.session.scalars(
            stmt.options(
                selectinload(ConcursoORM.areas_atuacao),
                selectinload(ConcursoORM.niveis_escolaridade),
            ).order_by(
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
            stmt.options(
                selectinload(ConcursoORM.areas_atuacao),
                selectinload(ConcursoORM.niveis_escolaridade),
            ).order_by(
                ConcursoORM.regiao,
                ConcursoORM.salario_max.desc().nulls_last(),
                ConcursoORM.inscricao_ate,
            ),
        )

        return [Concurso.model_validate(c) for c in concursos]
