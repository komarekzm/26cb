# Zagadki „papierowe" (matematyka + data science) do kartki-prezentu — motyw Szkoły Magii

**Cel dokumentu:** bank zagadek, które da się rozwiązać ołówkiem w 5–15 minut, bez komputera i bez wiedzy specjalistycznej, a które dają konkretną liczbę lub litery nadające się na elementy szyfru (kod hex adresu).

**Jak czytać wpisy:**
- **Treść** — gotowa do wydruku, w klimacie szkoły magii (można podmienić nazwy domów/eliksirów).
- **Dane** — wszystkie liczby potrzebne do policzenia (nic nie trzeba wymyślać).
- **Rozwiązanie** — pełne przeliczenie krok po kroku, żeby dało się sprawdzić bez komputera.
- **Wynik** — to, co gracz zapisuje.
- **Czas** — realny czas dla osoby bez wprawy, z ołówkiem.
- **Wiedza** — `zero` (wystarczy szkoła podstawowa + kartka z instrukcją) lub `średnia` (trzeba podać krótką definicję na kartce).
- **Ładny wynik?** — czy z wyniku da się zrobić cyfrę hex (0–9/A–F), indeks litery (1–26), datę albo rok.

> Uwaga metodologiczna: same **algorytmy** (Luhn, ISBN, Hamming, kod Graya, paradoks Simpsona, Buffon) są zweryfikowane źródłowo. **Konkretne liczby w zagadkach są moje (skonstruowane pod ładny wynik)** i przeliczone ręcznie — każde przeliczenie jest rozpisane poniżej, więc można je sprawdzić w 2 minuty. To nie są cytaty z podręczników.

---

## Część I. Arytmetyka reszt (modularna) — najłatwiejsze wejście

### 1. Turniej co 1000 dni (reszta z dzielenia przez 7)

> **Treść:** Ostatni mecz o Puchar Domów odbył się we **wtorek**. Kolejny mecz wyznaczono dokładnie **1000 dni** później. W jaki dzień tygodnia się odbędzie? Ile dni „zostaje z ogona" po odjęciu pełnych tygodni?

**Dane:** 1000 dni, start = wtorek.
**Rozwiązanie:** 1000 = 7 · 142 + **6**. Pełne tygodnie nie zmieniają dnia tygodnia, więc przesuwamy się o 6 dni: wtorek → środa(1) → czwartek(2) → piątek(3) → sobota(4) → niedziela(5) → **poniedziałek(6)**.
**Wynik:** poniedziałek; „ogon" = **6**.
**Czas:** 4–5 min. **Wiedza:** zero. **Ładny wynik?** TAK — 6 to czysta cyfra hex; dodatkowo poniedziałek = 1. dzień tygodnia (albo 8, jeśli numerujemy od niedzieli) → druga cyfra.

---

### 2. Klasa, której nikt nie policzył (dwie reszty / mini-CRT)

> **Treść:** W Sali Zaklęć stoi więcej niż **40** i mniej niż **50** uczniów. Gdy ustawią się trójkami, **jeden** zostaje bez pary. Gdy ustawią się piątkami, **trzech** zostaje bez pary. Ilu ich jest?

**Dane:** 40 < n < 50; n mod 3 = 1; n mod 5 = 3.
**Rozwiązanie:** liczby w przedziale dające resztę 3 z dzielenia przez 5: 43, 48. Sprawdzamy resztę z 3: 43 = 3·14 + **1** ✔ (48 = 3·16 + 0 ✘). Zostaje 43. (Kontrola: 43 = 5·8 + 3 ✔, 43 = 3·14 + 1 ✔.)
**Wynik:** **43**.
**Czas:** 6–8 min. **Wiedza:** zero. **Ładny wynik?** TAK — 43 → 4+3 = 7 (cyfra), albo 43 − 26 = 17 = Q, albo 43 jako numer strony/kodu.

---

## Część II. Cyfry kontrolne — „aha, to dlatego sklep wie, że się pomyliłem"

### 3. ISBN-10: cyfra kontrolna księgi (wynik 3)

> **Treść:** Księga Zaklęć ma numer **83-14-15926-?** Ostatnia cyfra została zjedzona przez mola. Odzyskaj ją. Zasada: cyfry mnoży się kolejno przez 10, 9, 8, …, 2, sumuje, a cyfra kontrolna domyka sumę do wielokrotności 11.

**Dane:** 8, 3, 1, 4, 1, 5, 9, 2, 6 (cyfry 3,1,4,1,5,9,2,6 to początek liczby π — smaczek dla spostrzegawczych).
**Rozwiązanie:**
10·8 = 80 | 9·3 = 27 | 8·1 = 8 | 7·4 = 28 | 6·1 = 6 | 5·5 = 25 | 4·9 = 36 | 3·2 = 6 | 2·6 = 12
Suma = 80+27+8+28+6+25+36+6+12 = **228**. 228 = 11·20 + **8**, więc cyfra kontrolna = 11 − 8 = **3**.
**Wynik:** **3**.
**Czas:** 7–8 min. **Wiedza:** zero (wystarczy podać regułę na kartce). **Ładny wynik?** TAK — pojedyncza cyfra hex.

---

### 4. ISBN-10 pułapka: cyfra „X" (wynik X = 10)

