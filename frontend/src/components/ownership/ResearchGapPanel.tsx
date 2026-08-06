import type { ResearchGap } from "../../api/types";
import { SourceList } from "./SourceList";
import styles from "./Ownership.module.css";

export function ResearchGapPanel({ gap }: { gap: ResearchGap }) {
  return (
    <aside className={styles.gap} aria-labelledby={`${gap.id}-title`}>
      <p className={styles.eyebrow}>Unresolved research gap</p>
      <h3 id={`${gap.id}-title`}>What we could not verify</h3>
      <p>{gap.explanation}</p>
      <details>
        <summary>Evidence reviewed and confidence</summary>
        <p>
          Research confidence: {Math.round(gap.confidence * 100)}%. This marks
          an unresolved question, not a verified ownership claim.
        </p>
        <SourceList sources={gap.sources} />
      </details>
    </aside>
  );
}
