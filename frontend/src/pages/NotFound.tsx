import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <main style={{ maxWidth: 980, margin: "28px auto", padding: "0 16px" }}>
      <div style={{ padding: 28, border: "1px solid #e6e6e6", borderRadius: 8, background: "#fff" }}>
        <h1>404 — Page not found</h1>
        <p>We couldn't find the page you were looking for. You can use the links below to get back to the site.</p>

        <nav aria-label="Main navigation" style={{ marginTop: 12 }}>
          <Link style={{ marginRight: 12, color: "#0f172a", fontWeight: 600 }} to="/">Newsfeed</Link>
          <Link style={{ marginRight: 12, color: "#0f172a", fontWeight: 600 }} to="/ai-tools">AI Tools</Link>
          <Link style={{ marginRight: 12, color: "#0f172a", fontWeight: 600 }} to="/sources">Sources</Link>
          <Link style={{ marginRight: 12, color: "#0f172a", fontWeight: 600 }} to="/about">About</Link>
        </nav>

        <div style={{ marginTop: 18 }}>
          <Link to="/" style={{ display: "inline-block", background: "#0f172a", color: "white", padding: "10px 14px", borderRadius: 6, textDecoration: "none" }}>Return to Newsfeed</Link>
        </div>
      </div>

      <footer style={{ marginTop: 40, padding: "20px 0", textAlign: "center", color: "#666" }}>
        <p>© 2025 GrowKnow — <Link to="/admin">Admin</Link></p>
      </footer>
    </main>
  );
}