> **Treść:** Stary rejestr czarów używa numerów ISBN-10. Numer **83-207-6954-?** kończy się znakiem, który nie jest cyfrą. Jakim? (Podpowiedź: w ISBN-10 „X" to nie litera, to liczba.)

**Dane:** 8, 3, 2, 0, 7, 6, 9, 5, 4.
**Rozwiązanie:**
10·8 = 80 | 9·3 = 27 | 8·2 = 16 | 7·0 = 0 | 6·7 = 42 | 5·6 = 30 | 4·9 = 36 | 3·5 = 15 | 2·4 = 8
Suma = 80+27+16+0+42+30+36+15+8 = **254**. 254 = 11·23 + **1**, więc cyfra kontrolna = 11 − 1 = **10 = X**.
**Wynik:** **X**, czyli **10**.
**Czas:** 8 min. **Wiedza:** średnia (trzeba wiedzieć, że „X" = 10). **Ładny wynik?** TAK, bardzo — X daje cyfrę 10 = **A** w hex. Idealne, jeśli kod ma zawierać literę.
**Dlaczego warto:** to jedyna zagadka, w której „litera w numerze" okazuje się liczbą — mocny efekt „aha".

---

### 5. ISBN-13: który numer jest fałszywy? (wynik: pozycja B + cyfra 8)

> **Treść:** Trzy numery ksiąg trafiły do archiwum. Jeden został podrobiony — nie przechodzi sumy kontrolnej ISBN-13. Wskaż go i podaj, jaka cyfra powinna tam być.
> **A:** 978-83-289-1788-0 **B:** 978-83-829-1788-0 **C:** 978-83-289-1787-3
> Zasada: cyfry mnoży się naprzemiennie przez 1 i 3, sumuje, a cyfra kontrolna domyka sumę do wielokrotności 10.

**Dane:** jak wyżej (12 cyfr + cyfra kontrolna).
**Rozwiązanie:**
- **A:** 9·1+7·3+8·1+8·3+3·1+2·3+8·1+9·3+1·1+7·3+8·1+8·3 = 9+21+8+24+3+6+8+27+1+21+8+24 = **160**. 160 mod 10 = 0 → cyfra kontrolna **0** ✔
- **B:** …+8·3+2·3+… = 9+21+8+24+3+24+2+27+1+21+8+24 = **172**. 172 mod 10 = 2 → cyfra kontrolna powinna być **8**, a jest 0 ✘
- **C:** 9+21+8+24+3+6+8+27+1+21+8+21 = **157**. 157 mod 10 = 7 → cyfra kontrolna **3** ✔
**Wynik:** fałszywy = **B** (pozycja 2), poprawna cyfra = **8**.
**Czas:** 10 min. **Wiedza:** zero. **Ładny wynik?** TAK — dwie cyfry (2 i 8) z jednej zagadki.
**Smaczek:** numer A jest prawdziwy — to ISBN książki „Szuflada szyfrów" (Wykurz, Helion 2025), czyli realny egzemplarz z księgarni.

---

### 6. Luhn: cyfra kontrolna numeru karty (wynik 6)

> **Treść:** Karta biblioteczna Akademii ma numer **3141 5926 5358 979?** — ostatnia cyfra się starła. Odzyskaj ją metodą Luhna: idąc od prawej, co drugą cyfrę podwajasz; jeśli wyjdzie liczba dwucyfrowa, odejmujesz 9; wszystko sumujesz; cyfra kontrolna domyka sumę do wielokrotności 10.

**Dane:** 3 1 4 1 5 9 2 6 5 3 5 8 9 7 9 (+ szukana cyfra).
**Rozwiązanie (podwajamy pozycje 1,3,5,7,9,11,13,15 od lewej, bo cyfr jest 15):**
podwojone: 3→6, 4→8, 5→10→**1**, 2→4, 5→10→**1**, 5→10→**1**, 9→18→**9**, 9→18→**9**
niepodwojone: 1, 1, 9, 6, 3, 8, 7
Suma = 6+1+8+1+1+9+4+6+1+3+1+8+9+7+9 = **74** → cyfra kontrolna = 10 − 4 = **6**.
Kontrola na pełnym numerze: 74 + 6 = 80 → 80 mod 10 = 0 ✔
**Wynik:** **6** (pełny numer: 3141592653589796).
**Czas:** 8–10 min. **Wiedza:** zero. **Ładny wynik?** TAK — jedna cyfra 0–9.
**Smaczek (potwierdzony w źródle):** Luhn nie wyłapie przestawienia **09 ↔ 90** ani par 22↔55, 33↔66, 44↔77. Świetne zdanie do prezentu: „dlatego banki nie ufają temu do końca".

---

## Część III. Kody binarne i kompresja

### 7. Drabina w kodzie Graya (wynik 13)

> **Treść:** Drabina do wieży ma 16 szczebli, numerowanych od 0 do 15. Każdy szczebel ma mosiężną tabliczkę z 4-bitowym **kodem Graya**, w którym dwa sąsiednie szczeble różnią się tylko jednym bitem. Szczebel 0 ma tabliczkę 0000. Jaki kod ma szczebel **9**? A który szczebel ma tabliczkę **1010**?

**Dane:** 4-bitowy kod Graya; reguła: gray(n) = n XOR (n przesunięte o 1 bit w prawo).
**Rozwiązanie:**
- 9 = 1001₂; 9>>1 = 0100₂; 1001 XOR 0100 = **1101** → szczebel 9 ma 1101 = 13.
- Dla 1010: pierwszy bit naturalny = 1; kolejne: 1 XOR 0 = 1, 1 XOR 1 = 0, 0 XOR 0 = 0 → 1100₂ = **12**.
Kontrola tabelą: 8→1100, 9→1101, 10→1111, 11→1110, 12→1010 ✔
**Wynik:** szczebel 9 = **1101** (13); tabliczka 1010 = szczebel **12**.
**Czas:** 5–6 min. **Wiedza:** zero (trzeba tylko umieć XOR, który można objaśnić jednym zdaniem). **Ładny wynik?** TAK — 13 = D w hex; 1101 binarnie to wprost 4 bity.
**Dlaczego warto:** piękne „aha" inżynierskie — kod Graya istnieje, żeby przy obrocie tarczy nie odczytać bzdury (przejście 0111→1000 w naturalnym binarnym może chwilowo dać 1111). To konkretny, opowiadalny fakt.

---

### 8. Drzewo Huffmana na 16 zaklęciach (wynik 30 bitów)

> **Treść:** W księdze występuje 5 runów. Ich liczby wystąpień: **R1 = 8, R2 = 4, R3 = 2, R4 = 1, R5 = 1** (razem 16 runów). Zbuduj drzewo Huffmana (zawsze łącz dwa najrzadsze) i policz, ile **bitów** zajmie cała księga. Ile bitów zajęłaby przy kodzie o stałej długości?

**Dane:** 8, 4, 2, 1, 1.
**Rozwiązanie:**
1+1 = **2** → zbiór {2, 2, 4, 8}
2+2 = **4** → {4, 4, 8}
4+4 = **8** → {8, 8}
8+8 = **16**
Koszt = suma wag wszystkich połączeń = 2 + 4 + 8 + 16 = **30 bitów**.
Długości kodów: 8→1 bit, 4→2, 2→3, 1→4, 1→4. Kontrola: 8·1+4·2+2·3+1·4+1·4 = 8+8+6+4+4 = **30** ✔ (zgadza się z sumą połączeń). Kody stałej długości: 5 runów → 3 bity → 16·3 = **48 bitów**.
**Wynik:** **30** bitów (oszczędność 18 bitów = 37,5%).
**Czas:** 10–12 min. **Wiedza:** średnia (jedno zdanie reguły). **Ładny wynik?** TAK — 30, albo oszczędność 18, albo 37,5%.

---

## Część IV. Szyfry klasyczne

### 9. Cezar o trzy kroki (wynik: MAGIA)

> **Treść:** Uczeń pchnął kartkę z zaszyfrowaną odpowiedzią: **PDJLD**. Wiadomo, że litery przesunięto o **3 miejsca w alfabecie do przodu**. Co tam napisano?

**Dane:** PDJLD, przesunięcie 3 wstecz.
**Rozwiązanie:** P−3 = M, D−3 = A, J−3 = G, L−3 = I, D−3 = A.
**Wynik:** **MAGIA**.
**Czas:** 3–4 min. **Wiedza:** zero. **Ładny wynik?** Litery, nie liczba — ale M,A,G,I,A to 13,1,7,9,1 (suma 31), a „13 1 7 9 1" to legalny zapis dziesiętny. Jeśli kod ma być hexowy, lepiej użyć wariantu z literami A–F, np. **CAFE** (0xCAFE = 51966) — wtedy sama odpowiedź *jest* liczbą hex.

---

### 10. Vigenère z kluczem MAG (wynik: SZKOLA)

> **Treść:** Szyfr wieloliterowy: każdą literę tekstu przesuwamy o wartość kolejnej litery klucza (A=0, B=1, …, Z=25), zawijając alfabet. Klucz: **MAG**, szyfrogram: **EZQALG**. Co było w środku?

**Dane:** klucz M=12, A=0, G=6; szyfrogram E Z Q A L G.
**Rozwiązanie:**
E(4) − M(12) = −8 → +26 = 18 = **S**
Z(25) − A(0) = 25 = **Z**
Q(16) − G(6) = 10 = **K**
A(0) − M(12) = −12 → 14 = **O**
L(11) − A(0) = 11 = **L**
G(6) − G(6) = 0 = **A**
**Wynik:** **SZKOLA**.
**Czas:** 8 min. **Wiedza:** średnia (tabelka A–Z z liczbami do wydruku). **Ładny wynik?** Litery; liczbowo 19,26,11,15,12,1 (suma 84 → 84 mod 26 = 6).
**Dlaczego warto:** pokazuje, czemu jeden klucz na całą wiadomość to za mało — motyw „dlaczego Enigma przegrała".

---

### 11. Base64 na kartce (wynik: MAGIA)

> **Treść:** Zamiast liter — ciąg **TUFHSUE=**. To Base64: każde 3 bajty zamienia się na 4 znaki po 6 bitów, według tabeli A–Z, a–z, 0–9, +, /. Rozszyfruj.

**Dane:** TUFHSUE= ; tabela: A=0 … Z=25, a=26 … z=51, 0=52 … 9=61.
**Rozwiązanie:**
T=19, U=20, F=5, H=7 → bity 010011 010100 000101 000111 → bajty 01001101 01000001 01000111 = 0x4D 0x41 0x47 = **M A G**
S=18, U=20, E=4, „=" → bity 010010 010100 000100 (jedno „=" → 2 bajty) → 01001001 01000001 = 0x49 0x41 = **I A**
**Wynik:** **MAGIA** (hex: 4D 41 47 49 41).
**Czas:** 10 min. **Wiedza:** średnia. **Ładny wynik?** TAK, podwójnie — litery **i** gotowe bajty hex 4D 41 47 49 41 do wpisania w kod.

---

### 12. Jednorazowy pad XOR (wynik: MAG)

> **Treść:** Szyfrogram w hex: **67 6B 6D**. Klucz (jeden bajt, powtarzany): **2A**. Zaszyfrowano nim trzyliterowe słowo. Odszyfruj. (XOR dwukrotnie z tym samym kluczem wraca do początku.)

**Dane:** 0x67, 0x6B, 0x6D; klucz 0x2A.
**Rozwiązanie (XOR bit po bicie):**
0x67 = 0110 0111 XOR 0010 1010 = 0100 1101 = **0x4D = 'M'**
0x6B = 0110 1011 XOR 0010 1010 = 0100 0001 = **0x41 = 'A'**
0x6D = 0110 1101 XOR 0010 1010 = 0100 0111 = **0x47 = 'G'**
**Wynik:** **MAG** (4D 41 47).
**Czas:** 6 min. **Wiedza:** średnia (trzeba pokazać tabelę XOR — 4 wiersze). **Ładny wynik?** TAK — surowe bajty hex.
**Smaczek:** jeśli ten sam klucz zaszyfruje dwa różne teksty, to XOR obu szyfrogramów = XOR obu tekstów jawnych. To najkrótsze możliwe wytłumaczenie, czemu „pad" musi być jednorazowy.

---

## Część V. Statystyka, czyli pułapki data science

### 13. Tabela wyników domów: średnia vs mediana (wynik 30 i 15)

> **Treść:** Oto punkty zdobyte przez uczniów w pojedynku z trollem.
> **Dom Smoka:** 12, 14, 15, 16, **93** (93 pkt to jednorazowa nagroda za pokonanie trolla).
> **Dom Feniksa:** 25, 26, 27, 28, 29.
> Policz **średnią** i **medianę** obu domów. Który dom wygrywa według średniej, a który według mediany?

**Dane:** jak wyżej.
**Rozwiązanie:**
Smok: suma = 150 → średnia **30**; mediana = **15**.
Feniks: suma = 135 → średnia **27**; mediana = **27**.
Średnia: Smok wygrywa (30 > 27). Mediana: Feniks wygrywa (27 > 15). Różnica średnich = **3**.
**Wynik:** 30 / 15 / 27 / 27; różnica średnich **3**.
**Czas:** 5–6 min. **Wiedza:** zero. **Ładny wynik?** TAK — trzy osobne cyfry (3, 1+5=6, 2+7=9) i gotowy „spór o sprawiedliwość".
**Dlaczego warto:** to najbardziej „prezentowa" zagadka z całego zestawu — jedna liczba 93 przewraca ranking. Efekt: „średnia kłamie, gdy jedna osoba dostanie nagrodę za trolla".

---

### 14. Regresja na trzech turniejach (wynik 11)

> **Treść:** Dom Smoka zdobył w trzech kolejnych turniejach: 1. turniej — **2** pkt, 2. — **7** pkt, 3. — **6** pkt. Dopasuj prostą y = a + bx (x = numer turnieju) i przepowiedz wynik w **5.** turnieju.

**Dane:** (1, 2), (2, 7), (3, 6).
**Rozwiązanie:**
x̄ = 2, ȳ = 15/3 = 5.
Odchylenia y: −3, +2, +1. Odchylenia x: −1, 0, +1.
Sxy = (−1)(−3) + 0·2 + 1·1 = 3 + 0 + 1 = 4; Sxx = 1 + 0 + 1 = 2.
b = 4/2 = **2**; a = ȳ − b·x̄ = 5 − 4 = **1**. Prosta: **y = 1 + 2x**.
Reszty: 2−3 = −1; 7−5 = +2; 6−7 = −1 (suma 0 ✔).
Prognoza x = 5: y = 1 + 10 = **11**.
**Wynik:** **11** (a = 1, b = 2).
**Czas:** 10–12 min. **Wiedza:** średnia (trzeba podać wzory na Sxy/Sxx). **Ładny wynik?** TAK — 11, a przy okazji a=1 i b=2 to dwie dodatkowe cyfry.

---

### 15. Paradoks Simpsona w tabeli domów (wynik 78% vs 83%)

> **Treść:** Dwa domy zmierzyły się w dwóch kategoriach: **zaklęcia łatwe** i **zaklęcia trudne**.
> Dom Feniksa: łatwe **81/87** (93%), trudne **192/263** (73%), razem **273/350**.
> Dom Smoka: łatwe **234/270** (87%), trudne **55/80** (69%), razem **289/350**.
> W obu kategoriach lepszy jest Feniks. Który dom ma lepszy wynik łączny?

**Dane:** jak wyżej.
**Rozwiązanie:**
81/87 = 93,1% vs 234/270 = 86,7% → Feniks lepszy.
192/263 = 73,0% vs 55/80 = 68,75% → Feniks lepszy.
Razem: 273/350 = **78,0%** (Feniks) vs 289/350 = **82,6%** (Smok) → wygrywa **Smok**.
**Wynik:** 78% i 83% (różnica 5 punktów procentowych); wygrywa dom, który przegrał obie kategorie.
**Czas:** 8–10 min. **Wiedza:** średnia (wystarczy dzielenie i procenty). **Ładny wynik?** TAK — 78 i 83 to dwie liczby, a różnica 5 to cyfra.
**Uwaga o wiarygodności:** to autentyczne dane z artykułu o leczeniu kamieni nerkowych (BMJ 1986) — 81/87, 192/263, 273/350 i 234/270, 55/80, 289/350 zgadzają się co do liczby. W wersji „domy magii" wystarczy podmienić etykiety; lepiej nie zmieniać liczb, bo są sprawdzone.

---

### 16. Test na magię: twierdzenie Bayesa na palcach (wynik 50%)

> **Treść:** W Akademii jest **100 uczniów**, z czego **10** potajemnie uprawia magię. Test wykrywający magię:
> – u osoby magicznej daje wynik dodatni w **90%** przypadków,
> – u osoby bez magii fałszywie wskazuje „magię" w **10%** przypadków.
> Uczeń X ma wynik dodatni. Jakie jest prawdopodobieństwo, że naprawdę uprawia magię?

**Dane:** 100 uczniów, 10 magicznych, czułość 90%, odsetek fałszywych alarmów 10%.
**Rozwiązanie (na osobach, nie na wzorach):**
magiczni: 10 → wykrytych 10·0,9 = **9**
niemagiczni: 90 → fałszywie dodatnich 90·0,1 = **9**
wszystkich dodatnich: 9 + 9 = **18**; prawdziwie magicznych wśród nich: **9**.
P = 9/18 = **1/2 = 50%**.
**Wynik:** **50%** (albo liczby 9, 9, 18).
**Czas:** 7–8 min. **Wiedza:** zero — cała sztuczka polega na liczeniu ludzi, nie procentów. **Ładny wynik?** TAK — 50%, a 9/18 daje dwie cyfry 9 i 1+8=9.
**Dlaczego warto:** „połowa dodatnich wyników to fałszywe alarmy" to najbardziej kontrintucyjny wynik w całym zestawie, a liczby są dobrane tak, że wychodzi równiutko 1/2.

---

## Część VI. Zasada szufladkowa i rachunek prawdopodobieństwa

### 17. Komnaty i urodziny (wynik 25)

> **Treść:** W Akademii jest **12 komnat**, każdy uczeń śpi w tej, która odpowiada miesiącowi jego urodzin. Ilu uczniów musi mieszkać w Akademii, żeby mieć **pewność**, że w jednej komnacie śpi co najmniej **3** uczniów?

**Dane:** 12 komnat, próg 3 osoby.
**Rozwiązanie:** przy 2 osobach na komnatę mieści się 12·2 = **24** uczniów bez naruszenia progu. Dopiero 25. osoba nie ma gdzie się schować → **25**.
**Wynik:** **25**.
**Czas:** 2–3 min. **Wiedza:** zero. **Ładny wynik?** TAK (25), ale uwaga: to zagadka „na jeden błysk", nie na 10 minut — dobra jako rozgrzewka lub jako druga część innej.
**Wariant:** „co najmniej 2 w tym samym miesiącu" → 13 (klasyk, za łatwy); „co najmniej 4" → 37.

---

### 18. Igła Buffona: Monte Carlo bez komputera (wynik 3,125)

> **Treść:** Na kartce narysowano równoległe linie w odstępie **2 razy większym niż długość zapałki**. Rzucono **100** zapałek. **32** z nich przecięły linię. Oszacuj π.
> Zasada (Buffon, 1777): prawdopodobieństwo przecięcia = 2L/(π·d). Jeśli odstęp d = 2L, to prawdopodobieństwo = 1/π, więc π ≈ liczba rzutów / liczba przecięć.

**Dane:** 100 rzutów, 32 przecięcia, d = 2L.
**Rozwiązanie:** π ≈ 100 / 32 = **3,125** = 25/8. Błąd względem π: (3,1416 − 3,125)/3,1416 ≈ **0,53%**.
**Wynik:** **3,125** (25/8).
**Czas:** 5 min (samo dzielenie), 10–15 min jeśli rzucamy naprawdę. **Wiedza:** zero. **Ładny wynik?** TAK — 3,125, a 25 i 8 to dwie liczby; „25/8" to gotowy ułamek.
**Wariant bez rzucania (siatka 10×10):** narysuj ćwiartkę koła o promieniu 10 kratek na siatce 10×10 i policz kratki, których **środek** leży w kole. Wychodzi dokładnie **79** kratek → π ≈ 4·79/100 = **3,16**. Liczenie: kolumna po kolumnie 10, 10, 10, 9, 9, 8, 8, 7, 5, 3 = 79. To wersja bardziej „na 10 minut", a wynik 79 jest ładną liczbą.

---

## Część VII. Kody korygujące błędy

### 19. Kod Hamminga (7,4): jeden przekłamany bit (wynik 1011 = 11)

> **Treść:** Odebrano 7-bitowe słowo: **0 1 1 0 1 1 1**. Wiadomo, że w drodze przekłamano **dokładnie jeden** bit. Pozycje 1, 2, 4 to bity kontrolne, pozycje 3, 5, 6, 7 to dane. Znajdź i popraw błąd, a potem odczytaj 4 bity danych.
> Reguła: p1 sprawdza pozycje 1,3,5,7; p2 — 2,3,6,7; p4 — 4,5,6,7. Te trzy kontrole ustawione jako liczba 3-bitowa (p4 p2 p1) wskazują numer błędnej pozycji.

**Dane:** 0 1 1 0 1 1 1.
**Rozwiązanie:**
kontrola p1 (1,3,5,7): 0,1,1,1 → trzy jedynki = nieparzysta → **s1 = 1**
kontrola p2 (2,3,6,7): 1,1,1,1 → cztery jedynki = parzysta → **s2 = 0**
kontrola p4 (4,5,6,7): 0,1,1,1 → trzy jedynki = nieparzysta → **s4 = 1**
syndrom (p4 p2 p1) = **101** = pozycja **5** → przekłamany bit to pozycja 5 (0→1).
Słowo poprawione: 0 1 1 0 **0** 1 1. Dane z pozycji 3,5,6,7: 1, 0, 1, 1 = **1011**.
**Wynik:** błąd na pozycji **5**; dane = **1011** = **11**.
**Czas:** 10–12 min. **Wiedza:** średnia (trzeba wydrukować regułę kontroli). **Ładny wynik?** TAK, bardzo — wynik to dosłownie 4 bity i liczba 11 (= B w hex).
**Weryfikacja:** dla danych 1011 poprawnym słowem jest 0110011 (p1=0, p2=1, p4=0) — zgadza się z kalkulatorem kodu Hamminga (7,4) i z demonstracją Wolframa.

---

### 20. Parzystość: który wiersz jest uszkodzony? (wynik 3)

> **Treść:** Sześć 8-bitowych zapisów runicznych. Każdy poprawny ma **parzystą** liczbę jedynek. Jeden został uszkodzony. Który?
> 1) 11001010 2) 00110110 3) 11100011 4) 01010101 5) 10011001 6) 01101001

