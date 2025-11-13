import type { AITool } from "./toolsTypes";
import { API_BASE } from './api';

let cachedTools: AITool[] = [];

// Helper: try to create a Supabase client dynamically
async function getSupabaseClient() {
  const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
  const key = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
  if (!url || !key) return null;

  try {
    const mod = await import('@supabase/supabase-js');
    const client = mod.createClient(url, key);
    return client;
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn('Supabase client not available; falling back to backend API.', err);
    return null;
  }
}

async function loadTools(): Promise<AITool[]> {
  if (cachedTools.length > 0) return cachedTools;

  const supabase = await getSupabaseClient();
  if (supabase) {
    try {
      const { data, error } = await supabase
        .from('tools')
        .select('*');

      if (error) throw error;

      cachedTools = (data as any[]) || [];
      return cachedTools;
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Failed to load tools from Supabase, falling back to backend API', err);
    }
  }

  // Fetch from backend API
  try {
    const res = await fetch(`${API_BASE}/api/news/tools/`);
    if (!res.ok) throw new Error('API fetch failed: ' + res.status);
    const data = await res.json();
    cachedTools = data as AITool[];
    return cachedTools;
  } catch (err) {
    throw new Error('Failed to load tools from backend API: ' + String(err));
  }
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
