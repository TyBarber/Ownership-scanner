import type {
  HighestVerifiedOwner,
  OwnershipRelationship,
  ResearchGap,
} from "../../api/types";
import {
  entityTypeLabel,
  formatDate,
  formatEffectiveDate,
  relationshipLabel,
} from "../../utils/format";
import { ResearchGapPanel } from "./ResearchGapPanel";
import { SourceList } from "./SourceList";
import styles from "./Ownership.module.css";

function RelationshipStep({
  relationship,
  index,
}: {
  relationship: OwnershipRelationship;
  index: number;
}) {
  return (
    <article className={styles.step}>
      <div className={styles.stepNumber} aria-hidden="true">
        {String(index + 1).padStart(2, "0")}
      </div>
      <div className={styles.stepBody}>
        <p className={styles.eyebrow}>
          {entityTypeLabel(relationship.child.type)}
        </p>
        <h3>{relationship.child.name}</h3>
        <div className={styles.relationship}>
          <span aria-hidden="true">↓</span>
          <strong>{relationshipLabel(relationship.relationship_type)}</strong>
        </div>
        <div className={styles.parent}>
          <p className={styles.eyebrow}>
            {entityTypeLabel(relationship.parent.type)}
          </p>
          <h3>{relationship.parent.name}</h3>
        </div>
        <div className={styles.verification}>
          <span className={styles.verified}>
            <span aria-hidden="true">●</span> Verified relationship
          </span>
          <span>
            {formatEffectiveDate(
              relationship.effective_from,
              relationship.effective_from_precision,
            )}
          </span>
          <span>Last checked {formatDate(relationship.last_verified_at)}</span>
        </div>
        <details className={styles.details}>
          <summary>Confidence and sources</summary>
          <p>
            Relationship confidence:{" "}
            {Math.round(relationship.confidence * 100)}%
          </p>
          <SourceList sources={relationship.sources} />
        </details>
      </div>
    </article>
  );
}

function ownerTypeLabel(owner: HighestVerifiedOwner): string {
  if (owner.type !== "company") return entityTypeLabel(owner.type);
  return entityTypeLabel(owner.type, owner.company_type);
}

export function OwnershipChain({
  chain,
  gaps,
  highestOwner,
  complete,
}: {
  chain: OwnershipRelationship[];
  gaps: ResearchGap[];
  highestOwner: HighestVerifiedOwner;
  complete: boolean;
}) {
  const renderedGapIds = new Set<string>();

  return (
    <section className={styles.section} aria-labelledby="ownership-heading">
      <div className={styles.sectionHeading}>
        <p className={styles.eyebrow}>Ownership path</p>
        <h2 id="ownership-heading">Who owns this product?</h2>
        <p>
          Each step below is a separately sourced relationship, shown in
          research order.
        </p>
      </div>
      <div className={styles.chain}>
        {chain.map((relationship, index) => {
          const attachedGaps = gaps.filter(
            (gap) =>
              gap.subject.id === relationship.parent.id ||
              gap.subject.id === relationship.child.id,
          );
          attachedGaps.forEach((gap) => renderedGapIds.add(gap.id));
          return (
            <div key={`${relationship.child.id}-${relationship.parent.id}`}>
              <RelationshipStep relationship={relationship} index={index} />
              {attachedGaps.map((gap) => (
                <ResearchGapPanel gap={gap} key={gap.id} />
              ))}
            </div>
          );
        })}
        {gaps
          .filter((gap) => !renderedGapIds.has(gap.id))
          .map((gap) => (
            <ResearchGapPanel gap={gap} key={gap.id} />
          ))}
      </div>
      <aside className={complete ? styles.owner : styles.ownerIncomplete}>
        <p className={styles.eyebrow}>
          {complete
            ? "Highest verified owner"
            : "Highest verified point in our research"}
        </p>
        <h2>{highestOwner.name}</h2>
        <p>
          {ownerTypeLabel(highestOwner)}
          {"country" in highestOwner && highestOwner.country
            ? ` · ${highestOwner.country}`
            : ""}
        </p>
        {!complete && (
          <p>
            The chain stops here because part of the ownership structure
            remains unresolved. This is not presented as the ultimate owner.
          </p>
        )}
        {"description" in highestOwner && highestOwner.description && (
          <p>{highestOwner.description}</p>
        )}
      </aside>
    </section>
  );
}
