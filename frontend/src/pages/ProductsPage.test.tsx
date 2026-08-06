import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProductsPage } from "./ProductsPage";
import { productList } from "../test/fixtures/products";
import { renderRoute } from "../test/render";

const apiMocks = vi.hoisted(() => ({
  listProducts: vi.fn(),
}));

vi.mock("../api/products", () => ({
  listProducts: apiMocks.listProducts,
}));

describe("ProductsPage", () => {
  beforeEach(() => {
    apiMocks.listProducts.mockResolvedValue(productList);
  });

  it("shows loading then the catalog", async () => {
    renderRoute(<ProductsPage />, "/products", "/products");
    expect(screen.getByText(/loading researched products/i)).toBeInTheDocument();
    expect(await screen.findByText("Spindrift Sparkling Water")).toBeVisible();
  });

  it("searches product and brand names and preserves q in the URL", async () => {
    const user = userEvent.setup();
    const { routing } = renderRoute(
      <ProductsPage />,
      "/products?q=Spindrift",
      "/products",
    );
    expect(await screen.findByText("Spindrift Sparkling Water")).toBeVisible();
    expect(screen.queryByText(/vegetarian chili/i)).not.toBeInTheDocument();

    const input = screen.getByRole("searchbox");
    await user.clear(input);
    await user.type(input, "Trader Joe's");
    await user.click(screen.getByRole("button", { name: "Search" }));
    expect(routing.history.at(-1)).toBe("/products?q=Trader+Joe%27s");
    expect(await screen.findByText(/organic vegetarian chili/i)).toBeVisible();
  });

  it("renders an empty result with a clear action", async () => {
    const user = userEvent.setup();
    renderRoute(
      <ProductsPage />,
      "/products?q=not-present",
      "/products",
    );
    expect(await screen.findByText(/we couldn’t find/i)).toBeVisible();
    await user.click(screen.getByRole("button", { name: /clear search/i }));
    expect(await screen.findByText("Spindrift Sparkling Water")).toBeVisible();
    expect(screen.getByRole("searchbox")).toHaveValue("");
  });

  it("renders API failure and retries", async () => {
    apiMocks.listProducts
      .mockRejectedValueOnce(new Error("network"))
      .mockResolvedValueOnce(productList);
    const user = userEvent.setup();
    renderRoute(<ProductsPage />, "/products", "/products");
    expect(
      await screen.findByText(/something went wrong while loading/i),
    ).toBeVisible();
    await user.click(screen.getByRole("button", { name: /try again/i }));
    await waitFor(() =>
      expect(screen.getByText("Spindrift Sparkling Water")).toBeVisible(),
    );
  });
});
