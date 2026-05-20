import csv
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pymupdf4llm


ssl._create_default_https_context = ssl._create_unverified_context  # ty:ignore[invalid-assignment]

TMP_DIR = Path("/tmp/pdf-to-md")
OUT_DIR = Path("out")
MAX_WORKERS = 4


def process_url(url: str) -> str:
    filename = Path(url).stem
    out_path = OUT_DIR / f"{filename}.md"

    if out_path.exists():
        return f"Skipping {url} — already exists"

    pdf_path = TMP_DIR / f"{filename}.pdf"
    urllib.request.urlretrieve(url, pdf_path)

    md_text = pymupdf4llm.to_markdown(pdf_path)
    out_path.write_text(md_text, encoding="utf-8")
    pdf_path.unlink()

    return f"Done {filename}"


def main():
    OUT_DIR.mkdir(exist_ok=True)
    TMP_DIR.mkdir(exist_ok=True)

    urls: list[str] = []
    with open("pdf_urls.csv", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                url = row[0].strip()
                if url:
                    urls.append(url)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        fut = {executor.submit(process_url, url): url for url in urls}
        for f in as_completed(fut):
            print(f.result())


if __name__ == "__main__":
    main()
