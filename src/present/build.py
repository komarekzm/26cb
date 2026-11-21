"""Renderuje docs/ (strona z zagadką i zaszyfrowanym hasłem) oraz build/karta-A4.html.

Zasada: na stronie nie ma ani kuponu, ani hasła jawnym tekstem. W HTML siedzi wyłącznie
szyfrogram AES-GCM, którego klucz powstaje ze słowa ułożonego w zagadce (PBKDF2-SHA256).
QR kuponu nie trafia na stronę wcale — ten papier leży pod monitorem.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from present import codec, config, figure, puzzle as puzzle_mod

ROOT = config.ROOT
TEMPLATES = ROOT / "templates"
DOCS = ROOT / "docs"
BUILD = ROOT / "build"

ITERATIONS = 210_000
KDF_STATE = BUILD / "kdf.json"  # sól i IV przeżywają rebuildy, żeby HTML nie skakał
ANSWER_FILE = BUILD / "answer.txt"  # dla testów; build/ jest w .gitignore


def qr_png(code: str) -> Path:
    BUILD.mkdir(exist_ok=True)
    path = BUILD / "qr.png"
    subprocess.run(
        ["qrencode", "-o", str(path), "-t", "PNG", "-s", "8", "-m", "2", code], check=True
    )
    return path


def verify_qr(path: Path, code: str) -> None:
    """Dekoduje QR z powrotem — zły QR pod monitorem psuje całą zabawę."""
    decoded = subprocess.run(
        ["zbarimg", "-q", "--raw", str(path)], check=True, capture_output=True, text=True
    ).stdout.strip()
    if decoded != code:
        raise SystemExit(f"QR nie odczytuje się poprawnie: {decoded!r} != {code!r}")


def kdf_material(rotate: bool = False) -> tuple[bytes, bytes]:
    """Sól i IV trzymamy na dysku, żeby kolejne buildy dawały ten sam HTML."""
    if KDF_STATE.exists() and not rotate:
        state = json.loads(KDF_STATE.read_text())
        return base64.b64decode(state["salt"]), base64.b64decode(state["iv"])
    salt, iv = os.urandom(16), os.urandom(12)
    BUILD.mkdir(exist_ok=True)
    KDF_STATE.write_text(
        json.dumps({"salt": base64.b64encode(salt).decode(), "iv": base64.b64encode(iv).decode()})
    )
    return salt, iv


def derive(answer: str, salt: bytes) -> bytes:
    # Ta sama procedura co w templates/unlock.js — inaczej przeglądarka nie odszyfruje.
    return hashlib.pbkdf2_hmac("sha256", answer.encode(), salt, ITERATIONS, 32)


def seal(payload: dict, answer: str, rotate: bool = False) -> dict:
    salt, iv = kdf_material(rotate)
    ciphertext = AESGCM(derive(answer, salt)).encrypt(iv, json.dumps(payload).encode(), None)
    return {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ciphertext).decode(),
        "iterations": ITERATIONS,
    }


def open_box(box: dict, answer: str) -> dict | None:
    """Kontrola przed publikacją: czy słowo z zagadki naprawdę otwiera wiadomość."""
    try:
        plain = AESGCM(derive(answer, base64.b64decode(box["salt"]))).decrypt(
            base64.b64decode(box["iv"]), base64.b64decode(box["ct"]), None
        )
    except Exception:
        return None
    return json.loads(plain)


def read_coupon() -> str:
    path = ROOT / "kupon.txt"
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) != 1:
        raise SystemExit("kupon.txt ma zawierać dokładnie jeden kod — jedną niepustą linię")
    return lines[0]


def main() -> None:
    cfg = config.load()
    site = config.site()
    code = read_coupon()
    rotate = "--rotate" in sys.argv

    if not cfg["page"]["test_mode"] and code.upper().startswith("TEST"):
        raise SystemExit(
            "page.test_mode = false, ale kupon.txt wciąż ma kod testowy. "
            "Wklej prawdziwy kod albo włącz test_mode."
        )

    puzzle = puzzle_mod.load(cfg)
    answer = puzzle.answer

    # QR generujemy mimo wszystko: to on idzie na wydruk pod monitor.
    qr_file = qr_png(code)
    verify_qr(qr_file, code)

    payload = {"text": cfg["voucher"]["location"]}
    box = seal(payload, answer, rotate=rotate)
    if open_box(box, answer) != payload:
        raise SystemExit("słowo z zagadki nie otwiera szyfrogramu — coś się rozjechało")
    if open_box(box, "nieprawdopodobne-haslo") is not None:
        raise SystemExit("złe hasło otworzyło szyfrogram — to nie powinno się zdarzyć")

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    first_hex = codec.to_hex(site.address)[:2]
    common = {
        "page": cfg["page"],
        "gift": {**cfg["gift"], "lead": cfg["gift"]["lead"].format(name=cfg["page"]["name"])},
        "voucher": cfg["voucher"],
        "card": cfg["card"],
        "puzzle": puzzle,
        "address": site.address,
        "hex_rows": codec.hex_rows(site.address),
        "ascii_table": codec.ascii_table(),
        "figure_svg": figure.svg(codec.to_hex(site.address)),
        "sample_hex": first_hex,
        "sample_dec": int(first_hex, 16),
        "sample_char": codec.from_hex(first_hex),
        "box": box,
    }

    unlock_js = (TEMPLATES / "unlock.js").read_text(encoding="utf-8")
    index = env.get_template("index.html.j2").render(unlock_js=unlock_js, **common)
    card = env.get_template("karta.html.j2").render(**common)

    # Bramka wyciekowa: ani kod kuponu, ani hasło nie mogą leżeć w opublikowanym HTML-u.
    for secret, label in ((code, "kod kuponu"), (answer, "hasło")):
        if secret.lower() in index.lower():
            raise SystemExit(f"{label} trafił jawnym tekstem do strony — przerywam")

    DOCS.mkdir(exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(index, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (BUILD / "karta-A4.html").write_text(card, encoding="utf-8")
    ANSWER_FILE.write_text(answer + "\n", encoding="utf-8")  # wyłącznie lokalnie

    print(f"kupon        : {code} (tylko pod monitorem i w build/qr.png)")
    print(f"adres        : {site.address} → hex na kartce")
    print(f"kwity        : {len(puzzle.receipts)}")
    print(f"po cenie/dram: {puzzle.built_word}  ← to jest hasło")
    print(f"po sumie     : {puzzle.trap_word}  ← pułapka dla nieuważnych")
    print(f"hasło        : {answer} (zapisane też w {ANSWER_FILE.relative_to(ROOT)})")
    print(f"strona       : {DOCS / 'index.html'}")
    print(f"kartka       : {BUILD / 'karta-A4.html'}")
    print(f"QR do wydruku: {qr_file}")


if __name__ == "__main__":
    sys.exit(main())
