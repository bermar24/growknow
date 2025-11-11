import { TOOL_CATEGORIES, PRICING_OPTIONS } from "../lib/toolsTypes";
import type { ToolsFilterParams } from "../lib/toolsApi";

interface ToolsFilterProps {
  filters: ToolsFilterParams;
  onFilterChange: (filters: ToolsFilterParams) => void;
}

export default function ToolsFilter({ filters, onFilterChange }: ToolsFilterProps) {
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, search: e.target.value, page: 1 });
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({ ...filters, category: e.target.value || undefined, page: 1 });
  };

  const handlePricingChange = (pricing: string) => {
    const current = filters.pricing || [];
    const updated = current.includes(pricing)
      ? current.filter((p) => p !== pricing)
      : [...current, pricing];
    onFilterChange({ ...filters, pricing: updated.length > 0 ? updated : undefined, page: 1 });
  };

  const handleClearAll = () => {
    onFilterChange({ page: 1 });
  };

  return (
    <aside className="filters">
      <div className="filter-header">
        <h2>Filters</h2>
        <button onClick={handleClearAll} className="clear-btn">
          Clear All
        </button>
      </div>

      <div className="filter-group">
        <label htmlFor="search">Search Tools</label>
        <input
          id="search"
          type="text"
          placeholder="Search by name or description..."
          value={filters.search || ""}
          onChange={handleSearchChange}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="category">Category</label>
        <select
          id="category"
          value={filters.category || ""}
          onChange={handleCategoryChange}
        >
          <option value="">All Categories</option>
          {TOOL_CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Pricing</label>
        <div className="checkbox-group">
          {PRICING_OPTIONS.map((pricing) => (
            <label key={pricing} className="checkbox-label">
              <input
                type="checkbox"
                checked={filters.pricing?.includes(pricing) || false}
                onChange={() => handlePricingChange(pricing)}
              />
              <span>{pricing}</span>
            </label>
          ))}
        </div>
      </div>
    </aside>
  );
}
