# Enterprise Employee Policy Search (RAG)

## 1. Topic Overview
This project is a Generative AI-powered enterprise assistant that helps employees ask natural-language questions about company policies and workplace laws, and receive accurate, citation-backed answers.

The system combines Retrieval-Augmented Generation (RAG) with a multi-agent LangGraph workflow. An LLM-based orchestrator (the Helpdesk Agent) classifies each incoming query and routes it to one of seven specialist agents — six domain-specific policy agents backed by an internal vector store, and one Labour Law agent that performs live web searches for national and regional employment regulations.

## 2. Business Use Cases
1. Leave policy Q&A  
Employee asks: “How many casual leaves can I carry forward?”

2. Insurance coverage clarification  
Employee asks: “Does parental insurance cover day-care procedures?”

3. Policy version awareness  
Employee asks: “What changed in WFH policy this quarter?”

4. National labour law queries  
Employee asks: “Am I legally entitled to overtime pay under federal law?” — answered by the Labour Law agent via live web search with a legal disclaimer.

5. HR escalation guidance  
When evidence is weak or conflicting, the system responds with “insufficient evidence” and routes the employee to an HR contact path.

## 3. Objectives
1. Provide trustworthy answers with source citations.
2. Reduce HR support load for repetitive questions.
3. Make policy access fast, conversational, and searchable.
4. Keep architecture API-first so Slack/Teams adapters can be added later.
5. Maximize GenAI framework usage with LangChain + LangGraph.

## 4. Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Docker & Docker Compose (optional, for containerized setup)
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd genai_mini_proj
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate 
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Setup

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Configure the `.env` with your settings:
```
DATABASE_URL=postgresql://user:password@localhost:5432/policy_search
GEMINI_API_KEY=your-gemini-api-key
LANGSMITH_API_KEY=your-langsmith-api-key
JWT_SECRET_KEY=your-secret-key
```

### Database Setup

1. Start PostgreSQL (if using Docker Compose):
```bash
docker-compose up -d
```

2. Run migrations:
```bash
bash scripts/bootstrap_db.sh
```

Or manually initialize the database:
```bash
psql -U postgres -d policy_search -f init.sql
```

### Running the Application

1. Start the FastAPI server:
```bash
python -m app.main
```
OR
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

2. Access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

3. Start the frontend (React 19 + Vite):
```bash
cd frontend
npm install
npm run dev
```

### Common Commands

- **Health check:**
```bash
curl http://localhost:8000/health
```

- **Upload a policy document:**
```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@policy.pdf"
```

- **Query the system:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many casual leaves can I take?"}'
```

- **List ingested documents:**
```bash
curl http://localhost:8000/documents \
  -H "Authorization: Bearer <token>"
```

## 5. High-Level Architecture

```mermaid
flowchart LR
    A["Employee Client (Web/Slack/Teams later)"] --> B["FastAPI Gateway"]
    B --> C["Auth Service (Basic login for pilot)"]
    B --> D["normalize_question"]
    D --> E["Helpdesk Agent (LLM Orchestrator)"]

    E -->|leave / insurance / hr-guidelines\ncompensation / remote-work / general| F["Policy Agents (×6)\n(RAG via PGVector)"]
    E -->|labour-law| G["Labour Law Agent\n(DuckDuckGo web search)"]

    F --> H["PostgreSQL + pgvector"]
    F --> I["Gemini LLM"]
    G --> I

    J["Admin Upload API"] --> K["Ingestion Pipeline (Loader + Splitter + Embedding)"]
    K --> H

    E --> L["Audit/Tracing (LangSmith-ready + app logs)"]
