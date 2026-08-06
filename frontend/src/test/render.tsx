import type { ReactNode } from "react";
import { render } from "@testing-library/react";
import { Route, Router } from "wouter";
import { memoryLocation } from "wouter/memory-location";

export function renderRoute(
  element: ReactNode,
  initialEntry = "/",
  path = "/",
) {
  const routing = memoryLocation({ path: initialEntry, record: true });
  const result = render(
    <Router hook={routing.hook} searchHook={routing.searchHook}>
      <Route path={path}>{element}</Route>
    </Router>,
  );
  return { ...result, routing };
}
