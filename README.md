# Prezent dla siostry

Kartka-prezent z dwoma poziomami: na papierze kod hex z adresem, na stronie zagadka,
za zagadką kupon. Bez serwera, bez bazy, bez IP — trzy pliki statyczne na GitHub Pages.

## Jak to działa

```
                        ┌─ karta A4: hex(adres), klucz ASCII          → druk
config.toml + kupon.txt ┤
                        └─ docs/index.html: zagadka + szyfrogram AES-GCM → Pages

przeglądarka: hasło z zagadki ──PBKDF2──> klucz ──AES-GCM──> {kod, QR} → pokaż
```

Kupon **nigdy nie leży na stronie jawnym tekstem**. W HTML-u jest tylko szyfrogram,
sól i IV; klucz powstaje z hasła, które gracz wylicza sam. `pokaż źródło` nic nie daje,
a kod nie trafia też do historii gita.

## Zagadka

Trzy kroki, dwie dziedziny, jedno hasło:

1. **Pokwitowanie z Gringotta** — 2 galeony · 9 sykli · 14 knutów. Kurs kanoniczny:
   1 galeon = 17 sykli, 1 sykiel = 29 knutów → **1261 knutów**.
2. **Puchar Domów** — pięć wydarzeń, cztery domy. Średnią wygrywa Slytherin (36,0),
   medianą Ravenclaw (**34**) — bo jeden wynik (55) odstaje. To jest pułapka zadania.
3. **Hasło** — reszta z 1261 ÷ 34 to **3**, a hasło to dom + reszta: `ravenclaw3`.
   Normalizacja po stronie przeglądarki znosi wielkość liter, spacje, myślniki
   i polskie znaki, więc „Ravenclaw 3” też przejdzie.

Build wypisuje całe rozwiązanie na końcu (`mise run build`) i zapisuje hasło lokalnie
do `build/answer.txt` — **gitignored**, żeby nie leżało w publicznym repo.

## Podmiana testowego kuponu na prawdziwy

1. Wklej kod do `kupon.txt` — jedna linia, nic więcej.
2. `test_mode = false` w `config.toml` (pasek „wersja testowa” zniknie).
3. `mise run build` — build sprawdzi, że QR odczytuje się z powrotem (`zbarimg`),
   że hasło otwiera szyfrogram, że złe hasło go nie otwiera i że ani kod, ani hasło
   nie wyciekły do HTML-u. Przy `test_mode = false` i kodzie na `TEST` odmówi publikacji.
4. `mise run deploy`.
5. `mise run rotate` — nowa sól i IV, czyli nowy szyfrogram dla tego samego hasła.
   Robi się raz po zmianie hasła albo kuponu.

## Komendy

| Komenda | Co robi |
|---|---|
| `mise run build` | `docs/index.html` (zagadka + szyfrogram) i `build/karta-A4.html` |
| `mise run test` | pytest (kodek, arytmetyka zagadki, brak wycieków) + Deno (odszyfrowanie w V8) |
| `mise run serve` | podgląd na <http://127.0.0.1:8788> — **przez HTTP**, nie z pliku |
| `mise run print` | `build/karta-A4.pdf`, 2 strony A4, headless chromium |
| `mise run deploy` | push na GitHub Pages + `curl` na wynikowy adres |
| `mise run decode` | hex z kartki → adres (kontrola przed drukiem) |

## Jak dodać lokalizację zamiast kuponu

Strona już to obsługuje: payload szyfrogramu to słownik, a glue renderuje tylko to,
co dostanie — `png` daje QR, `code` linijkę z kodem, `text` akapit (i chowa puste bloki).

1. W `config.toml` dopisz np. `[voucher] location = "Półka z książkami w salonie, tom trzeci"`.
2. W `build.py` zbuduj payload bez `png`: `payload = {"text": cfg["voucher"]["location"]}`.
   Można zostawić `note` jako komentarz dla siebie.
3. `mise run build && mise run test && mise run deploy`.

Wtedy QR zostaje na papierze (wkładasz go do koperty i chowasz), a strona mówi tylko,
gdzie szukać. Karta z kolei dostaje drugą wskazówkę — to jedyne miejsce, gdzie trzeba
dotknąć `templates/karta.html.j2`.

## Uwagi, które łatwo przeoczyć

- **Repo jest publiczne** (darmowe Pages nie działa inaczej). Kod kuponu i hasło są
  w nim nieobecne, ale karta do druku (`build/`, gitignored) i tak zawiera hex adresu.
- **PyPI zamiast firmowego indeksu**: globalny `uv.toml` wskazuje na repozytorium
  wymagające logowania, więc ten projekt ma własny `[[tool.uv.index]]` w `pyproject.toml`.
- **Test Deno** czyta `docs/index.html` i `build/answer.txt`, więc uruchamiaj go po
  `mise run build` (albo przez `mise run test`, które nie buduje — kolejność ma znaczenie).
- Fonty to stosy systemowe — strona nie ciągnie niczego z CDN, więc działa
  też za pięć lat i bez sieci poza samą stroną.
