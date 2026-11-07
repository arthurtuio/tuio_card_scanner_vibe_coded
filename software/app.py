"""Pokémon sorter MVP — manually confirmed, two-bin tilt stage.

Safe defaults: DRY_RUN=1, hardware motion disabled. Use a Raspberry Pi
running Linux + a 40-pin GPIO header, or mock mode on your laptop.

This is starter software, not a trained visual identification model.
It uses OCR + TCGdex candidates; the operator MUST confirm a card and bin.
"""
from __future__ import annotations
import io
import os
import re
import threading
import time
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from PIL import Image, ImageOps, ImageEnhance

app = FastAPI(title="Pokémon Sorter MVP", version="0.1.0")
LOCK = threading.Lock()
TCGDEX = "https://api.tcgdex.net/v2"
LANG = os.getenv("CARD_LANGUAGE", "en").strip()
DRY_RUN = os.getenv("DRY_RUN", "1") != "0"
TILT_LEFT = float(os.getenv("TILT_LEFT", "35"))
TILT_CENTER = float(os.getenv("TILT_CENTER", "90"))
TILT_RIGHT = float(os.getenv("TILT_RIGHT", "145"))
TILT_HOLD_S = float(os.getenv("TILT_HOLD_S", "1.5"))
MAX_UPLOAD_BYTES = 12 * 1024 * 1024
VALID_LANGUAGES = {"en", "pt", "fr", "es", "it", "de", "ja"}
if LANG not in VALID_LANGUAGES:
    raise RuntimeError(f"Unsupported CARD_LANGUAGE={LANG!r}")


class TiltStage:
    def __init__(self):
        self.kit = None
        self.last = "center"
        if not DRY_RUN:
            # I2C via PCA9685. Motor supply must be EXTERNAL, common GND.
            from adafruit_servokit import ServoKit
            self.kit = ServoKit(channels=16)
            self.kit.servo[0].angle = TILT_CENTER

    def move(self, side: str):
        if side not in {"left", "right"}:
            raise ValueError("side must be left or right")
        angle = TILT_LEFT if side == "left" else TILT_RIGHT
        if self.kit:
            self.kit.servo[0].angle = angle
        self.last = side
        time.sleep(TILT_HOLD_S)
        if self.kit:
            self.kit.servo[0].angle = TILT_CENTER
        self.last = "center"
        time.sleep(0.5)


stage = None


def get_stage() -> TiltStage:
    global stage
    if stage is None:
        stage = TiltStage()
    return stage


