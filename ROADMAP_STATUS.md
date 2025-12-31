# AI CAREER ROADMAP (2025 EDITION) - STATUS & PLAN

## 1. FOUNDATIONS
- **Status**: ✅ **DONE**
- **Current Implementation**: 
    - `agent_service/agent.py` demonstrates consistent prompt engineering and LLM usage (Groq/Llama).
    - `frontend` and `backend` show solid structure (Next.js, Django, Python).
- **Showcase**: 
    - The "Architect" Chat Interface itself is the showcase.
    - **Idea**: Add a "Debug Mode" toggle in the UI to show the raw prompts and JSON outputs to demonstrate "Structured outputs".

## 2. AGENTS + MCP
- **Status**: 🚧 **IN PROGRESS** (Advanced features missing)
- **Current Implementation**:
    - `backend/mcp_server` exists with tools (`get_roadmap`, `search_knowledge`).
    - `agent_service` consumes these tools.
- **Remaining Todos**:
    - Multi-agent systems (currently single agent).
    - AI controlling local tools (currently read-only/db-write).
- **How to Implement**:
    - Add a "Researcher Agent" separate from the main "Chat Agent" that can browse the web (using a search tool).
    - Implement a "Coder Agent" capability (sandboxed execution).
- **Showcase**:
    - Create a "Mission Control" dashboard page showing agents communicating with each other.

## 3. RAG SYSTEMS
- **Status**: ✅ **DONE**
- **Current Implementation**:
    - `backend/portfolio/utils/doc_loader.py` and `generate_embeddings.py`.
    - `pgvector` usage is implied by dependencies.
    - Chat uses `search_knowledge` tool.
- **Showcase**:
    - "Technical Dossier" page could have a visualization of the vector space or "Source Inspector" showing which chunks were retrieved for an answer.

## 4. IMAGE AI
- **Status**: ❌ **NOT STARTED**
- **Remaining Todos**:
    - SD tools, ControlNet, LoRA usage.
    - ComfyUI automation.
- **How to Implement**:
    - Integrate a distinct Image Generation API (e.g., Stability AI or a local ComfyUI endpoint).
    - Create a Python script to trigger ComfyUI workflows.
- **Showcase**:
    - **"The Gallery"**: A new page where the User can describe a system architecture, and the AI generates a blueprint style image using SD XL + ControlNet (Canny/Lineart).
    - Show "Generative UI" where the background image changes based on chat context.

## 5. LLM FINE-TUNING
- **Status**: ❌ **NOT STARTED**
- **Remaining Todos**:
    - QLoRA, SFT, Axolotl pipelines.
- **How to Implement**:
    - Create a Jupyter Notebook repo/folder `experiments/fine_tuning`.
    - Fine-tune a small model (e.g., TinyLlama) on the user's blog posts/portfolio data.
- **Showcase**:
    - Deploy the fine-tuned model as a "Mini-Me" specialized bot alongside the main "Architect" bot.
    - Add a "Model Card" page displaying training loss curves and dataset stats.

## 6. TRAINING YOUR OWN MODELS
- **Status**: ❌ **NOT STARTED**
- **Remaining Todos**:
    - Math essentials, Transformer internals.
- **How to Implement**:
    - Write deep-dive articles/interactive visualizations.
    - Implement a "Toy Transformer" in pure NumPy.
- **Showcase**:
    - **"Lab" Section**: Interactive JS-based visualization of attention mechanisms (using exact values from a small model run).

## 7. DEPLOYMENT & INFRASTRUCTURE
- **Status**: ✅ **DONE**
- **Current Implementation**:
    - Dockerized setup (`Dockerfile`, `docker-compose`).
    - Cloud deployment documentation (`DEPLOYMENT_SUCCESS.md`).
    - Backend API (Django/FastAPI mix).
- **Showcase**:
    - The "System Status" badge in the header is a good start.
    - Enhance it with a live "Infrastructure Monitor" modal showing Real-time CPU/Memory usage of the containers (via a new MCP tool `get_system_stats`).

## 8. MULTIMODAL AI
- **Status**: ❌ **NOT STARTED**
- **Remaining Todos**:
    - Speech, TTS, Whisper.
- **How to Implement**:
    - Add OpenAI Whisper / ElevenLabs API integration to the Agent Service.
- **Showcase**:
    - **Voice Command**: Add a microphone icon to the chat. "Talk to the Architect".
    - **Audio Briefings**: One-click "Generate Daily Briefing" that reads out the latest roadmap updates.

## 9. SAFETY & EVALUATION
- **Status**: ✅ **DONE**
- **Current Implementation**:
    - `SecurityAudit` model and Admin logging.
    - Agent Guardrails (`guardrails-ai` + custom validators) to block jailbreaks.
    - `bandit`, `safety` for static analysis.
    - **Advanced Eval frameworks**: `ragas` implemented in Agent service with `evaluate_rag.py`.
    - **Metrics UI**: Neural Health Widget displaying RAG scores.
- **Remaining Todos**:
    - Complex PII detection models.
- **How to Implement**:
    - Expand `evaluate_rag.py` to run against real production data during CI/CD.
    - **API**: ✅ `GET /agent/metrics` exposed Ragas scores.
    - **UI**: ✅ `NeuralHealthWidget` added to `page.tsx` footer (below "Secure Connection") to display these metrics.
- **Showcase**:
    - "Security Audit" log in the admin panel showing blocked unsafe prompts.
    - **"Neural Health" Widget**: ✅ A cyberpunk-style status box on the landing page (below the chat) showing real-time AI accuracy scores.

## 10. PRODUCT & CAREER
- **Status**: ✅ **DONE** (Ongoing)
- **Current Implementation**:
    - This portfolio is the product.
    - Roadmap tracking is built-in.
- **Showcase**:
    - Enhance the "Roadmap" page to be interactive (checking off items updates the database).
    - Add a "Hire Me" CTA that uses the Agent to schedule a meeting.
