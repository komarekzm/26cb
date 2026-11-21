"""Renderuje docs/ (to, co ląduje na Pages) i build/karta-A4.html (to, co idzie na papier)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from present import codec, config

ROOT = config.ROOT
TEMPLATES = ROOT / "templates"
DOCS = ROOT / "docs"
BUILD = ROOT / "build"


def qr_svg(code: str) -> str:
    """QR jako inline SVG: strona nie zależy wtedy od żadnego zewnętrznego pliku."""
    raw = subprocess.run(
        ["qrencode", "-t", "SVG", "-o", "-", code],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for pattern in (r"<\?xml[^>]*\?>", r"<!DOCTYPE[^>]*>", r"<!--.*?-->"):
        raw = re.sub(pattern, "", raw, flags=re.S)
    view_box = re.search(r'viewBox="([^"]+)"', raw)
    if not view_box:
        raise SystemExit("qrencode nie zwrócił viewBox — nie umiem skalować tego SVG")
    # Rozmiar narzuca CSS, więc width/height z qrencode trzeba wyrzucić.
    root = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{view_box.group(1)}" preserveAspectRatio="xMidYMid meet" '
        'role="img" aria-label="Kod QR kuponu">'
    )
    return re.sub(r"<svg[^>]*>", root, raw, count=1).strip()


def verify_qr(code: str) -> None:
    """Dekoduje wygenerowany QR z powrotem — zły QR na prezencie psuje całą zabawę."""
    BUILD.mkdir(exist_ok=True)
    png = BUILD / "qr.png"
    subprocess.run(["qrencode", "-o", str(png), "-t", "PNG", "-s", "6", code], check=True)
    decoded = subprocess.run(
        ["zbarimg", "-q", "--raw", str(png)], check=True, capture_output=True, text=True
    ).stdout.strip()
    if decoded != code:
        raise SystemExit(f"QR nie odczytuje się poprawnie: {decoded!r} != {code!r}")


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

    # Zabezpieczenie przed wysłaniem na świat placeholdera jako prawdziwego kuponu.
    if not cfg["page"]["test_mode"] and code.upper().startswith("TEST"):
        raise SystemExit(
            "page.test_mode = false, ale kupon.txt wciąż ma kod testowy. "
            "Wklej prawdziwy kod albo włącz test_mode."
        )

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    svg = qr_svg(code)
    verify_qr(code)

    address = site.address
    first_byte = codec.to_hex(address)[:2]
    common = {
        "page": cfg["page"],
        "gift": {**cfg["gift"], "lead": cfg["gift"]["lead"].format(name=cfg["page"]["name"])},
        "voucher": {**cfg["voucher"], "code": code},
        "card": cfg["card"],
        "hex_rows": codec.hex_rows(address),
        "address": address,
        "ascii_table": codec.ascii_table(),
        "sample_hex": first_byte,
        "sample_dec": int(first_byte, 16),
        "sample_char": codec.from_hex(first_byte),
    }

    index = env.get_template("index.html.j2").render(qr_svg=svg, **common)
    card = env.get_template("karta.html.j2").render(**common)

    DOCS.mkdir(exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(index, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (BUILD / "karta-A4.html").write_text(card, encoding="utf-8")

    print(f"kupon    : {code}")
    print(f"adres    : {address}")
    print(f"hex      : {codec.to_hex(address)}")
    for row in codec.hex_rows(address):
        print(f"           {row}")
    print(f"strona   : {DOCS / 'index.html'}")
    print(f"kartka   : {BUILD / 'karta-A4.html'}")


if __name__ == "__main__":
    sys.exit(main())