```

## 6. Core Components
1. API Layer (FastAPI)  
Handles auth, document upload, query endpoints, and health checks.

2. Ingestion Pipeline (LangChain)  
Uses PDF loader, text splitter, embedding model, and persists chunks to PostgreSQL `pgvector`.

3. Vector + Metadata Store (PostgreSQL + pgvector)  
Stores document metadata, chunk text, embeddings, versions, and query audit records.

4. Orchestration Layer (LangGraph)  
Implements a multi-agent workflow as a directed graph:

   ```
   normalize_question
         │
   helpdesk_agent  ← LLM orchestrator (classifies query, selects specialist)
         │
   ┌─────┴─────────────────────────────────────────────────────┐
   │  leave_agent          (vacation, PTO, sick leave …)       │
   │  insurance_agent      (health/dental/vision, HSA/FSA …)   │
   │  hr_guidelines_agent  (conduct, harassment, reviews …)    │
   │  compensation_agent   (salary, bonus, equity, payroll …)  │
   │  remote_work_agent    (WFH, hybrid, home-office …)        │
   │  general_agent        (catch-all company policy)          │
   │  labour_law_agent     (national/regional laws, web search)│
   └───────────────────────────────────────────────────────────┘
   ```

   Each policy agent performs retrieval from the internal vector store, grades evidence by cosine similarity, generates a grounded answer with citations, and falls back to a domain-scoped web search when confidence is low. The Labour Law agent always uses live web search (DuckDuckGo) for national and regional employment regulations.

5. LLM and Tools Layer  
Gemini via LangChain wrappers. The orchestrator uses structured output (`OrchestratorRoutingSchema`) to deterministically select the correct agent. Policy agents use `PolicyAnswerSchema`; the Labour Law agent uses `HelpdeskAnswerSchema` with a legal-advice disclaimer.

6. Observability Layer  
Request tracing, retrieval diagnostics, latency, citation coverage, and insufficient-evidence rates.

## 7. Logical Data Model
1. `documents`  
`doc_id`, `title`, `policy_type`, `version`, `effective_date`, `status`, `uploaded_by`, `uploaded_at`

2. `chunks`  
`chunk_id`, `doc_id`, `chunk_text`, `page`, `section`, `embedding vector`, `version`, `policy_type`

3. `query_audit`  
`request_id`, `user_id`, `question`, `retrieved_doc_ids`, `response_summary`, `confidence`, `latency_ms`, `created_at`

## 8. End-to-End Flows

### 8.1 Ingestion Flow
```mermaid
sequenceDiagram
    participant Admin
    participant API as FastAPI
    participant Ingest as LangChain Ingestion
    participant DB as PostgreSQL+pgvector

    Admin->>API: Upload policy PDF
    API->>Ingest: Parse + split + embed
    Ingest->>DB: Save document metadata
    Ingest->>DB: Save chunk text + embeddings
    API-->>Admin: Upload/index success with doc_id/version
```

### 8.2 Query Flow
```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant Norm as normalize_question
    participant Orch as Helpdesk Agent (Orchestrator)
    participant Spec as Specialist Agent
    participant Ret as Retriever (PGVector)
    participant Web as DuckDuckGo
    participant LLM as Gemini
    participant DB as PostgreSQL

    User->>API: POST /query
    API->>Norm: Clean question
    Norm->>Orch: normalized_question
    Orch->>LLM: Classify query → select agent (leave / insurance / … / labour-law)
    LLM-->>Orch: route + reasoning

    alt policy domain (leave, insurance, hr-guidelines, compensation, remote-work, general)
        Orch->>Spec: route to domain policy agent
        Spec->>Ret: Semantic + metadata retrieval
        Ret->>DB: Fetch top-k chunks
        alt confidence ≥ 0.45
            Spec->>LLM: Generate grounded answer from DB context
        else low confidence fallback
            Spec->>Web: Domain-scoped web search
            Spec->>LLM: Generate answer from search results
        end
    else labour-law
        Orch->>Spec: route to labour_law_agent
        Spec->>Web: Search national/regional employment laws
        Spec->>LLM: Generate answer with legal disclaimer
    end

    Spec->>DB: Write query_audit
    API-->>User: Answer + citations + confidence + escalation flag + follow-up questions
```

## 9. API Surface (v1)
1. `POST /auth/login`
2. `POST /auth/refresh`
3. `POST /documents/upload`
4. `GET /documents`
5. `GET /documents/{id}`
6. `POST /query`
7. `GET /health`
8. `GET /ready`

`/query` response schema:
- `answer`
- `citations[]` with `doc_id/title/page/section/snippet/version`
- `confidence`
- `escalation_required`
- `follow_up_questions[]`
- `request_id`

## 10. Security and Governance (Pilot Baseline)
1. Basic login with token-based session.
2. API route protection for upload/admin operations.
3. Audit logs for every query and retrieved evidence.
4. Strict grounded-answer policy to reduce hallucinations.
5. “Insufficient evidence” fallback + HR escalation guidance.

## 11. Utilities

- `visualize.py` — prints the LangGraph workflow as a Mermaid diagram or ASCII art:
```bash
python visualize.py
```

----
