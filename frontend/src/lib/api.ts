const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchArticles() {
    const res = await fetch(`${API_BASE}/api/articles/`);
    if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
    }
    return res.json();
}


import type { Article, FilterParams } from "./types";

let cachedArticles: Article[] = [];

// Helper: try to create a Supabase client dynamically (so the project won't fail to build if
// `@supabase/supabase-js` is not installed). Returns `null` when not configured/available.
async function getSupabaseClient() {
  const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
  const key = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
  if (!url || !key) return null;

  try {
    const mod = await import('@supabase/supabase-js');
    const client = mod.createClient(url, key);
    return client;
  } catch (err) {
    // If the package isn't installed, warn and fall back to local JSON.
    // eslint-disable-next-line no-console
    console.warn('Supabase client not available; falling back to local JSON.', err);
    return null;
  }
}

async function loadArticles(): Promise<Article[]> {
  if (cachedArticles.length > 0) return cachedArticles;

  // If Supabase is configured, try to load from the `articles` table first.
  const supabase = await getSupabaseClient();
  if (supabase) {
    try {
      const { data, error } = await supabase
        .from('articles')
        .select('*');

      if (error) throw error;

      // Map the returned data to the Article[] shape if necessary. Assume DB columns
      // match the frontend `Article` type keys (title, summary, publishedAt, etc.).
      cachedArticles = (data as any[]) || [];
      return cachedArticles;
    } catch (err) {
      // If Supabase query fails, log and fall back to local JSON.
      // eslint-disable-next-line no-console
      console.error('Failed to load articles from Supabase, falling back to local JSON', err);
    }
  }

  // Import the local JSON at build time (bundles in Vite). This avoids making a
  // network request to /data/articles.json which may not exist in public/.
  try {
    const mod = await import('../data/articles.json');
    cachedArticles = (mod as any).default || (mod as any);
    return cachedArticles as Article[];
  } catch (err) {
    // If even the local JSON isn't available, throw a clear error.
    throw new Error('Failed to load local articles fallback: ' + String(err));
  }
}

function getDateRangeFilter(dateRange?: string): { start: Date; end: Date } | null {
  const now = new Date();
  let start: Date;

  switch (dateRange) {
    case "24h":
      start = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      return { start, end: now };
    case "7d":
      start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      return { start, end: now };
    case "30d":
      start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      return { start, end: now };
    default:
      return null;
  }
}

export async function listArticles(params: FilterParams): Promise<{
  articles: Article[];
  total: number;
  page: number;
  pageSize: number;
}> {
  const articles = await loadArticles();
  let filtered = [...articles];

  // Search
  if (params.search?.trim()) {
    const query = params.search.toLowerCase();
    filtered = filtered.filter(
      (a) =>
        a.title.toLowerCase().includes(query) ||
        a.summary.toLowerCase().includes(query) ||
        a.tags.some((t) => t.toLowerCase().includes(query))
    );
  }

  // Categories
  if (params.categories?.length) {
    filtered = filtered.filter((a) =>
      a.categories.some((c) => params.categories!.includes(c))
    );
  }

  // Vendors
  if (params.vendors?.length) {
    filtered = filtered.filter((a) =>
      a.vendors.some((v) => params.vendors!.includes(v))
    );
  }

  // Date range
  if (params.dateRange) {
    const range = getDateRangeFilter(params.dateRange);
    if (range) {
      filtered = filtered.filter((a) => {
        const pubDate = new Date(a.publishedAt);
        return pubDate >= range.start && pubDate <= range.end;
      });
    }
  }

  // Sort by newest
  filtered.sort(
    (a, b) =>
      new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
  );

  // Pagination
  const pageSize = 12;
  const page = params.page || 1;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;

  return {
    articles: filtered.slice(start, end),
    total: filtered.length,
    page,
    pageSize,
  };
}
