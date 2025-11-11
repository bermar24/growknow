import { useState } from "react";

interface NavbarProps {
  onSearch: (query: string) => void;
  searchValue: string;
}

export default function Navbar({ onSearch, searchValue }: NavbarProps) {
  const [search, setSearch] = useState(searchValue);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearch(value);
    onSearch(value);
  };

  return (
    <nav className="navbar">
      <div className="container navbar-content">
        <a href="/" className="logo">
          <img src="/logo.png" alt="GrowKnow" />
          <span>GrowKnow</span>
        </a>

        <div className="nav-links">
          <a href="/">Newsfeed</a>
          <a href="/ai-tools">AI Tools</a>
          <a href="/sources">Sources</a>
          <a href="/about">About</a>
        </div>

        <div className="nav-search">
          <input
            type="search"
            placeholder="Search..."
            value={search}
            onChange={handleSearchChange}
          />
        </div>
      </div>
    </nav>
  );
}
