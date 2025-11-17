from abc import ABC, abstractmethod


class ConcursoClient(ABC):
    @abstractmethod
    async def get_concursos_ativos(self):
        pass
