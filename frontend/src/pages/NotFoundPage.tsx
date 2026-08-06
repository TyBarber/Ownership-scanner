import { Link } from "wouter";
import styles from "./Pages.module.css";

export function NotFoundPage() {
  return (
    <div className={styles.page}>
      <section className={styles.emptyState}>
        <p className={styles.kicker}>404 · Page not found</p>
        <h1>This trail ends here.</h1>
        <p>The page may have moved, but the product catalog is still here.</p>
        <Link className={styles.primaryAction} to="/">
          Return home
        </Link>
      </section>
    </div>
  );
}
