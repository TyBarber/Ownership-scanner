import { Link } from "wouter";
import styles from "./Pages.module.css";

export function AboutPage() {
  return (
    <div className={`${styles.page} ${styles.prosePage}`}>
      <header className={styles.pageHeader}>
        <p className={styles.kicker}>About Protest</p>
        <h1>Product labels show a brand. Protest traces what sits behind it.</h1>
        <p>
          Protest is a consumer-transparency project for understanding
          product-to-company ownership through sourced, inspectable research.
        </p>
      </header>
      <section>
        <h2>A small, deliberate start</h2>
        <p>
          The current development dataset contains 13 manually researched
          products. It is a feasibility catalog, not a complete representation
          of the marketplace.
        </p>
      </section>
      <section>
        <h2>Current limitations</h2>
        <ul>
          <li>Most products have not been researched yet.</li>
          <li>Some ownership structures contain explicit research gaps.</li>
          <li>Camera barcode scanning is not implemented in this milestone.</li>
          <li>CSV research updates require rebuilding the API package.</li>
          <li>There are no accounts, ratings, or purchasing recommendations.</li>
        </ul>
      </section>
      <section>
        <h2>What Protest does not do</h2>
        <p>
          Protest does not score companies, generate ownership claims with AI,
          recommend boycotts, or tell consumers what to buy. It presents
          ownership research and its evidence so people can inspect it.
        </p>
      </section>
      <Link className={styles.primaryAction} to="/products">
        Explore the current catalog
      </Link>
    </div>
  );
}
