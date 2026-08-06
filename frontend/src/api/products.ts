import { requestJson } from "./client";
import { apiSchemas } from "./schemas";
import type { ProductListResponse, ProductOwnershipResponse } from "./types";

export function listProducts(signal?: AbortSignal): Promise<ProductListResponse> {
  return requestJson("/products", apiSchemas.productList, { signal });
}

export function getProductOwnership(
  gtin: string,
  signal?: AbortSignal,
): Promise<ProductOwnershipResponse> {
  return requestJson(
    `/products/${encodeURIComponent(gtin)}`,
    apiSchemas.productOwnership,
    { signal },
  );
}
