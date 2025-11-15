import re

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

from python_service_template.domain.concursos.repository import ConcursoClient

LINK = "https://www.pciconcursos.com.br/concursos/"

REGION_CONFIG = {
    "nacional": {"start": "<h2>NACIONAL</h2>", "end": "<h2>REGIÃO SUDESTE</h2>"},
    "CE": {
        "start": '<div class="uf">CEARÁ</div>',
        "end": '<div class="uf">MARANHÃO</div>',
    },
    "SP": {
        "start": '<div class="uf">SÃO PAULO</div>',
        "end": '<div class="uf">RIO DE JANEIRO</div>',
    },
    "RJ": {
        "start": '<div class="uf">RIO DE JANEIRO</div>',
        "end": '<div class="uf">MINAS GERAIS</div>',
    },
    "MG": {
        "start": '<div class="uf">MINAS GERAIS</div>',
        "end": '<div class="uf">ESPÍRITO SANTO</div>',
    },
    "ES": {
        "start": '<div class="uf">ESPÍRITO SANTO</div>',
        "end": "<h2>REGIÃO SUL</h2>",
    },
    "PR": {
        "start": '<div class="uf">PARANÁ</div>',
        "end": '<div class="uf">RIO GRANDE DO SUL</div>',
    },
    "SC": {
        "start": '<div class="uf">SANTA CATARINA</div>',
        "end": "<h2>REGIÃO CENTRO-OESTE</h2>",
    },
    "DF": {
        "start": '<div class="uf">DISTRITO FEDERAL</div>',
        "end": '<div class="uf">GOIÁS</div>',
    },
    "GO": {
        "start": '<div class="uf">GOIÁS</div>',
        "end": '<div class="uf">MATO GROSSO DO SUL</div>',
    },
    "MS": {
        "start": '<div class="uf">MATO GROSSO DO SUL</div>',
        "end": '<div class="uf">MATO GROSSO</div>',
    },
    "MT": {
        "start": '<div class="uf">MATO GROSSO</div>',
        "end": "<h2>REGIÃO NORTE</h2>",
    },
    "AM": {
        "start": '<div class="uf">AMAZONAS</div>',
        "end": '<div class="uf">ACRE</div>',
    },
    "AC": {"start": '<div class="uf">ACRE</div>', "end": '<div class="uf">PARÁ</div>'},
    "PA": {
        "start": '<div class="uf">PARÁ</div>',
        "end": '<div class="uf">RONDÔNIA</div>',
    },
    "RO": {
        "start": '<div class="uf">RONDÔNIA</div>',
        "end": '<div class="uf">TOCANTINS</div>',
    },
    "TO": {
        "start": '<div class="uf">TOCANTINS</div>',
        "end": "<h2>REGIÃO NORDESTE</h2>",
    },
    "AL": {
        "start": '<div class="uf">ALAGOAS</div>',
        "end": '<div class="uf">BAHIA</div>',
    },
    "BA": {
        "start": '<div class="uf">BAHIA</div>',
        "end": '<div class="uf">CEARÁ</div>',
    },
    "MA": {
        "start": '<div class="uf">MARANHÃO</div>',
        "end": '<div class="uf">PARAÍBA</div>',
    },
    "PB": {
        "start": '<div class="uf">PARAÍBA</div>',
        "end": '<div class="uf">PERNAMBUCO</div>',
    },
    "PE": {
        "start": '<div class="uf">PERNAMBUCO</div>',
        "end": '<div class="uf">PIAUÍ</div>',
    },
    "PI": {
        "start": '<div class="uf">PIAUÍ</div>',
        "end": '<div class="uf">RIO GRANDE DO NORTE</div>',
    },
    "RN": {
        "start": '<div class="uf">RIO GRANDE DO NORTE</div>',
        "end": '<div class="uf">SERGIPE</div>',
    },
    "SE": {
        "start": '<div class="uf">SERGIPE</div>',
        "end": '<p style="text-align:center; margin:0; padding:10px 0 0 0; font-weight:bold; color:#205c98;">VISITE PERIODICAMENTE - ATUALIZAÇÃO DIÁRIA!!!</p>',
    },
}


class PciConcursosClient(ConcursoClient):
    async def _exam_region(self, source_code, region):
        source_code_str = str(source_code)

        if region not in REGION_CONFIG:
            raise ValueError(f"'{region}' não é uma região válida.")

        config = REGION_CONFIG[region]
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
            nivel = "/".join(re.findall(r"Superior|Médio", cd_content))
            salario = "".join(re.findall(r"R\$ *\d*\.*\d*\,*\d*", cd_content))
            inscricao = "".join(re.findall(r"\d+/\d+/\d+", ce_content))

            combinacao_concursos.append([name, vagas, nivel, salario, inscricao, link])

        return combinacao_concursos

    async def get_concursos_ativos(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(LINK) as response:
                soup = BeautifulSoup(await response.text(), "html.parser")

        state = await self._exam_region(soup, "PR")

        df = pd.DataFrame(state)

        df = df.replace(r"^\s*$", "-", regex=True)
        return df.to_csv(index=False)
