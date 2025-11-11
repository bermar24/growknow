import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import ToolsFilter from "../components/ToolsFilter";
import ToolCard from "../components/ToolCard";
import { listTools, type ToolsFilterParams } from "../lib/toolsApi";
import type { AITool } from "../lib/toolsTypes";

export default function AITools() {
  const [tools, setTools] = useState<AITool[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<ToolsFilterParams>({ page: 1 });
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    loadTools();
  }, [filters]);

  const loadTools = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await listTools(filters);
      
      if (filters.page === 1) {
        setTools(result.tools);
      } else {
        setTools((prev) => [...prev, ...result.tools]);
      }
      
      setTotal(result.total);
      setHasMore(result.tools.length === result.pageSize && tools.length + result.tools.length < result.total);
    } catch (err) {
      setError("Failed to load AI tools. Please try again later.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters: ToolsFilterParams) => {
    setFilters(newFilters);
  };

  const handleLoadMore = () => {
    setFilters({ ...filters, page: (filters.page || 1) + 1 });
  };

  return (
    <div className="app">
      <Navbar onSearch={() => {}} searchValue="" />
      <main className="main-content">
        <div className="container">
          <div className="content-layout">
            <ToolsFilter filters={filters} onFilterChange={handleFilterChange} />
            
            <div className="content-area">
              <div className="page-header">
                <h1>AI Tools Directory</h1>
                <p className="subtitle">{total} tools found</p>
              </div>

              {error && <div className="error-state">{error}</div>}

              {loading && filters.page === 1 ? (
                <div className="loading-state">Loading tools...</div>
              ) : tools.length === 0 ? (
                <div className="empty-state">
                  <p>No tools found matching your criteria.</p>
                </div>
              ) : (
                <>
                  <div className="tools-grid">
                    {tools.map((tool) => (
                      <ToolCard key={tool.id} tool={tool} />
                    ))}
                  </div>

                  {hasMore && (
                    <div className="load-more">
                      <button onClick={handleLoadMore} disabled={loading}>
                        {loading ? "Loading..." : "Load More"}
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