**Dane:** jak wyżej.
**Rozwiązanie:** licz jedynki w każdym wierszu: 4, 4, **5**, 4, 4, 4. Jeden nieparzysty → wiersz 3.
**Wynik:** wiersz **3**.
**Czas:** 3–4 min. **Wiedza:** zero. **Ładny wynik?** TAK (3) — ale to zagadka „na 3 minuty", dobra jako element większej.
**Wariant trudniejszy (na 10 min):** dodaj kolumnę parzystości pionowej (bit parity whole-byte) i poproś o wskazanie błędu dwuwymiarowo — wtedy gracz naprawia słowo i odczytuje z niego cyfrę.

---

### 21. Sieć sortująca na 5 zawodnikach (wynik: 5 zamian, 10 porównań)

> **Treść:** Oto sieć sortująca na 5 torach (10 komparatorów, każdy porównuje dwie sąsiednie wartości i zamienia je, jeśli są w złej kolejności):
> **(1,2) (2,3) (1,2) (3,4) (2,3) (1,2) (4,5) (3,4) (2,3) (1,2)**
> Przepuść przez nią listę wyników: **[4, 1, 5, 2, 3]**. Ile razy komparator faktycznie zamienił wartości? Ile porównań wykonano?
> Pytanie bonusowe: dlaczego sieć wykonuje zawsze 10 porównań, nawet gdy lista jest już posortowana?

