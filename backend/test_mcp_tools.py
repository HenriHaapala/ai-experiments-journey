#!/usr/bin/env python3
"""Test script for MCP tools"""
import os
import json

import pytest

pytestmark = pytest.mark.django_db

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from mcp_server.handlers import (
    handle_get_roadmap,
    handle_get_learning_entries,
    handle_get_progress_stats
)


def test_get_progress_stats():
    result = handle_get_progress_stats({})
    assert result["success"] is True
    assert "stats" in result


def test_get_roadmap():
    result = handle_get_roadmap({})
    assert result["success"] is True
    assert "roadmap" in result
    assert result["total_sections"] == len(result["roadmap"])


def test_get_learning_entries_limit_respected():
    result = handle_get_learning_entries({"limit": 3})
    assert result["success"] is True
    assert result["count"] == len(result["entries"])
    assert isinstance(result["entries"], list)
    assert result["count"] <= 3


if __name__ == "__main__":
    print("=" * 60)
    print("Testing MCP Tools")
    print("=" * 60)

    print("\n1. Testing get_progress_stats...")
    stats = handle_get_progress_stats({})
    print(json.dumps(stats, indent=2))

    print("\n2. Testing get_roadmap...")
    roadmap = handle_get_roadmap({})
    print(f"Success: {roadmap['success']}")
    print(f"Sections: {roadmap['total_sections']}, Items: {roadmap['total_items']}")

    print("\n3. Testing get_learning_entries...")
    entries = handle_get_learning_entries({"limit": 3})
    print(f"Success: {entries['success']}, Count: {entries['count']}")

    print("\n" + "=" * 60)
    print("All MCP tools tested successfully!")
    print("=" * 60)
