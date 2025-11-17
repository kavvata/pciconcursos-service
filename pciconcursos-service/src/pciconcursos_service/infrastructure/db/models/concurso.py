from datetime import datetime

from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm.decl_api import mapped_column

from pciconcursos_service.infrastructure.db.models.core import BaseORM


class ConcursoORM(BaseORM):
    __tablename__ = "concurso"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    vagas: Mapped[int]
    salario_max: Mapped[int]
    inscricao_ate: Mapped[datetime]
    url: Mapped[str]
