import { z } from "zod";
import type {
  HealthResponse,
  ProductListResponse,
  ProductOwnershipResponse,
} from "./types";

const confidenceSchema = z.number().min(0).max(1);
const entityTypeSchema = z.enum(["brand", "company", "ownership_group"]);
const datePrecisionSchema = z.enum(["year", "month", "day"]);
const gtinSchema = z.string().regex(/^(?:\d{8}|\d{12}|\d{13}|\d{14})$/);

const healthSchema: z.ZodType<HealthResponse> = z.object({
  status: z.literal("healthy"),
});

const productBrandSchema = z.object({
  id: z.string(),
  name: z.string(),
});

const productSummarySchema = z.object({
  id: z.string(),
  gtin: gtinSchema,
  name: z.string(),
  category: z.string(),
  brand: productBrandSchema,
});

const productListSchema: z.ZodType<ProductListResponse> = z.object({
  products: z.array(productSummarySchema),
  total: z.number().int().nonnegative(),
  limit: z.number().int().min(1).max(100),
  offset: z.number().int().nonnegative(),
});

const brandReferenceSchema = z.object({
  type: z.literal("brand"),
  id: z.string(),
  name: z.string(),
});

const companyReferenceSchema = z.object({
  type: z.literal("company"),
  id: z.string(),
  name: z.string(),
});

const ownershipGroupReferenceSchema = z.object({
  type: z.literal("ownership_group"),
  id: z.string(),
  name: z.string(),
});

const entityReferenceSchema = z.discriminatedUnion("type", [
  brandReferenceSchema,
  companyReferenceSchema,
  ownershipGroupReferenceSchema,
]);

const parentReferenceSchema = z.discriminatedUnion("type", [
  companyReferenceSchema,
  ownershipGroupReferenceSchema,
]);

const sourceSchema = z.object({
  title: z.string(),
  url: z.string().url(),
  publisher: z.string(),
  source_type: z.string(),
  support_type: z.enum(["primary", "secondary"]),
  published_at: z.string().nullable(),
  retrieved_at: z.string(),
});

const relationshipSchema = z.object({
  child: entityReferenceSchema,
  relationship_type: z.enum([
    "owned_by",
    "controlled_by_group",
    "affiliated_with_group",
  ]),
  parent: parentReferenceSchema,
  verification_status: z.enum(["verified", "probable", "unresolved"]),
  confidence: confidenceSchema,
  effective_from: z.string().nullable(),
  effective_from_precision: datePrecisionSchema.nullable(),
  effective_until: z.string().nullable(),
  last_verified_at: z.string(),
  sources: z.array(sourceSchema),
});

const highestVerifiedOwnerSchema = z.discriminatedUnion("type", [
  brandReferenceSchema,
  companyReferenceSchema.extend({
    company_type: z.enum(["public", "private", "cooperative"]),
    country: z.string(),
  }),
  ownershipGroupReferenceSchema.extend({
    description: z.string(),
    country: z.string(),
  }),
]);

const researchGapSchema = z.object({
  id: z.string(),
  subject: z.object({
    type: entityTypeSchema,
    id: z.string(),
  }),
  issue_type: z.string(),
  status: z.literal("unresolved"),
  confidence: confidenceSchema,
  explanation: z.string(),
  sources: z.array(sourceSchema),
});

const productOwnershipSchema: z.ZodType<ProductOwnershipResponse> = z.object({
  product: z.object({
    id: z.string(),
    gtin: gtinSchema,
    name: z.string(),
    category: z.string(),
    package_company_text: z.string(),
  }),
  brand: z.object({
    id: z.string(),
    name: z.string(),
    website: z.string(),
  }),
  ownership_chain: z.array(relationshipSchema),
  highest_verified_owner: highestVerifiedOwnerSchema,
  chain_complete: z.boolean(),
  overall_status: z.enum([
    "verified",
    "verified_with_gaps",
    "cycle_detected",
  ]),
  stop_reason: z.enum([
    "terminal_owner",
    "research_gap",
    "unresolved_relationship",
    "multiple_verified_parents",
    "cycle_detected",
  ]),
  research_gaps: z.array(researchGapSchema),
});

export const apiSchemas = {
  health: healthSchema,
  productList: productListSchema,
  productOwnership: productOwnershipSchema,
};
