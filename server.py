#!/usr/bin/env python3
"""Local Hangul handwriting practice server."""
import base64
import html
import json
import os
import sys
import re
import unicodedata
from io import BytesIO
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "vendor"))
from kohandocr.reader import Reader

MODEL = "ko-hand-ocr 41M"
MODEL_DIR = ROOT / "models" / "ko-hand-ocr-single"
_reader = None
_reader_lock = Lock()
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8765"))
CUSTOM_PATH = ROOT / "custom_words.json"
_words_lock = Lock()
WORDS = [
    {"korean": "사과", "romanization": "sagwa", "meaning": "apple"},
    {"korean": "학교", "romanization": "hakgyo", "meaning": "school"},
    {"korean": "바다", "romanization": "bada", "meaning": "sea"},
    {"korean": "고양이", "romanization": "goyangi", "meaning": "cat"},
    {"korean": "친구", "romanization": "chingu", "meaning": "friend"},
    {"korean": "커피", "romanization": "keopi", "meaning": "coffee"},
    {"korean": "나무", "romanization": "namu", "meaning": "tree"},
    {"korean": "의자", "romanization": "uija", "meaning": "chair"},
    {"korean": "우유", "romanization": "uyu", "meaning": "milk"},
    {"korean": "전화", "romanization": "jeonhwa", "meaning": "phone"},
    {"korean": "모자", "romanization": "moja", "meaning": "hat"},
    {"korean": "하늘", "romanization": "haneul", "meaning": "sky"},
    {"korean": "토끼", "romanization": "tokki", "meaning": "rabbit"},
    {"korean": "도서관", "romanization": "doseogwan", "meaning": "library"},
    {"korean": "컴퓨터", "romanization": "keompyuteo", "meaning": "computer"},
    {"korean": "안녕하세요", "romanization": "annyeonghaseyo", "meaning": "hello"},
    {"korean": "사람", "romanization": "saram", "meaning": "person"},
    {"korean": "아이", "romanization": "ai", "meaning": "child"},
    {"korean": "아기", "romanization": "agi", "meaning": "baby"},
    {"korean": "엄마", "romanization": "eomma", "meaning": "mom"},
    {"korean": "아빠", "romanization": "appa", "meaning": "dad"},
    {"korean": "어머니", "romanization": "eomeoni", "meaning": "mother"},
    {"korean": "아버지", "romanization": "abeoji", "meaning": "father"},
    {"korean": "언니", "romanization": "eonni", "meaning": "older sister (female speaker)"},
    {"korean": "오빠", "romanization": "oppa", "meaning": "older brother (female speaker)"},
    {"korean": "동생", "romanization": "dongsaeng", "meaning": "younger sibling"},
    {"korean": "집", "romanization": "jip", "meaning": "house"},
    {"korean": "방", "romanization": "bang", "meaning": "room"},
    {"korean": "문", "romanization": "mun", "meaning": "door"},
    {"korean": "창문", "romanization": "changmun", "meaning": "window"},
    {"korean": "길", "romanization": "gil", "meaning": "road"},
    {"korean": "공원", "romanization": "gongwon", "meaning": "park"},
    {"korean": "산", "romanization": "san", "meaning": "mountain"},
    {"korean": "강", "romanization": "gang", "meaning": "river"},
    {"korean": "섬", "romanization": "seom", "meaning": "island"},
    {"korean": "숲", "romanization": "sup", "meaning": "forest"},
    {"korean": "밥", "romanization": "bap", "meaning": "cooked rice"},
    {"korean": "물", "romanization": "mul", "meaning": "water"},
    {"korean": "빵", "romanization": "ppang", "meaning": "bread"},
    {"korean": "달걀", "romanization": "dalgyal", "meaning": "egg"},
    {"korean": "고기", "romanization": "gogi", "meaning": "meat"},
    {"korean": "생선", "romanization": "saengseon", "meaning": "fish (food)"},
    {"korean": "김치", "romanization": "gimchi", "meaning": "kimchi"},
    {"korean": "국", "romanization": "guk", "meaning": "soup"},
    {"korean": "소금", "romanization": "sogeum", "meaning": "salt"},
    {"korean": "설탕", "romanization": "seoltang", "meaning": "sugar"},
    {"korean": "바나나", "romanization": "banana", "meaning": "banana"},
    {"korean": "딸기", "romanization": "ttalgi", "meaning": "strawberry"},
    {"korean": "포도", "romanization": "podo", "meaning": "grape"},
    {"korean": "수박", "romanization": "subak", "meaning": "watermelon"},
    {"korean": "귤", "romanization": "gyul", "meaning": "tangerine"},
    {"korean": "복숭아", "romanization": "boksunga", "meaning": "peach"},
    {"korean": "배", "romanization": "bae", "meaning": "pear"},
    {"korean": "당근", "romanization": "danggeun", "meaning": "carrot"},
    {"korean": "감자", "romanization": "gamja", "meaning": "potato"},
    {"korean": "양파", "romanization": "yangpa", "meaning": "onion"},
    {"korean": "책", "romanization": "chaek", "meaning": "book"},
    {"korean": "연필", "romanization": "yeonpil", "meaning": "pencil"},
    {"korean": "종이", "romanization": "jongi", "meaning": "paper"},
    {"korean": "가방", "romanization": "gabang", "meaning": "bag"},
    {"korean": "신발", "romanization": "sinbal", "meaning": "shoes"},
    {"korean": "옷", "romanization": "ot", "meaning": "clothes"},
    {"korean": "시계", "romanization": "sigye", "meaning": "clock"},
    {"korean": "열쇠", "romanization": "yeolsoe", "meaning": "key"},
    {"korean": "거울", "romanization": "geoul", "meaning": "mirror"},
    {"korean": "사진", "romanization": "sajin", "meaning": "photo"},
    {"korean": "개", "romanization": "gae", "meaning": "dog"},
    {"korean": "새", "romanization": "sae", "meaning": "bird"},
    {"korean": "말", "romanization": "mal", "meaning": "horse"},
    {"korean": "소", "romanization": "so", "meaning": "cow"},
    {"korean": "돼지", "romanization": "dwaeji", "meaning": "pig"},
    {"korean": "양", "romanization": "yang", "meaning": "sheep"},
    {"korean": "닭", "romanization": "dak", "meaning": "chicken"},
    {"korean": "물고기", "romanization": "mulgogi", "meaning": "fish (animal)"},
    {"korean": "곰", "romanization": "gom", "meaning": "bear"},
    {"korean": "사자", "romanization": "saja", "meaning": "lion"},
    {"korean": "눈", "romanization": "nun", "meaning": "eye"},
    {"korean": "코", "romanization": "ko", "meaning": "nose"},
    {"korean": "입", "romanization": "ip", "meaning": "mouth"},
    {"korean": "귀", "romanization": "gwi", "meaning": "ear"},
    {"korean": "손", "romanization": "son", "meaning": "hand"},
    {"korean": "발", "romanization": "bal", "meaning": "foot"},
    {"korean": "머리", "romanization": "meori", "meaning": "head"},
    {"korean": "얼굴", "romanization": "eolgul", "meaning": "face"},
    {"korean": "이", "romanization": "i", "meaning": "tooth"},
    {"korean": "어깨", "romanization": "eokkae", "meaning": "shoulder"},
    {"korean": "오늘", "romanization": "oneul", "meaning": "today"},
    {"korean": "내일", "romanization": "naeil", "meaning": "tomorrow"},
    {"korean": "어제", "romanization": "eoje", "meaning": "yesterday"},
    {"korean": "아침", "romanization": "achim", "meaning": "morning"},
    {"korean": "저녁", "romanization": "jeonyeok", "meaning": "evening"},
    {"korean": "밤", "romanization": "bam", "meaning": "night"},
    {"korean": "낮", "romanization": "nat", "meaning": "daytime"},
    {"korean": "비", "romanization": "bi", "meaning": "rain"},
    {"korean": "눈송이", "romanization": "nunsongi", "meaning": "snowflake"},
    {"korean": "바람", "romanization": "baram", "meaning": "wind"},
    {"korean": "빨강", "romanization": "ppalgang", "meaning": "red"},
    {"korean": "파랑", "romanization": "parang", "meaning": "blue"},
    {"korean": "노랑", "romanization": "norang", "meaning": "yellow"},
    {"korean": "초록", "romanization": "chorok", "meaning": "green"},
    {"korean": "검정", "romanization": "geomjeong", "meaning": "black"},
    {"korean": "하양", "romanization": "hayang", "meaning": "white"},
    {"korean": "분홍", "romanization": "bunhong", "meaning": "pink"},
    {"korean": "보라", "romanization": "bora", "meaning": "purple"},
    {"korean": "회색", "romanization": "hoesaek", "meaning": "gray"},
    {"korean": "갈색", "romanization": "galsaek", "meaning": "brown"},
    {"korean": "가다", "romanization": "gada", "meaning": "to go"},
    {"korean": "오다", "romanization": "oda", "meaning": "to come"},
    {"korean": "먹다", "romanization": "meokda", "meaning": "to eat"},
    {"korean": "마시다", "romanization": "masida", "meaning": "to drink"},
    {"korean": "보다", "romanization": "boda", "meaning": "to see"},
    {"korean": "듣다", "romanization": "deutda", "meaning": "to listen"},
    {"korean": "읽다", "romanization": "ikda", "meaning": "to read"},
    {"korean": "쓰다", "romanization": "sseuda", "meaning": "to write"},
    {"korean": "자다", "romanization": "jada", "meaning": "to sleep"},
    {"korean": "웃다", "romanization": "utda", "meaning": "to laugh"},
]
BASE_WORD_COUNT = len(WORDS)


