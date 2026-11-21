# Prezent dla siostry

Kartka-prezent: na papierze kod hex, w kodzie adres strony, na stronie QR z kuponem
do escape roomu. Bez serwera, bez bazy, bez IP — trzy pliki statyczne na GitHub Pages.

## Jak to działa

```
kupon.txt ──┐
            ├─► present.build ─► docs/index.html   (QR inline + kod, na Pages)
config.toml ┘                 └─► build/karta-A4.html (hex + klucz ASCII, do druku)
```

`config.toml: page.url` to adres strony bez `https://`. Z niego liczymy hex, który
idzie na kartkę, więc **każda zmiana adresu wymaga ponownego wydruku karty**.

## Podmiana testowego kuponu na prawdziwy

1. Wklej kod do `kupon.txt` — jedna linia, nic więcej.
2. `test_mode = false` w `config.toml` (pasek „wersja testowa” zniknie).
3. `mise run build` — build sam sprawdzi, czy QR odczytuje się z powrotem
   (`zbarimg`) i odmówi publikacji, jeśli `test_mode = false`, a w `kupon.txt`
   wciąż siedzi kod zaczynający się od `TEST`.
4. `mise run deploy`.

## Komendy

| Komenda | Co robi |
|---|---|
| `mise run build` | generuje `docs/` i `build/karta-A4.html` |
| `mise run test` | testy kodeka: hex i bity muszą wracać do tego samego adresu |
| `mise run serve` | podgląd na <http://127.0.0.1:8788> |
| `mise run print` | `build/karta-A4.pdf` przez headless chromium (2 strony A4) |
| `mise run deploy` | push na GitHub Pages + `curl` na wynikowy adres |
| `mise run decode` | odkodowanie hex z kartki z powrotem na adres — kontrola przed drukiem |

## Uwagi, które łatwo przeoczyć

- **Repo jest publiczne** (darmowe Pages nie działa inaczej), więc kod kuponu jest
  technicznie widoczny w gicie. Strona ma `noindex,nofollow,noarchive` i krótki,
  nieoczywisty adres — to chroni przed przypadkiem, nie przed intencją.
- **PyPI zamiast firmowego indeksu**: globalny `uv.toml` wskazuje na repozytorium
  wymagające logowania, więc ten projekt ma własny `[[tool.uv.index]]` w
  `pyproject.toml`. Bez tego `uv sync` nie znajduje `jinja2`.
- Fonty to stosy systemowe — strona nie ciągnie niczego z CDN, więc działa
  też z pliku i za pięć lat.
