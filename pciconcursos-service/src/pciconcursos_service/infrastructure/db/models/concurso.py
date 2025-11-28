from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm.decl_api import mapped_column

from pciconcursos_service.infrastructure.db.models.core import BaseORM

concurso_area_atuacao_association: Table = Table(
    "concurso_area_atuacao",
    BaseORM.metadata,
    Column(
        "area_atuacao_id",
        Integer,
        ForeignKey("area_atuacao.id"),
        primary_key=True,
    ),
    Column(
        "concurso_id",
        Integer,
        ForeignKey("concurso.id"),
        primary_key=True,
    ),
)


class AreaAtuacaoORM(BaseORM):
    __tablename__ = "area_atuacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    descricao: Mapped[str]
    concursos: Mapped[list["ConcursoORM"]] = relationship(
        "ConcursoORM",
        secondary="concurso_area_atuacao",
        back_populates="areas_atuacao",
    )


class ConcursoORM(BaseORM):
    __tablename__ = "concurso"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    regiao: Mapped[str]
    vagas: Mapped[int | None]
    salario_max: Mapped[int | None]
    inscricao_ate: Mapped[datetime | None]
    url: Mapped[str]
    areas_atuacao: Mapped[list["AreaAtuacaoORM"]] = relationship(
        "AreaAtuacaoORM",
        secondary="concurso_area_atuacao",
        back_populates="concursos",
    )
