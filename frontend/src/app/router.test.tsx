import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Router } from "wouter";
import { memoryLocation } from "wouter/memory-location";
import { completeOwnership, productList } from "../test/fixtures/products";
import { AppRouter } from "./router";

const apiMocks = vi.hoisted(() => ({
  listProducts: vi.fn(),
  getProductOwnership: vi.fn(),
}));

vi.mock("../api/products", () => ({
  listProducts: apiMocks.listProducts,
  getProductOwnership: apiMocks.getProductOwnership,
}));

function renderPath(path: string) {
  const routing = memoryLocation({ path, record: true });
  const result = render(
    <Router hook={routing.hook} searchHook={routing.searchHook}>
      <AppRouter />
    </Router>,
  );
  return { ...result, routing };
}

describe("application routing", () => {
  beforeEach(() => {
    apiMocks.listProducts.mockResolvedValue(productList);
    apiMocks.getProductOwnership.mockResolvedValue(completeOwnership);
  });

  it.each([
    ["/", "Know Who Profits."],
    ["/products", "Products we’ve traced."],
    ["/methodology", "How Protest knows what it knows."],
    [
      "/about",
      "Product labels show a brand. Protest traces what sits behind it.",
    ],
  ])("renders the required route %s", async (path, heading) => {
    renderPath(path);
    expect(
      await screen.findByRole("heading", { level: 1, name: heading }),
    ).toBeVisible();
  });

  it("extracts a validated GTIN from the dynamic product route", async () => {
    renderPath("/products/850017142350");
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Spindrift Sparkling Water",
      }),
    ).toBeVisible();
    expect(apiMocks.getProductOwnership).toHaveBeenCalledWith(
      "850017142350",
      expect.any(AbortSignal),
    );
  });

  it("renders the catch-all page for an unknown route", () => {
    renderPath("/not-a-real-route");
    expect(
      screen.getByRole("heading", { level: 1, name: "This trail ends here." }),
    ).toBeVisible();
  });

  it("keeps query strings during catalog navigation", async () => {
    const { routing } = renderPath("/products?q=Spindrift");
    expect(await screen.findByText("Spindrift Sparkling Water")).toBeVisible();
    expect(routing.history).toEqual(["/products?q=Spindrift"]);
  });

  it("builds catalog destinations only from digit-only GTINs", async () => {
    renderPath("/products");
    expect(await screen.findByText("Spindrift Sparkling Water")).toBeVisible();
    const ownershipLinks = screen.getAllByRole("link", {
      name: "View ownership",
    });
    expect(ownershipLinks).toHaveLength(productList.products.length);
    for (const link of ownershipLinks) {
      expect(link.getAttribute("href")).toMatch(
        /^\/products\/(?:\d{8}|\d{12}|\d{13}|\d{14})$/,
      );
    }
  });

  it("marks catalog navigation active on product detail routes", async () => {
    renderPath("/products/850017142350");
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Spindrift Sparkling Water",
      }),
    ).toBeVisible();
    expect(screen.getByRole("link", { name: "Products" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it("supports browser back and forward navigation", async () => {
    window.history.replaceState({}, "", "/");
    const user = userEvent.setup();
    render(<AppRouter />);

    await user.click(
      screen.getByRole("link", { name: "Browse 13 researched products" }),
    );
    expect(window.location.pathname).toBe("/products");
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Products we’ve traced.",
      }),
    ).toBeVisible();

    act(() => window.history.back());
    await waitFor(() => expect(window.location.pathname).toBe("/"));
    expect(
      screen.getByRole("heading", { level: 1, name: "Know Who Profits." }),
    ).toBeVisible();

    act(() => window.history.forward());
    await waitFor(() => expect(window.location.pathname).toBe("/products"));
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "Products we’ve traced.",
      }),
    ).toBeVisible();
  });
});
