from __future__ import annotations

SYSTEM_PROMPT = """You are a senior SDET generating maintainable pytest API tests.
Return only Python code. Do not include markdown fences.
Use the existing RestfulBookerClient from shared.tooling.api_tool.
Do not call requests directly.
Use environment-driven SSL behavior through the client.
Make tests deterministic by creating their own data when needed.
Avoid relying on public preloaded booking IDs.
"""

USER_PROMPT_TEMPLATE = """Generate pytest tests for this API contract and strategy.

Contract:
{contract}

Test strategy:
{strategy}

Required tests:
- ping/health check
- booking IDs list
- create and read booking
- create, patch, and delete booking with auth token

Return a single valid Python test module.
"""
