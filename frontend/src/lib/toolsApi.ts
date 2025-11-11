import type { AITool } from "./toolsTypes";

let cachedTools: AITool[] = [];

async function loadTools(): Promise<AITool[]> {
  if (cachedTools.length > 0) return cachedTools;

  const response = await fetch("/data/tools.json");
  if (!response.ok) throw new Error("Failed to load tools");

  cachedTools = await response.json();
  return cachedTools;
}

export interface ToolsFilterParams {
  search?: string;
  category?: string;
  subcategory?: string;
  pricing?: string[];
  page?: number;
}

export async function listTools(params: ToolsFilterParams): Promise<{
  tools: AITool[];
  total: number;
  page: number;
  pageSize: number;
}> {
  const tools = await loadTools();
  let filtered = [...tools];

  // Search
  if (params.search?.trim()) {
    const query = params.search.toLowerCase();
    filtered = filtered.filter(
      (t) =>
        t.name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.tags.some((tag) => tag.toLowerCase().includes(query))
    );
  }

  // Category
  if (params.category) {
    filtered = filtered.filter((t) => t.category === params.category);
  }

  // Subcategory
  if (params.subcategory) {
    filtered = filtered.filter((t) =>
      t.subcategories.includes(params.subcategory!)
    );
  }

  // Pricing
  if (params.pricing?.length) {
    filtered = filtered.filter((t) => params.pricing!.includes(t.pricing));
  }

  // Pagination
  const pageSize = 12;
  const page = params.page || 1;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;

  return {
    tools: filtered.slice(start, end),
    total: filtered.length,
    page,
    pageSize,
  };
}
