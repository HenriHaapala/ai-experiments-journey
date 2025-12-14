"""
Parsers for incoming automation events (e.g., GitHub webhooks).
"""
from typing import Dict, List, Any, Optional


def parse_push_event(payload: Dict[str, Any], delivery_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Parse a GitHub push event into a list of learning entry payloads.

    Aggregates all commits in the push into a single learning entry to avoid spamming the log.
    """
    repository = payload.get("repository", {}) or {}
    repo_name = repository.get("full_name") or repository.get("name") or "unknown repository"
    ref = payload.get("ref") or ""
    branch = ref.split("/")[-1] if ref else "unknown-branch"
    commits = payload.get("commits") or []

    if not commits:
        return []

    commit_lines: List[str] = []
    commit_messages: List[str] = []

    for commit in commits:
        message = (commit.get("message") or "").strip()
        commit_messages.append(message)
        author = (commit.get("author") or {}).get("name") or "unknown author"
        sha_short = (commit.get("id") or commit.get("sha") or "")[:7]
        url = commit.get("url")

        line = f"- {message} (by {author}"
        if sha_short:
            line += f", {sha_short}"
        line += ")"
        if url:
            line += f" {url}"

        commit_lines.append(line)

    compare_url = payload.get("compare")

    content_lines = [
        f"GitHub Delivery ID: {delivery_id or 'unknown'}",
        f"Repository: {repo_name}",
        f"Branch: {branch}",
    ]
    if compare_url:
        content_lines.append(f"Compare: {compare_url}")

    content_lines.append("")
    content_lines.append("Commits:")
    content_lines.extend(commit_lines)

    entry = {
        "title": f"GitHub push • {repo_name} • {branch} ({len(commits)} commit{'s' if len(commits) != 1 else ''})",
        "content": "\n".join(content_lines),
        "is_public": True,
        "messages": commit_messages,
        # Extra context for downstream LLM summarization
        "summary_payload": {
            "event_type": "push",
            "delivery_id": delivery_id,
            "repository": repo_name,
            "branch": branch,
            "compare_url": compare_url,
            "commit_messages": commit_messages,
            "commit_lines": commit_lines,
        },
    }

    return [entry]


def parse_pull_request_event(payload: Dict[str, Any], delivery_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Parse a GitHub pull_request event into a learning entry payload.
    """
    pr = payload.get("pull_request") or {}
    action = payload.get("action") or "unknown"

    # Only process meaningful state changes
    supported_actions = {"opened", "closed", "reopened", "ready_for_review"}
    if action not in supported_actions:
        return []

    repository = payload.get("repository", {}) or {}
    repo_name = repository.get("full_name") or repository.get("name") or "unknown repository"

    number = pr.get("number") or "?"
    title = (pr.get("title") or "").strip() or "Untitled PR"
    user = (pr.get("user") or {}).get("login") or "unknown"
    html_url = pr.get("html_url")
    base_ref = (pr.get("base") or {}).get("ref") or "unknown-base"
    head_ref = (pr.get("head") or {}).get("ref") or "unknown-head"
    merged = pr.get("merged") or False
    body = (pr.get("body") or "").strip()

    labels = pr.get("labels") or []
    label_names = [lbl.get("name") for lbl in labels if lbl.get("name")]

    state_line = f"Action: {action}"
    if merged:
        state_line = "Action: merged (closed)"

    content_lines = [
        f"GitHub Delivery ID: {delivery_id or 'unknown'}",
        f"Repository: {repo_name}",
        f"PR: #{number} {title}",
        state_line,
        f"Author: {user}",
        f"Branches: {head_ref} -> {base_ref}",
    ]
    if html_url:
        content_lines.append(f"URL: {html_url}")
    if label_names:
        content_lines.append("Labels: " + ", ".join(label_names))
    if body:
        content_lines.append("")
        content_lines.append("PR Description:")
        content_lines.append(body)

    entry = {
        "title": f"Pull request • {repo_name} • #{number} {title}",
        "content": "\n".join(content_lines),
        "is_public": True,
        "messages": [title, body] + label_names,
        "summary_payload": {
            "event_type": "pull_request",
            "delivery_id": delivery_id,
            "repository": repo_name,
            "title": title,
            "action": action,
            "author": user,
            "base_branch": base_ref,
            "head_branch": head_ref,
            "url": html_url,
            "labels": label_names,
            "body": body,
        },
    }

    return [entry]