**Dane:** lista [4,1,5,2,3], sieć 10 komparatorów.
**Rozwiązanie (krok po kroku):**
C1 (1,2): 4,1 → zamiana **#1** → [1,4,5,2,3]
C2 (2,3): 4,5 → bez zmian
C3 (1,2): 1,4 → bez zmian
C4 (3,4): 5,2 → zamiana **#2** → [1,4,2,5,3]
C5 (2,3): 4,2 → zamiana **#3** → [1,2,4,5,3]
C6 (1,2): 1,2 → bez zmian
C7 (4,5): 5,3 → zamiana **#4** → [1,2,4,3,5]
C8 (3,4): 4,3 → zamiana **#5** → [1,2,3,4,5]
C9 (2,3): 2,3 → bez zmian
C10 (1,2): 1,2 → bez zmian
**Wynik:** **5 zamian**, **10 porównań**, lista posortowana.
**Czas:** 8–10 min. **Wiedza:** średnia (trzeba narysować 5 linii i kreski). **Ładny wynik?** TAK — 5 i 10 to dwie cyfry.
**Bonusowe „aha" (potwierdzone):** sieć jest *data-oblivious* — zawsze robi 10 porównań. Tymczasem optymalny algorytm sortowania 5 elementów potrzebuje **7** porównań w najgorszym przypadku (metoda Forda–Johnsona, 1959); sortowanie przez wstawianie potrzebuje 10. To pokazuje, że „równoległość kosztuje" — bardzo dobre zdanie do prezentu.

