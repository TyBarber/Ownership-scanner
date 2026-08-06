import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import {
  completeOwnership,
  cooperativeOwnership,
  traderJoesOwnership,
} from "../../test/fixtures/products";
import { OwnershipChain } from "./OwnershipChain";

function renderOwnership(
  data:
    | typeof completeOwnership
    | typeof traderJoesOwnership
    | typeof cooperativeOwnership,
) {
  return render(
    <OwnershipChain
      chain={data.ownership_chain}
      complete={data.chain_complete}
      gaps={data.research_gaps}
      highestOwner={data.highest_verified_owner}
    />,
  );
}

describe("OwnershipChain", () => {
  it("renders a complete chain, sources, confidence, and partial dates", async () => {
    const user = userEvent.setup();
    renderOwnership(completeOwnership);
    expect(screen.getByText("Highest verified owner")).toBeVisible();
    expect(screen.getByText("Since March 2024")).toBeVisible();
    await user.click(screen.getByText("Confidence and sources"));
    expect(screen.getByText(/relationship confidence: 95%/i)).toBeVisible();
    const source = screen.getByRole("link", {
      name: /spindrift privacy notice/i,
    });
    expect(source).toHaveAttribute("target", "_blank");
    expect(source).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("keeps the Trader Joe's research gap prominent and qualified", () => {
    renderOwnership(traderJoesOwnership);
    expect(screen.getByText("Unresolved research gap")).toBeVisible();
    expect(
      screen.getByText(/exact legal parent and foundation/i),
    ).toBeVisible();
    expect(
      screen.getByText("Highest verified point in our research"),
    ).toBeVisible();
    expect(screen.getByText(/not presented as the ultimate owner/i)).toBeVisible();
    expect(screen.getByText("Since 1979")).toBeVisible();
  });

  it("distinguishes cooperatives and ownership groups", () => {
    const { rerender } = renderOwnership(cooperativeOwnership);
    expect(screen.getByText(/cooperative · US/i)).toBeVisible();
    rerender(
      <OwnershipChain
        chain={traderJoesOwnership.ownership_chain}
        complete={false}
        gaps={traderJoesOwnership.research_gaps}
        highestOwner={traderJoesOwnership.highest_verified_owner}
      />,
    );
    expect(screen.getByText(/ownership group · DE/i)).toBeVisible();
  });
});
