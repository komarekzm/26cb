"""Renderuje docs/ (to, co ląduje na Pages) i build/karta-A4.html (to, co idzie na papier)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from present import codec, config, puzzle as puzzle_mod

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


def verify_puzzle(puzzle: puzzle_mod.Puzzle, scrambled: str, address: str) -> None:
    """Kod z kartki musi wracać do adresu — inaczej nikt tam nie dojdzie."""
    decoded = codec.from_hex(codec.to_hex(scrambled))
    if decoded != scrambled:
        raise SystemExit("hex nie odwraca się poprawnie")
    if codec.caesar(decoded, -puzzle.shift) != address:
        raise SystemExit(
            f"po cofnięciu o {puzzle.shift} nie wychodzi {address!r}. "
            "Zagadka i adres przestały do siebie pasować."
        )


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

    puzzle = puzzle_mod.load(cfg)
    address = site.address
    scrambled = codec.caesar(address, puzzle.shift)  # to trafia na kartkę jako hex
    verify_puzzle(puzzle, scrambled, address)

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    svg = qr_svg(code)
    verify_qr(code)

    first_hex = codec.to_hex(scrambled)[:2]
    first_char = codec.from_hex(first_hex)
    common = {
        "page": cfg["page"],
        "gift": {**cfg["gift"], "lead": cfg["gift"]["lead"].format(name=cfg["page"]["name"])},
        "voucher": {**cfg["voucher"], "code": code},
        "card": cfg["card"],
        "puzzle": puzzle,
        "receipt": cfg["puzzle"]["receipt"],
        "events": cfg["puzzle"]["house_points"]["events"],
        "hex_rows": codec.hex_rows(scrambled),
        "address": address,
        "ascii_table": codec.ascii_table(),
        "sample_hex": first_hex,
        "sample_dec": int(first_hex, 16),
        "sample_char": first_char,
        "sample_shifted": codec.caesar(first_char, -puzzle.shift),
    }

    index = env.get_template("index.html.j2").render(qr_svg=svg, **common)
    card = env.get_template("karta.html.j2").render(**common)

    DOCS.mkdir(exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(index, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (BUILD / "karta-A4.html").write_text(card, encoding="utf-8")

    print(f"kupon      : {code}")
    print(f"adres      : {address}")
    print(f"knuty      : {puzzle.total_knuts} (pokwitowanie)")
    print(f"średnia    : wygrywa {puzzle.average_winner.name} ({puzzle.average_winner.average:.1f})")
    print(f"mediana    : wygrywa {puzzle.median_winner.name} ({puzzle.median_winner.median})")
    print(f"przesunięcie: {puzzle.shift} → na kartce hex z {scrambled!r}")
    for row in codec.hex_rows(scrambled):
        print(f"             {row}")
    print(f"strona     : {DOCS / 'index.html'}")
    print(f"kartka     : {BUILD / 'karta-A4.html'}")


if __name__ == "__main__":
    sys.exit(main())
