# Software architecture — Python Raspberry Pi stack

## Design intent

Start with a simple **human-confirmed** recognizer and a dry-run servo controller. No machine motion happens during image recognition; `/api/sort` is a separate explicit call. Always use low-value cards until the mechanics are validated. This starter code does *not* claim to solve exact card-print identification automatically.

```text
          Pi camera / uploaded image
                    |
              Image capture
                    |
           Crop + orientation
                    |
       OCR of name + collector #
                    |
    TCGdex lookup / local catalog cache
                    |
     Candidate ranking + card image
                    |
      User verifies exact printing
                    |
        Rules / bin destination
                    |
          Motion safety guard
                    |
             PCA9685 I2C
                    |
            Tilt servo +/-55°
                    |
       Confirm / log / return center
```

**Exact card identity requires name, collector number, set identity and sometimes artwork / stamped variant.** The same card number exists across many sets. OCR alone is not enough to discriminate exact printing, foil/reverse foil, condition or price. Recommended V2: image embeddings or perceptual hash ranking of a locally cached reference artwork corpus, plus set codes and collector number; route unconfident scans to manual review.

## Python modules in the supplied starter

`software/app.py` contains separate functions for camera capture, OCR, catalog queries, candidate ranking, and servo motion; a modular production app would split them into `camera.py`, `vision.py`, `catalog.py`, `rules.py`, `actuators.py`, `storage.py`, `api.py`.

`GET /api/status` — current simulated/hardware status.

`POST /api/identify` — multipart image upload, OCR, top eight TCGdex candidates (no motion).

`POST /api/identify-camera` — take a Raspberry Pi CSI camera photo, identify candidates (no motion).

`POST /api/sort` — motor movement, requires explicit manual confirmation of hands-clear and side.

`GET /docs` — interactive FastAPI Swagger interface; use this before creating a custom dashboard.

The `/api/identify-camera` method opens and closes the camera each time; once scanning speed matters, use a persistent camera worker, lock its controls, and take snapshots while the stage is level. Add a single processing queue and a persistent SQLite `scans` table. Record timestamp, photo hash, OCR, candidates, confirmed card ID, decision, destination and hardware event.

## Raspberry Pi setup (Raspberry Pi OS)

Check exact model and camera:

```bash
cat /proc/device-tree/model
rpicam-hello --list-cameras
pinout
```

Install system packages:

```bash
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv \
  python3-pil tesseract-ocr tesseract-ocr-eng tesseract-ocr-por \
  i2c-tools python3-venv
```

Start project in a virtual environment. `--system-site-packages` makes apt's camera stack visible:

```bash
cd software
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt
python test_app.py
DRY_RUN=1 uvicorn app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` in the Pi browser, or use SSH port forwarding from your computer (`ssh -L 8000:localhost:8000 <pi-hostname>`). Start with picture upload, then with camera capture. If the card is sideways in the camera image, set `IMAGE_ROTATION=90` or `270` before launching; the name must be at the TOP of the captured image for the default OCR crop. Do not expose motor-control endpoints to untrusted networks.

When wired, start the servo controller only after centering the horn and confirming clearance. Enable I2C in `raspi-config`, then:

```bash
sudo i2cdetect -y 1
pip install adafruit-circuitpython-servokit
# Only after physical checks and e-stop installation:
DRY_RUN=0 uvicorn app:app --host 127.0.0.1 --port 8000
```

## Catalog choice

TCGdex has a free multilingual JSON REST API; initial prototype queries `https://api.tcgdex.net/v2/en/cards?name=pikachu` (or `/pt/` for Brazilian Portuguese cards). Exact printed variants still require a card image comparison / human review. For better performance, sync card metadata into SQLite and build an offline index for name and collector-number search. **Avoid starting a new app on the legacy Pokémon TCG API:** its site says it is deprecated and scheduled to shut down March 1, 2027.

## Proposed V2 state machine

`IDLE -> PRESENT -> STABLE -> CAPTURE -> IDENTIFY -> CONFIRM -> ROUTE -> VERIFY_EXIT -> HOME -> IDLE`

Every motion state must support `E_STOP`, `JAM`, and `TIMEOUT`. The operator should physically clear a jam before resuming. The feeder starts **only** after center/home sensor confirmation and an empty stage. All motor moves should be serialized by one worker; do not drive servos from concurrent HTTP requests.

## Sorting rule examples

- LEFT = confirmed exact ID and rarity in a curated wanted/rare list; RIGHT = bulk.
- LEFT = specified set/collector range; RIGHT = all other confirmed cards.
- If OCR/artwork conflict, card must remain pending review; operator chooses a route and confirms. Add a third review bin only after developing a new mechanical route.

References:
- https://tcgdex.dev/rest/cards
- https://tcgdex.dev/rest/filtering-sorting-pagination
- https://www.raspberrypi.com/documentation/accessories/camera-software.html
