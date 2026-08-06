import { Link, useParams } from "wouter";
import { ApiError } from "../api/errors";
import { ErrorState, LoadingState } from "../components/feedback/RequestState";
import { OwnershipChain } from "../components/ownership/OwnershipChain";
import { useProductOwnership } from "../hooks/useProductOwnership";
import styles from "./Pages.module.css";

export function ProductPage() {
  const { gtin = "" } = useParams<{ gtin?: string }>();
  const { data, error, loading, retry } = useProductOwnership(gtin);

  if (loading) {
    return (
      <div className={styles.page}>
        <LoadingState label="Tracing product ownership…" />
      </div>
    );
  }

  if (error instanceof ApiError && error.kind === "not-researched") {
    return (
      <div className={styles.page}>
        <section className={styles.emptyState}>
          <p className={styles.kicker}>Not yet researched</p>
          <h1>This barcode isn’t in Protest yet.</h1>
          <p>
            The barcode is valid, but it is not part of our current 13-product
            development catalog.
          </p>
          <Link className={styles.primaryAction} to="/products">
            Browse researched products
          </Link>
        </section>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.page}>
        <h1 className="srOnly">Product lookup error</h1>
        <ErrorState error={error} onRetry={retry} />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className={styles.page}>
      <Link className={styles.backLink} to="/products">
        <span aria-hidden="true">←</span> All products
      </Link>
      <header className={styles.productHeader}>
        <div>
          <p className={styles.kicker}>{data.product.category}</p>
          <h1>{data.product.name}</h1>
          <p className={styles.brandLine}>
            Brand:{" "}
            {data.brand.website ? (
              <a
                href={data.brand.website}
                rel="noopener noreferrer"
                target="_blank"
              >
                {data.brand.name}
                <span className="srOnly"> (opens in a new tab)</span>
              </a>
            ) : (
              data.brand.name
            )}
          </p>
        </div>
        <dl className={styles.productFacts}>
          <div>
            <dt>GTIN</dt>
            <dd>{data.product.gtin}</dd>
          </div>
          <div>
            <dt>Research status</dt>
            <dd>
              {data.chain_complete
                ? "Verified chain"
                : "Verified with research gaps"}
            </dd>
          </div>
        </dl>
      </header>
      {data.product.package_company_text && (
        <aside className={styles.packageNote}>
          <p className={styles.kicker}>Printed on package</p>
          <p>“{data.product.package_company_text}”</p>
          <small>
            Package wording is a research lead, not proof of ownership.
          </small>
        </aside>
      )}
      <OwnershipChain
        chain={data.ownership_chain}
        complete={data.chain_complete}
        gaps={data.research_gaps}
        highestOwner={data.highest_verified_owner}
      />
    </div>
  );
}
