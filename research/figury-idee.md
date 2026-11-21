# Research: figury 2D z 42 znaków hex — czytelne ręcznie z A4

## Streszczenie

42 znaki hex to 21 bajtów i dokładnie 168 bitów — czyli **42 = 6 × 7 komórek**, pełny prostokąt bez pustych pól, co jest rzadkim i bardzo wygodnym zbiegiem okoliczności dla projektu na kartkę. Istnieje kilkanaście nazwanych technik, które mieszczą ten ładunek, ale tylko trzy mają sens dla dorosłego nie-matematyka z 10–20 minutami i bez linijki: **plaster miodu z jednym „oczkiem" w siatce 4×4 na heks**, **dwa panele kresek 0–3 (szyfr Polybiusza 4×4)** oraz — najbardziej „figuralnie", ale i najbardziej ryzykownie — **trasa po krawędziach heksów**. Najważniejsze odkrycie poboczne: sama trasa „42 cyfry hex" **nie dowozi adresu**, bo odbiorca nie ma jak zamienić hex na ASCII; jeśli figura ma być użyteczna, trzeba ją domknąć kluczem 6×6 na znaki (21 × 2 wartości 0–5), co jest zarazem **łatwiejsze do odczytania** (max 5 kresek) niż wariant heksowy (max 15).

---

## 0. Dane wejściowe — rozbiór łańcucha (obliczenia własne, nie cytat)

`6B6F6D6172656B7A6D2E6769746875622E696F2F70` → 21 bajtów:

| # | hex | dec | znak | # | hex | dec | znak | # | hex | dec | znak |
|---|-----|-----|------|---|-----|-----|------|---|-----|-----|------|
| 1 | 6B | 107 | k | 8 | 7A | 122 | z | 15 | 75 | 117 | u |
| 2 | 6F | 111 | o | 9 | 6D | 109 | m | 16 | 62 | 98 | b |
| 3 | 6D | 109 | m | 10 | 2E | 46 | . | 17 | 2E | 46 | . |
| 4 | 61 | 97 | a | 11 | 67 | 103 | g | 18 | 69 | 105 | i |
| 5 | 72 | 114 | r | 12 | 69 | 105 | i | 19 | 6F | 111 | o |
| 6 | 65 | 101 | e | 13 | 74 | 116 | t | 20 | 2F | 47 | / |
| 7 | 6B | 107 | k | 14 | 68 | 104 | h | 21 | 70 | 112 | p |

Fakty projektowe (wszystkie policzone przeze mnie, do sprawdzenia jednym `wc`/skryptem):

- **42 znaki = 168 bitów = 12 × 14** (bitmapa) oraz **42 = 6 × 7** (siatka znaków). Oba dzielniki są „czyste" — żadnego wypełniacza, żadnych pustych komórek. To eliminuje największe źródło niejednoznaczności w tego typu figurach: „które komórki nic nie znaczą?".
- Rozkład wartości: `6` występuje **13×** (31%), `7` — 6×, `2` — 5×, `F` — 3×; wartości `3` i `C` **nie występują wcale**. Powtarzalność jest nieistotna dla kodowań pozycyjnych (jedna wartość = jedna komórka) i szkodliwa dla kodowań „długości serii" (nonogram, tally).
- Wszystkie 21 bajtów mieści się w zakresie ASCII drukowalnego 0x20–0x7E — to daje **wbudowaną sumę kontrolną**: każdy błąd odczytu prawie na pewno daje znak niedrukowalny albo bezsensowny ciąg, a poprawny wynik (`komarekzm.github.io/p`) jest rozpoznawalny na pierwszy rzut oka. Wykorzystam to w ocenie technik.

---

## 1. Ustalenie kluczowe (researcher inference): „ostatnia mila" — hex nie dowozi adresu

To nie jest technika, tylko ograniczenie, które przesądza o wyborze. Odbiorca odczyta z figury 42 cyfry hex. I co dalej? Żeby zamienić je na `komarekzm.github.io/p`, potrzebuje **tablicy ASCII (95 pozycji)** albo znajomości kodów — czyli figura kończy się tabelką, a nie adresem.

Trzy wyjścia (od najlepszego):

1. **Kodować znaki, nie hex.** Adres używa tylko `a–z`, `.`, `/` → 28 znaków. Szyfr Polybiusza **6×6** (klucz 36-polowy, mieści 28 znaków + 8 zapasowych) zamienia każdy znak na parę (wiersz, kolumna) ∈ 1–6 → 21 znaków = **42 wartości 0–5**. To ta sama liczba komórek co wariant heksowy, ale **maksimum kresek do policzenia spada z 15 do 5**, a klucz to miniaturowy kwadrat 6×6, który mieści się w 4 cm². Hex jest tu tylko krokiem pośrednim (i tak trzeba go policzyć raz, przy projektowaniu).
2. **Hex + wąska tabelka 16 pozycji.** W adresie występuje 16 różnych bajtów; tabelka „bajt → znak" ma 16 wierszy. Wciąż tekst na kartce, ale mały i tylko dekoracyjny.
3. **Hex bez klucza**, z założeniem, że odbiorca zna ASCII. Dla osoby dorosłej, nie-matematyka — nierealne w 15 minut.

Dlatego wszystkie techniki poniżej opisuję **na 42 znakach hex** (zgodnie z zadaniem), ale w „TOP 3" wskazuję, gdzie podmiana na klucz 6×6 (technika 11) jest konieczna, żeby kartka miała sens.

---

## 2. Techniki

Konwencja: przykład liczbowy zawsze na pierwszych 6 znakach łańcucha, `6B6F6D` (= „kom", wartości 6, 11, 6, 15, 6, 13), chyba że technika wymaga innej długości — wtedy mówię wprost.

### T1. Snake / boustrophedon na siatce 6×7 (szyfr trasowy, tablica transpozycyjna)

**Jak koduje 42 znaki.** Siatka 6 kolumn × 7 wierszy. Wiersze wypełnia się naprzemiennie: lewa→prawa, potem prawa→lewa. Odczytywany tekst to zawsze zwykłe czytanie wierszami od góry. Figura wygląda więc jak tablica, ale w co drugim wierszu trzeba iść „pod prąd". To klasyczna transpozycja trasowa — route cipher z prostą trasą (istnieje w wariantach spiralnym, diagonalnym, „L"; tu: snake poziomy).

**Odczyt krok po kroku.** (1) Weź wiersz 1 od lewej. (2) Wiersz 2 od prawej. (3) Wiersz 3 od lewej… (7) Wiersz 7 od lewej. Zapisz w jednej linii.

