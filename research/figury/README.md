# Figury 2D z łańcucha hex — cztery prototypy

Łańcuch: `6B6F6D6172656B7A6D2E6769746875622E696F2F70`

42 znaki hex = 21 bajtów ASCII = **`komarekzm.github.io/p`**. Suma cyfr: 302,
więc trasa „cyfra = liczba pól” ma 303 pola (łącznie z polem startowym).

Wszystkie prototypy są czystym Pythonem 3.13+ (tylko stdlib), rysują SVG
150 × 150 mm ręcznie stringami i mają `decode(svg)`, który czyta **geometrię
SVG**, nie oryginalny napis. Round-trip: `python3 selftest.py`.

| Prototyp | Plik | SVG | PNG | Kodowanie |
|---|---|---|---|---|
| A. plaster miodu | `honeycomb.py` | `honeycomb.svg` | `honeycomb.png` | paciorki na spirali heksów; cyfra = liczba pól między paciorkami |
| B. labirynt | `labirynt.py` | `labirynt.svg` | `labirynt.png` | bramki-rombiki w jednokorytarzowym labiryncie; cyfra = liczba pól między bramkami |
| C. mapa skarbu | `mapa.py` | `mapa.svg` | `mapa.png` | 21 punktów na siatce trójkątnej; cyfra = **różnica** współrzędnych |
| D. róża | `roza.py` | `roza.svg` | `roza.png` | 42 promienie; cyfra = długość promienia − 1 pierścień |

PNG do obejrzenia:

- `research/figury/honeycomb.png`
- `research/figury/labirynt.png`
- `research/figury/mapa.png`
- `research/figury/roza.png`

Wszystkie PNG są 1600 × 1600 px, czarno-białe, z białym tłem; SVG ma
`width="150mm" height="150mm"`, więc mieści się w polu 150 × 150 mm na A4.

## Jak odczytywać

### A. Plaster miodu (`honeycomb.py`)

Start jest na brzegu plastra (strzałka „start”), meta w środku. Ścieżka to
spirala: wchodzi o jedno pole do środka po każdym okrążeniu, więc się nie
przecina. Na ścieżce leżą paciorki (puste kółka). **Cyfra = ile pól mijasz od
jednego paciorka do następnego, licząc pole drugiego paciorka** (pole
pierwszego nie jest liczone). Cyfra 0 to dwa pierścienie w tym samym polu.

Dekoder bierze łamaną spiralę z SVG, zamienia współrzędne na pola axialne
`(q, r)`, a potem sortuje środki paciorków po indeksie pola i liczy różnice.

**To jest odstępstwo od dosłownego opisu A.** Wersja „42 proste odcinki,
każdy o długości 1–16 pól w kierunku zgodnym z regułą skrętu” po sprawdzeniu
daje 344 pola; pierwsza znaleziona trasa bez przecięć ma bbox 35 × 37 pól
(przy 150 mm to ok. 2,8 mm na heks). Przy 42 skrętach to gęsty wąż, w którym nie
da się policzyć pól bez lupy. Dlatego A jest spiralą z paciorkami: cyfra nadal
jest liczbą pól do przejścia, ale kierunek narzuca spirala, a granice cyfr —
paciorki. B, C i D realizują swoje opisy bez takiego ustępstwa.

### B. Labirynt (`labirynt.py`)

Siatka 24 × 14 pól, trasa to jedna spirala (303 z 336 pól). Ściany powstają
wyłącznie z trasy: między sąsiednimi polami stoi ściana, chyba że są kolejnymi
polami trasy. Labirynt jest **unicursalny** — nie ma rozwidleń, więc trasa jest
jednoznaczna.

Bramki to rombiki. **Cyfra = ile pól od jednej bramki do następnej, licząc pole
drugiej bramki.** Cyfra 0 to dwa romby w jednym polu: wypełniony i otwarty
(otwarty jest większy, więc widać podwójną bramkę). Start ma strzałkę, meta ma
ramkę i podpis „meta”.

Dekoder czyta ściany (grube linie), odtwarza graf korytarza i szuka jedynej
drogi od wejścia do mety. Bramki czyta jako środki rombów, mapuje na indeksy
pola w tej drodze i liczy różnice.

### C. Mapa skarbu (`mapa.py`)

To jest prototyp, w którym **sprawdzony został problem z parami cyfr**.
Dla tego łańcucha górne półbajty to tylko `2` (3×), `6` (13×) i `7` (5×).
Gdyby punktami mapy były pary `(górna cyfra, dolna cyfra)`, wszystkie 21
punktów leżałoby na trzech pionowych liniach — z mapy zrobiłby się pasek.

Dlatego mapa koduje **różnice**, nie współrzędne:

```
d_0 = v_0
d_i = (v_i - v_{i-1}) mod 16
```

21 punktów to pary `(d_0,d_1), (d_2,d_3), ...`. Różnice dają 15 różnych
wartości z 16 możliwych, x w zakresie 0–F, y w 1–F — dopiero to jest mapa.
Osie siatki trójkątnej są podpisane 0–F; punkt czyta się jako dwie cyfry
różnicy, a potem sumuje mod 16 od zera.

Numery 1–21 przy punktach to kolejność, nie dane. Trasa jest przerywana i może
się przecinać, więc numery są potrzebne do jednoznacznego odczytu.

### D. Róża (`roza.py`)

42 promienie na tarczy z 16 pierścieniami co 3,8 mm. Start to gruby promień
na godzinie 12; czytamy zgodnie z ruchem wskazówek zegara. **Cyfra = liczba
pierścieni promienia − 1**, czyli cyfra 0 to promień do pierwszego pierścienia.
Co czwarty pierścień jest grubszy i podpisany `4`, `8`, `C`, `10` (hex).
Kropka na końcu promienia pokazuje dokładny pierścień.

