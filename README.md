# HangulFree

A local Hangul writing practice platform. Pick an English word, draw its Korean spelling one syllable per section, and check your writing. The app reads each section with a local OCR model, then shows which consonants or vowels differ from the answer. You can correct the model's reading before grading.

## Run locally

Requirements: Python 3.10 or newer, Git, an internet connection for the first setup, and enough disk space for PyTorch and the 144 MB OCR model. Linux and macOS:

```bash
git clone https://github.com/Arahman0115/HangulFree.git
cd HangulFree
./run.sh
```

Open **http://127.0.0.1:8765/**. Stop the server with `Ctrl+C`. Later runs use the downloaded model and installed packages; the core practice app works offline. No Ollama, API key, or GPU is needed.

If `./run.sh` is not executable, run `bash run.sh`. To use a specific Python installation, run `PYTHON=python3.11 bash run.sh`.

### Windows (PowerShell)

```powershell
git clone https://github.com/Arahman0115/HangulFree.git
cd HangulFree
py -3 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python download_model.py
.venv\Scripts\python server.py
```

Open **http://127.0.0.1:8765/**. For later runs, only the last command is needed.

## Use

- Draw one complete Hangul syllable in each section, then select **Check writing**.
- If the OCR reading is wrong, edit **Read as** before grading.
- Use **Next word** to skip or continue. The word bank can be searched and paged.
- Use **+** in the word bank to add a word. Enter Korean and romanization yourself, or use **Suggest Korean online** and review its answer. `custom_words.json` supplies the starter custom words and saves new ones.
- Hover over a word in the bank and select **×** to delete it. On touch screens, the **×** is always visible. Deleted built-in words are remembered locally in `deleted_words.json`.

The number of drawing sections is the number of Hangul syllable characters in the Korean spelling. The drawing, word bank, and model inference stay on your computer. **Suggest Korean online** sends only the English term to MyMemory.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| `python3` or `py` is missing | Install Python 3.10+ and retry. On Windows, enable the Python launcher during installation. |
| Virtual environment creation fails | Install your OS's Python `venv` package, then retry `bash run.sh`. |
| Package installation fails | Check your internet connection and Python version. Delete `.venv` and rerun the setup. CPU PyTorch is sufficient. |
| Model download fails or checksum mismatches | Check the connection and rerun `bash run.sh` or `python download_model.py`. The model is downloaded from the pinned official release and checked with SHA-256. |
| Port 8765 is already in use | Stop the other server, or run `PORT=8766 bash run.sh` and open `http://127.0.0.1:8766/`. On PowerShell, set `$env:PORT=8766` before starting the server. |
| The page says a block is empty | Draw in that section and check again. If the OCR reading is uncertain, edit **Read as** before grading. |
| The OCR misreads a drawing | Edit **Read as** to match what you drew, then grade it. The model can make mistakes. |
| Online word suggestion fails | Enter Korean and romanization manually. Suggestion requires internet access and is subject to MyMemory limits. |

## Credits

The app code is MIT licensed (see [`LICENSE`](LICENSE)). Third-party inference code and model files retain their own terms.

- Handwriting recognition: [ko-hand-ocr](https://github.com/jysvai/ko-hand-ocr) by its contributors, using the 41M single model from [release v0.4.1](https://github.com/jysvai/ko-hand-ocr/releases/tag/v0.4.1). The model runs locally on the CPU. The vendored inference code is under Apache 2.0; see [`vendor/LICENSE`](vendor/LICENSE) and [`vendor/NOTICE`](vendor/NOTICE). The downloaded model archive includes its own license and provenance files.
- Optional English to Korean suggestions: [MyMemory Translation API](https://mymemory.translated.net/doc/spec.php). Its output may be imperfect; review it before adding a word.