def meaning_key(meaning):
    return re.sub(r"[\s'-]+", " ", meaning.casefold()).strip()


WORD_MEANINGS = {meaning_key(word["meaning"]) for word in WORDS}
WORD_KOREAN = {word["korean"] for word in WORDS}


def valid_word(meaning, korean, romanization):
    meaning = meaning.strip()
    korean = unicodedata.normalize("NFC", korean.strip())
    romanization = romanization.strip().lower()
    if not re.fullmatch(r"[A-Za-z][A-Za-z '-]{0,49}", meaning):
        raise ValueError("Enter a short English word or phrase.")
    if not 1 <= len(korean) <= 8 or not all("가" <= ch <= "힣" for ch in korean):
        raise ValueError("Korean must contain 1–8 Hangul syllables, without spaces.")
    if not re.fullmatch(r"[a-z][a-z'-]{0,59}", romanization):
        raise ValueError("Enter romanization using Latin letters.")
    return {"meaning": meaning, "korean": korean, "romanization": romanization}


def public_word(word, index):
    return {"id": index, "meaning": word["meaning"], "korean": word["korean"], "romanization": word["romanization"], "syllables": len(word["korean"])}


RR_INITIAL = ("g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h")
RR_VOWEL = ("a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i")
RR_FINAL = ("", "k", "k", "k", "n", "n", "n", "t", "l", "k", "m", "l", "l", "l", "p", "l", "m", "p", "p", "t", "t", "ng", "t", "t", "k", "t", "p", "t")


