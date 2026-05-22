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
    region: list[PciConcursosRegion] | None = Query([], description="Optionally set one or more regions to filter by"),  # noqa: B008
    area_atuacao: list[str] | None = Query([], description="Optionally search for area atuacao"),  # noqa: B008
    nome: str | None = Query("", description="Optionally search by concurso nome"),
):
    return await service.get_concursos(region, area_atuacao, nome)


@router.get("/scrape/", response_model=list[Concurso])
async def scrape_concursos(
    service: t.Annotated[ConcursoService, Depends(concurso_service)],
    region: list[PciConcursosRegion] | None = Query([], description="Optionally set one or more regions to filter by"),  # noqa: B008
):
    concursos = await service.scrape_concursos(region)
    if not concursos:
        raise HTTPException(status_code=204, detail="Nenhum novo concurso encontrado.")
    return concursos


@router.get("/new/", response_model=list[Concurso])
async def get_new_concursos(
    service: t.Annotated[ConcursoService, Depends(concurso_service)],
    region: list[PciConcursosRegion] | None = Query([], description="Optionally set one or more regions to filter by"),  # noqa: B008
    area_atuacao: list[str] | None = Query([], description="Optionally search for area atuacao"),  # noqa: B008
    nome: str | None = Query("", description="Optionally search by concurso nome"),
):
    concursos = await service.get_new_concursos(
        region,
        area_atuacao,
        nome,
    )
    if not concursos:
        raise HTTPException(status_code=204, detail="Nenhum novo concurso encontrado.")
    return concursos


@router.get("/rescrape/", response_model=list[Concurso])
async def re_scrape_concursos(
    service: t.Annotated[ConcursoService, Depends(concurso_service)],
):
    return await service.re_scrape_concursos()


@router.get("/rescrape/{concurso_id}", response_model=Concurso)
async def re_scrape_concurso(service: t.Annotated[ConcursoService, Depends(concurso_service)], concurso_id: int):
    concurso = await service.get_concurso_by_id(concurso_id)

    if not concurso:
        raise HTTPException(status_code=404, detail="Not found.")

    updated = await service.re_scrape_concurso(concurso)

    if not updated:
        raise HTTPException(status_code=204, detail="No update needed.")

    return updated
