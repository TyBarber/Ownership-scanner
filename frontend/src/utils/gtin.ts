export function normalizeGtin(value: string): string {
  return value.replace(/[\s-]/g, "");
}

export function validateGtin(value: string): string | null {
  const gtin = normalizeGtin(value);
  if (!/^\d+$/.test(gtin) || ![8, 12, 13, 14].includes(gtin.length)) {
    return "Enter an 8-, 12-, 13-, or 14-digit barcode.";
  }

  const digits = [...gtin].map(Number);
  const checkDigit = digits.at(-1);
  const total = digits
    .slice(0, -1)
    .reverse()
    .reduce(
      (sum, digit, index) => sum + digit * (index % 2 === 0 ? 3 : 1),
      0,
    );
  const expected = (10 - (total % 10)) % 10;
  return expected === checkDigit
    ? null
    : "That barcode’s check digit does not match.";
}
