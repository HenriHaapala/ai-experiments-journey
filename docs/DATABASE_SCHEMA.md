# Database Schema & Data Models

This document outlines the core entities and their relationships within the PostgreSQL database. It is intended to help AI assistants understand the *intent* behind the schema, rather than just the literal table structures.

---

## 🗄️ Relational Database (Django ORM)

The primary data source for the application, storing structured content and application logs.

### 1. Roadmap & Learning Entries
These models form the core content of the portfolio, structured as a chronological learning path.

*   **`RoadmapSection`**: High-level grouping of topics (e.g., "Phase 1: Foundations", "Phase 2: Advanced AI").
    *   *Ordering*: Sorted explicitly by an `order` integer.
*   **`RoadmapItem`**: Specific milestones or projects within a section (e.g., "Build a RAG system").
    *   *Relationship*: `ForeignKey` to `RoadmapSection`.
    *   *State*: Tracks progress via a `status` choice (`NOT_STARTED`, `IN_PROGRESS`, `DONE`).
*   **`LearningEntry`**: A specific log, note, or update detailing work done.
    *   *Relationship*: Optional `ForeignKey` to `RoadmapItem`. An entry can be standalone or attached to a specific roadmap goal.
    *   *Content*: Stores raw Markdown text.
*   **`Media`**: Images, videos, or links attached to a specific `LearningEntry`.
    *   *Relationship*: `ForeignKey` to `LearningEntry`.

### 2. General Content
*   **`SiteContent`**: Arbitrary, standalone pages or content blocks (e.g., an "About Me" blurb) accessed via a unique `slug`.

### 3. Security & Logging
*   **`SecurityAudit`**: A critical table tracking infractions detected by the FastAPI Agent's guardrails.
    *   *Types of Violations Tracked*: `JAILBREAK`, `TOXICITY`, `PROMPT_INJECTION`, `PII_LEAK`.
    *   *Actions Tracked*: Whether the prompt was `BLOCKED` or just `FLAGGED`.

---

## 🧠 Vector Database (`pgvector`)

While the relational tables store the raw text, the vector tables store numerical representations (embeddings) of that text, allowing the LangChain agent to perform semantic searches.

> [!IMPORTANT]
> The project uses **Cohere's `embed-english-v3.0`** model. All vector fields enforce a **1024-dimension** constraint.

### 1. `Embedding` (Legacy / Direct 1-to-1 Mapping)
*   *Relationship*: Direct `OneToOneField` mapping to a single `LearningEntry`.
*   *Purpose*: Storing the embedding for the entire learning entry text.

### 2. `KnowledgeChunk` (Primary RAG Source)
This is the **most important table for the AI functionality**. When the site owner uploads documents or saves learning entries, the backend (`doc_loader.py` or similar utils) splits the text into smaller, overlapping "chunks" and stores them here.

*   **`source_type`**: Identifies where the text came from (`learning_entry`, `roadmap_item`, `site_content`, `document`).
*   **`source_id`**: The integer ID linking back to the original relational table.
*   **`vector`**: The 1024-dimension `pgvector` field.
*   **`content`**: The actual string of text that this chunk represents.

### 3. `DocumentUpload` & `KnowledgeSource`
*   *Purpose*: These are administrative tracking tables. They do *not* store raw files (like PDFs), but rather log that a file was uploaded and parsed into `KnowledgeChunk` records via the Django admin interface.
