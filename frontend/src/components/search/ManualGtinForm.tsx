import { FormEvent, useId, useState } from "react";
import { useLocation } from "wouter";
import { normalizeGtin, validateGtin } from "../../utils/gtin";
import styles from "./Search.module.css";

export function ManualGtinForm() {
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const inputId = useId();
  const errorId = `${inputId}-error`;
  const [, navigate] = useLocation();

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalized = normalizeGtin(value);
    const validationError = validateGtin(normalized);
    setError(validationError);
    if (!validationError) navigate(`/products/${normalized}`);
  }

  return (
    <form className={styles.manualForm} onSubmit={submit} noValidate>
      <div>
        <label htmlFor={inputId}>Enter a product barcode</label>
        <p id={`${inputId}-hint`}>
          Use the 8, 12, 13, or 14 digits printed beneath the barcode.
        </p>
      </div>
      <div className={styles.inputRow}>
        <input
          id={inputId}
          aria-describedby={`${inputId}-hint${error ? ` ${errorId}` : ""}`}
          aria-invalid={Boolean(error)}
          autoComplete="off"
          inputMode="numeric"
          name="gtin"
          onChange={(event) => {
            setValue(event.target.value);
            if (error) setError(null);
          }}
          placeholder="00016000124790"
          type="text"
          value={value}
        />
        <button type="submit">Look it up</button>
      </div>
      {error && (
        <p className={styles.error} id={errorId} role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
