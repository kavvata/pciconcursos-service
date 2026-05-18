import re
from datetime import datetime

import aiohttp
import structlog
from bs4 import BeautifulSoup
from structlog.stdlib import BoundLogger

from pciconcursos_service.domain.concursos.entity import AreaAtuacao, Concurso, NivelEscolaridade
from pciconcursos_service.domain.concursos.repository import ConcursoClient
from pciconcursos_service.settings import PciConcursosRegion


class PciConcursosClient(ConcursoClient):
    def __init__(self, link: str, region_config: dict) -> None:
        self.log: BoundLogger = structlog.get_logger(__name__).bind(class_name=self.__class__.__name__)
        self.link = link
        self.region_config = region_config

    async def get_possible_areas_from_concurso_link(self, link: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

        article_soup = soup.find(attrs={"itemprop": "articleBody"})

        if not article_soup:
            return []

        return [
            re.sub(r"\s*\(.*\)\s*$", "", li.get_text(strip=True)).strip()
            for ul in article_soup.find_all("ul")
            for li in ul.find_all("li")
        ]

    async def _build_entities_from_soup(self, soup: BeautifulSoup) -> list[Concurso]:
        concurso_list: list[Concurso] = []

        for line in soup.find_all(class_="ca"):
            name_anchor = line.find("a", href=True)

            assert name_anchor

            name = name_anchor.text.strip()
            link = name_anchor.get("href")

            cd_soup = line.find(class_="cd")

            assert cd_soup

            ce_soup = line.find(class_="ce")
            cd_content = str(cd_soup)
            ce_content = str(ce_soup)

            cd_span = cd_soup.find("span")
            assert cd_span
            area_str, nivel_str = list(cd_span._all_strings())[:2]

            vagas = "".join(re.findall(r"(\d*) vaga", cd_content))
            nivel_list = [a.strip() for a in re.split(r"[-/]+", nivel_str) if a.strip()]
            area_atuacao_list = [a.strip() for a in area_str.split(",") if a]
            salario = "".join(re.findall(r"R\$ *\d*\.*\d*\,*\d*", cd_content))

            if "Vários Cargos" in area_atuacao_list:
                area_atuacao_list = await self.get_possible_areas_from_concurso_link(str(link))

            parent = line.parent
            assert parent

            regiao_soup = parent.find_previous("div", class_="uf")

            assert regiao_soup

            regiao = regiao_soup.text

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
                    niveis_escolaridade=[NivelEscolaridade(descricao=n) for n in nivel_list],
                    areas_atuacao=[AreaAtuacao(descricao=a) for a in area_atuacao_list],
                    salario_max=salario or None,
                    inscricao_ate=datetime.strptime(inscricao, "%d/%m/%Y") if inscricao else None,
                    url=str(link),
                )
            )
        return concurso_list

    async def get_concursos_ativos(self, region_list: list[PciConcursosRegion] | None) -> list[Concurso]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.link) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

        if not region_list:
            region_list = [PciConcursosRegion.TODOS]

        if len(region_list) == 1 and region_list[0] == PciConcursosRegion.TODOS:
            return await self._build_entities_from_soup(soup)

        concurso_list: list[Concurso] = []

        for region in region_list:
            region_soup = soup
            if region != PciConcursosRegion.TODOS:
                source_code_str = str(region_soup)
                if region not in self.region_config:
                    raise ValueError(f"'{region}' não é uma região válida.")

                config = self.region_config[region]
                initial_tag = source_code_str.find(config["start"]) + len(config["start"])
                final_tag = source_code_str.find(config["end"]) + len(config["end"])

                concursos_tag = source_code_str[initial_tag:final_tag]
                region_soup = BeautifulSoup(concursos_tag, "html.parser")

            concurso_list += await self._build_entities_from_soup(region_soup)

        return concurso_list
