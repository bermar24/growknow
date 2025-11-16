import type { Article } from "../lib/types";
import { relativeTime } from "../lib/relativeTime";

function hostFallback(url?: string) {
  if (!url) return 'source';
  try {
    const u = new URL(url);
    return u.hostname.replace(/^www\./, '');
  } catch (e) {
    return url;
  }
}

export default function ArticleCard({ article }: { article: Article }) {
  const sourceName = article?.source?.name || hostFallback(article?.source?.url);
  const favicon = article?.source?.favicon || '/logo.png';

  return (
    <article className="article-card">
      <div className="article-header">
        <div className="article-source">
          <img src={favicon} alt={sourceName} />
          <span>{sourceName}</span>
        </div>
        <span className="article-time">{relativeTime(article.publishedAt)}</span>
      </div>

      <h3 className="article-title">{article.title}</h3>
      <p className="article-summary">{article.summary}</p>

      <div className="article-tags">
        {article.tags.map((tag) => (
          <span key={tag} className="tag">{tag}</span>
        ))}
      </div>

      <div className="article-tags">
        {article.categories.map((cat) => (
          <span key={cat} className="category">{cat}</span>
        ))}
      </div>

      <a href={article.url} target="_blank" rel="noopener noreferrer" className="article-link">
        Read Article →
      </a>
    </article>
  );
}
