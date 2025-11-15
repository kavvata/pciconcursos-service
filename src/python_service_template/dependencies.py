import typing as t
from functools import lru_cache

from fastapi import Depends

from python_service_template.domain.concursos.repository import ConcursoClient
from python_service_template.domain.concursos.service import PciConcursosService
from python_service_template.infrastructure.client.pci_concursos import PciConcursosClient
from python_service_template.settings import PciConcursosConfig, Settings


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
