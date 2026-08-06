import { publicErrorMessage } from "../../api/errors";
import styles from "./RequestState.module.css";

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className={styles.state} aria-live="polite" role="status">
      <span className={styles.loader} aria-hidden="true" />
      <p>{label}</p>
    </div>
  );
}

export function ErrorState({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry?: () => void;
}) {
  return (
    <section className={`${styles.state} ${styles.error}`} aria-live="assertive">
      <p>{publicErrorMessage(error)}</p>
      {onRetry && (
        <button type="button" onClick={onRetry}>
          Try again
        </button>
      )}
    </section>
  );
}
