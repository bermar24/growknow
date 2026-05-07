// Normalize VITE_API_URL: allow developers to accidentally paste multiple values or comments.
// We pick the first token that looks like a valid http(s) URL.
function _normalizeApiUrl(raw: string | undefined): string | null {
  if (!raw) return null;
  // Split on whitespace, commas, semicolons
  const tokens = raw.split(/[\s;,]+/).map(t => t.trim()).filter(Boolean);
  for (const t of tokens) {
    if (/^https?:\/\//i.test(t)) return t.replace(/\/+$/, ''); // remove trailing slashes
  }
  return null;
}

const _rawApi = import.meta.env.VITE_API_URL as string | undefined;
const _normalized = _normalizeApiUrl(_rawApi);
export const API_BASE = _normalized || 'http://localhost:8000';
if (!_normalized && _rawApi) {
  // Warn once: developer provided an invalid VITE_API_URL
  // eslint-disable-next-line no-console
  console.warn('VITE_API_URL was present but could not be parsed as a valid URL. Falling back to', API_BASE, 'Original value:', _rawApi);
}

export async function fetchArticles() {
    const res = await fetch(`${API_BASE}/api/news/articles/`);
    if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
    }
    return res.json();
}


import type { Article, FilterParams } from "./types";

let cachedArticles: Article[] = [];

function htmlToText(value: unknown): string {
  if (typeof value !== 'string' || !value) return '';


  // Best-effort DOM-based decode + tag stripping. Works in the browser.
  try {
    if (typeof document !== 'undefined') {
      const tmp = document.createElement('div');
      tmp.innerHTML = value;
      let text = tmp.textContent || '';

      // If the decoded text still contains HTML-like tags (e.g. the source used
      // HTML entities like `&lt;p&gt;...&lt;/p&gt;`), parse the decoded text
      // again so those tags become actual nodes and their textContent can be
      // extracted.
      if (/[<>]/.test(text)) {
        tmp.innerHTML = text;
        text = tmp.textContent || '';
      }

      return text.replace(/\s+/g, ' ').trim();
    }
  } catch (e) {
    // fall through to conservative fallback
  }

  // Fallback: remove tags and numeric entities roughly.
  return String(value)
    .replace(/<\/?p[^>]*>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&#(\d+);/g, (_m, n) => String.fromCharCode(Number(n)))
    .replace(/&(amp|lt|gt|quot|apos);/gi, (m) => {
      switch (m.toLowerCase()) {
        case '&amp;': return '&';
        case '&lt;': return '<';
        case '&gt;': return '>';
        case '&quot;': return '"';
        case '&apos;': return "'";
        default: return '';
      }
    })
    .replace(/\s+/g, ' ')
    .trim();
}

function normalizeArticle(article: Article): Article {
  return {
    ...article,
    summary: htmlToText(article.summary),
  };
}

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
    // If the package isn't installed, warn and fall back to backend API.
    // eslint-disable-next-line no-console
    console.warn('Supabase client not available; falling back to backend API.', err);
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
      cachedArticles = ((data as any[]) || []).map((article) => normalizeArticle(article as Article));
      return cachedArticles;
    } catch (err) {
      // If Supabase query fails, log and fall back to backend API.
      // eslint-disable-next-line no-console
      console.error('Failed to load articles from Supabase, falling back to backend API', err);
    }
  }

  // Fetch from backend API
  try {
    const res = await fetch(`${API_BASE}/api/news/articles/`);
    if (!res.ok) throw new Error('API fetch failed: ' + res.status);
    const data = await res.json();
    cachedArticles = (data as Article[]).map(normalizeArticle);
    return cachedArticles;
  } catch (err) {
    throw new Error('Failed to load articles from backend API: ' + String(err));
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
