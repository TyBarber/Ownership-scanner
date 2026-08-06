import type {
  ProductListResponse,
  ProductOwnershipResponse,
} from "../../api/types";

export const productList: ProductListResponse = {
  products: [
    {
      id: "product-spindrift",
      gtin: "850017142350",
      name: "Spindrift Sparkling Water",
      category: "Soft Drink",
      brand: { id: "brand-spindrift", name: "Spindrift" },
    },
    {
      id: "product-trader-joes",
      gtin: "00712996",
      name: "Trader Joe's Organic Vegetarian Chili",
      category: "Canned Goods",
      brand: { id: "brand-trader-joes", name: "Trader Joe's" },
    },
    {
      id: "product-wakefern",
      gtin: "041190055661",
      name: "Light Red Kidney Beans",
      category: "Canned Goods",
      brand: { id: "brand-wholesome", name: "Wholesome Pantry Organic" },
    },
  ],
  total: 3,
  limit: 100,
  offset: 0,
};

export const completeOwnership: ProductOwnershipResponse = {
  product: {
    id: "product-spindrift",
    gtin: "850017142350",
    name: "Spindrift Sparkling Water",
    category: "Soft Drink",
    package_company_text: "Distributed by Spindrift Sparkling Water Co.",
  },
  brand: {
    id: "brand-spindrift",
    name: "Spindrift",
    website: "https://drinkspindrift.com",
  },
  ownership_chain: [
    {
      child: { type: "brand", id: "brand-spindrift", name: "Spindrift" },
      relationship_type: "owned_by",
      parent: {
        type: "company",
        id: "company-spindrift",
        name: "Spindrift Beverage Co.",
      },
      verification_status: "verified",
      confidence: 0.95,
      effective_from: "2024-03",
      effective_from_precision: "month",
      effective_until: null,
      last_verified_at: "2026-07-20",
      sources: [
        {
          title: "Spindrift Privacy Notice",
          url: "https://drinkspindrift.com/pages/privacy-notice",
          publisher: "Spindrift",
          source_type: "official_company_page",
          support_type: "primary",
          published_at: "2025-05-01",
          retrieved_at: "2026-07-20",
        },
      ],
    },
  ],
  highest_verified_owner: {
    type: "company",
    id: "company-spindrift",
    name: "Spindrift Beverage Co.",
    company_type: "private",
    country: "US",
  },
  chain_complete: true,
  overall_status: "verified",
  stop_reason: "terminal_owner",
  research_gaps: [],
};

export const traderJoesOwnership: ProductOwnershipResponse = {
  product: {
    id: "product-trader-joes",
    gtin: "00712996",
    name: "Trader Joe's Organic Vegetarian Chili",
    category: "Canned Goods",
    package_company_text: "Distributed and sold exclusively by Trader Joe's",
  },
  brand: {
    id: "brand-trader-joes",
    name: "Trader Joe's",
    website: "https://traderjoes.com",
  },
  ownership_chain: [
    {
      child: {
        type: "brand",
        id: "brand-trader-joes",
        name: "Trader Joe's",
      },
      relationship_type: "owned_by",
      parent: {
        type: "company",
        id: "company-trader-joes",
        name: "Trader Joe's Company",
      },
      verification_status: "verified",
      confidence: 0.95,
      effective_from: null,
      effective_from_precision: null,
      effective_until: null,
      last_verified_at: "2026-07-17",
      sources: [],
    },
    {
      child: {
        type: "company",
        id: "company-trader-joes",
        name: "Trader Joe's Company",
      },
      relationship_type: "controlled_by_group",
      parent: {
        type: "ownership_group",
        id: "ownership-group-aldi-nord",
        name: "ALDI Nord ownership group",
      },
      verification_status: "verified",
      confidence: 0.85,
      effective_from: "1979",
      effective_from_precision: "year",
      effective_until: null,
      last_verified_at: "2026-07-17",
      sources: [],
    },
  ],
  highest_verified_owner: {
    type: "ownership_group",
    id: "ownership-group-aldi-nord",
    name: "ALDI Nord ownership group",
    description:
      "A documented ownership group, not asserted to be the exact legal parent.",
    country: "DE",
  },
  chain_complete: false,
  overall_status: "verified_with_gaps",
  stop_reason: "research_gap",
  research_gaps: [
    {
      id: "gap-aldi",
      subject: {
        type: "ownership_group",
        id: "ownership-group-aldi-nord",
      },
      issue_type: "unresolved_parent_structure",
      status: "unresolved",
      confidence: 0.4,
      explanation:
        "Exact legal parent and foundation/controller structure could not be independently verified.",
      sources: [],
    },
  ],
};

export const cooperativeOwnership: ProductOwnershipResponse = {
  ...completeOwnership,
  product: {
    ...completeOwnership.product,
    id: "product-wakefern",
    gtin: "041190055661",
    name: "Light Red Kidney Beans",
  },
  highest_verified_owner: {
    type: "company",
    id: "company-wakefern",
    name: "Wakefern Food Corp.",
    company_type: "cooperative",
    country: "US",
  },
};
