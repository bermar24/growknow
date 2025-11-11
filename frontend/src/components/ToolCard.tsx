import type { AITool } from "../lib/toolsTypes";

export default function ToolCard({ tool }: { tool: AITool }) {
  return (
    <article className="tool-card">
      <div className="tool-header">
        {tool.logo && (
          <div className="tool-logo">
            <img src={tool.logo} alt={tool.name} />
          </div>
        )}
        <div className="tool-info">
          <h3 className="tool-name">{tool.name}</h3>
          <div className="tool-pricing">
            <span className="pricing-badge">{tool.pricing}</span>
            {tool.priceFrom && <span className="price">from ${tool.priceFrom}/mo</span>}
          </div>
        </div>
      </div>

      <p className="tool-description">{tool.description}</p>

      <div className="tool-tags">
        {tool.tags.slice(0, 3).map((tag) => (
          <span key={tag} className="tag">{tag}</span>
        ))}
      </div>

      {tool.rating && (
        <div className="tool-rating">
          {"⭐".repeat(Math.round(tool.rating))}
        </div>
      )}

      <a href={tool.url} target="_blank" rel="noopener noreferrer" className="tool-link">
        Visit Tool →
      </a>
    </article>
  );
}
