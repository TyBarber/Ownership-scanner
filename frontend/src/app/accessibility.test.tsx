import { render, screen } from "@testing-library/react";
import { axe } from "vitest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Router } from "wouter";
import { memoryLocation } from "wouter/memory-location";
import { AppRouter } from "./router";
import { completeOwnership, productList } from "../test/fixtures/products";

const apiMocks = vi.hoisted(() => ({
  listProducts: vi.fn(),
  getProductOwnership: vi.fn(),
}));

vi.mock("../api/products", () => ({
  listProducts: apiMocks.listProducts,
  getProductOwnership: apiMocks.getProductOwnership,
}));

function renderApp(initialEntry: string) {
  const routing = memoryLocation({ path: initialEntry });
  return render(
    <Router hook={routing.hook} searchHook={routing.searchHook}>
      <AppRouter />
    </Router>,
  );
}

describe("core page accessibility", () => {
  beforeEach(() => {
    apiMocks.listProducts.mockResolvedValue(productList);
    apiMocks.getProductOwnership.mockResolvedValue(completeOwnership);
  });

  it.each([
    ["/", /know who profits/i],
    ["/methodology", /how protest knows/i],
  ])("has no automated axe violations at %s", async (path, heading) => {
    const { container } = renderApp(path);
    expect(
      await screen.findByRole("heading", { level: 1, name: heading }),
    ).toBeVisible();
    expect((await axe(container)).violations).toEqual([]);
  });

  it("has accessible navigation and catalog landmarks", async () => {
    const { container } = renderApp("/products");
    expect(
      screen.getByRole("link", { name: /skip to main content/i }),
    ).toHaveAttribute("href", "#main-content");
    expect(screen.getByRole("navigation", { name: /primary/i })).toBeVisible();
    expect(await screen.findByText("Spindrift Sparkling Water")).toBeVisible();
    expect((await axe(container)).violations).toEqual([]);
  });

  it("has no automated axe violations on a product result", async () => {
    const { container } = renderApp("/products/850017142350");
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Spindrift Sparkling Water",
      }),
    ).toBeVisible();
    expect((await axe(container)).violations).toEqual([]);
  });
});
