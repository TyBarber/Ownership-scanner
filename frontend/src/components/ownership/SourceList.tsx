import type { SupportingSource } from "../../api/types";
import { formatDate } from "../../utils/format";
import styles from "./Ownership.module.css";

export function SourceList({ sources }: { sources: SupportingSource[] }) {
  return (
    <div className={styles.sources}>
      <h4>Supporting evidence</h4>
      <ul>
        {sources.map((source) => (
          <li key={`${source.url}-${source.title}`}>
            <a href={source.url} rel="noopener noreferrer" target="_blank">
              {source.title}
              <span className="srOnly"> (opens in a new tab)</span>
            </a>
            <p>
              {source.publisher} ·{" "}
              {source.support_type === "primary"
                ? "Primary source"
                : "Secondary source"}
              {source.published_at
                ? ` · Published ${formatDate(source.published_at)}`
                : ""}
              {" · "}Retrieved {formatDate(source.retrieved_at)}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
