// Odszyfrowanie kuponu w przeglądarce: PBKDF2-SHA256 → AES-GCM.
// Bez zależności i bez sieci — cała kryptografia siedzi w WebCrypto.
// Hasło nie jest nigdzie zapisane: w stronie leży tylko szyfrogram, sól i IV.
// Ten plik jest wstrzykiwany do <script> w index.html i testowany przez Deno.

globalThis.presentUnlock = (() => {
  const ITERACJE = 210000;

  // Polskie znaki diakrytyczne składamy do ASCII, żeby "Hufflepuff 7", "hufflepuff7"
  // i "HUFFLEPUFF-7" trafiły w to samo hasło.
  function normalize(value) {
    return value
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/ł/gi, "l")
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "");
  }

  function bytes(b64) {
    return Uint8Array.from(atob(b64), (char) => char.charCodeAt(0));
  }

  async function deriveKey(password, salt, iterations) {
    const material = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(password),
      "PBKDF2",
      false,
      ["deriveKey"],
    );
    return crypto.subtle.deriveKey(
      { name: "PBKDF2", salt, iterations, hash: "SHA-256" },
      material,
      { name: "AES-GCM", length: 256 },
      false,
      ["decrypt"],
    );
  }

  // Zwraca {code, png} albo null, gdy hasło nie pasuje (AEAD tego nie udaje).
  async function unlock(answer, box) {
    const password = normalize(answer);
    if (!password) return null;
    try {
      const key = await deriveKey(password, bytes(box.salt), box.iterations || ITERACJE);
      const plain = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: bytes(box.iv) },
        key,
        bytes(box.ct),
      );
      return JSON.parse(new TextDecoder().decode(plain));
    } catch {
      return null;
    }
  }

  return { normalize, unlock };
})();
