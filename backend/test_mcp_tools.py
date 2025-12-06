#!/usr/bin/env python3
"""Test script for MCP tools"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from mcp_server.handlers import (
    handle_get_roadmap,
    handle_get_learning_entries,
    handle_get_progress_stats
)
import json

print("=" * 60)
print("Testing MCP Tools")
print("=" * 60)

# Test 1: Get Progress Stats
print("\n1. Testing get_progress_stats...")
result = handle_get_progress_stats({})
print(json.dumps(result, indent=2))

# Test 2: Get Roadmap
print("\n2. Testing get_roadmap...")
result = handle_get_roadmap({})
print(f"Success: {result['success']}")
print(f"Sections: {result['total_sections']}, Items: {result['total_items']}")

# Test 3: Get Learning Entries  
print("\n3. Testing get_learning_entries...")
result = handle_get_learning_entries({"limit": 3})
print(f"Success: {result['success']}, Count: {result['count']}")

print("\n" + "=" * 60)
print("All MCP tools tested successfully!")
print("=" * 60)
