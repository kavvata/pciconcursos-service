import typing as t
from functools import lru_cache

from fastapi import Depends
from redis import asyncio as aioredis
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from pciconcursos_service.domain.concursos.repository import ConcursoClient, ConcursoRepository
from pciconcursos_service.domain.concursos.service import PciConcursosService
from pciconcursos_service.infrastructure.client.concurso_repository import AsyncConcursoRepository
from pciconcursos_service.infrastructure.client.pci_concursos import PciConcursosClient
from pciconcursos_service.infrastructure.client.redis_cache import RedisConcursoCache
from pciconcursos_service.infrastructure.db.core import DatabaseSessionManager
from pciconcursos_service.settings import PciConcursosConfig, Settings


@lru_cache
def settings() -> Settings:
    return Settings()


@lru_cache
def cache_client(settings: t.Annotated[Settings, Depends(settings)]):
    redis_client = aioredis.from_url(
        url=f"redis://{settings.cache_user}:{settings.cache_password}@{settings.cache_host}:{settings.cache_port}/{settings.cache_name}",
        decode_responses=True,
    )
    return RedisConcursoCache(redis_client)


@lru_cache
def db_session_manager(settings: t.Annotated[Settings, Depends(settings)]):
    return DatabaseSessionManager(
        f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}",
    )


async def db_session(manager: t.Annotated[DatabaseSessionManager, Depends(db_session_manager)]):
    async with manager.session() as session:
        yield session


def pci_concursos_config() -> PciConcursosConfig:
    return PciConcursosConfig()


def concurso_repository(session: t.Annotated[AsyncSession, Depends(db_session)]):
    return AsyncConcursoRepository(session)


def concurso_client(
    config: t.Annotated[Settings, Depends(pci_concursos_config)],
):
    return PciConcursosClient(config.link, config.region_config)


def concurso_service(
    client: t.Annotated[ConcursoClient, Depends(concurso_client)],
    repository: t.Annotated[ConcursoRepository, Depends(concurso_repository)],
    cache: t.Annotated[ConcursoRepository, Depends(cache_client)],
):
    return PciConcursosService(client, repository, cache)