**Przykład (`6B6F6D`, siatka 3×2).** Wypełnienie snake: wiersz 1 = `6 B 6`, wiersz 2 (od prawej) = `F 6 D`, czyli na wydruku:

```
6 B 6
D 6 F
```

Odczyt snake: `6 B 6` + `F 6 D` = **6B6F6D** ✓

**Pełna siatka dla adresu (6×7, gotowa do przerysowania):**

```
6 B 6 F 6 D
5 6 2 7 1 6
6 B 7 A 6 D
9 6 7 6 E 2
7 4 6 8 7 5
9 6 E 2 2 6
6 F 2 F 7 0
```

(wiersze 2, 4, 6 są „pod prąd")

- **Ile kratek na A4:** 42; przy komórce 2,2 cm → 13,2 × 15,4 cm. Zostaje miejsce na tytuł i legendę.
- **Trudność odczytu:** łatwy. Jedyne ryzyko to zapomnieć o odwróceniu wiersza.
- **Ryzyko niejednoznaczności:** niskie (kształt siatki wymusza kierunek). Uwaga: 6×7 czyta się dobrze, ale 7×6 (7 kolumn) wygląda na kartce lepiej — wtedy odwracają się kolumny, nie wiersze.
- **Wygląd:** najsłabszy punkt — to cyfry w tabelce, czyli najbliżej „ciągu znaków" i najbliżej „wykresu z Excela" z całej listy.

### T2. Spirala / route cipher po 6×7 (z narysowaną trasą)

**Jak koduje.** Te same 42 komórki, ale tekst wpisuje się wierszami, a czyta po spirali zgodnie z ruchem wskazówek zegara, od wybranej komórki startowej do środka. Figura = tablica + **narysowana trasa** (cienka linia ze strzałką). Wariant: spirala od środka na zewnątrz — wtedy nie trzeba zaznaczać startu na brzegu, tylko w środku (wygodniejsze dla oka).

**Odczyt.** (1) Znajdź komórkę ze znaczkiem startu (kropka). (2) Idź po narysowanej linii, przepisując cyfry. 42 przystanki.

**Przykład (`6B6F6D617`, 9 znaków, siatka 3×3).** Wypełnienie wierszami:

```
6 B 6
F 6 D
6 1 7
```

Spirala od lewego górnego rogu do środka: (1,1)→(1,2)→(1,3)→(2,3)→(3,3)→(3,2)→(3,1)→(2,1)→(2,2) daje
`6 B 6 D 7 1 6 F 6` = **6B6D716F6**. To jest postać na wydruku; odczyt spirali zwraca `6B6F6D617` ✓

- **Ile kratek:** 42. Ten sam rozmiar co T1.
- **Trudność:** łatwy, jeśli trasa jest **narysowana**; średni/trudny, jeśli trzeba ją sobie wyobrazić. Dla tej kartki: rysować.
- **Ryzyko:** niskie. Spirala na 6×7 nie jest kwadratowa, więc „środek" wypada między komórkami — trzeba go zaznaczyć, inaczej ostatnie 2–3 komórki są dwuznaczne. **To realna wada**: 42 nie tworzy kwadratu (potrzeba 49).
- **Wygląd:** lepszy niż T1 — linia nadaje figurze charakter „mapy trasy". W połączeniu z motywem Huncwotów (T2b) działa.

**T2b. Wariant tematyczny: „Mapa Huncwotów / plan Hogwartu".** To nie jest osobna metoda kodowania — to **ubranie** T1/T2: zamiast siatki rysujemy korytarze zamku, a trasę jako ślad stóp. Kanoniczna Mapa Huncwotów jest w lore mapą planu Hogwartu śledzącą pozycje ludzi (Homonculous Charm), więc metaforycznie „trasa po planie" jest wierna źródłu. Uwaga krytyczna: **motyw nie dodaje mechanizmu kodowania**, a korytarze rysowane „ładnie" łamią regularność siatki i tym samym wprowadzają niejednoznaczność, której wymagania zabraniają. Rekomendacja: motyw tylko jako dekoracja brzegu kartki, siatka musi pozostać regularna.

### T3. Dwa panele kresek 0–3 — szyfr Polybiusza 4×4 (najodporniejszy na błąd)

**Jak koduje.** Klasyczny kwadrat Polybiusza zamienia znak na parę współrzędnych. Tu: **cyfra hex = para (wiersz, kolumna) w kwadracie 4×4**, bo 4×4 = 16 = dokładnie tyle, ile wartości hex. Konwersja: `wiersz = (v div 4) + 1`, `kolumna = (v mod 4) + 1`.

Zamiast pisać cyfry, rysujemy **dwa identyczne panele 6×7**: w panelu A liczba wypełnionych kropek w komórce = `v div 4` (czyli 0–3), w panelu B = `v mod 4` (0–3). Żadna cyfra nie jest drukowana.

**Odczyt.** Dla pozycji *i*: policz kropki w panelu A → to rząd (0–3, po dodaniu 1 daje 1–4), policz kropki w panelu B → to kolumna. Trafienie w kwadrat 4×4 daje cyfrę hex. 42 pozycje, **84 mikro-odczyty, żaden większy niż 3**.

**Przykład (`6B6F6D`).** Wartości 6, 11, 6, 15, 6, 13:

| poz. | v | v div 4 | v mod 4 | panel A (kropki) | panel B (kropki) | kwadrat 4×4 |
|------|---|---------|---------|------------------|------------------|-------------|
| 1 | 6 | 1 | 2 | • | •• | (2,3) |
| 2 | 11 | 2 | 3 | •• | ••• | (3,4) |
| 3 | 6 | 1 | 2 | • | •• | (2,3) |
| 4 | 15 | 3 | 3 | ••• | ••• | (4,4) |
| 5 | 6 | 1 | 2 | • | •• | (2,3) |
| 6 | 13 | 3 | 1 | ••• | • | (4,2) |

Panel A na wydruku: `• •• • ••• • •••` · Panel B: `•• ••• •• ••• •• •`

- **Ile kratek:** 84 (dwa panele 6×7). Przy komórce 1,6 cm → 9,6 × 11,2 cm każdy; dwa obok siebie ≈ 20 cm szerokości — **ciasno na A4**, lepiej jeden nad drugim (wtedy 9,6 × 22,4 cm, mieści się).
- **Trudność:** łatwy. Liczenie do 3 to jedyna operacja.
- **Ryzyko niejednoznaczności:** **najniższe z całej listy.** Dwa niezależne panele dają wzajemne sprawdzenie — jeśli w panelu A wyjdzie 4 kropki, wiadomo, że to błąd. Zero pustych komórek. Jedyny minus: „0 kropek" (pusta komórka) musi być odróżnialne od „komórki nieużywanej" — dlatego 6×7 bez wypełniaczy jest tu istotne.
- **Wygląd:** dwa rzędy kropek to najczystsza geometria na liście, ale dwa panele czyta się jak „dwie tabelki". Nie jest to figura — jest to wykres kropkowy, i to jest jego słabość estetyczna.

### T4. Plaster miodu: 42 heksy, w każdym jedno „oczko" w siatce 4×4 (rekomendowana)

**Jak koduje.** Sześciokąty ułożone w plaster (6 rzędów po 7, rzędy przesunięte). W każdym heksie narysowana **wewnętrzna siatka 4×4 punktów**; dokładnie jeden punkt jest zaczerniony. Pozycja punktu (rząd 1–4, kolumna 1–4) = cyfra hex: `v = (rząd−1)×4 + (kolumna−1)`. To dosłownie szyfr Polybiusza 4×4, ale **zamiast numerów wierszy/kolumn mamy fizyczne położenie w heksie** — nie trzeba czytać żadnej etykiety.

**Odczyt.** Heks po heksie, rząd heksów od góry, w rzędzie od lewej (heksy „flat-top", więc rząd jest poziomy i nie ma wątpliwości, co jest „następne"). W każdym heksie: policz punkt w pionie (1–4), policz w poziomie (1–4) → cyfra.

**Przykład (`6B6F6D`).** 6→(2,3), B=11→(3,4), 6→(2,3), F=15→(4,4), 6→(2,3), D=13→(4,2). Sześć pierwszych heksów, w każdym oczko w podanej pozycji siatki 4×4.

- **Ile kratek:** 42 heksy, w każdym 16 punktów (672 punktów łącznie, ale **odczytów tylko 84, każdy ≤ 4**). Heks o szerokości 2,6 cm → 7 kolumn ≈ 18 cm, 6 rzędów ≈ 13,5 cm. **Mieści się na A4 z zapasem.**
- **Trudność:** łatwy/średni. Dwa liczenia po ≤4 na heks.
- **Ryzyko niejednoznaczności:** niskie. Kluczowe: kropka musi być **wyraźnie wewnątrz** komórki siatki, a sama siatka 4×4 musi być cienka (0,2 mm). Przy druku laserowym 600 dpi to bezpieczne; przy atramentówce 300 dpi — na granicy. Alternatywa redukująca ryzyko: zamiast 4×4 punktów narysować w heksie **2×2 większe pola** i czytać 4 bity (T5).
- **Wygląd:** najlepszy na liście dla tego zadania. Plaster miodu jest rozpoznawalny, „magiczny" (pszczoły, miód, Gringotty), nie ma osi ani etykiet, więc **nie przypomina wykresu**. Bonus narracyjny: 42 komórki to mrugnięcie do „42" z Adamsa.

### T5. Plaster miodu gęsty: heks z 4 bitami 2×2

**Jak koduje.** Ten sam plaster, ale w każdym heksie jest **2×2 dużych pól** (jak okienko): wypełnione = 1, puste = 0, wagi 8-4-2-1 (kolejność TL, TR, BL, BR — musi być wydrukowana raz w legendzie). To „nibble w heksie": jeden heks = jedna cyfra hex.

**Odczyt.** 4 decyzje binarne na heks (zamiast 2 liczeń). 42 heksy = 168 decyzji.

**Przykład (`6B6F6D`).** 6 = `0110` → TL pusty, TR pełny, BL pełny, BR pusty. B = `1011`. 6 = `0110`. F = `1111` (wszystkie cztery). 6 = `0110`. D = `1101`.

- **Ile kratek:** 42 heksy × 4 pola = 168 pól. Ten sam rozmiar kartki co T4.
- **Trudność:** średni. Więcej decyzji, ale każda trywialna; brak liczenia.
- **Ryzyko:** niskie, ale **wymaga legendy z kolejnością wag** — bez niej 4 bity w rogach są dwuznaczne (który róg to 8?). To jedyna technika z tej listy, w której legenda jest obowiązkowa.
- **Wygląd:** bardzo dobry; wygląda jak plaster z okienkami. Mniej „magiczny" niż T4, bardziej „techniczny".

### T6. Trasa skoczka szachowego po 6×7 (ścieżka z warunkami)

**Jak koduje.** 42 komórki planszy 6×7 = 42 cyfry hex, ale ułożone nie wierszami — **w kolejności trasy skoczka**. W każdej komórce leży jedna cyfra, a w rogu małym drukiem numer porządkowy 1–42 (albo tylko start). Istnienie trasy: dla planszy m×n ze Schwenka zamknięta trasa skoczka istnieje zawsze, o ile m ≤ n i nie zachodzi: m,n obie nieparzyste; m ∈ {1,2,4}; m=3 i n ∈ {4,6,8}. Dla 6×7 (m=6 parzyste, m∉{1,2,4}, m≠3) **trasa istnieje**.

**Odczyt.** Start z komórki #1, potem 41 skoków. Jeśli numery są wydrukowane — trywialne. Jeśli nie: z każdej komórki trzeba znaleźć jedyne nieodwiedzone pole skoczka. **To daje samokontrolę**: przy dobrej trasie w każdej chwili jest zwykle dokładnie jeden taki skok, więc pomyłka od razu się blokuje.

**Przykład (`6B6F6D`, 6 pierwszych komórek trasy).** Komórka #1 = `6`, #2 = `B`, #3 = `6`, #4 = `F`, #5 = `6`, #6 = `D`. Odczyt trasy daje `6B6F6D`; reszta trasy to kolejne 36 cyfr.

- **Ile kratek:** 42 (plansza 6×7). Komórka 2,2 cm → 13,2 × 15,4 cm.
- **Trudność:** **trudny** bez numerów, średni z numerami. Skoki skoczka są „niewidoczne" — oko gubi się między 1-2 a 1-3.
- **Ryzyko:** średnie. Z numerami — niskie. Bez numerów — średnie (jedno potknięcie przesuwa cały odczyt; ratuje to samokontrola „jedynego nieodwiedzonego sąsiada", ale nie zawsze jest jedyny).
- **Wygląd:** bardzo dobry, „szachowy", zero Excela. Wada praktyczna: **muszę wygenerować konkretną trasę** (patrz: brakujące dowody) — nie da się jej narysować odręcznie bez błędu.

### T7. Kratka Cardana jako czytnik (Cardan grille)

**Jak koduje.** Oryginalna kratka Cardana (Cardano, 1550) to maska z wyciętymi okienkami nakładana na tekst — służy do ukrywania, nie do kodowania. Tu odwracam role: **figura to gęsta siatka cyfr (np. 8×8 = 64 komórki), a kratka wskazuje 42 komórki, które znaczą**. Pozostałe 22 to „szum" (też cyfry hex, ale przypadkowe). Kratka jest drukowana osobno — jako szablon do wycięcia albo jako **jasnoszary nadruk** na tej samej kartce (zgięcie po linii, przykładamy).

**Odczyt.** (1) Przyłóż kratkę do siatki (znaczek w rogu orientuje wyrównanie). (2) Czytaj tylko odsłonięte komórki, wierszami. 42 odczyty.

**Przykład (`6B6F6D`, siatka 4×4, 6 okienek).**

```
[6]  0  [B]  1        nawiasy = okienka kratki w pozycjach
 2  [6]  3   4        (1,1) (1,3) (2,2) (3,1) (3,4) (4,2)
[F]  5   7  [6]
 8  [D]  9   A
```

Odczyt przez okienka wierszami: `6 B 6 F 6 D` = **6B6F6D** ✓

- **Ile kratek:** 64 na siatkę + kratka. Rozmiar: 8×8 przy 2 cm = 16 × 16 cm.
- **Trudność:** łatwy (odczyt), ale **średni na wykonanie** — trzeba wyciąć albo precyzyjnie złożyć. Wariant „szary nadruk" znosi wycinanie, ale wprowadza ryzyko: przy kopiowaniu/kserowaniu szary może zniknąć.
- **Ryzyko:** niskie co do wartości, **wysokie co do rejestracji** — przesunięcie kratki o pół komórki psuje wszystko. Znaczek orientacyjny w rogu jest obowiązkowy.
- **Wygląd:** bardzo ładny (gęsta siatka + maska = „mapa z siatką"), ale to technika **pomocnicza**, nie samodzielna — nie zmniejsza liczby odczytów, tylko usuwa problem „które komórki są danymi". Świetnie się łączy z T4 (plaster miodu nie potrzebuje kratki, bo 42 = 6×7 bez reszty, więc kratka jest tu zbędna).

### T8. Nonogram jako nośnik + liczby na marginesie jako suma kontrolna

**Jak koduje.** 168 bitów = bitmapa **12 × 14** (czarne/białe pola). Obramowanie: **liczby nonogramowe** (długości serii) dla każdego wiersza i każdej kolumny. Figura wygląda jak zagadka nonogram, ale odbiorca **nie rozwiązuje** jej — po prostu czyta obrazek bit po bicie. Liczby na marginesie są tam po to, żeby **wykryć błąd odczytu**: jeśli przepisane bity nie zgadzają się z podpowiedziami, odbiorca wie, że się pomylił, jeszcze przed wpisaniem adresu.

**Odczyt.** 14 wierszy po 12 bitów; 8 bitów = 1 bajt = 1 znak. 168 decyzji binarnych.

**Przykład (`6B6F6D`, 24 bity, siatka 4×6).** Bity: `0110 1011 0110 1111 0110 1101`.

```
0 1 1 0 1 0
1 1 0 1 1 0
1 1 1 1 0 1
1 0 1 1 0 1
```

Podpowiedzi wierszy: `{2}`, `{2,2}`, `{4,1}`, `{1,2,1}`.
Podpowiedzi kolumn: `{3}`, `{3}`, `{1,2}`, `{3}`, `{2}`, `{2}`.

- **Ile kratek:** 168 pól (12×14). Przy polu 1,5 cm → 18 × 21 cm — **wypełnia całą kartkę**, zero miejsca na cokolwiek innego.
- **Trudność:** **trudny** (168 decyzji to najwięcej na liście; szacunkowo 6–10 min samego odczytu).
- **Ryzyko:** niskie co do wartości (bit jest bitem), ale **wysokie co do wytrzymałości odbiorcy** — to najbardziej nużąca technika. Za to jedyna z **wbudowaną sumą kontrolną**.
- **Wygląd:** bardzo dobry — to dosłownie zagadka z gazety, nie wykres. Minus: bez podpowiedzi wygląda jak rozsypanka; z podpowiedziami wygląda jak zadanie domowe.
- **Precedens naukowy:** zamiana tekstu w łamigłówkę jest metodą publikowaną — Erik Demaine i in. zbudowali całe **fonty zagadkowe**, m.in. *Tatamibari Font* (26 unikalnie rozwiązywalnych zagadek, po jednej na literę) i *Spiral Galaxies Font*, gdzie rozwiązanie zagadki **tworzy obraz litery**. Istnieje też font, w którym „losowe konfiguracje dają się jednoznacznie odczytać z powrotem do tekstu" (*Linkage font*). To dowód, że pomysł „figura-zagadka jako nośnik tekstu" jest praktykowany, a nie egzotyczny.

### T9. Róża wiatrów 0–F: 42 strzałki

**Jak koduje.** W każdej z 42 komórek jedna strzałka wskazująca jeden z **16 kierunków** (co 22,5°). Kąt = wartość hex: 0 = północ, 1 = NNE, … 15 = NNW. Legenda: róża wiatrów z podpisanymi sektorami 0–F — czyli legenda **jest** jednocześnie przyrządem odczytu.

**Odczyt.** Dla każdej komórki: w którą stronę wskazuje strzałka → sektor → cyfra. Jeden odczyt wizualny, zero liczenia.

**Przykład (`6B6F6D`).** 6 = 135° (SE), B=11 = 247,5° (WSW), 6 = SE, F=15 = 337,5° (NNW), 6 = SE, D=13 = 292,5° (WNW).

- **Ile kratek:** 42 (6×7) + róża. Komórka 2,2 cm.
- **Trudność:** **łatwy** — najszybszy odczyt z całej listy (42 decyzje, każda natychmiastowa).
- **Ryzyko:** średnie. 22,5° to dużo dla druku, ale mało dla odręcznego rysowania; strzałka „prawie NE" jest realnym problemem. Ograniczenie: musi być druk, nie rysunek.
- **Wygląd:** bardzo dobry, „kompas/talisman". Minus filozoficzny: to wciąż **jeden glif na komórkę**, czyli pod względem odczytu bliżej pisma niż figury.

### T10. Trasa po krawędziach heksów w stylu Hive (najbardziej „figuralna")

**Jak koduje.** Jedna linia biegnąca po plastrze miodu — **żadnych cyfr, żadnych kropek, tylko trasa**. Każda cyfra hex to jeden odcinek: `kierunek = v mod 6` (0–5, sześć boków heksu), `długość = (v div 6) + 1` (1–3 heksy). 16 wartości mieści się w 18 kodach (6 kierunków × 3 długości), więc dwa kody (16, 17) zostają nieużywane — i to jest **darmowa suma kontrolna**: jeśli z odczytu wyjdzie 16 lub 17, to znaczy, że źle policzyłeś.

To jest dokładnie mechanizm notacji gry **Hive**: ruch opisuje się jako „kierunek + sąsiad", gdzie kierunki mają nazwy (noon/afternoon/sunset/midnight/sunrise/forenoon), a pionki siedzą na heksach — kodowanie informacji w kierunkach, nie w liczbach.

**Odczyt.** Start z heksu ze znaczkiem. Dla każdego z 42 kroków: (1) którym bokiem wychodzi linia → kierunek 0–5; (2) ile heksów przechodzi, aż skręci lub się zatrzyma → 1, 2 lub 3; (3) `v = (długość−1)×6 + kierunek`.

**Przykład (`6B6F6D`).**

| v | v mod 6 | v div 6 + 1 | odcinek |
|---|---------|-------------|---------|
| 6 | 0 | 2 | 2 heksy na wschód |
| 11 | 5 | 2 | 2 heksy na południowy wschód |
| 6 | 0 | 2 | 2 heksy na wschód |
| 15 | 3 | 3 | 3 heksy na zachód |
| 6 | 0 | 2 | 2 heksy na wschód |
| 13 | 1 | 3 | 3 heksy na północny wschód |

- **Ile kratek:** ~42 heksy trasy, ale **plansza musi być większa** — trasa się wije, więc realnie 8×8 heksów (64), żeby nie wyszła za kartkę. Przy heksie 2 cm → 16 × 14 cm.
- **Trudność:** **średni**. Liczenie 1–3 heksów jest łatwe, ale 42 odcinki bez etykiet — jedno potknięcie i cała reszta się rozjeżdża (błąd kumuluje się, w przeciwieństwie do T3/T4).
- **Ryzyko niejednoznaczności:** **najwyższe z listy** — trasa może się przecinać i wracać po tych samych krawędziach; wtedy nie wiadomo, który odcinek jest który. Można to złagodzić tylko projektując trasę jako **samounikającą się** (bez powtórzonych krawędzi), co jest twardym ograniczeniem projektowym, nie gwarancją.
- **Wygląd:** **najlepszy**. To jedyna technika, która w ogóle nie zawiera cyfr ani kropek — jest linią na plastrze miodu. Idealna pod motyw „ścieżka", „labirynt", „trasa do skarbca".

### T11. Polybiusz 6×6 na ZNAKI (domknięcie „ostatniej mili")

**Jak koduje.** 21 znaków adresu, każdy jako para (wiersz, kolumna) w kwadracie 6×6. Kwadrat wypełniony: `a b c d e f / g h i j k l / m n o p q r / s t u v w x / y z . / ▢ ▢ ▢ ▢` (28 znaków + 8 zapasowych). Każda współrzędna ∈ 1–6, czyli **kreski 0–5** — maksimum 5, nie 15.

**Odczyt.** Ze znaku na parę: (1) policz kreski w panelu A → wiersz klucza; (2) policz w panelu B → kolumna; (3) odczytaj literę z klucza 6×6 wydrukowanego w rogu kartki. 42 mikro-odczyty po 21 liter.

**Przykład (`kom`).** Klucz jak wyżej: `k` = (2,5), `o` = (3,3), `m` = (3,1).
Zapis 0-indeksowany (kreski): A = `1, 2, 2`, B = `4, 2, 0`.
Odczyt: A=1,B=4 → wiersz 2, kolumna 5 → `k`; A=2,B=2 → `o`; A=2,B=0 → `m` → **kom** ✓

- **Ile kratek:** 42 × 2 panele = 84 komórek z kreskami (albo 42, jeśli kreski A i B narysujemy w jednej komórce jako dwie kolumny). Klucz 6×6 zajmuje 4 cm².
- **Trudność:** łatwy. **Maks. 5 kresek do policzenia** — najłagodniejszy próg liczbowy z całej listy.
- **Ryzyko:** bardzo niskie. Bonus: klucz 6×6 jest **szyfrem** — bez niego figura nie zdradza adresu, więc kartka nie wypala niespodzianki osobie, która tylko zerknie.
- **Wygląd:** jak T3 (dwa panele kresek) — czyste, ale tabelkowe. W połączeniu z plastrem miodu (T4 jako układ komórek) daje najlepszy wynik: plaster + kreski ≤ 5.

---

## 3. Rodziny, które trzeba było odrzucić — i dlaczego (analiza ilościowa)

### Catan / Settlers — za mała plansza na 168 bitów
Catan ma **19 heksów terenu i 18 żetonów numerów** o wartościach 2–12 bez 7, czyli **10 różnych wartości**. Pojemność: 18 × log₂(10) ≈ **60 bitów** — potrzebujemy 168. Nawet kładąc po dwa żetony na heks: 36 × 3,32 ≈ 120 bitów, wciąż za mało. Wniosek: **plansza w stylu Catan musi mieć ≥ 42 heksy z 16 wartościami** (czyli powiększony „Catan"), albo 51+ żetonów. Drugi problem jest gorszy: **żetony Catan są zadrukowane cyframi**, więc użycie ich jako nośnika natychmiast reintrodukuje „ciąg znaków". Wymóg „bez koloru, bez tekstu" wymusza kreski/oczka, a wtedy to już T4 w kostiumie.

### Hive — kierunki tak, plansza nie
Notacja Hive koduje ruch jako **kierunek + pionek odniesienia**, z nazwanymi kierunkami (noon/afternoon/sunset/midnight/sunrise/forenoon). To jest realny, sprawdzony sposób kodowania informacji na heksach — i dlatego trafił do T10 jako mechanizm. Ale sama plansza Hive jest **dynamiczna** (pionki się dokładają), więc nie nadaje się na statyczny wydruk; brak też naturalnego sposobu na 42 wartości.

### Hex (Nash) — bezużyteczny jako nośnik
Hex to gra o **łączeniu dwóch boków** — nie ma w niej liczb ani wartości. Zero pojemności informacyjnej poza jednym bitem wyniku. Odrzucony.

### Hexcells / minesweeper na heksach — liczby są zbyt małe i skrępowane
Hexcells (heksagonalny minesweeper) używa liczby 0–6 = ile niebieskich heksów sąsiaduje. Pojemność: log₂(7) ≈ 2,8 bita na heks → 168 bitów wymaga **60 heksów**, czyli więcej niż 42. Gorzej: wartości **nie są swobodne** — muszą być wzajemnie spójne (jak w minesweeperze), więc narzucenie dowolnego ciągu heksowego psuje łamigłówkę albo czyni ją nierozwiązywalną. **Odrzucone jako nośnik, dopuszczalne jako ozdoba.**

### Nurikabe / Slitherlink — pętla tak, liczby nie
- **Slitherlink**: ładunek = **jeden zamknięty cykl**. Pętla nie ma naturalnego „początku ani numeracji", więc 42 wartości trzeba by kodować długościami odcinków, a te są skrępowane geometrią (pętla musi się domykać). To wariant T10 z dodatkowym, twardym warunkiem domknięcia — technicznie możliwy, praktycznie bardzo trudny do zaprojektowania ręcznie.
- **Nurikabe**: liczby 1–8 są **kluczami zagadki** i wynikają z rozwiązania, nie odwrotnie. Nie da się ich swobodnie wybrać i zachować rozwiązywalności. **Odrzucone.**
- **Nonogram**: jedyna z tej rodziny, która naprawdę działa — bo **obrazek może być dowolny**, a podpowiedzi wylicza się z obrazka. Dlatego trafił do T8.
- **Precedens**: cała rodzina „puzzle fontów" Demaine'a (Tatamibari, Spiral Galaxies, Path Puzzles, Sudoku font, Yin-Yang font) pokazuje, że zagadka może **tworzyć** literę jako swoje rozwiązanie. Ale każdy z tych fontów koduje **jeden znak na zagadkę** — skalowanie do 21 znaków oznacza 21 zagadek, czyli kartkę nie do przejrzenia w 15 minut.

### Motywy świata magii — co jest metaforą, a co mechanizmem
| Motyw | Rola | Ocena |
|---|---|---|
| Mapa Huncwotów | trasa po planie (ubranie T1/T2) | dobra dekoracja, **słaby mechanizm** — nieregularne korytarze psują jednoznaczność |
| Plan Hogwartu | siatka pomieszczeń | to samo; działa tylko jako rama brzegowa |
| Skarbce Gringotta | numerowane drzwi w korytarzu | **zła** — numeracja = tekst |
| Boisko do quidditcha | 3 obręcze na różnych wysokościach | pojemność: 3 wartości na „scenę" → ~1,5 bita; absurdalnie mało |
| Plaster miodu | **metafora heksów** | **najlepsza** — daje nazwę i wygląd dla T4/T5/T10 |

**Czy gdzieś realnie użyto heksagonalnej siatki w zagadce?** Tak, ale **nie jako nośnika danych**: Hexcells (logika jak w minesweeperze), Hive (kierunki jako notacja), Hex Nasha (gra o łączeniu). Nie znalazłem przykładu, w którym **heksagonalna siatka koduje ciąg znaków** — to będzie autorski pomysł, nie cytowalna technika. (Patrz: brakujące dowody.)

---

## 4. Tabela porównawcza

| # | Technika | wartości/komórka | odczytów | max liczony | komórek | trudność | ryzyko | wygląd |
|---|----------|------------------|----------|-------------|---------|----------|--------|--------|
| T1 | Snake 6×7 | 1 (cyfra) | 42 | 15 (odczyt) | 42 | łatwy | niskie | słaby |
| T2 | Spirala | 1 (cyfra) | 42 | 15 | 42 | łatwy | niskie/średnie | dobry |
| T3 | 2 panele 0–3 | 2×(0–3) | 84 | **3** | 84 | łatwy | **najniższe** | średni |
| T4 | Heks + oczko 4×4 | 0–15 | 84 | **4** | 42 | łatwy/średni | niskie | **najlepszy** |
| T5 | Heks + 4 bity | 0–15 | 168 | 1 | 42 | średni | niskie | bardzo dobry |
| T6 | Skoczek 6×7 | 1 (cyfra) | 42 | — | 42 | **trudny** | średnie | bardzo dobry |
| T7 | Kratka Cardana | 1 (cyfra) | 42 | 15 | 64 | łatwy (odczyt) | wysokie (rejestracja) | bardzo dobry |
| T8 | Nonogram 12×14 | 1 bit | **168** | 1 | 168 | **trudny** | niskie + **checksum** | bardzo dobry |
| T9 | Róża 16 kierunków | 0–15 | **42** | 0 | 42 | **najłatwiejszy** | średnie | bardzo dobry |
| T10 | Trasa po heksach | 0–15 | 42 | 3 | ~64 plansza | średni | **najwyższe** | **najlepszy** |
| T11 | Polybiusz 6×6 na znaki | 2×(0–5) | 84 | **5** | 84 | łatwy | bardzo niskie | średni |

Czas odczytu (mój szacunek, nie pomiar): T9 ≈ 5–8 min, T4/T3/T11 ≈ 8–12 min, T5 ≈ 10–15 min, T1/T2/T7 ≈ 6–10 min, T6 ≈ 15–25 min, T8 ≈ 12–20 min. **Wszystkie poza T6 i T8 mieszczą się w 10–20 min.**

---

## 5. TOP 3 dla tej kartki

### 🥇 1. Plaster miodu z kreskami 0–5 wg klucza 6×6 (T4 jako układ + T11 jako wartości)

**Dlaczego.** Jedyne rozwiązanie, które jednocześnie: (a) **dowozi adres**, a nie 42 cyfry bez wyjścia; (b) ma **najniższy próg liczbowy** — maksymalnie 5 kresek w komórce; (c) **nie wygląda jak wykres** — plaster miodu bez osi, bez etykiet, z motywem miodu/Gringotta; (d) **mieści się na A4** z zapasem na tytuł (7 kolumn × 2,6 cm ≈ 18 cm); (e) 42 komórki bez reszty (6×7) → **zero pustych pól**, czyli zero „a to pole co znaczy?".

**Jak to złożyć.** Plaster 6 rzędów × 7 heksów. W każdym heksie dwie małe kolumny kropek (A i B), 0–5 w każdej. W rogu kartki klucz 6×6 na 28 znaków. Odczyt: heks → para kresek → litera. 84 mikro-odczyty po ≤5.

**Cena.** Dwa razy więcej komórek do policzenia niż wariant „jedna cyfra na heks" (84 vs 42 odczyty). To jest świadomy trade-off: płacisz 2× robotę, żeby odbiorca dostał adres, a nie zagadkę na drugą kartkę.

**Ryzyko, które trzeba zaadresować.** Kreski 0 i 1 muszą być odróżnialne od „pola pustego" — przy 42 komórkach bez wypełniaczy to nie problem, ale rysunek musi być konsekwentny (kropki zawsze w tych samych dwóch kolumnach).

### 🥈 2. Dwa panele kresek 0–3 (T3, szyfr Polybiusza 4×4) — jeśli ma być ściśle 42 cyfry hex

**Dlaczego.** Najniższe ryzyko błędu z całej listy i jedyna technika z **wzajemnym sprawdzeniem**: dwa niezależne panele, więc pomyłka w jednym zwykle wychodzi jako niespójność. Maksimum 3 kreski. Zero legendy poza kwadratem 4×4 (a i ten można wydrukować jako 16 cyfr — to nie jest „ciąg znaków", to klucz).

**Cena.** Wygląda jak dwie tabelki kropkowe — najbliżej „wykresu" z całej trójki. I wciąż zostaje „ostatnia mila" (hex → ASCII). Jeśli wybierasz tę drogę, **kartka musi mieć wąską tabelkę 16 bajtów → znak** (16 wierszy, bo adres używa 16 różnych bajtów) — to jedyny sposób, żeby odbiorca doszedł do adresu bez znajomości ASCII.

**Kiedy wybrać.** Gdy chcesz, żeby figura była **czysto geometryczna i bezsłowna** (klucz 4×4 można pominąć, bo 16 wartości to naturalny kwadrat), a tabelkę 16 bajtów traktujesz jako „instrukcję", nie część figury.

### 🥉 3. Trasa po krawędziach heksów w stylu Hive (T10) — jeśli figura ma być FIGURĄ, nie siatką

**Dlaczego.** Jedyna technika, w której **nie ma ani jednej cyfry, ani kropki, ani kreski** — jest tylko linia wijąca się po plastrze miodu. To odpowiada na najtrudniejszy wymóg z zadania („nie może wyglądać jak wykres z Excela") najmocniej ze wszystkich. Ma też wbudowaną sumę kontrolną: kody 16 i 17 są nieużywane, więc niemożliwy odczyt = sygnał błędu.

**Cena i ryzyko.** Najwyższe ryzyko niejednoznaczności: trasa może wracać po tych samych krawędziach, a błąd w jednym odcinku **kumuluje się** (przesuwa wszystkie następne). Wymaga zaprojektowania trasy jako samounikającej się — to ograniczenie projektowe, nie gwarancja, i trzeba je sprawdzić programem. Odczyt 42 odcinków (kierunek + długość 1–3) jest średni.

**Kiedy wybrać.** Gdy „efekt wow" jest ważniejszy niż odporność na błąd, a odbiorca ma więcej niż 15 minut albo kartka jest prezentem, który ma zaskoczyć, a nie zostać odczytany do końca.

### Plan awaryjny
**T1 (snake 6×7)** — najszybszy do zrobienia (jedna siatka, zero legendy, gotowa tablica w sekcji T1), najłatwiejszy odczyt, ale wygląda jak tabela. Sensowny, jeśli czas na przygotowanie jest krótki, a nie zależy nam na estetyce.

---

## 6. Sprzeczności

- **Cardano: „kratka ukrywa" vs „kratka koduje".** Źródła są zgodne, że oryginalna kratka Cardana to **steganografia** (ukrywanie w istniejącym tekście), a nie szyfr — Cipher Museum wprost: „Weak (steganography, not encryption)", „Hiding a message ≠ encrypting a message". Moje użycie w T7 (kratka jako **czytnik** wskazujący 42 komórki danych) jest **odwróceniem roli** i nie jest historycznym zastosowaniem. Zaznaczam to jako interpretację researcher, nie cytat. Uwaga dodatkowa: kratka Cardana „nie ma ustalonego wzoru" (Wikipedia) — więc konkretny układ 6 okienek jest mój, nie kanoniczny.
- **Trasa skoczka: „istnieje" vs „da się narysować".** Schwenk gwarantuje **istnienie** trasy na 6×7, ale nie daje gotowej trasy do wydruku. To nie sprzeczność, tylko luka (patrz niżej).
- **Rozmiar siatki a „42 bez reszty".** T1/T3/T4 korzystają z 42 = 6×7. Spirala (T2) **nie** ma naturalnego środka na 6×7, bo 42 nie jest kwadratem — to realna słabość T2 względem pozostałych, nie przeoczenie.

## 7. Brakujące dowody / czego nie zweryfikowałem

1. **Nie wygenerowałem konkretnej trasy skoczka na 6×7.** Wiem, że istnieje (Schwenk), nie mam numeracji 1–42 do wydruku. Bez tego T6 jest nieużywalne w praktyce — trzeba to policzyć programem.
2. **Nie sprawdziłem jednoznaczności nonogramu z T8** (przykład 4×6 z podpowiedziami `{2},{2,2},{4,1},{1,2,1}` / `{3},{3},{1,2},{3},{2},{2}`). Wygląda spójnie, ale unikalność wymaga solvera. Dla pełnej bitmapy 12×14 — tym bardziej.
3. **Nie sprawdziłem, czy trasa z T10 (42 odcinki kierunek+długość) mieści się na planszy 8×8 bez powtórzonych krawędzi** dla tego konkretnego łańcucha. To trzeba przeliczyć — może się okazać, że wymaga większej planszy albo innego przypisania kierunków do wartości (`v mod 6` jest arbitralne; można dobrać tak, żeby trasa była ładniejsza).
4. **Nie znalazłem żadnego źródła, w którym heksagonalna siatka koduje ciąg znaków.** Heksy w zagadkach (Hexcells, Hive, Hex) kodują logikę albo ruchy, nie dane. T4/T5/T10 są więc **autorskie** — nie mają precedensu do cytowania, co jest ryzykiem (nie wiadomo, jak zachowuje się odczyt na prawdziwym człowieku).
5. **Brak pomiaru czasu odczytu.** Wszystkie liczby czasowe w sekcji 4 to moje szacunki, nie dane z testu. Jedyne wiarygodne źródło to test na jednej osobie z kartką na kolanach.
6. **Rozdzielczość druku.** Utrzymanie cienkiej siatki 4×4 w heksie (T4) zależy od drukarki; nie sprawdziłem, czy 300 dpi wystarcza. To trzeba przetestować fizycznie.
7. **`source_check` nie był dostępny** w tym uruchomieniu — kluczowe twierdzenia opieram na źródłach pierwotnych (erikdemaine.org, catan.com — oficjalny PDF zasad, Wikipedia dla Schwenka/Cardana) i własnych obliczeniach, ale bez niezależnej walidacji treści.

## 8. Następne kroki (najbardziej opłacalne)

1. **Napisać skrypt** (Python) generujący: (a) gotowe SVG/PDF dla T4 i T3 na A4 z dokładnymi wymiarami, (b) trasę skoczka 6×7, (c) sprawdzenie samounikania trasy T10. To odblokowuje wszystkie trzy rekomendacje.
2. **Test na jednej osobie**: dwie kartki (T4 i T3), stoper, kartka na kolanach. Zmierzyć czas i liczbę pomyłek. Dopiero to rozstrzyga między #1 a #2 z TOP 3.
3. **Sprawdzić nonogram solverem**, jeśli T8 wchodzi do gry jako wariant z sumą kontrolną.

## 9. Źródła

**Kept:**
- Route Cipher — Crypto-IT (https://www.crypto-it.net/eng/simple/route-cipher.html) — definicja szyfru trasowego, mechanizm „wypełnij siatkę, czytaj po trasie", przykład spiralny; podstawa T1/T2.
- Route Cipher — Cipher Decipher (https://www.cipherdecipher.com/tools/route-cipher) — 7 wariantów tras (snake poziomy/pionowy, spirala, diagonalna), odwołanie do FM 34-40-2; potwierdza nazewnictwo snake/boustrophedon.
- Polybius Square — Text Machine (https://textmachine.org/en/text-tools/polybius-square) — mechanika kwadratu 5×5/6×6, konwencja (wiersz, kolumna), przykład HELLO → 23 15 31 31 34; podstawa T3/T11.
- Hexagonal Grids — Red Blob Games (https://www.redblobgames.com/grids/hexagons/) — geometria i układy współrzędnych heksów (offset/axial/cube), „rings and spirals"; podstawa terminologiczna T4/T5/T10 i uzasadnienie, że heksy mają 6 sąsiadów.
- Knight's Tour / Schwenk's theorem — Wikipedia (https://en.wikipedia.org/wiki/Knight%27s_tour) — twierdzenie o istnieniu tras na m×n; warunki wykluczające nie obejmują 6×7, więc trasa istnieje.
- Knight's Tour jako szyfr — Mountain Vista Software (https://www.mountainvistasoft.com/cryptoden/index.php/algorithms/knight-s-tour.html) — konkretny przykład transpozycji trasą skoczka na 8×8, reguła Warnsdorffa; podstawa T6.
- Cryptotours — George Jelliss (https://mayhematics.com/t/1f.htm) — historyczne użycie trasy skoczka do zapisu tekstu (XIX w.), czyli precedens dla T6.
- Cardan grille — Wikipedia (https://en.wikipedia.org/wiki/Cardan_grille) — historia (Cardano, 1550), brak ustalonego wzoru, 4 pozycje kratki; podstawa T7.
- Cardano Grille — The Cipher Museum (https://ciphermuseum.com/ciphers/cardano-grille.html) — jednoznaczne rozróżnienie steganografia vs szyfrowanie, liczby kombinacji; źródło zastrzeżenia w sekcji „Sprzeczności".
- Catan — oficjalne zasady (https://www.catan.com/sites/default/files/2021-06/catan_base_rules_2020_200707.pdf) — 19 heksów, 18 żetonów numerów, wartości 2–12 bez 7, tabela prawdopodobieństw; podstawa analizy pojemności w sekcji 3.
- Hive — Direction-Based Notation (https://pavelsoukenik.com/direction-based-notation-for-hive) — nazwane kierunki (noon/afternoon/sunset/midnight/sunrise/forenoon), kodowanie ruchu przez kierunek + pionek odniesienia; podstawa T10.
- Hexcells — MobyGames (https://www.mobygames.com/game/70366/hexcells/) — liczby 0–6 = liczba sąsiednich niebieskich heksów, mechanika jak minesweeper na heksach; podstawa odrzucenia w sekcji 3.
- Puzzle fonts — Erik Demaine (https://erikdemaine.org/fonts/) — katalog fontów-zagadek (Tatamibari, Spiral Galaxies, Path Puzzles, Sudoku, Linkage „uniquely decoded back to text"); **najsilniejszy dowód, że figura-zagadka może być nośnikiem tekstu**.
- Tatamibari Font (https://erikdemaine.org/fonts/tatamibari/) i Spiral Galaxies Font (https://erikdemaine.org/fonts/spiralgalaxies/) — 26/36 unikalnie rozwiązywalnych zagadek, po jednej na literę; precedens dla T8.
- The Marauder's Map — Harry Potter Encyclopedia (https://www.harrypotter.com/fact-file/objects/the-marauders-map) — plan Hogwartu + śledzenie pozycji (Homonculous Charm); podstawa oceny motywu T2b.

**Rejected/deprioritized:**
- Harry Potter: Puzzles & Spells — lista „hazardów" (zyngasupport.helpshift.com) — gra mobilna, zero wartości dla kodowania; tylko szum w wynikach.
- Hive at Boardspace.net (https://www.boardspace.net/english/about_hive_notation.html) — autorka sama oznacza sekcję jako „largely obsolete"; notacja kierunkowa Pavla Soukenika jest nowsza i lepiej udokumentowana.
- Star Grid Observatory (bunbunpark.com) — gra dla dzieci o układzie współrzędnych; pomocniczo potwierdza, że „czytanie (x,y) z siatki" jest umiejętnością 9–12 lat, ale nie wnosi techniki.
- ARGNet / MIT Mystery Hunt 2026 — barwny opis, ale bez konkretnej techniki kodowania; pominięty.
- Tatamibari is NP-complete (PDF, erikdemaine.org) — cytowany tylko pośrednio; właściwym źródłem dla fontu jest strona fontu, nie artykuł o złożoności.
