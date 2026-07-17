# Manual Research Guide

## What to collect

For each of at least 10 US packaged grocery or household products:

1. Select the physical product.
2. Record the barcode digits exactly, including leading zeros. Do not let spreadsheet software convert the value to a number.
3. Record the full product name, brand, category, and the manufacturer/distributor text printed on the package.
4. Optionally record a stable HTTPS image URL. Do not substitute an image for the printed text.
5. Research who owns the brand and then who owns each company in the chain.

Aim for at least five brands and at least three distinct highest verified ownership entities across the 10 products.

## Source priority

Use the strongest available evidence in this order:

1. Official company or brand page
2. Official acquisition announcement
3. SEC filing or government record
4. Reputable business publication

For every ownership edge, capture the source title, HTTPS URL, publisher, source type, publication date when available, retrieval date, and useful notes.

Never use an AI answer, unsourced list, random blog, or social-media post as the sole evidence.

## Entering ownership

- Enter every ownership step separately. For example: brand → operating company → subsidiary → public parent.
- Do not skip an intermediate company merely because a higher ownership entity is well known.
- Use effective start and end dates when evidence supports them. This preserves ownership history after a sale.
- Mark strong, directly supported edges `verified`.
- Mark a well-supported inference that is not directly confirmed `probable`.
- Mark conflicting or insufficient evidence `unresolved`; never silently turn uncertainty into fact.
- Give confidence as a decimal from `0` through `1`, consistent with the evidence and status.
- Record `last_verified_at` as the date you last checked the evidence.

## Before handing off the data

Confirm that you have provided:

- 10 or more real product names and exact GTINs
- Each product's brand and category
- Exact manufacturer/distributor package text
- Brand websites when available
- Legal/display names, countries, types, websites, and SEC CIKs when applicable for every company
- Every brand-to-company and company-to-company edge, without skipped subsidiaries
- Effective dates when known
- One credible source record for every ownership edge
- A verification status, confidence, and last-verified date for every edge
- Notes identifying conflicts or missing evidence

Then run `python3 scripts/validate_data.py`. Research is ready for review only when the feasibility gate passes.
