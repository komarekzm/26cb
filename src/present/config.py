"""Wczytuje config.toml i wyprowadza z niego adres, repo i nazwę katalogu Pages."""

from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

def _find_root(start: Path) -> Path:
    """Szukaj katalogu projektu po config.toml — działa i z src/, i po instalacji."""
    for candidate in (start, *start.parents):
        if (candidate / "config.toml").exists():
            return candidate
    raise SystemExit(f"nie znalazłem config.toml nad {start}")


ROOT = _find_root(Path(__file__).resolve().parent)
CONFIG_PATH = ROOT / "config.toml"


@dataclass(frozen=True)
class Site:
    address: str  # to, co ląduje na kartce jako hex — bez https://
    repo: str  # "owner/name", do gh
    url: str  # pełny adres do przeglądarki i do deployu

    @property
    def owner(self) -> str:
        return self.repo.split("/")[0]


def load(path: Path = CONFIG_PATH) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def site(path: Path = CONFIG_PATH) -> Site:
    address = load(path)["page"]["url"].strip().strip("/")
    if "://" in address:
        raise SystemExit(f'config.toml: page.url ma być bez schematu, jest "{address}"')
    owner, _, rest = address.partition(".github.io")
    if not rest:
        raise SystemExit(
            "config.toml: page.url musi mieć postać <user>.github.io/<repo>, "
            "inaczej deploy nie wie, gdzie pushować"
        )
    return Site(address=address, repo=f"{owner}/{rest.strip('/')}", url=f"https://{address}/")


if __name__ == "__main__":
    # `python -m present.config repo|url|address` — konsumowane przez mise run deploy.
    _site = site()
    field = sys.argv[1] if len(sys.argv) > 1 else "url"
    print(getattr(_site, field))
