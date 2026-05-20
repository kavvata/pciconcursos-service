from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AreaAtuacao(BaseModel):
    id: int | None = None
    descricao: str

    model_config = ConfigDict(from_attributes=True)


class NivelEscolaridade(BaseModel):
    id: int | None = None
    descricao: str

    model_config = ConfigDict(from_attributes=True)


class Concurso(BaseModel):
    id: int | None = None
    nome: str
    regiao: str
    vagas: int | None = None
    salario_max: int | None = None
    inscricao_ate: datetime | None = None
    url: str
    edital_pdf_url: str | None = None
    niveis_escolaridade: list[NivelEscolaridade]
    areas_atuacao: list[AreaAtuacao]

    model_config = ConfigDict(from_attributes=True)
