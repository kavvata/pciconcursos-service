from pydantic import TypeAdapter
from redis.asyncio.client import Redis

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoCache


class RedisConcursoCache(ConcursoCache):
    def __init__(self, client: Redis) -> None:
        self.client = client
        self.adapter = TypeAdapter(list[Concurso])

    async def get(self, key: str) -> str | None:
        json_str = await self.client.get(key)

        if not json_str:
            return None

        return self.adapter.validate_json(json_str)

    async def set(
        self,
        key: str,
        value: list[Concurso],
        ex: int | None = None,
    ) -> None:
        await self.client.set(
            key,
            self.adapter.dump_json(value),
            ex=ex,
        )
