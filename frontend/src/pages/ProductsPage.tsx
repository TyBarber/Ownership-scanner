import { useMemo } from "react";
import { useSearchParams } from "wouter";
import { ErrorState, LoadingState } from "../components/feedback/RequestState";
import { ProductCard } from "../components/products/ProductCard";
import { ProductSearch } from "../components/search/ProductSearch";
import { useProducts } from "../hooks/useProducts";
import styles from "./Pages.module.css";

export function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get("q") ?? "";
  const { data, error, loading, retry } = useProducts();
  const products = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    if (!data || !normalized) return data?.products ?? [];
    return data.products.filter(
      (product) =>
        product.name.toLocaleLowerCase().includes(normalized) ||
        product.brand.name.toLocaleLowerCase().includes(normalized),
    );
  }, [data, query]);

  function search(value: string) {
    setSearchParams(value ? { q: value } : {});
  }

  return (
    <div className={styles.page}>
      <header className={styles.pageHeader}>
        <p className={styles.kicker}>Research catalog</p>
        <h1>Products we’ve traced.</h1>
        <p>
          Search the current development catalog by product or brand. Every
          result is linked to a sourced ownership record.
        </p>
      </header>
      <div className={styles.catalogSearch}>
        <ProductSearch key={query} initialValue={query} onSearch={search} />
      </div>

      {loading && <LoadingState label="Loading researched products…" />}
      {error != null && <ErrorState error={error} onRetry={retry} />}
      {data && !loading && !error && (
        <>
          <div className={styles.resultsMeta} aria-live="polite">
            <strong>{products.length}</strong>{" "}
            {products.length === 1 ? "product" : "products"}
            {query ? ` matching “${query}”` : " researched"}
          </div>
          {products.length ? (
            <div className={styles.productGrid}>
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <section className={styles.emptyState}>
              <p className={styles.kicker}>No matches</p>
              <h2>We couldn’t find that product or brand.</h2>
              <p>Try a shorter search, or clear it to browse all 13 products.</p>
              <button type="button" onClick={() => search("")}>
                Clear search
              </button>
            </section>
          )}
        </>
      )}
    </div>
  );
}
