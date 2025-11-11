import type { Article, FilterParams } from "./types";

let cachedArticles: Article[] = [];

async function loadArticles(): Promise<Article[]> {
  if (cachedArticles.length > 0) return cachedArticles;

  const response = await fetch("/data/articles.json");
  if (!response.ok) throw new Error("Failed to load articles");

  cachedArticles = await response.json();
  return cachedArticles;
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
