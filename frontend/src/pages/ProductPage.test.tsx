import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "../api/errors";
import { completeOwnership, traderJoesOwnership } from "../test/fixtures/products";
import { renderRoute } from "../test/render";
import { ProductPage } from "./ProductPage";

const apiMocks = vi.hoisted(() => ({
  getProductOwnership: vi.fn(),
}));

vi.mock("../api/products", () => ({
  getProductOwnership: apiMocks.getProductOwnership,
}));

describe("ProductPage", () => {
  beforeEach(() => {
    apiMocks.getProductOwnership.mockResolvedValue(completeOwnership);
  });

  it("shows loading then a complete ownership result", async () => {
    renderRoute(
      <ProductPage />,
      "/products/850017142350",
      "/products/:gtin",
    );
    expect(screen.getByText(/tracing product ownership/i)).toBeVisible();
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Spindrift Sparkling Water",
      }),
    ).toBeVisible();
    expect(screen.getByText("Highest verified owner")).toBeVisible();
  });

  it("renders Trader Joe's gap beside the affected point", async () => {
    apiMocks.getProductOwnership.mockResolvedValue(traderJoesOwnership);
    renderRoute(<ProductPage />, "/products/00712996", "/products/:gtin");
    expect(
      await screen.findByText(/exact legal parent and foundation/i),
    ).toBeVisible();
    expect(
      screen.getByText("Highest verified point in our research"),
    ).toBeVisible();
  });

  it("renders a distinct not-researched 404 state", async () => {
    apiMocks.getProductOwnership.mockRejectedValue(
      new ApiError("not-researched", "Product not found", 404),
    );
    renderRoute(<ProductPage />, "/products/00000000", "/products/:gtin");
    expect(await screen.findByText(/isn’t in Protest yet/i)).toBeVisible();
    expect(screen.getByText(/not part of our current 13-product/i)).toBeVisible();
  });

  it.each([
    ["network", "could not reach the ownership service"],
    ["server", "temporarily unavailable"],
    ["invalid-response", "could not safely display"],
  ] as const)("renders a public %s failure state", async (kind, message) => {
    apiMocks.getProductOwnership.mockRejectedValue(new ApiError(kind, "private"));
    renderRoute(
      <ProductPage />,
      "/products/850017142350",
      "/products/:gtin",
    );
    expect(await screen.findByText(new RegExp(message, "i"))).toBeVisible();
  });

  it("allows retry after an error", async () => {
    apiMocks.getProductOwnership
      .mockRejectedValueOnce(new ApiError("server", "private"))
      .mockResolvedValueOnce(completeOwnership);
    const user = userEvent.setup();
    renderRoute(
      <ProductPage />,
      "/products/850017142350",
      "/products/:gtin",
    );
    await user.click(
      await screen.findByRole("button", { name: /try again/i }),
    );
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Spindrift Sparkling Water",
      }),
    ).toBeVisible();
  });
});