def romanize(korean):
    result = []
    for ch in korean:
        n = ord(ch) - 0xAC00
        if not 0 <= n < 11172:
            raise ValueError("Translation must contain Hangul syllables only.")
        result.append(RR_INITIAL[n // 588] + RR_VOWEL[(n % 588) // 28] + RR_FINAL[n % 28])
    return "".join(result)


if CUSTOM_PATH.exists():
    for saved in json.loads(CUSTOM_PATH.read_text(encoding="utf-8")):
        word = valid_word(saved["meaning"], saved["korean"], saved["romanization"])
        key = meaning_key(word["meaning"])
        if key in WORD_MEANINGS or word["korean"] in WORD_KOREAN:
            continue
        WORDS.append(word)
        WORD_MEANINGS.add(key)
        WORD_KOREAN.add(word["korean"])


def suggest_word(meaning):
    verb = meaning.lower().startswith("to ")
    query = meaning[3:] if verb else meaning
    url = "https://api.mymemory.translated.net/get?" + urlencode({"q": query, "langpair": "en|ko"})
    try:
        with urlopen(url, timeout=10) as response:
            result = json.loads(response.read(250_000))
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ValueError("Online suggestion unavailable. Enter Korean and romanization manually.") from exc
    if not isinstance(result, dict) or result.get("responseStatus") != 200 or result.get("quotaFinished"):
        raise ValueError("Online suggestion limit reached. Enter Korean and romanization manually.")
    candidates = [result.get("responseData", {}).get("translatedText", "")]
    for match in result.get("matches", []):
        try:
            if float(match.get("match", 0)) >= .95:
                candidates.append(match.get("translation", ""))
        except (AttributeError, TypeError, ValueError):
            continue
    if verb:
        candidates.sort(key=lambda candidate: not str(candidate or "").strip().endswith("다"))
    for candidate in candidates:
        korean = re.sub(r"\s+", "", html.unescape(candidate))
        try:
            return valid_word(meaning, korean, romanize(korean))
        except (ValueError, TypeError):
            continue
    raise ValueError("No one-word Korean suggestion found. Enter one manually.")

CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
JUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
JONG = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"


def parts(ch):
    n = ord(ch) - 0xAC00
    if not 0 <= n < 11172:
        return None
    return (CHO[n // 588], JUNG[(n % 588) // 28], JONG[n % 28].strip())


def grade(answer, reading):
    """Return position based feedback; compare individual Hangul components."""
    errors = []
    for i in range(max(len(answer), len(reading))):
        want = answer[i] if i < len(answer) else ""
        got = reading[i] if i < len(reading) else ""
        if want == got:
            continue
        a, b = parts(want) if want else None, parts(got) if got else None
        if a and b:
            for label, x, y in zip(("initial", "vowel", "final"), a, b):
                if x != y:
                    errors.append({"index": i, "part": label, "expected": x or "∅", "read": y or "∅"})
        else:
            errors.append({"index": i, "part": "syllable", "expected": want or "∅", "read": got or "∅"})
    return {"correct": not errors, "errors": errors}


def transcribe(raws):
    global _reader
    images = []
    for block, raw in enumerate(raws, 1):
        with Image.open(BytesIO(base64.b64decode(raw))) as image:
            if image.width * image.height > 2_000_000:
                raise ValueError("Drawing is too large.")
            clean = image.convert("RGB")
            if not ImageChops.difference(clean, Image.new("RGB", clean.size, "white")).getbbox():
                raise ValueError(f"Block {block} is empty. Draw one complete syllable in each section.")
            images.append(clean)
    with _reader_lock:
        if _reader is None:
            _reader = Reader(MODEL_DIR, device="cpu", threads=4)
        readings = _reader.read(images)
    if len(readings) != len(images):
        raise ValueError("Some syllables could not be read. Try drawing them again.")
    syllables = []
    for block, reading in enumerate(readings, 1):
        clean = "".join(ch for ch in reading if parts(ch))
        if len(clean) != 1:
            raise ValueError(f"Block {block} was unclear. Write one complete syllable there and check again.")
        syllables.append(clean)
    return "".join(syllables)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "static"), **kwargs)

    def do_GET(self):
        if self.path == "/api/words":
            with _words_lock:
                return self.send_json([public_word(word, i) for i, word in enumerate(WORDS)])
        if self.path == "/api/health":
            return self.send_json({"ready": (MODEL_DIR / "model.safetensors").is_file(), "model": MODEL})
        return super().do_GET()

    def do_POST(self):
        if self.path not in ("/api/check", "/api/suggest", "/api/words"):
            return self.send_json({"error": "Not found"}, 404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 3_000_000:
                return self.send_json({"error": "Request is too large or missing."}, 400)
            if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
                return self.send_json({"error": "Expected JSON."}, 415)
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                return self.send_json({"error": "Expected a JSON object."}, 400)
            if self.path == "/api/suggest":
                meaning = data.get("meaning", "")
                if not isinstance(meaning, str) or not re.fullmatch(r"[A-Za-z][A-Za-z '-]{0,49}", meaning.strip()):
                    return self.send_json({"error": "Enter a short English word or phrase."}, 400)
                return self.send_json(suggest_word(meaning.strip()))
            if self.path == "/api/words":
                if not all(isinstance(data.get(key), str) for key in ("meaning", "korean", "romanization")):
                    return self.send_json({"error": "Fill in all three word fields."}, 400)
                word = valid_word(data["meaning"], data["korean"], data["romanization"])
                with _words_lock:
                    key = meaning_key(word["meaning"])
                    if key in WORD_MEANINGS or word["korean"] in WORD_KOREAN:
                        return self.send_json({"error": "That English clue or Korean spelling is already in the bank."}, 409)
                    saved = WORDS[BASE_WORD_COUNT:] + [word]
                    temp = CUSTOM_PATH.with_suffix(".tmp")
                    temp.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    temp.replace(CUSTOM_PATH)
                    WORDS.append(word)
                    WORD_MEANINGS.add(key)
                    WORD_KOREAN.add(word["korean"])
                    return self.send_json(public_word(word, len(WORDS) - 1), 201)
            index = data.get("id")
            images = data.get("images", [])
            if not isinstance(index, int) or not 0 <= index < len(WORDS):
                return self.send_json({"error": "Invalid word."}, 400)
            if not isinstance(images, list) or len(images) != len(WORDS[index]["korean"]):
                return self.send_json({"error": "Invalid drawing."}, 400)
            raws = []
            for image in images:
                if not isinstance(image, str) or not image.startswith("data:image/png;base64,"):
                    return self.send_json({"error": "Invalid drawing."}, 400)
                raw = image.split(",", 1)[1]
                if len(base64.b64decode(raw, validate=True)) > 2_000_000:
                    return self.send_json({"error": "Image is too large."}, 400)
                raws.append(raw)
            word = WORDS[index]
            reading = transcribe(raws)
            return self.send_json({"transcription": reading, "answer": word["korean"], **grade(word["korean"], reading)})
        except (ValueError, KeyError, OSError) as e:
            return self.send_json({"error": str(e)}, 400)

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"Open http://{HOST}:{PORT} — model: {MODEL}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
