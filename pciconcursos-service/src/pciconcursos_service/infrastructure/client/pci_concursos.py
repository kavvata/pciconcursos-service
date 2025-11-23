import re
from datetime import date, datetime

import aiohttp
import structlog
from bs4 import BeautifulSoup
from pydantic import ValidationError
from pydantic.type_adapter import TypeAdapter
from redis.asyncio.client import Redis

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoClient
from pciconcursos_service.settings import PciConcursosRegion


class PciConcursosClient(ConcursoClient):
    def __init__(self, link: str, region_config: dict, cache: Redis) -> None:
        self.log = structlog.get_logger(__name__).bind(class_name=self.__class__.__name__)
        self.link = link
        self.cache = cache
        self.region_config = region_config
        self.cache_type_adapter = TypeAdapter(list[Concurso])

    async def get_concursos_ativos(self, region):
        cache_id: str = f"scraped_concursos:{date.today()}"

        cached_items: str = await self.cache.get(cache_id)

        if cached_items:
            try:
                return self.cache_type_adapter.validate_json(cached_items)
            except ValidationError as e:
                await self.log.awarning(f"Error while validating cached scraped results:\n{e}\nContinuing...")

        async with aiohttp.ClientSession() as session:
            async with session.get(self.link) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

        if region != PciConcursosRegion.TODOS:
            source_code_str = str(soup)
            if region not in self.region_config:
                raise ValueError(f"'{region}' não é uma região válida.")

            config = self.region_config[region]
            initial_tag = source_code_str.find(config["start"]) + len(config["start"])
            final_tag = source_code_str.find(config["end"]) + len(config["end"])

            concursos_tag = source_code_str[initial_tag:final_tag]
            soup = BeautifulSoup(concursos_tag, "html.parser")

        concurso_list: list[Concurso] = []

        for line in soup.find_all(class_="ca"):
            name = line.find("a").text.strip()
            link = line.find("a", href=True)["href"]

            cd_content = str(line.find(class_="cd"))
            ce_content = str(line.find(class_="ce"))

            vagas = "".join(re.findall(r"(\d*) vaga", cd_content))
            nivel = "/".join(re.findall(r"Superior|Médio|Técnico|Fundamental", cd_content))
            salario = "".join(re.findall(r"R\$ *\d*\.*\d*\,*\d*", cd_content))

            regiao = line.parent.find_previous("div", class_="uf").text

            inscricoes_list = re.findall(r"\d+/\d+/\d+", ce_content)

            inscricao = inscricoes_list[-1] if len(inscricoes_list) > 1 else "".join(inscricoes_list)

            if salario:
                salario = "".join(filter(str.isdigit, salario))
                salario = int(salario)

            concurso_list.append(
                Concurso(
                    nome=name,
                    regiao=regiao,
                    vagas=int(vagas) if vagas else None,
                    nivel=nivel,
                    salario_max=salario or None,
                    inscricao_ate=datetime.strptime(inscricao, "%d/%m/%Y") if inscricao else None,
                    url=link,
                )
            )

        expiration_time_seconds = 60 * 60 * 24  # 24 hours
        await self.cache.set(cache_id, self.cache_type_adapter.dump_json(concurso_list), ex=expiration_time_seconds)
        return concurso_list
