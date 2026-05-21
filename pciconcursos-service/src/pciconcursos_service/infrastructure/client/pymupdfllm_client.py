import tempfile
from pathlib import Path

import aiohttp
import pymupdf4llm as pmpllm

from pciconcursos_service.domain.concursos.repository import PDFClient


class PyMuPDFClient(PDFClient):
    async def pdf_url_to_md(self, pdf_url: str) -> str:
        filename = Path(pdf_url).stem
        tmp_dir = tempfile.gettempdir()
        pdf_path = Path(tmp_dir) / f"{filename}.pdf"

        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                assert response.ok, str(response)

                with open(pdf_path, "wb") as file:
                    async for chunk in response.content.iter_chunked(1024):
                        file.write(chunk)

        md_text: str = pmpllm.to_markdown(pdf_path)
        pdf_path.unlink()
        return md_text
