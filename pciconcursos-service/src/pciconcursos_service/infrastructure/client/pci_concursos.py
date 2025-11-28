import re
from datetime import datetime

import aiohttp
import structlog
from bs4 import BeautifulSoup, Tag
from structlog.stdlib import BoundLogger

from pciconcursos_service.domain.concursos.entity import Concurso
from pciconcursos_service.domain.concursos.repository import ConcursoClient
from pciconcursos_service.settings import PciConcursosRegion


class PciConcursosClient(ConcursoClient):
    def __init__(self, link: str, region_config: dict) -> None:
        self.log: BoundLogger = structlog.get_logger(__name__).bind(class_name=self.__class__.__name__)
        self.link = link
        self.region_config = region_config

    async def get_concursos_ativos(self, region) -> list[Concurso]:
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

            cd_soup: Tag = line.find(class_="cd")
            ce_soup = line.find(class_="ce")
            cd_content = str(cd_soup)
            ce_content = str(ce_soup)

            cd_span = cd_soup.find("span")
            area_str, nivel_str = list(cd_span._all_strings())[:2]

            vagas = "".join(re.findall(r"(\d*) vaga", cd_content))
            nivel = "/".join([a.strip() for a in nivel_str.split("-")])
            salario = "".join(re.findall(r"R\$ *\d*\.*\d*\,*\d*", cd_content))
            area_atuacao_list = [a.strip() for a in area_str.split(",") if a]

            await self.log.ainfo("found list", area_list=area_atuacao_list, nivel=nivel)

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
                    area_atuacao=area_atuacao_list,
                    nivel=nivel,
                    salario_max=salario or None,
                    inscricao_ate=datetime.strptime(inscricao, "%d/%m/%Y") if inscricao else None,
                    url=link,
                )
            )

        return concurso_list
