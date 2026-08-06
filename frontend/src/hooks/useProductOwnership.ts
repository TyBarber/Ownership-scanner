import { useCallback, useEffect, useState } from "react";
import { getProductOwnership } from "../api/products";
import type { ProductOwnershipResponse } from "../api/types";

export function useProductOwnership(gtin: string) {
  const [data, setData] = useState<ProductOwnershipResponse | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setError(null);
    setLoading(true);
    getProductOwnership(gtin, controller.signal)
      .then(setData)
      .catch((requestError: unknown) => {
        if (!controller.signal.aborted) setError(requestError);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [attempt, gtin]);

  const retry = useCallback(() => setAttempt((value) => value + 1), []);
  return { data, error, loading, retry };
}
