"""D. RÓŻA — 42 promienie na tarczy z pierścieniami.

Każda cyfra hex to jeden promień. Długość promienia (w pierścieniach)
= cyfra + 1, więc cyfra 0 to krótki kolec do pierwszego pierścienia.
Promienie czyta się zgodnie z ruchem wskazówek zegara od znaku startu
na górze. Pierścienie co 4 mm są jednostką; co czwarty jest grubszy
i podpisany 4, 8, C, 10 (hex).

Dekoder czyta z SVG końce promieni: kąt daje numer promienia,
odległość od środka daje cyfrę.
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET

HEX = "6B6F6D6172656B7A6D2E6769746875622E696F2F70"

CX, CY = 75.0, 72.0
RSTEP = 4.0
N = 42
SPOKE_ANGLES = [2.0 * math.pi * k / N for k in range(N)]


def render(hex_str: str) -> str:
    digits = [int(ch, 16) for ch in hex_str]
    if len(digits) != N:
        raise ValueError(f"róża ma dokładnie {N} promieni")

    parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="150mm" '
        'viewBox="0 0 150 150">',
        '<rect width="150" height="150" fill="white"/>',
        '<g id="rings" fill="none" stroke="black">',
    ]

    for ring in range(1, 17):
        width = 0.34 if ring % 4 == 0 else 0.12
        parts.append(
            f'<circle class="ring" cx="{CX}" cy="{CY}" r="{ring * RSTEP}" '
            f'stroke-width="{width}"/>'
        )
    parts.append(
        f'<circle class="rim" cx="{CX}" cy="{CY}" r="{16 * RSTEP + 2.2}" '
        f'stroke-width="0.22"/>'
    )
    parts.append("</g>")

    # promienie
    parts.append('<g id="spokes" stroke="black" stroke-linecap="round">')
    for k, digit in enumerate(digits):
        angle = -math.pi / 2.0 + SPOKE_ANGLES[k]
        length = (digit + 1) * RSTEP
        x1 = CX + 1.8 * math.cos(angle)
        y1 = CY + 1.8 * math.sin(angle)
        x2 = CX + length * math.cos(angle)
        y2 = CY + length * math.sin(angle)
        width = 0.9 if k == 0 else 0.55
        parts.append(
            f'<line class="spoke" x1="{x1:.2f}" y1="{y1:.2f}" '
            f'x2="{x2:.2f}" y2="{y2:.2f}" stroke-width="{width}"/>'
        )
        parts.append(
            f'<circle cx="{x2:.2f}" cy="{y2:.2f}" r="0.72" fill="black" stroke="none"/>'
        )
    parts.append("</g>")

    # podział na sześć sektorów po siedem promieni
    parts.append('<g id="sectors" stroke="black" stroke-width="0.26">')
    for k in range(0, N, 7):
        angle = -math.pi / 2.0 + SPOKE_ANGLES[k]
        x1 = CX + 2.2 * math.cos(angle)
        y1 = CY + 2.2 * math.sin(angle)
        x2 = CX + (16 * RSTEP + 3.4) * math.cos(angle)
        y2 = CY + (16 * RSTEP + 3.4) * math.sin(angle)
        parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    parts.append("</g>")

    # podpisy pierścieni 4, 8, C, 10
    parts.append(
        '<g font-family="monospace" font-size="2.4" fill="black" '
        'stroke="white" stroke-width="0.9" paint-order="stroke">'
    )
    for ring in (4, 8, 12, 16):
        label = f"{ring:X}"
        x = CX + ring * RSTEP + 1.4
        y = CY + 1.0
        parts.append(f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="start">{label}</text>')
    parts.append("</g>")

    # znak startu i kierunek
    top_x, top_y = CX, CY - 16 * RSTEP - 8.5
    parts.append(
        f'<g id="start"><polygon points="{top_x - 2.2:.2f},{top_y - 3.0:.2f} '
        f'{top_x + 2.2:.2f},{top_y - 3.0:.2f} {top_x:.2f},{top_y + 0.6:.2f}" '
        f'fill="black"/>'
        f'<text x="{top_x:.2f}" y="{top_y - 5.2:.2f}" font-family="sans-serif" '
        f'font-size="2.6" text-anchor="middle" fill="black">start</text></g>'
    )

    # strzałka kierunku zgodnego z ruchem wskazówek zegara
    r_arrow = 16 * RSTEP + 6.0
    a1, a2 = math.radians(-64), math.radians(-28)
    p1 = (CX + r_arrow * math.cos(a1), CY + r_arrow * math.sin(a1))
    p2 = (CX + r_arrow * math.cos(a2), CY + r_arrow * math.sin(a2))
    parts.append(
        f'<path d="M {p1[0]:.2f} {p1[1]:.2f} A {r_arrow:.2f} {r_arrow:.2f} 0 0 1 '
        f'{p2[0]:.2f} {p2[1]:.2f}" fill="none" stroke="black" stroke-width="0.45"/>'
    )
    tip = (CX + r_arrow * math.cos(a2 + 0.10), CY + r_arrow * math.sin(a2 + 0.10))
    parts.append(
        f'<polygon points="{tip[0]:.2f},{tip[1]:.2f} '
        f'{tip[0] - 3.0 * math.cos(a2 - 0.35):.2f},{tip[1] - 3.0 * math.sin(a2 - 0.35):.2f} '
        f'{tip[0] - 3.0 * math.cos(a2 + 0.35):.2f},{tip[1] - 3.0 * math.sin(a2 + 0.35):.2f}" '
        f'fill="black"/>'
    )

    parts.append(
        f'<circle cx="{CX}" cy="{CY}" r="1.8" fill="black"/>'
    )

    parts.append(
        '<text x="75" y="146" font-family="sans-serif" font-size="3.2" '
        'text-anchor="middle" fill="black">'
        'D · RÓŻA — długość promienia = cyfra + 1 pierścieni</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def decode(svg: str) -> str:
    root = ET.fromstring(svg)

    spokes: list[tuple[int, int]] = []
    for element in root.iter():
        if _local_name(element.tag) != "line" or element.get("class") != "spoke":
            continue
        x2 = float(element.get("x2", "0"))
        y2 = float(element.get("y2", "0"))
        dx, dy = x2 - CX, y2 - CY
        length = math.hypot(dx, dy)
        rings = round(length / RSTEP)
        digit = rings - 1
        if not 0 <= digit <= 15:
            raise ValueError(f"promień poza skalą: {rings}")
        angle = math.degrees(math.atan2(dy, dx))
        k = round(((angle + 90.0) % 360.0) / (360.0 / N)) % N
        spokes.append((k, digit))

    if len(spokes) != N:
        raise ValueError(f"oczekiwano {N} promieni, jest {len(spokes)}")
    spokes.sort()
    if [k for k, _ in spokes] != list(range(N)):
        raise ValueError("zduplikowany lub brakujący promień")
    return "".join(f"{digit:X}" for _, digit in spokes)


if __name__ == "__main__":
    from pathlib import Path

    svg = render(HEX)
    target = Path(__file__).with_suffix(".svg")
    target.write_text(svg, encoding="utf-8")
    decoded = decode(svg)
    assert decoded == HEX, (decoded, HEX)
    print("OK", decoded)
    print("SVG", target)
