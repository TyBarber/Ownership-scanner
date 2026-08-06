import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ManualGtinForm } from "./ManualGtinForm";
import { renderRoute } from "../../test/render";

describe("ManualGtinForm", () => {
  it("preserves a leading-zero GTIN when navigating", async () => {
    const user = userEvent.setup();
    const { routing } = renderRoute(<ManualGtinForm />);
    await user.type(
      screen.getByLabelText(/enter a product barcode/i),
      "00016000124790",
    );
    await user.click(screen.getByRole("button", { name: /look it up/i }));
    expect(routing.history.at(-1)).toBe("/products/00016000124790");
  });

  it("shows an accessible inline validation error", async () => {
    const user = userEvent.setup();
    const { routing } = renderRoute(<ManualGtinForm />);
    const input = screen.getByLabelText(/enter a product barcode/i);
    await user.type(input, "123");
    await user.click(screen.getByRole("button", { name: /look it up/i }));
    expect(screen.getByRole("alert")).toHaveTextContent(/8-, 12-, 13-/);
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(routing.history).toEqual(["/"]);
  });
});
