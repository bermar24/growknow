import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function About() {
  return (
    <div className="main-layout">
      <Navbar onSearch={() => {}} searchValue="" />

      <main className="main-content">
        <div className="container">
          <div className="page-header">
            <h1>About GrowKnow</h1>
            <p>Your central hub for AI news and learning.</p>
          </div>

          <section style={{ marginTop: "1.5rem" }}>
            <h2>Our Vision</h2>
            <p style={{ color: "var(--text-muted)" }}>
              We will build a central hub that consolidates current AI developments, organizes tools by
              real utility, and shows structured learning paths for IT professionals (orientation
              without noise, faster decisions, and measurable learning progress).
            </p>

            <h2 style={{ marginTop: "1rem" }}>Our Mission</h2>
            <p style={{ color: "var(--text-muted)" }}>
              Deliver reliable, transparent AI updates and practical resources: an automated news
              feed + newsletter, a curated tool directory, and role-based roadmaps that make it
              straightforward to learn and apply AI in real projects.
            </p>
          </section>

          <section style={{ marginTop: "2rem" }}>
            <h3>What do we whant to build?</h3>

            <ul style={{ color: "var(--text-muted)", lineHeight: 1.6 }}>
              <li>
                <strong>Automated news & newsletter:</strong> agents crawl sources, remove
                duplicates, extract key points, tag posts with source, date and relevance, and
                publish a compact newsletter explaining what changed and what is actionable today.
              </li>

              <li>
                <strong>Curated tool directory:</strong> tools are categorized by task (generate,
                analyze, automate, build, secure), ranked by strengths, and annotated with domains,
                limits, alternatives, and short example workflows to help teams choose quickly.
              </li>

              <li>
                <strong>Role-based roadmaps:</strong> clear learning sequences for Data Eng,
                ML Eng, DevOps, Backend, Security and more — with objectives, recommended order,
                and precise resources (courses, docs, labs, practice projects) to measure progress.
              </li>
            </ul>

            <p style={{ color: "var(--text-muted)", marginTop: "1rem" }}>
              Under the hood we use automations for crawling, embeddings, classification,
              summarization and fact-checking. Human review remains for sensitive judgements and an
              open feedback channel lets the community suggest sources, tools or new roadmaps.
            </p>
          </section>

          <section style={{ marginTop: "2rem", display: "flex", gap: "1rem", alignItems: "center" }}>
            <div>
              <p style={{ color: "white", margin: 0 }}>
                <strong>
                  Want more detail about the team and our process? Read our
                  <a
                    href="https://knowgrow7.wordpress.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "var(--accent)", marginLeft: "0.25rem" }}
                  >
                    Blog
                  </a>
                  , where we explain decisions, publish updates, and share behind-the-scenes notes.
                </strong>
              </p>
              <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
                To receive the most important AI updates in a compact, reliable format, subscribe to
                our weekly newsletter (coming soon).
              </p>
            </div>
          </section>

          <p style={{ color: "var(--text-muted)", marginTop: "2rem" }}>
            GrowKnow Team
          </p>



        <div className="page-header" id="privacy">
            <h1>Privacy</h1>
            <p style={{ color: "var(--text-muted)", marginTop: "2rem" }}>
                This page is under development. Soon you will find our Privacy here.
            </p>
        </div>

        <div className="page-header" id="terms">
            <h1>Terms</h1>
            <p style={{ color: "var(--text-muted)", marginTop: "2rem" }}>
                This page is under development. Soon you will find our terms here.
            </p>
        </div>

        <div className="page-header" id="imprint">
            <h1>Imprint</h1>
            <p style={{ color: "var(--text-muted)", marginTop: "2rem" }}>
                This page is under development. Soon you will find our Imprint here.
            </p>
        </div>

        </div>
      </main>

      <Footer />
    </div>
  );
}
