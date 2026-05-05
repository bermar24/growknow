# n8n workflow reference

## Index

- [Overview](#overview)
- [Workflow characteristics](#workflow-characteristics)
- [End-to-end automation steps](#end-to-end-automation-steps)
- [Node-by-node map](#node-by-node-map)
- [Operational notes](#operational-notes)
- [Configuration summary](#configuration-summary)
- [Limitations](#limitations)

## Overview

This document describes the current n8n automation defined in `n8n/workflow.json`.

The workflow is responsible for:

- periodically checking an external AI news RSS feed,
- filtering the feed items with a local Ollama model,
- keeping only items that are AI/ML-related,
- formatting the accepted items for the Django backend,
- and pushing the final payload into the backend API.

In the current architecture, n8n acts as the ingestion layer between external sources and the Django application.

## Workflow characteristics

- **Trigger type:** scheduled automation
- **Schedule:** runs every hour
- **Source:** external RSS feed from an AI news website
- **Filter method:** Ollama-based classification
- **Destination:** Django backend API
- **Transport:** HTTP requests inside the workflow
- **Persistence:** handled by n8n's own data volume when deployed through Docker Compose

## End-to-end automation steps

### 1) Schedule trigger

The workflow starts with a recurring schedule trigger.

What it does:

- activates once per hour,
- starts the ingestion cycle automatically,
- avoids manual execution for normal operation.

Why it matters:

- keeps the dataset fresh,
- makes the news pipeline continuous,
- reduces the need for operator intervention.

### 2) Fetch RSS feed

The workflow requests the external RSS feed from the configured source.

What it does:

- downloads the feed content over HTTP,
- retrieves the latest published items,
- prepares the raw XML for parsing.

### 3) Convert XML to JSON

The RSS XML is converted into a JSON structure.

What it does:

- normalizes the feed into a format that n8n can process more easily,
- makes downstream splitting and filtering simpler,
- preserves article metadata such as title, link, description, and publication date.

### 4) Split feed items

The workflow separates the feed into individual items.

What it does:

- takes the list of RSS entries,
- creates one processing path per article,
- enables item-by-item filtering.

### 5) Ollama classification

Each item is sent to a local Ollama model for a simple relevance check.

What it does:

- reads the item title,
- asks whether the article is specifically about AI or machine learning,
- returns only `True` or `False`.

Why it matters:

- prevents unrelated articles from entering the backend,
- keeps the workflow focused on the project’s domain,
- uses local model inference rather than an external paid API.

### 6) Keep AI-only items

The workflow filters the classification result.

What it does:

- keeps only entries where the Ollama response indicates `true`,
- drops items that are not clearly about AI/ML,
- reduces noise before persistence.

### 7) Format the payload for Django

Accepted items are mapped into the backend payload shape.

What it does:

- copies the title,
- maps the source link to `url`,
- maps the RSS description to `summary`,
- converts the publication date into ISO format,
- attaches a source object with the feed name and website.

### 8) Push to the backend

The formatted payload is posted to the Django API.

What it does:

- sends the item over HTTP `POST`,
- targets the article endpoint in the backend,
- persists the item for frontend consumption and future processing.

## Node-by-node map

| Node | Role | Purpose |
|---|---|---|
| Schedule Trigger | Trigger | Starts the workflow every hour |
| Fetch RSS | HTTP request | Downloads the AI news feed |
| XML to JSON | Parser | Converts RSS XML into JSON |
| Split Items | Splitter | Creates one item per article |
| Ollama Chat Model | Model provider | Supplies the local LLM used by the filter |
| Ollama Filter | LLM chain | Classifies each article as AI/ML or not |
| Filter AI Only | Conditional filter | Keeps only positive matches |
| Format for Django | Formatter | Builds the payload expected by the backend |
| Push to Backend | HTTP request | Sends the final payload to Django |

## Operational notes

### Backend connectivity

The workflow uses `host.docker.internal` to reach local services from inside the n8n container.

Important endpoints used by the workflow:

- Ollama: `http://host.docker.internal:11434`
- Django backend: `http://host.docker.internal:8000/api/news/articles/`

On Linux, the Docker Compose setup should map `host.docker.internal` through the host gateway so these addresses resolve correctly.

### Ollama dependency

The workflow depends on Ollama being available and running.

The model referenced in the workflow is:

- `llama3.2:latest`

If Ollama is down or the model is unavailable, the classification step will not behave as expected.

### Data quality behavior

The workflow is intentionally simple and conservative:

- it filters by title-based classification,
- it does not perform deep deduplication,
- it does not enrich articles with advanced metadata,
- it assumes the RSS item contains usable title, link, description, and publication date values.

## Configuration summary

Key hard-coded values in the current workflow:

| Setting | Value |
|---|---|
| Trigger interval | 1 hour |
| RSS source | `https://www.artificialintelligence-news.com/feed/` |
| Ollama model | `llama3.2:latest` |
| Ollama base URL | `http://host.docker.internal:11434` |
| Backend POST URL | `http://host.docker.internal:8000/api/news/articles/` |
| Source name used in payload | `AI News` |
| Source website used in payload | `https://www.artificialintelligence-news.com` |

## Limitations

- The relevance check is based on the article title, so some relevant items may be missed.
- The workflow relies on the upstream RSS feed structure staying stable.
- The current setup assumes the backend is reachable from n8n through Docker networking.
- The workflow does not replace editorial review if a stricter publishing process is needed.

If you want, I can also add a short link to this document from `README.md` and `docs/api_workflow.md` so it is easier to find from the main docs.