---

## Zestawienie: co daje jaką cyfrę

| # | Zagadka | Wynik | Cyfra hex? | Czas | Wiedza |
|---|---|---|---|---|---|
| 1 | Turniej co 1000 dni | 6 / poniedziałek | 6 ✔ | 5 min | zero |
| 2 | Klasa 40–50 | 43 | 4+3=7 ✔ | 7 min | zero |
| 3 | ISBN-10 cyfra kontrolna | 3 | 3 ✔ | 8 min | zero |
| 4 | ISBN-10 z „X" | X = 10 | A ✔ | 8 min | średnia |
| 5 | ISBN-13 fałszywy numer | B / 2 / 8 | 2 i 8 ✔ | 10 min | zero |
| 6 | Luhn | 6 | 6 ✔ | 9 min | zero |
| 7 | Kod Graya | 13 / 1101 | D ✔ | 6 min | zero |
| 8 | Huffman | 30 | 3+0=3 ✔ | 12 min | średnia |
| 9 | Cezar | MAGIA | litery | 4 min | zero |
| 10 | Vigenère | SZKOLA | litery | 8 min | średnia |
| 11 | Base64 | MAGIA / 4D41474941 | bajty hex ✔ | 10 min | średnia |
| 12 | XOR | MAG / 4D 41 47 | bajty hex ✔ | 6 min | średnia |
| 13 | Średnia vs mediana | 30 / 15 / 27 | 3, 6, 9 ✔ | 6 min | zero |
| 14 | Regresja 3 punkty | 11 / a=1, b=2 | B ✔ | 11 min | średnia |
| 15 | Paradoks Simpsona | 78% vs 83% | 5 (różnica) ✔ | 10 min | średnia |
| 16 | Bayes | 50% (9/18) | 9, 9, 1+8=9 ✔ | 8 min | zero |
| 17 | Szufladkowa | 25 | 2+5=7 ✔ | 3 min | zero |
| 18 | Buffon / siatka | 3,125 / 79 | 25 i 8 ✔ | 5–10 min | zero |
| 19 | Hamming (7,4) | 1011 = 11 | B ✔ | 11 min | średnia |
| 20 | Parzystość | 3 | 3 ✔ | 4 min | zero |
| 21 | Sieć sortująca | 5 zamian, 10 porównań | 5 i 0 ✔ | 9 min | średnia |

