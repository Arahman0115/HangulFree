#!/usr/bin/env python3
"""Download and verify the official ko-hand-ocr single-model release."""
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "models" / "ko-hand-ocr-single"
URL = "https://github.com/jysvai/ko-hand-ocr/releases/download/v0.4.1/ko-hand-ocr-single.zip"
SHA256 = "a3ecb62116640705a2333feb642c67dd18793eebfc184aed2c539a27b228d9cc"
FILES = {"model.safetensors", "config.json", "generation_config.json", "vocab.json", "LICENSE", "NOTICE", "PROVENANCE.md", "MODEL_CARD.md"}


def main():
    if (DEST / "model.safetensors").is_file() and (DEST / "config.json").is_file():
        print("OCR model already installed.")
        return
    DEST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        archive = Path(temp) / "model.zip"
        digest = hashlib.sha256()
        print("Downloading ko-hand-ocr 41M model (144 MB)...", flush=True)
        with urlopen(URL, timeout=60) as response, archive.open("wb") as out:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                out.write(chunk)
        if digest.hexdigest() != SHA256:
            raise SystemExit("Model checksum mismatch. Retry the download.")
        with zipfile.ZipFile(archive) as bundle:
            found = {}
            for entry in bundle.infolist():
                name = Path(entry.filename).name
                if name in FILES and not entry.is_dir():
                    found[name] = entry
            if not {"model.safetensors", "config.json", "vocab.json"} <= found.keys():
                raise SystemExit("Model archive is missing required files.")
            for name, entry in found.items():
                target = DEST / name
                with bundle.open(entry) as source, target.open("wb") as out:
                    shutil.copyfileobj(source, out)
    print("OCR model ready.")


if __name__ == "__main__":
    main()
