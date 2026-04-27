from urllib.parse import urlparse
class SourceMetadataAdapter:
    HOST_MAP = {
        "openai.com": "OpenAI",
        "deepmind.com": "DeepMind",
        "anthropic.com": "Anthropic",
        "mistral.ai": "Mistral",
        "xai.com": "xAI",
        "cohere.com": "Cohere",
        "stability.ai": "Stability AI",
        "techcrunch.com": "TechCrunch",
        "venturebeat.com": "VentureBeat",
        "europa.eu": "EU Official Journal",
        "aisafety.org": "AI Safety Institute",
        "ai.meta.com": "Meta AI Blog",
        "meta.com": "Meta",
    }
    @classmethod
    def from_article(cls, article) -> dict[str, str | None]:
        # SOLID (SRP): serializer delegates URL/source parsing to a dedicated adapter.
        # Pattern (Adapter): converts NewsArticle source fields into the frontend `source` shape.
        # Benefit: mapping logic is reusable and keeps serializer focused on serialization.
        url = getattr(article, "source_url", None) or article.source_link or ""
        name = getattr(article, "source_name", None) or None
        favicon = getattr(article, "source_favicon", None) or None
        if not name and url:
            try:
                parsed = urlparse(url)
                host = (parsed.netloc or "").split(":")[0].lower()
                host_clean = host.replace("www.", "")
                name = cls.HOST_MAP.get(host_clean)
                if not name and host_clean:
                    name = host_clean.split(".")[0].replace("-", " ").title()
                if not favicon and host_clean:
                    favicon = f"https://{host_clean}/favicon.ico"
            except ValueError:
                pass
        return {
            "name": name,
            "url": url,
            "favicon": favicon,
        }
