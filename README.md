# **GrowKnow Documentation**

## Documentation
If you want to explore the Documentation for our project pleas e visit our [GrowKnow_Documentation Repository](https://github.com/bermar24/GrowKnow_Documentation).

## 🌍 Vision & Mission
We are building a **central hub** that consolidates the latest developments in AI, organizes tools by real utility, and provides **structured learning paths for IT professionals**.

Our mission is to deliver:
- **Orientation without noise** → reliable, vetted updates.
- **Faster decisions** → curated tools and filters to match needs.
- **Measurable learning progress** → role-based roadmaps with clear objectives.

---

## 🚀 Core Features

### 📢 AI News & Newsletter
- Automated AI news feed powered by custom agents.
- Duplicates removed, key points extracted, and tagged (source, date, relevance, industry/use case).
- Weekly **compact newsletter** highlighting what changed and what is actionable.
- **Transparency-first**: every claim links to the original source.

### 🛠️ AI Tool Directory
- A growing library of AI tools categorized by tasks (generate, analyze, automate, build, secure).
- Ranked by **strengths, limits, and workflows**.
- Filters for goal, budget, maturity, and integration effort.
- Helps teams **choose faster and smarter**.

### 📚 Role-Based IT Roadmaps
- Roadmaps for **Data Engineer, ML Engineer, DevOps, Backend Engineer, Security Engineer**.
- Structured sequence from **foundations to practice projects**.
- Each step includes objectives, resources, and progress checks.
- Makes required skills **visible, structured, and trackable**.

---

## ⚙️ Technology Stack

- **Frontend**: [React](https://reactjs.org/) → responsive, accessible UI for browsing news, tools, and roadmaps.
- **Backend**: [Node.js](https://nodejs.org/) & APIs → services, data processing, and integrations.
- **Automations**: [n8n](https://n8n.io/) → workflows for crawling, tagging, summarization, and newsletter delivery.
- **Database**: [Supabase](https://supabase.com/) → Postgres-based storage for unified schemas (news, tools, roadmaps).
- **Search**: [OpenSearch](https://opensearch.org/) / [Elasticsearch](https://www.elastic.co/) → full-text search and filters.

This stack is **automation-friendly, scalable, and developer-friendly**, supporting our MVP and future extensions.

---

## 👥 Team

We follow the **Rational Unified Process (RUP)**, so our roles evolve across phases (Inception → Elaboration → Construction → Transition). Primary responsibilities:

**Joaquín**
- Project Manager / Software Architect: planning, architecture, requirements → design.
- Backend Developer: APIs, DB interactions, automation pipelines.

**Emin**
- Frontend Developer / UX Designer: UI, navigation, accessibility, responsive design.
- Tester / Quality Engineer: defines & executes test cases, ensures usability and robustness.

**Roic**
- Database Engineer / Data Pipeline Specialist: schemas, ingestion, embeddings, fact-checking.
- DevOps / Release Manager: CI/CD, monitoring, deployments, release coordination.

---

## 🤝 Contributing

We welcome contributions!
- Suggest AI tools or sources.
- Propose corrections or improvements.
- Request new role-based roadmaps.

Open an issue or start a discussion in this repository.  



## Testing (behave)
Quick start (from the project root):

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate
# Install dependencies
pip install -r backend/requirements.txt 
pip install behave behave-django # run behave (recommended for behave-django) 
python manage.py behave --settings=backend.settings 
```

## Backend
Quick start (from the project root):

```bash
# For local development: 
#Use backend runtime requirements for deploying or running the backend server: 
pip install -r backend/requirements.txt 

# run django dev server 
python manage.py runserver 
```

## Frontend (frontend)
Quick start (from the project root):

```bash
cd frontend
# Install dependencies with npm (will create/update package-lock.json)
npm install 
# Start the dev server
npm run dev
```