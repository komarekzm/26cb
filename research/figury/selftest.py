"""Wspólny test czterech prototypów: render -> SVG -> decode -> ten sam hex."""

from __future__ import annotations

import importlib

HEX = "6B6F6D6172656B7A6D2E6769746875622E696F2F70"
MODULES = ("honeycomb", "labirynt", "mapa", "roza")


def main() -> None:
    for name in MODULES:
        module = importlib.import_module(name)
        svg = module.render(HEX)
        decoded = module.decode(svg)
        assert decoded == HEX, (name, decoded, HEX)
        assert 'width="150mm"' in svg and 'height="150mm"' in svg, name
        print(f"{name:10s} OK  {decoded}")


if __name__ == "__main__":
    main()
