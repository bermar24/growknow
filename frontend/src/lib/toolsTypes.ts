export interface AITool {
  id: string;
  name: string;
  description: string;
  url: string;
  logo?: string;
  category: string;
  subcategories: string[];
  pricing: "Free" | "Freemium" | "Trial" | "Paid";
  priceFrom?: number;
  rating?: number;
  tags: string[];
}

export const TOOL_CATEGORIES = [
  "Misc. AI Tools",
  "AI Art Generators",
  "AI Text Generators",
  "AI Resources",
  "AI Image Generators",
  "AI For Business",
  "AI Audio Generators",
  "AI Automation Tools",
  "AI Developer Tools",
  "AI Video Tools",
  "AI Productivity Tools",
] as const;

export const PRICING_OPTIONS = ["Free", "Freemium", "Trial", "Paid"] as const;
