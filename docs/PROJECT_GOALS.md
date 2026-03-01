# Project Goals & Overview

This document provides a high-level summary of the AI Portfolio Project. Understanding these goals is critical for making aligned architectural and design decisions.

---

## 🎯 Primary Objective

The main purpose of the "AI Portfolio" is to serve as an interactive, intelligent resume and project showcase. It demonstrates advanced integration of Large Language Models (LLMs) into a traditional web application, allowing visitors to interact with a personalized AI agent that has intimate knowledge of the creator's skills, projects, and learning journey.

## 👥 Target Audience

1.  **Recruiters & Hiring Managers:** Looking for a quick, interactive way to assess technical skills and cultural fit.
2.  **Fellow Developers:** Interested in the architecture, implementation details, and open-source components of the portfolio itself.
3.  **Potential Clients:** Looking for proof of competence in AI integration and full-stack development.

## ✨ Core Features & Use Cases

### 1. The Interactive AI Agent (The "ChatWidget")
*   **Description:** A persistent chat interface on the frontend.
*   **Functionality:** Visitors can ask questions naturally (e.g., "What is Henri's experience with React?", "How did you build the backend for this site?").
*   **Mechanism:** The agent uses Retrieval-Augmented Generation (RAG) against a `pgvector` database containing the creator's documentation, resume, and learning logs to provide accurate, grounded answers.

### 2. The Learning Log & Roadmap
*   **Description:** Structured sections displaying the creator's ongoing technical education and future project plans.
*   **Functionality:** Visitors can browse chronologically or categorically.
*   **Mechanism:** Data is served via the Django REST API from the relational PostgreSQL database.

### 3. Agent Transparency (Neural Health Widget)
*   **Description:** A UI component that shows real-time metrics of the AI agent's performance.
*   **Functionality:** Displays latency, token usage, or recent internal reasoning steps.
*   **Mechanism:** Fetches data points from the underlying FastAPI agent service.

## 🛡️ Key Design Principles

> [!TIP]
> When implementing new features, ensure they align with these core philosophies.

1.  **Safety First (Guardrails):** Because the AI agent is public-facing, security is paramount. Prompts are aggressively audited and sanitized (`guardrails_config.py`) to prevent prompt injection, jailbreaks, or the AI exposing sensitive internal system info.
2.  **Separation of Concerns:** Heavy AI orchestration (LangChain) is deliberately separated into a FastAPI microservice, distinct from the standard CRUD operations handled by the stable Django backend.
3.  **Modern Aesthetics:** The frontend must feel premium, responsive, and dynamic, reflecting high competence in modern web presentation (Next.js, Tailwind).
