import { Link } from "react-router-dom";
import Navbar from "../components/Navbar.tsx";
import Footer from "../components/Footer.tsx";

export default function NotFound() {
  return (
      <div className="main-layout">
          <Navbar onSearch={() => {}} searchValue="" />
    <main style={{ maxWidth: 980, margin: "28px auto", padding: "0 16px" }}>
        <div style={{ padding: 28, border: "1px solid #e6e6e6", borderRadius: 8}}>
        <h1>404 — Page not found</h1>
        <p>We couldn't find the page you were looking for. You can use the links below to get back to the site.</p>

        <div style={{ marginTop: 18 }}>
          <Link to="/" style={{ display: "inline-block", background: "#fff", color: "black", padding: "10px 14px", borderRadius: 6, textDecoration: "none" }}>Return to Newsfeed</Link>
        </div>
      </div>
    </main>

        <Footer />
    </div>
  );
}

