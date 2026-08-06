import { Link } from "wouter";
import type { ProductSummary } from "../../api/types";
import styles from "./ProductCard.module.css";

export function ProductCard({ product }: { product: ProductSummary }) {
  return (
    <article className={styles.card}>
      <div className={styles.meta}>
        <span>{product.category}</span>
        <span>{product.gtin}</span>
      </div>
      <h2>
        <Link to={`/products/${product.gtin}`}>{product.name}</Link>
      </h2>
      <p>{product.brand.name}</p>
      <Link className={styles.action} to={`/products/${product.gtin}`}>
        View ownership <span aria-hidden="true">→</span>
      </Link>
    </article>
  );
}