def extract_number(text: str) -> str | None:
    """Collector number e.g. 025/198; does not determine set or foil variant."""
    patterns = [
        r"\b([A-Z]{0,4}\s*\d{1,4})\s*[/|\\]\s*\d{1,4}\b",
        r"\b([A-Z]{0,4}\d{1,4})\s*(?:of)\s*\d{1,4}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return re.sub(r"\s+", "", match.group(1)).upper()
    return None


def clean_name(raw: str) -> str:
    """Top-band OCR heuristic; will require corrections on some cards."""
    lines = [re.sub(r"[^\wÀ-ÿ'\- ]", " ", line).strip()
             for line in raw.splitlines()]
    lines = [re.sub(r"\s+", " ", x) for x in lines if len(x.strip()) >= 3]
    lines = [x for x in lines if not x.lower().startswith((
        "basic", "stage", "pokemon", "pokémon", "hp", "evolves", "evolui", "trainer"))]
    return lines[0][:55] if lines else ""


def read_card(image_bytes: bytes) -> dict:
    import pytesseract
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError("Uploaded content is not a readable image") from exc
    image = ImageOps.exif_transpose(image)
    rotation = int(os.getenv("IMAGE_ROTATION", "0"))
    if rotation not in (0, 90, 180, 270):
        raise ValueError("IMAGE_ROTATION must be 0, 90, 180, or 270")
    if rotation:
        image = image.rotate(rotation, expand=True)
    w, h = image.size
    if w < 300 or h < 300:
        raise ValueError("Image is too small for the collector number OCR")
    # Camera framing calibration: full image should tightly contain the card.
    # Change crop coordinates once the camera is mounted.
    top = image.crop((0, 0, w, int(h * 0.32)))
    bottom = image.crop((0, int(h * 0.70), w, h))
    def ocr_crop(crop):
        c = ImageEnhance.Contrast(crop).enhance(1.5)
        c = c.resize((c.width * 2, c.height * 2))
        return pytesseract.image_to_string(c, config="--psm 6", lang={"en": "eng", "pt": "por"}.get(LANG, "eng"))
    name_ocr = ocr_crop(top)
    number_ocr = ocr_crop(bottom)
    return {
        "name_guess": clean_name(name_ocr),
        "collector_number_guess": extract_number(number_ocr) or extract_number(name_ocr),
        "ocr_top": name_ocr[:800], "ocr_bottom": number_ocr[:800],
        "needs_confirmation": True,
    }


def find_candidates(name: str, collector: str | None) -> list[dict]:
    if not name or len(name) < 3:
        return []
    # TCGdex: name= is substring match, no API key required.
    query = {"name": name}
    try:
        response = requests.get(f"{TCGDEX}/{LANG}/cards", params=query, timeout=12)
        response.raise_for_status()
        cards = response.json()
    except (requests.RequestException, ValueError):
        return []
    if not isinstance(cards, list):
        return []
    candidate_scores = []
    for card in cards[:800]:
        if not isinstance(card, dict):
            continue
        name_score = SequenceMatcher(None, name.lower(), card.get("name", "").lower()).ratio()
        match_num = bool(collector and card.get("localId", "").lstrip("0").lower()
                         == collector.lstrip("0").lower())
        # Ranking is a HEURISTIC, not a statistical confidence probability.
        score = 0.45 * name_score + (0.55 if match_num else 0)
        candidate_scores.append((score, card))
    candidate_scores.sort(key=lambda item: item[0], reverse=True)
    return [{"id": card.get("id"), "name": card.get("name"),
             "collector": card.get("localId"), "image": card.get("image"),
             "match_score": round(score, 3)}
            for score, card in candidate_scores[:8]]


class ManualSort(BaseModel):
    side: Literal["left", "right"]
    confirm_card_removed_from_hands: bool = Field(description="Safety acknowledgement")


@app.get("/api/status")
def status():
    return {"dry_run": DRY_RUN, "motor_enabled": not DRY_RUN,
            "stage": get_stage().last, "language": LANG,
            "warning": "Motion is manual-confirmation only; KEEP FINGERS CLEAR"}


@app.post("/api/identify")
async def identify(file: UploadFile = File(...)):
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Image too large")
    try:
        extracted = read_card(data)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400, str(exc)) from exc
    extracted["candidates"] = find_candidates(
        extracted["name_guess"], extracted["collector_number_guess"])
    return extracted


@app.post("/api/identify-camera")
def identify_camera():
    try:
        from picamera2 import Picamera2
    except ImportError as exc:
        raise HTTPException(503, "Picamera2 unavailable on this host") from exc
    with LOCK:
        camera = Picamera2()
        try:
            config = camera.create_still_configuration(main={"size": (2304, 1296)})
            camera.configure(config)
            camera.start()
            time.sleep(1.4)
            path = Path("/tmp/tcg-sorter-capture.jpg")
            camera.capture_file(str(path))
            return {**(result := read_card(path.read_bytes())),
                    "candidates": find_candidates(result["name_guess"], result["collector_number_guess"])}
        finally:
            camera.stop()
            camera.close()


@app.post("/api/sort")
def sort_card(data: ManualSort):
    if not data.confirm_card_removed_from_hands:
        raise HTTPException(400, "Remove hands from the moving stage first")
    if not LOCK.acquire(blocking=False):
        raise HTTPException(409, "Sorter busy")
    try:
        get_stage().move(data.side)
        return {"sorted_to": data.side, "dry_run": DRY_RUN,
                "message": "Simulated move" if DRY_RUN else "Stage moved, returning to center"}
    except Exception as exc:
        raise HTTPException(500, f"Hardware error: {exc}") from exc
    finally:
        LOCK.release()


@app.get("/")
def index():
    from fastapi.responses import HTMLResponse
    # No JS framework required; scan using the interactive API /docs.
    return HTMLResponse("""<!doctype html><html lang='en'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Pokémon Sorter MVP</title><body style='font:16px system-ui;max-width:650px;margin:3rem auto;padding:1rem'><h1>Pokémon Sorter MVP</h1><p>This prototype defaults to <b>DRY_RUN</b>. A person must confirm identification and sorting.</p><p>Open <a href='/docs'>the interactive API</a> to upload a card image or test Left/Right.</p><p>Install and calibrate physical hardware before enabling motors.</p></body></html>""")
