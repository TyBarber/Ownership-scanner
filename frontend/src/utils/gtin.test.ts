import { describe, expect, it } from "vitest";
import { normalizeGtin, validateGtin } from "./gtin";

describe("GTIN validation", () => {
  it("preserves leading zeros while normalizing spaces and hyphens", () => {
    expect(normalizeGtin("0001 6000-124790")).toBe("00016000124790");
  });

  it("accepts valid 8-, 12-, 13-, and 14-digit values", () => {
    for (const gtin of [
      "00712996",
      "850017142350",
      "4006381333931",
      "00016000124790",
    ]) {
      expect(validateGtin(gtin)).toBeNull();
    }
  });

  it("rejects incorrect lengths, characters, and check digits", () => {
    expect(validateGtin("123")).toMatch(/8-, 12-, 13-, or 14-digit/);
    expect(validateGtin("not-a-code")).toMatch(/8-, 12-, 13-, or 14-digit/);
    expect(validateGtin("00016000124791")).toMatch(/check digit/);
  });
});
