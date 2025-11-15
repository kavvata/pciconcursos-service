import typing as t
from functools import lru_cache

from fastapi import Depends

from python_service_template.domain.concursos.repository import ConcursoClient
from python_service_template.domain.concursos.service import PciConcursosService
from python_service_template.infrastructure.client.pci_concursos import PciConcursosClient
from python_service_template.settings import Settings


@lru_cache
def settings() -> Settings:
    return Settings()


def concurso_client(settings: t.Annotated[Settings, Depends(settings)]):
    # TODO: pass necessary settings as argument
    return PciConcursosClient()


def concurso_service(client: t.Annotated[ConcursoClient, Depends(concurso_client)]):
    return PciConcursosService(client)
