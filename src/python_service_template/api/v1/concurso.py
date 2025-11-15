import typing as t

from fastapi import APIRouter, Depends, HTTPException

from python_service_template.dependencies import concurso_service
from python_service_template.domain.concursos.service import ConcursoService

router = APIRouter(prefix="/api/v1/concurso")


@router.get("/")
async def get_concursos_ativos(service: t.Annotated[ConcursoService, Depends(concurso_service)]):
    concursos = await service.get_concursos_ativos()
    if concursos is None:
        raise HTTPException(status_code=404, detail="Nenhum concurso encontrado.")
    return concursos
