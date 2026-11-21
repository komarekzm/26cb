# Prezent dla siostry

Kartka-prezent z trzema poziomami: na papierze kod hex z adresem, na stronie zagadka
z kwitów eliksirowych, a rozwiązanie — słowo — prowadzi do koperty pod monitorem.
Bez serwera, bez bazy, bez IP: trzy pliki statyczne na GitHub Pages plus jeden wydruk.

## Jak to działa

```
karta A4 ──hex(adres)──► docs/index.html ──zagadka──► SŁOWO
                                                       │
                    pod monitorem: koperta ◄───────────┘
                    (to samo słowo + QR kuponu)
```

Strona **nie zawiera** ani słowa, ani QR-a, ani kodu kuponu. W HTML siedzi wyłącznie
szyfrogram AES-GCM; klucz powstaje ze słowa ułożonego w zagadce (PBKDF2-SHA256).
`pokaż źródło` pokazuje szyfrogram i tabelę kwitów, nic więcej.

## Zagadka

Bez liczenia — sama wiedza i skojarzenie. Dziewięć notatek opisuje **skutki zaklęć**,
ale nie podaje ich nazw. Pod notatkami jest bank dziewięciu zaklęć (alfabetycznie,
żeby nie sugerował kolejności). Rozpoznajesz zaklęcie z każdej notatki, bierzesz jego
**pierwszą literę** i czytasz litery w kolejności notatek:

```
Accio · Lumos · Oppugno · Homenum Revelio · Obliviate
Muffliato · Orchideous · Reducto · Aguamenti
→ A L O H O M O R A
```

Pułapka jest w banku: czytany po kolei daje `AAHLMOOOR`, czyli nic. Inicjały działają
dopiero po dopasowaniu notatek do nazw. Testy pilnują też, że żadna notatka nie
powtarza się, żadne zaklęcie nie występuje dwa razy i w notatkach nie ma ani jednej cyfry.

Build wypisuje rozwiązanie (`mise run build`) i zapisuje słowo do `build/answer.txt`
(**gitignored**), żeby nie leżało w publicznym repo.

## Co leży pod monitorem

Wydruk `build/qr.png` z kodem kuponu plus karteczka z napisem `ALOHOMORA`. Strona mówi
po poprawnym słowie tylko tyle, że ma tam zajrzeć — treść tej wiadomości to
`[voucher] location` w `config.toml`.

## Podmiana testowego kuponu na prawdziwy

1. Wklej kod do `kupon.txt` — jedna linia.
2. `test_mode = false` w `config.toml`.
3. `mise run build` — sprawdzi QR (`zbarimg`), otwarcie szyfrogramu słowem, odrzucenie
   złego słowa i brak wycieków w HTML. Przy `test_mode = false` i kodzie na `TEST` odmówi.
4. `mise run print` — kartka A4 (3 strony: kod, klucz ASCII, figura).
5. Wydrukuj `build/qr.png` i połóż pod monitorem razem ze słowem.
6. `mise run deploy`, potem `mise run rotate` (nowa sól i IV szyfrogramu).

## Komendy

| Komenda | Co robi |
|---|---|
| `mise run build` | `docs/index.html` (zagadka + szyfrogram), `build/karta-A4.html`, `build/qr.png` |
| `mise run test` | 26 testów pytest (kodek, figura, arytmetyka zagadki, brak wycieków) + Deno (odszyfrowanie w V8) |
| `mise run serve` | podgląd na <http://127.0.0.1:8788> |
| `mise run print` | `build/karta-A4.pdf`, 3 strony A4 |
| `mise run deploy` | push na GitHub Pages + `curl` na wynikowy adres |
| `mise run decode` | hex z kartki → adres |

## Bramki poprawności (to nie są ozdobniki)

- **Figura na kartce** jest odczytywana w testach z samego SVG: `(podstawa − szczyt) / kratka`,
  szczyt musi leżeć dokładnie na linii siatki, kratka ≥ 4,5 mm przy skali druku, rysunek
  wyłącznie szary.
- **Zagadka** jest rozwiązywana w teście z opublikowanego HTML-a: parser czyta notatki
  w kolejności i bank zaklęć, dopasowuje (mapowanie z configu) i składa słowo.
  Jeśli wyjdzie coś innego niż `ALOHOMORA`, test nie przejdzie.
- **Wycieki**: kod kuponu i słowo nie mogą wystąpić w HTML-u; nie może też być gotowego
  `data:image/png;base64,…`.
- **Szyfrogram**: build odszyfrowuje go poprawnym słowem i sprawdza, że złe słowo nie
  przechodzi.

## Uwagi, które łatwo przeoczyć

- Repo jest publiczne (darmowe Pages nie działa inaczej). Hasła i kodu kuponu w nim nie ma,
  ale karta do druku (`build/`, gitignored) zawiera hex adresu.
- Globalny `uv.toml` wskazuje na firmowe repozytorium wymagające logowania, więc projekt ma
  własny `[[tool.uv.index]]` w `pyproject.toml`.
- Test Deno czyta `docs/index.html` i `build/answer.txt`, więc kolejność to `build` → `test`.
- Zmiana słowa albo kwot przelicza wszystko: hex na kartce zostaje (adres się nie zmienia),
  ale szyfrogram i tabela tak. Po każdej zmianie `mise run build` i `mise run rotate`.
