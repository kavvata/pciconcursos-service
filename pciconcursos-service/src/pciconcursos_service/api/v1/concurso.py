import typing as t

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pciconcursos_service.dependencies import concurso_service, db_session
from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.service import ConcursoService

router = APIRouter(prefix="/api/v1/concurso")


@router.get("/", response_model=list[Concurso])
async def get_concursos_ativos(service: t.Annotated[ConcursoService, Depends(concurso_service)]):
    concursos = await service.get_concursos_ativos()
    if concursos is None:
        raise HTTPException(status_code=404, detail="Nenhum concurso encontrado.")
    return concursos


@router.get("/test/")
async def test_db(session: t.Annotated[AsyncSession, Depends(db_session)]):
    response = (await session.scalars(select(1))).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Failed to stablish a database connection.")
    return response