**Jak złożyć z tego kod (propozycja, nie fakt źródłowy):** wybierz 4–6 zagadek, z których każda daje jedną cyfrę 0–15, i sklej je w hex. Przykład: 3 (ISBN-10) → 3, 7 (Gray) → D, 6 (Luhn) → 6, 19 (Hamming) → B, 4 (ISBN X) → A daje **3D6BA**. Jeśli kod ma być tekstem ASCII w hex, użyj zagadek 11 i 12 — one dają dosłownie bajty (4D 41 47 49 41 = „MAGIA"). To pozwala zrobić adres w stylu `…/4d41474941`, który sam w sobie jest zagadką.

---

## TOP 3 do użycia na kartce

### 1. ISBN-13: który numer jest fałszywy? (zagadka #5)
**Dlaczego:** to jedyna zagadka, w której gracz *odkrywa regułę działającą w prawdziwym świecie* — i od razu kojarzy ją z każdym numerem, jaki ma w portfelu. Ma trzy cechy, których brakuje innym: (a) **zero wymaganej wiedzy** poza jednym zdaniem reguły, (b) **dane są prawdziwe** (numer A to realny ISBN książki o szyfrach), więc „aha" jest podwójne — „to nie wymyślone, to naprawdę tak działa", (c) daje **dwie odpowiedzi** (pozycja B i cyfra 8), czyli dwie cegiełki do kodu z jednego zadania. Czas 10 minut mieści się w środku widełek.

### 2. Tabela domów: średnia vs mediana (zagadka #13)
**Dlaczego:** najbardziej „prezentowa" i najlepiej dopasowana do motywu szkoły magii — bo to po prostu tabela wyników domów, a nie abstrakcyjne zadanie. Efekt jest natychmiastowy i opowiadalny: **jedna nagroda za pokonanie trolla (93 pkt) przewraca cały ranking**. Zero wiedzy, 6 minut, cztery ładne liczby (30, 15, 27, 27) i gotowy temat do rozmowy przy stole: „czy średnia jest sprawiedliwa?". Dodatkowy plus: można ją wydrukować jako *prawdziwą tabelę* i to jest cała oprawa graficzna, jakiej potrzebuje kartka.

### 3. Test na magię: Bayes na 100 uczniach (zagadka #16)
**Dlaczego:** najlepszy stosunek „zaskoczenie / czas / wiedza". Gracz liczy na palcach (9 wykrytych + 9 fałszywych alarmów = 18, czyli 50%) i przeżywa prawdziwe „aha, połowa to pomyłki". Liczby są dobrane tak, że wynik wychodzi **równiutko 1/2** — zero ułamków, zero brzydkich procentów, a mimo to wynik jest kontrintucyjny. Idealnie pasuje do motywu („test na magię" w szkole magii jest naturalny, nie doklejony) i daje trzy cyfry (9, 9, 9).

**Poza podium, ale warte rozważenia:**
- **Kod Hamminga (#19)** — najbardziej „wow techniczne" (dosłownie *naprawiasz przekłamany bit*), ale 11 minut + trzeba wydrukować regułę kontroli. Najlepsze, jeśli prezent ma być o *informatyce*, nie o statystyce.
- **Igła Buffona (#18)** — najbardziej urocza (π z rzucania zapałek), ale wymaga rzucania albo siatki; świetna jako element interaktywny, słabsza jako czyste „policz na kartce".
- **Paradoks Simpsona (#15)** — mocny merytorycznie, ale liczby są duże (273/350), więc męczy; warto dać kalkulator albo skrócić do „który dom wygrywa łącznie?" bez liczenia procentów.

**Praktyczna uwaga:** na jedną kartkę wejdą **3–4 zagadki**, nie 21. Rekomendowany zestaw: #5 (ISBN-13), #13 (średnia/mediana), #16 (Bayes) + jedna szybka rozgrzewka #1 lub #17. Każda daje 1–2 cyfry, razem 4–5 cyfr hex — dokładnie tyle, ile potrzeba na krótki kod.

---

## Źródła i weryfikacja

**Zachowane (merytorycznie nośne):**
- Luhn algorithm — Wikipedia (https://en.wikipedia.org/wiki/Luhn_algorithm) — pełny opis kroków, przykład 1789372997 → 4 (suma 56), informacja o ISO/IEC 7812-1 i o tym, że **nie** wykrywa przestawienia 09↔90 oraz par 22↔55/33↔66/44↔77. Użyte do zagadki #6 i do „smaczku".
- ISBN — Wolfram MathWorld (https://mathworld.wolfram.com/ISBN.html) — reguła ISBN-10 (wagi 10…1, mod 11, X = 10, suma podzielna przez 11 daje 0) i ISBN-13 (wagi 1,3 naprzemiennie). Użyte do #3, #4, #5.
- ISBN — Wikipedia (https://en.wikipedia.org/wiki/ISBN) — kontekst (ISO 2108, 978/979, format 13-cyfrowy od 2007). Użyte jako tło.
- Kod Graya — polska Wikipedia (https://pl.wikipedia.org/wiki/Kod_Graya) — własność „jeden bit na krok", konstrukcja przez odbicie lustrzane, konwersja gray→binarny z przykładem 1010 → 1100 = 12. Użyte do #7.
- Kody Graya — eSezam PW (https://esezam.okno.pw.edu.pl/...) — tabela 4-bitowa 0…15 (0→0000, 7→0100, 8→1100, 12→1010, 15→1000), użyta jako kontrola.
- Kod Graya — eduinf.waw.pl (https://www.eduinf.waw.pl/inf/alg/006_bin/0025.php) — uzasadnienie inżynierskie (tarcza kodowa, 01111→10000 może dać stan pośredni 11110). Użyte do „dlaczego warto".
- Hamming code calculator (https://truthtablekit.com/hamming-code/) — niezależne potwierdzenie, że dane **1011** kodują się jako **0110011** (p1=0, p2=1, p4=0), oraz że syndrom odczytuje pozycję błędu. Użyte do weryfikacji #19.
- The Hamming(7,4) Code — Wolfram Demonstrations (https://demonstrations.wolfram.com/TheHamming74Code/) — „trzy bity parzystości jako liczba 3-bitowa wskazują pozycję błędu". Potwierdza mechanizm #19.
- Charig i in., *Comparison of treatment of renal calculi…*, BMJ 1986 (https://www.bmj.com/content/bmj/292/6524/879.full.pdf) — pierwotne dane paradoksu Simpsona: 81/87 (93%) vs 234/270 (87%) w grupie 1, 192/263 (73%) vs 55/80 (69%) w grupie 2, łącznie 273/350 (78%) vs 289/350 (83%). Użyte bez zmian do #15.
- Sorting network — Wikipedia (https://en.wikipedia.org/wiki/Sorting_network) — tabela optymalnych sieci: dla n = 5 **rozmiar 9, głębokość 5**; definicja komparatora i zasada zero-jedynkowa. Użyte do #21.
- „How fast can we sort 5 elements" (https://wiki.tcl-lang.org/page/How+fast+can+we+sort+5+elements) + cs.stackexchange (https://cs.stackexchange.com/questions/44981/) — 5 elementów można posortować w **7** porównaniach (Ford–Johnson 1959 / Demuth 1956), a sortowanie przez wstawianie/bąbelkowe potrzebuje **10**. Użyte do bonusowego „aha" w #21.
- Buffon's Needle — Jonathan Davidson (https://jjdavidson.github.io/teaching/pi-day/buffons-needle/) — P = 2L/(πd), przy d = 2L dostajemy P = 1/π, więc π ≈ 1/p̂. Użyte do #18.
- Pi Toss — Exploratorium (https://www.exploratorium.edu/snacks/pi-toss) — praktyczna wersja „podziel liczbę rzutów przez liczbę przecięć", wprost jako przykład metody Monte Carlo. Użyte do #18.
- Matematyczne łamańce (Helion, fragment PDF) — przykład polskich „matematyka towarzyska" zagadek z gwarantowanym wynikiem; użyte tylko jako benchmark stylu i poziomu (nie do treści).

**Odrzucone / zdeprioryzowane:**
- Wyniki wyszukiwania księgarni (Helion, edukacyjna.pl) o książkach z zagadkami — przydatne tylko jako dowód, że ISBN-y w zagadkach są realne; nie nadają się na źródło treści.
- Stripe „What is the Luhn algorithm" — marketing + powtórzenie Wikipedii; pominięte.
- math.stackexchange „sort 5 elements in 7 comparisons" — pytanie z błędną przesłanką; wykorzystałem tylko komentarz wskazujący Forda–Johnsona, a tezę potwierdziłem na cs.stackexchange i w artykule o Tcl.
- Kod Hamminga (PDF CS 444, UMass) — poprawny, ale ma inną numerację pozycji niż moja zagadka; użyty tylko pomocniczo, żeby nie wprowadzić sprzeczności.

---

## Czego nie zweryfikowałem / ryzyka

1. **Liczby w zagadkach są skonstruowane przeze mnie** pod ładny wynik — nie pochodzą z podręczników. Wszystkie przeliczenia są rozpisane krok po kroku powyżej; radzę przepuścić #3, #4, #5, #6, #14, #19 jeszcze raz przy druku (to najbardziej „arytmetycznie gęste").
2. **Zagadka #5** — twierdzenie, że numer A jest ISBN-em realnej książki, pochodzi z wyniku wyszukiwania (karta katalogowa Helion). To prawdopodobne, ale nie sprawdziłem tego w bazie ISBN. Jeśli to ma być argument w treści prezentu, warto sprawdzić.
3. **Zagadka #21** — sieć, którą podaję, jest poprawna (prześledzona ręcznie), ale **nie jest optymalna** (10 komparatorów zamiast 9). To celowe: łatwiej ją narysować i prześledzić. Jeśli ktoś zapyta „czy da się mniej?", odpowiedź brzmi: tak, 9 komparatorów (potwierdzone w tabeli Wikipedii).
4. **Zagadka #18 (siatka 10×10)** — liczba 79 kratek jest moim ręcznym przeliczeniem warunku (i+0,5)² + (j+0,5)² ≤ 100 dla i,j = 0…9. Warto policzyć jeszcze raz przy rysowaniu, bo zależy od tego, czy liczymy środki kratek (79), czy całe kratki wewnątrz koła (mniej, ok. 69–70).
5. **Czas rozwiązywania** to moje oszacowanie dla osoby bez wprawy, nie pomiar na grupie. Doświadczalnie warto dodać 30–50% buforu, jeśli odbiorca nie lubi rachunków.
6. **Motyw szkoły magii** jest tu tylko szatą graficzną — żadna z zagadek nie wymaga wiedzy o uniwersum; to zaleta (nie trzeba nic tłumaczyć), ale też ograniczenie (nie da się zrobić zagadek „fabularnych" opartych na kanonie).
