from datetime import datetime

from pydantic import BaseModel


class Concurso(BaseModel):
    id: int | None = None
    nome: str
    regiao: str
    vagas: int | None = None
    salario_max: int | None = None
    inscricao_ate: datetime | None = None
    url: str
