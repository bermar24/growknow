import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function Sources() {
  return (
    <div className="main-layout">
      <Navbar onSearch={() => {}} searchValue="" />

      <main className="main-content">
        <div className="container">
          <div className="page-header">
            <h1>Sources</h1>
            <p>
              Here you will find information about the sources and selection process we use to
              power GrowKnow's AI news and analysis.
            </p>
          </div>

          <section style={{ marginTop: "1.25rem" }}>
            <h2>Overview</h2>
            <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
              GrowKnow aggregates and curates news from a mixture of primary sources (official blogs,
              research papers, vendor announcements) and reputable secondary reporting (trusted
              industry outlets and specialized newsletters). Our goal is to surface actionable,
              verifiable information for engineers, product teams and technical leaders.
            </p>
          </section>

          <section style={{ marginTop: "1.25rem" }}>
            <h2>How we select sources</h2>
            <ul style={{ color: "var(--text-muted)", lineHeight: 1.6 }}>
              <li>
                <strong>Authority:</strong> preference for official or well-cited sources (papers, vendor
                posts, major outlets).
              </li>
              <li>
                <strong>Relevance:</strong> signal-to-noise for practical engineering and product work —
                we prioritize tangible updates and tooling news.
              </li>
              <li>
                <strong>Reliability:</strong> cross-checks and de-duplication reduce repeated or
                unverified claims.
              </li>
              <li>
                <strong>Transparency:</strong> we show source metadata and links so you can read the
                originals.
              </li>
            </ul>
          </section>

          <section style={{ marginTop: "1.25rem" }}>
            <h2>Types of sources</h2>
            <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
              We include: research papers and preprints, official product announcements and changelogs,
              posts from major AI research labs, technical deep-dives from trusted blogs, and
              investigative reporting from established publications. We exclude anonymous rumors and
              unverifiable social posts unless corroborated.
            </p>
          </section>

          <section style={{ marginTop: "1.25rem" }}>
            <h2>Transparency & attribution</h2>
            <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
              Every story includes source attribution and a link to the original item when available.
              Automated processing (scraping, embeddings, summarization) is combined with human
              review for sensitive or ambiguous cases. If you spot a missing attribution or an error,
              please let us know so we can correct it.
            </p>
          </section>

          <section style={{ marginTop: "1.25rem" }}>
            <h2>Suggest a source</h2>
            <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
              Have a source we should include? Send a suggestion through our feedback form (coming
              soon) or open an issue on our repository with a short description and URL. We review
              community suggestions regularly.
            </p>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  );
}
