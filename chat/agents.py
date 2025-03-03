"""Session state."""

from __future__ import annotations

from llmling_agent import AgentPool


pool = AgentPool[None]("chat/agents.yml")