Dekoder czyta końce promieni: kąt daje numer promienia (0–41), odległość od
środka daje długość w pierścieniach, a stąd cyfrę.

## Co czyta się najlepiej, a co najgorzej

**Najlepiej: D (róża).** 42 niezależne odczyty, każdy to policzenie pierścieni
od środka do kropki. Brak arytmetyki, brak trasy do śledzenia, błąd jest
lokalny. Wygląda też najbardziej „prezentowo”: mieści się w kwadracie, ma
wyraźny środek, obrzeże i kierunek.

**Drugie: B (labirynt).** Trasa jest wymuszona przez ściany, więc nie ma
wątpliwości, gdzie iść; kropkowana siatka pozwala liczyć pola, a bramki są
duże. Minus: trzeba przejść cały labirynt i pilnować, gdzie jest początek
bramki; przy 42 bramkach to dłuższe niż róża.

**Trzecie: A (plaster miodu).** Spirala jest czytelna i ładna, pociągnięcie
jednej linii wystarcza. Minus: przy środku plastra paciorki zagęszczają się,
a pole startowe na brzegu sąsiaduje z pustymi polami zewnętrznego pierścienia;
trzeba pilnować konwencji „z polem drugiego paciorka”.

**Najgorzej: C (mapa skarbu).** Wizualnie najbardziej „zagadkowa”, ale odczyt
jest najkosztowniejszy: trzeba trafić w węzeł siatki trójkątnej, odczytać dwie
współrzędne, policzyć różnicę, zsumować mod 16 i nie pomylić kolejności
punktów na krzyżującej się trasie. To trzy źródła błędu na jeden punkt.
Na kartkę-prezent dla osoby bez wprawy — zbyt dużo pracy.

## Niejednoznaczności i pułapki

| Prototyp | Gdzie można się pomylić |
|---|---|
| A | Konwencja liczenia: od paciorka do paciorka **z polem drugiego**, bez pola pierwszego. Zero = dwa współśrodkowe pierścienie. Puste pola zewnętrznego pierścienia nie należą do trasy; start wskazuje strzałka. |
| B | Konwencja jak w A, ale z rombami. Zero = romb wypełniony + większy otwarty. Start i meta też są bramkami; meta jest ostatnią bramką. Labirynt nie ma rozwidleń, więc trasa nie jest zagadką — zagadką jest liczenie. |
| C | Punkty to **różnice**, nie współrzędne. Numery 1–21 są kolejnością, nie danymi. Trasa się przecina, więc bez numerów kolejność jest niejednoznaczna. Sumowanie jest mod 16 (po F wraca 0). Pierwsza różnica to po prostu pierwsza cyfra. |
| D | Start to gruby promień na 12; kierunek jest zgodny z ruchem wskazówek zegara (mała strzałka na obrzeżu). Podpisy `4, 8, C, 10` to etykiety pierścieni, nie cyfry kodu. Zero to promień długości jednego pierścienia, nie brak promienia. |

Wspólna pułapka: **wszystkie figury kodują 42 cyfry, ale różnie dzielą je na
jednostki.** W A i B jednostką jest odcinek między paciorkami/bramkami, w C —
punkt mapy (dwie różnice), w D — promień (jedna cyfra). Mieszanie tych
jednostek daje pozornie sensowne, ale błędne łańcuchy.

## Rekomendacja na kartkę do prezentu

**D — róża.** Jest najładniejsza, najszybciej się czyta i najlepiej znosi
druk: 42 promienie, 16 pierścieni, jeden kierunek. Jeśli chcesz, żeby kartka
była bardziej „zagadką drogi” niż „mandalą”, weź **B** (labirynt) — też jest
jednoznaczny i mieści się bez upychania. **C** zostawiłbym osobie, która lubi
współrzędne i arytmetykę; **A** jest dobrym dodatkiem dekoracyjnym, ale
najmniej wygodnym w odczycie przy środku.

## Odtworzenie rysunków

```bash
cd research/figury
python3 selftest.py          # cztery round-tripy, wypisuje OK i łańcuch
./build_png.sh               # SVG + PNG 1600 x 1600 przez chromium
```

Pojedynczo:

```bash
python3 honeycomb.py         # zapisuje honeycomb.svg, wypisuje OK <hex>
python3 labirynt.py
python3 mapa.py
python3 roza.py
```

`build_png.sh` używa:

```bash
chromium --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=1600,1600 --screenshot=figura.png file:///tmp/wrapper.html
```

Wrapper to zwykły HTML z `<img src="file:///.../figura.svg">` na białym tle;
SVG jest skalowane do kwadratu 1600 × 1600 px. Nie ma żadnych zależności poza
Pythonem i chromium.

## Co zostało sprawdzone

- Cztery razy `render(HEX) -> SVG -> decode(SVG) == HEX`; `selftest.py`.
- SVG ma dokładnie 150 × 150 mm; PNG ma 1600 × 1600 px (`file *.png`).
- Dodatkowo A i B przeszły round-trip na krótszym `0123456789ABCDEF`, C na
  tym samym, D na `"0"*42` i `"F"*42` — kodowanie nie jest przywiązane do
  konkretnych cyfr, tylko do długości łańcucha i siatki.
- C: policzone górne półbajty (`2`: 3×, `6`: 13×, `7`: 5×) i rozkład różnic
  (15 wartości, x 0–F, y 1–F) — to uzasadnia obejście z różnicami.

Nie ruszano `src/`, `templates/`, `docs/`, `tests/`; nie było commitów ani
operacji git.
