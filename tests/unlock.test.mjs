// Sprawdza, że część przeglądarkowa odszyfrowuje to, co zapisał Python.
// Uruchamiane z `mise run test`: deno run --allow-read tests/unlock.test.mjs
//
// Testy nie trzymają hasła w repo — biorą je z build/answer.txt (gitignored).

const html = await Deno.readTextFile("docs/index.html");
const answer = (await Deno.readTextFile("build/answer.txt")).trim();

const match = html.match(/<script type="application\/json" id="box">([\s\S]*?)<\/script>/);
if (!match) throw new Error("w docs/index.html nie ma bloku #box");

const box = JSON.parse(match[1]);
await import("../templates/unlock.js");
const { unlock, normalize } = globalThis.presentUnlock;

const opened = await unlock(answer, box);
if (!opened || !opened.code || !opened.png) {
  throw new Error(`poprawne hasło nie otworzyło kuponu (hasło: ${answer})`);
}

const wrong = await unlock("zupelnie-nie-to-haslo", box);
if (wrong !== null) throw new Error("błędne hasło otworzyło kupon");

// Wpisywanie "z ręki" musi działać: wielkie litery, spacja, myślnik, polski znak.
const messy = answer.slice(0, -1).toUpperCase() + " - " + answer.slice(-1);
if (!(await unlock(messy, box))) {
  throw new Error(`normalizacja nie przepuściła ${JSON.stringify(messy)}`);
}
if (normalize("Ravenclaw 3") !== normalize("ravenclaw3")) {
  throw new Error("normalizacja nie skleja spacji");
}

console.log(`OK: kupon ${opened.code} odszyfrowany w Deno, hasło "${answer}"`);
