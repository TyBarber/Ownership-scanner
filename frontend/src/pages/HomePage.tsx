import { Link } from "wouter";
import { ManualGtinForm } from "../components/search/ManualGtinForm";
import { ProductSearch } from "../components/search/ProductSearch";
import styles from "./Pages.module.css";

export function HomePage() {
  return (
    <>
      <section className={styles.hero}>
        <div className={styles.heroInner}>
          <p className={styles.kicker}>Product Ownership Intelligence</p>
          <h1>
            Know Who
            <br />
            <em>Profits.</em>
          </h1>
          <p className={styles.heroCopy}>
            Protest traces familiar products through brands, companies,
            cooperatives, and ownership groups—then shows you the evidence and
            the gaps.
          </p>
          <div className={styles.heroActions}>
            <Link className={styles.primaryAction} to="/products">
              Browse 13 researched products
            </Link>
            <Link className={styles.textAction} to="/methodology">
              How the research works
            </Link>
          </div>
        </div>
        <aside className={styles.heroNote}>
          <span>01</span>
          <p>
            Ownership is complex. We separate what is verified from what
            remains unresolved.
          </p>
        </aside>
      </section>

      <section className={styles.lookupSection} aria-labelledby="lookup-heading">
        <div className={styles.sectionIntro}>
          <p className={styles.kicker}>Start with a product</p>
          <h2 id="lookup-heading">Look beneath the label.</h2>
        </div>
        <div className={styles.lookupGrid}>
          <div className={styles.toolCard}>
            <span className={styles.toolNumber}>A</span>
            <ProductSearch />
          </div>
          <div className={styles.toolCard}>
            <span className={styles.toolNumber}>B</span>
            <ManualGtinForm />
          </div>
          <div className={`${styles.toolCard} ${styles.comingSoon}`}>
            <span className={styles.toolNumber}>C</span>
            <p className={styles.kicker}>Camera scanner</p>
            <h3>Point. Scan. Understand.</h3>
            <p>
              Camera barcode scanning is coming in the next milestone. No
              camera access is requested yet.
            </p>
          </div>
        </div>
      </section>

      <section className={styles.principles} aria-labelledby="principles-heading">
        <div>
          <p className={styles.kicker}>Built for clarity</p>
          <h2 id="principles-heading">Evidence, not verdicts.</h2>
        </div>
        <ol>
          <li>
            <strong>Trace</strong>
            <span>Follow each verified ownership relationship in order.</span>
          </li>
          <li>
            <strong>Inspect</strong>
            <span>Open the sources behind every relationship.</span>
          </li>
          <li>
            <strong>Question</strong>
            <span>See unresolved research gaps instead of hidden certainty.</span>
          </li>
        </ol>
      </section>
    </>
  );
}
