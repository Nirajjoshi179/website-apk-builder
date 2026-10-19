
import os
import shutil
import urllib.request
import urllib.parse
import zipfile
from pathlib import Path

kind = os.environ["SOURCE_TYPE"].lower()
assets = Path("app/src/main/assets")
base = os.environ["SUPABASE_URL"].rstrip("/")
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

if assets.exists():
    shutil.rmtree(assets)
assets.mkdir(parents=True)

def download_source(path):
    if not path or path.startswith("/") or ".." in Path(path).parts:
        raise ValueError("Invalid Supabase Storage path")

    url = (
        f"{base}/storage/v1/object/apk-files/"
        + urllib.parse.quote(path, safe="/")
    )

    req = urllib.request.Request(url, headers={
        "apikey": key,
        "Authorization": f"Bearer {key}"
    })

    with urllib.request.urlopen(req, timeout=90) as response:
        data = response.read()

    if len(data) > 40 * 1024 * 1024:
        raise ValueError("Source file exceeds 40 MB")

    return data

if kind == "url":
    from urllib.parse import urlparse

    url = os.environ["WEBSITE_URL"].strip()
    parsed = urlparse(url)

    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("A valid HTTPS website URL is required")

    (assets / "start-url.txt").write_text(url)

elif kind == "html":
    html = os.environ.get("HTML_CODE", "")

    if not html.strip():
        raise ValueError("HTML code is empty")

    (assets / "index.html").write_text(
        html, encoding="utf-8"
    )

elif kind == "file":
    path = os.environ["SOURCE_PATH"]

    if not path.lower().endswith((".html", ".htm")):
        raise ValueError("Select an HTML file")

    (assets / "index.html").write_bytes(
        download_source(path)
    )

elif kind == "zip":
    path = os.environ["SOURCE_PATH"]

    if not path.lower().endswith(".zip"):
        raise ValueError("Select a ZIP file")

    archive = Path("/tmp/site.zip")
    archive.write_bytes(download_source(path))

    target = Path("/tmp/site")
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()

    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            dest = (target / info.filename).resolve()

            if (
                dest != target.resolve()
                and not str(dest).startswith(
                    str(target.resolve()) + os.sep
                )
            ):
                raise ValueError("Unsafe ZIP path")

        z.extractall(target)

    indexes = list(target.rglob("index.html"))
    if not indexes:
        indexes = list(target.rglob("index.htm"))

    if not indexes:
        raise ValueError("ZIP must contain index.html")

    site = indexes[0].parent

    for file in site.rglob("*"):
        if file.is_file():
            dest = assets / file.relative_to(site)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dest)

else:
    raise ValueError("Unknown input mode")

print("Source prepared:", kind)

