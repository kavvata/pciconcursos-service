import typing as t

from fastapi import APIRouter, Depends, HTTPException, Query

from pciconcursos_service.dependencies import concurso_service
from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.service import ConcursoService
from pciconcursos_service.settings import PciConcursosRegion

router = APIRouter(prefix="/api/v1/concurso")


@router.get("/", response_model=list[Concurso])
async def get_concursos(
    service: t.Annotated[ConcursoService, Depends(concurso_service)],
    region_list: list[PciConcursosRegion] | None = Query([], description="List of regions to filter by"),  # noqa: B008
):
    return await service.get_concursos(region_list)


@router.get("/scrape/", response_model=list[Concurso])
async def scrape_concursos(service: t.Annotated[ConcursoService, Depends(concurso_service)]):
    concursos = await service.scrape_concursos()
    if concursos is None:
        raise HTTPException(status_code=204, detail="Nenhum novo concurso encontrado.")
    return concursos
