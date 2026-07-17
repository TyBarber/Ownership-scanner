# Product Intake Review — 2026-07-17

## Scope and preservation

The original `/Users/tybarber/Desktop/products-intake.csv` was inspected read-only and was not modified. It contains five records. The photo columns contain only `yes`; they do not provide filenames or image paths, so the photos could not be inspected.

## Barcode findings

The saved barcode strings were not preserved at standard GTIN lengths. Leading zeros appear to have been removed before or during CSV creation.

| Brand | Saved value | Saved length | Provisional UPC-A value | Check digit |
|---|---:|---:|---:|---|
| Joseph's Bakery | `7411700734` | 10 | `074117000734` | Valid; confirmed from barcode photo |
| Trader Joe's | `712996` | 6 | `00712996` (UPC-E) | Valid; confirmed from barcode photo |
| ShopRite | `41190055661` | 11 | `041190055661` | Valid; confirmed from barcode photo |
| Tuttorosso | `72940757092` | 11 | `072940757092` | Valid; confirmed from barcode photo |
| Nature's Path Organic | `58449870241` | 11 | `058449870241` | Valid; confirmed from barcode photo |

The Joseph's Bakery value was read directly from the barcode photo as `0 74117 00073 4`. The intake value was missing both the leading number-system digit and one zero within the code, so simple left-padding would not have recovered it. Its confirmed UPC-A check digit is valid.

The Nature's Path Organic value was read directly from the barcode photo as `0 58449 87024 1`; its confirmed UPC-A check digit is valid.

The Tuttorosso value was read directly from the barcode photo as `0 72940 75709 2`; its confirmed UPC-A check digit is valid.

The light red kidney beans value was read directly from the barcode photo as `0 41190 05566 1`; its confirmed UPC-A check digit is valid.

The Trader Joe's value is a UPC-E printed as `0 071299 6`, giving the exact eight-digit code `00712996`. Its check digit is valid. Its expanded UPC-A equivalent is `007129000096`; the dataset preserves the exact printed UPC-E rather than the previously assumed left-padded value.

All five barcode values have now been confirmed from photos.

## Normalization applied

- Trimmed leading/trailing whitespace.
- Normalized product, brand, and category capitalization.
- Corrected obvious transcription spelling in package text (`excusively`, `Distrubuted`, and `distrubuted`).
- Expanded `dist.` to `Distributed` while preserving meaning.
- Added `https://` to brand websites.
- Kept image URLs blank because `yes` is not a usable URL.

The CSV model has no company-address field, so addresses remain documented here and are not silently inserted into another field.

## Missing or ambiguous package information

- **Joseph's Bakery:** Package text is blank. The address `30 International Way, Lawrence, MA 01843` has no company name attached in the intake. No company record was created.
- **Trader Joe's:** Package text identifies `Trader Joe's`, but does not state its precise legal entity name or establish ownership. A research-required company record was created from the package name only.
- **ShopRite / Wholesome Pantry:** The barcode photo says `Wholesome Pantry Organic is a registered trademark of Wakefern Food Corp. ©2023`, while the intake identifies the brand as ShopRite. Confirm the consumer-facing brand from the front label before changing the product or brand record. The trademark statement is a strong research lead but is not yet entered as a verified ownership edge because no source record has been researched.
- **Tuttorosso:** The photo confirms `Distributed by Red Gold, LLC, PO Box 83, Elwood, IN 46036`. This resolves the intake's `Red Gold, Inc.` discrepancy in favor of the package text. Distribution still does not establish brand ownership.
- **Nature's Path Organic:** The photo confirms the visible address text as `c/o Nature's Path Foods, #275-250 H St., Blaine, WA`. The ZIP code and country from the intake are not visible in this photo and remain to be confirmed from other package information.
- **All products:** Front, barcode, and company-information photos were marked present but were not linked. Package sizes/variants were not consistently captured and should be confirmed if printed in the product name area.

## Ownership handling

No ownership relationships or sources were created. Manufacturer/distributor wording is a research lead only, not an ownership claim. Nothing has been marked verified.
