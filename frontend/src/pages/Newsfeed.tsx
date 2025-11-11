import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Filters from "../components/Filters";
import ArticleCard from "../components/ArticleCard";
import { listArticles } from "../lib/api";
import type { Article, FilterParams } from "../lib/types";

export default function Newsfeed() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [filters, setFilters] = useState<FilterParams>({ page: 1 });
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadArticles = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await listArticles(filters);
        if (filters.page === 1) {
          setArticles(result.articles);
        } else {
          setArticles((prev) => [...prev, ...result.articles]);
        }
        setTotal(result.total);
      } catch (err) {
        setError("Failed to load articles");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadArticles();
  }, [filters]);

  const handleFilterChange = (newFilters: FilterParams) => {
    setFilters(newFilters);
  };

  const handleSearch = (query: string) => {
    setFilters({ ...filters, search: query, page: 1 });
  };

  const handleLoadMore = () => {
    const nextPage = (filters.page || 1) + 1;
    setFilters({ ...filters, page: nextPage });
  };

  const hasMore = articles.length < total;

  return (
    <div className="main-layout">
      <Navbar onSearch={handleSearch} searchValue={filters.search || ""} />

      <main className="main-content">
        <div className="container">
          <div className="page-header">
            <h1>AI News Newsfeed</h1>
            <p>Stay updated with the latest developments in artificial intelligence.</p>
          </div>

          <div className="newsfeed-layout">
            <aside className="filters-sidebar">
              <Filters filters={filters} onFilterChange={handleFilterChange} />
            </aside>

            <section className="articles-section">
              {error && <div className="error-state">{error}</div>}

              {articles.length === 0 && !loading && !error && (
                <div className="empty-state">No articles found</div>
              )}

              {articles.length > 0 && (
                <>
                  <div className="articles-grid">
                    {articles.map((article) => (
                      <ArticleCard key={article.id} article={article} />
                    ))}
                  </div>

                  <div className="load-more-container">
                    {hasMore ? (
                      <button
                        onClick={handleLoadMore}
                        disabled={loading}
                        className="load-more-button"
                      >
                        {loading ? "Loading..." : `Load More (${articles.length}/${total})`}
                      </button>
                    ) : (
                      <p className="load-more-message">
                        {total === 0 ? "No articles found" : `All ${total} articles shown`}
                      </p>
                    )}
                  </div>
                </>
              )}
            </section>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
