import re

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

from python_service_template.domain.concursos.repository import ConcursoClient
from python_service_template.settings import PciConcursosRegion


class PciConcursosClient(ConcursoClient):
    def __init__(self, link: str, region_config: dict) -> None:
        self.link = link
        self.region_config = region_config

    async def get_concursos_ativos(self, region):
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

        combinacao_concursos = [
            [
                "Concurso",
                "Vagas",
                "Nível",
                "Salário Até",
                "Inscrição Até",
                "Link",
            ]
        ]

        for line in soup.find_all(class_="ca"):
            name = line.find("a").text.strip()
            link = line.find("a", href=True)["href"]

            cd_content = str(line.find(class_="cd"))
            ce_content = str(line.find(class_="ce"))

            vagas = "".join(re.findall(r"(\d*) vaga", cd_content))
            nivel = "/".join(re.findall(r"Superior|Médio|Técnico|Fundamental", cd_content))
            salario = "".join(re.findall(r"R\$ *\d*\.*\d*\,*\d*", cd_content))
            inscricao = "".join(re.findall(r"\d+/\d+/\d+", ce_content))

            combinacao_concursos.append([name, vagas, nivel, salario, inscricao, link])

        df = pd.DataFrame(combinacao_concursos)
        df = df.replace(r"^\s*$", "-", regex=True)

        return df.to_csv(index=False)
