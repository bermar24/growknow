# **GrowKnow Documentation**

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

## Documentation
This repo contain the Documentation for our project.
If you want to explore how we implement it pleas e visit our [GrowKnow Repository](https://github.com/bermar24/growKnow.git).

## References

| References                                                                                                                                                          |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [GrowKnow Documentation – Software Requirements Specification](https://github.com/bermar24/GrowKnow_Documentation/blob/main/Software_Requirements_Specification.md) |
| [GrowKnow Documentation – Software Architecture Document](https://github.com/bermar24/GrowKnow_Documentation/blob/main/Software_Architecture_Document.md)           |
| [GrowKnow Blog](https://knowgrow7.wordpress.com/)                                                                                                                   |
| [GrowKnow - GitHub Repository](https://github.com/bermar24/GrowKnow)                                                                                                |


| GrowKnow blog posts                                                                                                                                                                                        |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Homepage Blog](https://knowgrow7.wordpress.com/)                                                                                                                                                          |
| [#1 Blog - Our Vision & Mission](https://knowgrow7.wordpress.com/2025/09/15/our-vision-mission/)                                                                                                           |
| [#2 Blog - Team and Technology](https://knowgrow7.wordpress.com/2025/09/22/team-and-technology/)                                                                                                           |
| [#3 Blog - Introducing Our Software Requirements Specification and Use Case Diagram](https://knowgrow7.wordpress.com/2025/10/01/introducing-our-software-requirements-specification-and-use-case-diagram/) |
| [#4 Blog - Detailing Two Core Use Cases](https://knowgrow7.wordpress.com/2025/10/08/detailing-two-core-use-cases/)                                                                                         |
| [#5 Blog -Bringing Our Use Cases to Life with BDD](https://knowgrow7.wordpress.com/2025/10/15/bringing-our-use-cases-to-life-with-bdd/)                                                                    |
| [#6 Blog - Sprint & Task Management](https://knowgrow7.wordpress.com/2025/10/16/sprint-task-management/)                                                                                                   |
| [#7 Blog - Architecture, Design Patterns, and the Decoupled Stack](https://knowgrow7.wordpress.com/2025/10/29/architecture-design-patterns-and-the-decoupled-stack/)                                       |
| [#8 Blog - Visualizing Our System: Database & UML Diagrams](https://knowgrow7.wordpress.com/2025/11/05/visualizing-our-system-database-uml-diagrams/)                                                      |
| [#9 Blog - Retrospective](https://knowgrow7.wordpress.com/2025/11/12/retrospective/)                                                                                                                       |


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


# Running the Project Locally
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