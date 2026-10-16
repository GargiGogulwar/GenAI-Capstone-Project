"""Regression checks for the capstone's provider and evidence boundaries."""
from unittest.mock import Mock
import pytest
from pydantic import ValidationError
from app.core.config import settings, Settings
from app.core.groq import resolve_model, selector_models, GROQ_BASE_URL
from app.infrastructure.rag.retrieval import chunk_document
from app.application.agents.capstone import Plan, normalize_citations
from app.infrastructure.llm.client import LLMClient


def test_only_groq_models_are_selectable():
    assert all(item["provider"] == "groq" for item in selector_models())
    assert resolve_model("krait-2.0") == settings.groq_model
    assert resolve_model("anthropic/obsolete-model") == settings.groq_model


def test_legacy_routes_cannot_send_the_key_to_another_provider(monkeypatch):
    monkeypatch.setattr(settings, "groq_api_key", "gsk_test")
    cached = Mock()
    monkeypatch.setattr("app.infrastructure.llm.client._get_cached_client", cached)
    client = LLMClient("sk_old", "openrouter", "openrouter/auto")
    assert client.provider == "groq"
    cached.assert_called_once_with("groq", "gsk_test", settings.groq_model, base_url=GROQ_BASE_URL)
    with pytest.raises(ValueError, match="Custom AI endpoints"):
        LLMClient("gsk_test", "groq", settings.groq_model, base_url="https://example.com")


def test_configuration_accepts_standard_groq_variable(monkeypatch):
    monkeypatch.delenv("AI_GROQ_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "gsk_local_test")
    assert Settings(_env_file=None).groq_api_key == "gsk_local_test"


def test_chunks_preserve_unicode_evidence_and_line_locations():
    content = "\n".join(f"line {i}: λ = {i}" for i in range(500))
    chunks = chunk_document(content)
    assert len(chunks) > 1 and all(len(c["content"]) <= 1700 for c in chunks)
    assert chunks[0]["line_start"] == 1
    assert "line 499" in chunks[-1]["content"]
    assert all(c["content"] in content for c in chunks)
    assert all(a["line_end"] >= b["line_start"] for a, b in zip(chunks, chunks[1:]))
    with pytest.raises(ValueError):
        chunk_document(content, size=10, overlap=10)


def test_structured_planner_rejects_arbitrary_agents_and_unbounded_fanout():
    assert Plan.model_validate_json('{"specialists":["security"],"needs_tools":true}').needs_tools
    with pytest.raises(ValidationError):
        Plan(specialists=["shell_execution"])
    with pytest.raises(ValidationError):
        Plan(specialists=["security", "code", "architecture"])


def test_citations_are_normalized_and_unknown_ids_are_not_presented_as_sources():
    assert normalize_citations("Pool 12【S1】; invented [S99]", 1) == "Pool 12[S1]; invented [unverified source]"


@pytest.mark.asyncio
async def test_concurrency_limit_remains_held_until_stream_finishes():
    from app.api.dependencies import backpressure as bp
    bp.init_backpressure(max_llm=1)
    await bp.acquire_llm_slot()
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        await bp.acquire_llm_slot()
    await bp.release_llm_slot()
    await bp.acquire_llm_slot()
    await bp.release_llm_slot()


@pytest.mark.asyncio
async def test_conversation_owner_is_checked_before_reusing_history():
    from app.application.chat.conversation_repository import ensure_conversation
    from unittest.mock import AsyncMock
    from fastapi import HTTPException
    db = AsyncMock()
    result = Mock()
    result.scalar_one_or_none.return_value = Mock(user_id="owner", workspace_id="workspace")
    db.execute.return_value = result
    with pytest.raises(HTTPException):
        await ensure_conversation(db, "conversation", "intruder", "workspace")
    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_provider_tool_generation_is_retried_without_executing_it(monkeypatch):
    import httpx
    from openai import BadRequestError
    from unittest.mock import AsyncMock
    monkeypatch.setattr(settings, "groq_api_key", "gsk_test")
    client = LLMClient("gsk_test", "groq", settings.groq_fast_model)
    response = httpx.Response(400, request=httpx.Request("POST", GROQ_BASE_URL))
    invalid = BadRequestError("tool_use_failed", response=response, body={})
    generate = AsyncMock(side_effect=[invalid, ("safe answer", [], {
        "model": client.model, "provider": "groq", "input_tokens": 5, "output_tokens": 3})])
    monkeypatch.setattr(client, "_generate_once", generate)
    result = await client.generate([{"role": "user", "content": "list projects"}])
    assert result["content"] == "safe answer"
    assert generate.await_count == 2
    assert "No tools are available" in generate.call_args.args[0][0]["content"]
