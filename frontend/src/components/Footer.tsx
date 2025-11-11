export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <img src="/logo.png" alt="GrowKnow" style={{ width: "24px", height: "24px" }} />
              <strong>GrowKnow</strong>
            </div>
            <p style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
              Your hub for AI news and learning.
            </p>
          </div>

          <div className="footer-section">
            <h4>Links</h4>
            <ul>
              <li><a href="/">Newsfeed</a></li>
              <li><a href="/ai-tools">AI Tools</a></li>
              <li><a href="/sources">Sources</a></li>
              <li><a href="/about">About</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Legal</h4>
            <ul>
              <li><a href="#privacy">Privacy</a></li>
              <li><a href="#terms">Terms</a></li>
              <li><a href="#imprint">Imprint</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; {year} GrowKnow. All rights reserved.</p>
          <div style={{ display: "flex", gap: "1.5rem" }}>
            <a href="#">Twitter</a>
            <a href="https://github.com/bermar24/GrowKnow_Documentation">GitHub</a>
            <a href="#">LinkedIn</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
