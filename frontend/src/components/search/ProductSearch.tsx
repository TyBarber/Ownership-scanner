import { FormEvent, useId, useState } from "react";
import { useLocation } from "wouter";
import styles from "./Search.module.css";

type ProductSearchProps = {
  initialValue?: string;
  onSearch?: (value: string) => void;
};

export function ProductSearch({
  initialValue = "",
  onSearch,
}: ProductSearchProps) {
  const [value, setValue] = useState(initialValue);
  const inputId = useId();
  const [, navigate] = useLocation();

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = value.trim();
    if (onSearch) {
      onSearch(query);
    } else {
      navigate(query ? `/products?q=${encodeURIComponent(query)}` : "/products");
    }
  }

  return (
    <form className={styles.searchForm} role="search" onSubmit={submit}>
      <label htmlFor={inputId}>Search products or brands</label>
      <div className={styles.inputRow}>
        <input
          id={inputId}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Try Cheerios or Gerber"
          type="search"
          value={value}
        />
        <button type="submit">Search</button>
      </div>
    </form>
  );
}
