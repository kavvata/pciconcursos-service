import typing as t
from functools import lru_cache

from fastapi import Depends

from pciconcursos_service.domain.concursos.repository import ConcursoClient
from pciconcursos_service.domain.concursos.service import PciConcursosService
from pciconcursos_service.infrastructure.client.pci_concursos import PciConcursosClient
from pciconcursos_service.settings import PciConcursosConfig, Settings


@lru_cache
def settings() -> Settings:
    return Settings()


@lru_cache
def pci_concursos_config() -> PciConcursosConfig:
    return PciConcursosConfig()


def concurso_client(config: t.Annotated[Settings, Depends(pci_concursos_config)]):
    return PciConcursosClient(config.link, config.region_config)


def concurso_service(client: t.Annotated[ConcursoClient, Depends(concurso_client)]):
    return PciConcursosService(client)
