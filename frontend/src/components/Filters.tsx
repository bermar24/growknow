import type { FilterParams } from "../lib/types";
import { CATEGORIES, VENDORS } from "../lib/types";

interface FiltersProps {
  filters: FilterParams;
  onFilterChange: (filters: FilterParams) => void;
}

export default function Filters({ filters, onFilterChange }: FiltersProps) {
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, search: e.target.value, page: 1 });
  };

  const handleCategoryToggle = (category: string) => {
    const categories = filters.categories || [];
    const updated = categories.includes(category)
      ? categories.filter((c) => c !== category)
      : [...categories, category];
    onFilterChange({ ...filters, categories: updated, page: 1 });
  };

  const handleVendorToggle = (vendor: string) => {
    const vendors = filters.vendors || [];
    const updated = vendors.includes(vendor)
      ? vendors.filter((v) => v !== vendor)
      : [...vendors, vendor];
    onFilterChange({ ...filters, vendors: updated, page: 1 });
  };

  const handleDateRange = (range: "24h" | "7d" | "30d") => {
    onFilterChange({
      ...filters,
      dateRange: filters.dateRange === range ? undefined : range,
      page: 1,
    });
  };

  const handleClearAll = () => {
    onFilterChange({
      search: "",
      categories: [],
      vendors: [],
      dateRange: undefined,
      page: 1,
    });
  };

  const hasActiveFilters =
    filters.search ||
    (filters.categories && filters.categories.length > 0) ||
    (filters.vendors && filters.vendors.length > 0) ||
    filters.dateRange;

  return (
    <div className="filters">
      <div className="filter-section">
        <label className="filter-label">Search</label>
        <input
          type="search"
          placeholder="Search articles..."
          value={filters.search || ""}
          onChange={handleSearch}
          className="filter-input"
        />
      </div>

      <div className="filter-section">
        <label className="filter-label">Date Range</label>
        <div className="filter-buttons">
          {(["24h", "7d", "30d"] as const).map((range) => (
            <button
              key={range}
              onClick={() => handleDateRange(range)}
              className={`filter-button ${filters.dateRange === range ? "active" : ""}`}
            >
              {range === "24h" ? "Last 24h" : range === "7d" ? "Last 7 days" : "Last 30 days"}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-section">
        <label className="filter-label">Categories</label>
        <div className="filter-buttons">
          {CATEGORIES.map((category) => (
            <button
              key={category}
              onClick={() => handleCategoryToggle(category)}
              className={`filter-button ${filters.categories?.includes(category) ? "active" : ""}`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-section">
        <label className="filter-label">Vendors</label>
        <div className="filter-buttons">
          {VENDORS.map((vendor) => (
            <button
              key={vendor}
              onClick={() => handleVendorToggle(vendor)}
              className={`filter-button ${filters.vendors?.includes(vendor) ? "active" : ""}`}
            >
              {vendor}
            </button>
          ))}
        </div>
      </div>

      {hasActiveFilters && (
        <button onClick={handleClearAll} className="clear-filters">
          Clear All Filters
        </button>
      )}
    </div>
  );
}
