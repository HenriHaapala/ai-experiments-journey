# AI Commands & Workflow Features

This document explains the special syntax and commands you can use to interact with the AI assistant more efficiently within this repository.

## 1. Workflow Automation Flags (`// turbo`)

When creating `.md` files in the `.agents/workflows/` directory, you can add special comments above bash command blocks to give the AI permission to execute them automatically, without interrupting you for approval. 

Normally, whenever an AI wants to run a terminal command on your machine, it pauses and forces you to explicitly click "Approve" for security reasons. The turbo flags bypass this for trusted, routine workflows.

*   **`// turbo`**: When placed on the line immediately above a bash block, this grants the AI permission to execute *only that specific command* automatically. This is useful for safe, repetitive commands (like running tests or generating migrations).
*   **`// turbo-all`**: When placed *anywhere* in the workflow file, this grants the AI permission to automatically run *every single* bash command within that entire workflow document.

**Example usage in a workflow:**
```markdown
## Step 1: Generate Migrations
// turbo
```bash
docker-compose exec backend python manage.py makemigrations
```
```

## 2. Slash Commands

Whenever you create a new file in the `.agents/workflows/` directory (e.g., `my_custom_script.md`), you are actually creating a custom "Slash Command" that you can invoke instantly in the chat.

The AI automatically reads that directory and exposes them as slash commands. Based on the current workflows in this project, you can type the following commands directly into the chat to trigger those exact step-by-step processes:

*   **/deploy**: Triggers the deployment instructions found in `deploy.md`.
*   **/add_new_api_endpoint**: Triggers the API creation steps found in `add_new_api_endpoint.md`.
*   **/database_migration_steps**: Triggers the migration process found in `database_migration_steps.md`.

## 3. System Rules & Context Pointers (The "AI Brain")

To ensure the AI strictly follows your instructions (like not force-killing the dev server, formatting with `ruff`, or using Tailwind v4), these rules have been embedded into `.antigravity/rules.md`. 

### The "System Rules + Pointers" Methodology
This setup is the industry standard for senior developers working with AI for the following reasons:

1.  **Guarantees Absolute Consistency:** Instead of manually pasting long `AI_INSTRUCTIONS.md` files into the chat (which the AI will eventually "forget" when the context window gets too full), placing rules in a `.rules` file injects them directly into the AI's *System Prompt*. The AI is physically incapable of forgetting them, no matter how long the chat gets.
2.  **Saves Tokens & Money:** Instead of loading thousands of words of technical documentation into every chat message, the `.antigravity/rules.md` file contains **Pointers**. It tells the AI: *"If the user asks about the database, use your tools to read `docs/DATABASE_SCHEMA.md` first."* The AI only reads the deep technical documentation when it explicitly needs to, keeping responses fast, cheap, and highly focused.
3.  **Separation of Concerns:** 
    *   `.antigravity/rules.md` = The Company Handbook (Strict boundaries, what tech stack to use).
    *   `docs/` folder = The Technical Wikis (Architecture, API contracts).
    *   `.agents/workflows/` = Standard Operating Procedures (Checklists for deployments or migrations).

### Configuring Other AI Tools
If you use an AI editor other than Antigravity (like Cursor, Windsurf, or GitHub Copilot), you must ensure it also reads these root instructions. 

To give other frontends the same "brain," simply copy the contents of `.antigravity/rules.md` into the tool's respective system rule file:
*   **Cursor:** Copy to `.cursorrules` in the root directory.
*   **Windsurf:** Copy to `.windsurfrules` in the root directory.
*   **GitHub Copilot:** Copy to `.github/copilot-instructions.md`.
