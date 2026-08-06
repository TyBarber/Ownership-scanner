import styles from "./Pages.module.css";

export function MethodologyPage() {
  return (
    <div className={`${styles.page} ${styles.prosePage}`}>
      <header className={styles.pageHeader}>
        <p className={styles.kicker}>Methodology</p>
        <h1>How Protest knows what it knows.</h1>
        <p>
          Ownership research is a chain of evidence. We preserve each link,
          its sources, and the limits of what those sources establish.
        </p>
      </header>
      <section>
        <h2>Sources before claims</h2>
        <p>
          Every displayed ownership relationship has at least one supporting
          source. Official company material and government records are marked
          as primary support; reputable reporting may provide secondary
          support. Source links, publishers, and retrieval dates remain visible.
        </p>
      </section>
      <section>
        <h2>Verified is not the same as certain</h2>
        <p>
          Verification status records whether a relationship met the project’s
          evidence standard. Confidence records the strength of that evidence
          on a 0–100% scale and is available in expanded details. Neither is an
          ethical rating.
        </p>
      </section>
      <section>
        <h2>Dates keep their precision</h2>
        <p>
          If evidence establishes only a year, Protest displays only that year.
          Month and day precision appear only when supported. Missing dates stay
          missing rather than being inferred.
        </p>
      </section>
      <section>
        <h2>Research gaps stay visible</h2>
        <p>
          A chain may reach a company or ownership group while its exact parent
          structure remains unresolved. In that case, Protest identifies the
          highest verified point in the research and explains the gap. It does
          not silently present that point as the ultimate owner.
        </p>
      </section>
      <section>
        <h2>What product labels can—and cannot—tell us</h2>
        <p>
          Manufacturer and distributor language printed on packaging is
          preserved as a research lead. Distribution does not automatically
          prove ownership.
        </p>
      </section>
    </div>
  );
}
