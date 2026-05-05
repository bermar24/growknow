# GrowKnow

GrowKnow is a modular platform for **AI news**, **AI tool discovery**, and **structured learning paths** for IT professionals. The project combines a React/Vite frontend, a Django REST backend, and n8n automations that ingest and enrich content.

## Index

- [Vision and mission](#vision-and-mission)
- [Core features](#core-features)
- [Architecture](#architecture)
- [Technology stack](#technology-stack)
- [Repository structure](#repository-structure)
- [Local development](#local-development)
- [Documentation](#documentation)
- [References](#references)
- [Team](#team)
- [Contributing](#contributing)

## Vision and mission
We are building a **central hub** that consolidates the latest developments in AI, organizes tools by real utility, and provides **structured learning paths for IT professionals**.

Our mission is to deliver:

- **Orientation without noise** → reliable, vetted updates.
- **Faster decisions** → curated tools and filters that match real needs.
- **Measurable learning progress** → role-based roadmaps with clear objectives.

## Core features

### AI news & newsletter
- Automated AI news feed powered by custom agents and n8n workflows.
- Duplicates removed, key points extracted, and tagged by source, date, relevance, and use case.
- Weekly compact newsletter highlighting what changed and what is actionable.
- Transparency-first approach: every claim should link back to the original source.

### AI tool directory
- A growing library of AI tools categorized by tasks such as generate, analyze, automate, build, and secure.
- Ranked by strengths, limits, and workflow fit.
- Filters for goal, budget, maturity, and integration effort.
- Helps teams choose faster and smarter.

### Role-based IT roadmaps

- Roadmaps for Data Engineer, ML Engineer, DevOps, Backend Engineer, and Security Engineer.
- Structured sequences from foundations to practice projects.
- Each step can include objectives, resources, and progress checks.
- Makes required skills visible, structured, and trackable.

## Architecture

GrowKnow is split into three main runtime parts:

- `frontend/` — React + Vite UI for browsing news, tools, and related content.
- `backend/` — Django project exposing the API and admin interface.
- `n8n/` — automation workflows that fetch, filter, and push content into Django.

Data access follows this pattern:

1. The frontend loads data from the API base URL defined by `VITE_API_URL`.
2. When configured, the frontend can try Supabase first for reads.
3. If Supabase is unavailable, the frontend falls back to the Django API.
4. n8n periodically ingests external news and sends accepted items to the backend.

## Technology stack

- **Frontend**: [React](https://reactjs.org/) + [Vite](https://vitejs.dev/) for a responsive UI.
- **Backend**: [Django](https://www.djangoproject.com/) + Django REST Framework for APIs and admin.
- **Automations**: [n8n](https://n8n.io/) for crawling, filtering, and workflow orchestration.
- **Database**: [Supabase](https://supabase.com/) / Postgres in production, SQLite locally.
- **Search**: [OpenSearch](https://opensearch.org/) / [Elasticsearch](https://www.elastic.co/) for full-text search and filters when needed.

## Repository structure

- `backend/` — Django project, app code, settings, and API routing.
- `frontend/` — Vite application, components, and API helpers.
- `n8n/` — workflow definition and persistent n8n data.
- `docs/` — workflow, architecture, and design documents.
- `installer/` — installer logic invoked by `install.sh`.
- `scripts/` — utility scripts such as smoke checks.

## Local development

### Backend

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python manage.py runserver
```

### Frontend

From the `frontend/` directory:

```bash
npm install
npm run dev
```

### Testing

The repository also includes BDD-style tests. From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pip install behave behave-django
python manage.py behave --settings=backend.settings
```

For a guided setup flow, see `README_INSTALLER.md`.

## Documentation

- `docs/api_workflow.md` — end-to-end API workflow and architecture map.
- `docs/n8n_workflow.md` — detailed n8n automation steps and characteristics.
- `README_INSTALLER.md` — Linux-first installation guide.
- `README.md` — project overview and quick links.

## References

### Project links

| Reference                           | Link |
|-------------------------------------|---|
| GrowKnow Repository                 | https://github.com/bermar24/GrowKnow |
| GrowKnow Blog                       | https://knowgrow7.wordpress.com/ |
| GrowKnow Documentation Repository   | https://github.com/bermar24/GrowKnow_Documentation |
| GrowKnow est Plan                   | |
| Software Requirements Specification | https://github.com/bermar24/GrowKnow_Documentation/blob/main/Software_Requirements_Specification.md |
| Software Architecture Document      | https://github.com/bermar24/GrowKnow_Documentation/blob/main/Software_Architecture_Document.md |

### GrowKnow blog posts

| Post                                                                               | Link |
|------------------------------------------------------------------------------------|---|
| Homepage Blog                                                                      | https://knowgrow7.wordpress.com/ |
| #1 Blog - Our Vision & Mission                                                     | https://knowgrow7.wordpress.com/2025/09/15/our-vision-mission/ |
| #2 Blog - Team and Technology                                                      | https://knowgrow7.wordpress.com/2025/09/22/team-and-technology/ |
| #3 Blog - Introducing Our Software Requirements Specification and Use Case Diagram | https://knowgrow7.wordpress.com/2025/10/01/introducing-our-software-requirements-specification-and-use-case-diagram/ |
| #4 Blog - Detailing Two Core Use Cases                                             | https://knowgrow7.wordpress.com/2025/10/08/detailing-two-core-use-cases/ |
| #5 Blog - Bringing Our Use Cases to Life with BDD                                  | https://knowgrow7.wordpress.com/2025/10/15/bringing-our-use-cases-to-life-with-bdd/ |
| #6 Blog - Sprint & Task Management                                                 | https://knowgrow7.wordpress.com/2025/10/16/sprint-task-management/ |
| #7 Blog - Architecture, Design Patterns, and the Decoupled Stack                   | https://knowgrow7.wordpress.com/2025/10/29/architecture-design-patterns-and-the-decoupled-stack/ |
| #8 Blog - Visualizing Our System: Database & UML Diagrams                          | https://knowgrow7.wordpress.com/2025/11/05/visualizing-our-system-database-uml-diagrams/ |
| #9 Blog - Retrospective                                                            | https://knowgrow7.wordpress.com/2025/11/12/retrospective/ |
| #10 Blog - Midterm Milestone                                                       | https://knowgrow7.wordpress.com/2025/11/18/midterm-milestone-first-client-presentation/|
| #11 Blog - Welcome Back!                                                           | https://knowgrow7.wordpress.com/2026/03/17/welcome-back/ |
| #12 Blog - Risk Register Implementation                                            | https://knowgrow7.wordpress.com/2026/03/19/risk-register-implementation/ |
| #13 Blog - Estimating Effort with Function Points                                  |https://knowgrow7.wordpress.com/2026/03/26/estimating-effort-with-function-points/ |
| #14 Blog - Testing, Testing… Is This Thing On?                                     | https://knowgrow7.wordpress.com/2026/04/02/testing-testing-is-this-thing-on/|
| #15 Blog - Refactoring Lab                                                         | https://knowgrow7.wordpress.com/2026/04/09/refactoring-lab/ |
| #16 Blog - Sprint Retrospective                                                    | https://knowgrow7.wordpress.com/2026/04/16/sprint-retrospective/ |
| #17 Blog - SOLID Principles and Design Patterns in Practice                        | https://knowgrow7.wordpress.com/2026/04/27/solid-principles-and-design-patterns-in-practice/ |
| #18 Blog - Metrics                                                                 | https://knowgrow7.wordpress.com/2026/04/30/metrics/ |
| #19 Blog - Final Presentation                                                      | https://knowgrow7.wordpress.com/2026/05/05/final-presentation/ |

## Team

We follow the **Rational Unified Process (RUP)**, so roles evolve across phases: Inception → Elaboration → Construction → Transition.

### Joaquín

- Project Manager / Software Architect: planning, architecture, requirements to design.
- Backend Developer: APIs, database interactions, and automation pipelines.

### Emin  (Left the project beginning of December 2025)

- Frontend Developer / UX Designer: UI, navigation, accessibility, and responsive design.
- Tester / Quality Engineer: defines and executes test cases, ensures usability and robustness.

### Roic  (Left the project beginning of December 2025)

- Database Engineer / Data Pipeline Specialist: schemas, ingestion, embeddings, and fact-checking.
- DevOps / Release Manager: CI/CD, monitoring, deployments, and release coordination.

## Contributing

We welcome contributions.

- Suggest AI tools or sources.
- Propose corrections or improvements.
- Request new role-based roadmaps.

Open an issue or start a discussion in this repository.
