from datetime import datetime

from pydantic import BaseModel


class Concurso(BaseModel):
    id: int
    nome: str
    vagas: int
    salario_max: int
    inscricao_ate: datetime
    url: str
