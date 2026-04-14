"""Tests for AI chatbot proxy endpoint."""
import os
import pytest


class TestChatEndpoint:
    def test_chat_returns_reply(self, client):
        """Chat endpoint should always return a reply (even if AI providers fail)."""
        payload = {
            "messages": [
                {"role": "user", "text": "What is a fake account?"}
            ]
        }
        resp = client.post("/api/chat", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert len(data["reply"]) > 0

    def test_chat_with_conversation_history(self, client):
        """Should accept multi-turn conversation history."""
        payload = {
            "messages": [
                {"role": "user", "text": "What does SHAP mean?"},
                {"role": "assistant", "text": "SHAP stands for SHapley Additive exPlanations."},
                {"role": "user", "text": "How does it help?"},
            ]
        }
        resp = client.post("/api/chat", json=payload)
        assert resp.status_code == 200
        assert "reply" in resp.json()

    def test_chat_empty_messages_fails(self, client):
        """Empty messages list should still work (no crash)."""
        payload = {"messages": []}
        resp = client.post("/api/chat", json=payload)
        # Should either succeed with a fallback or return 200
        assert resp.status_code == 200

    def test_chat_invalid_payload(self, client):
        """Missing required fields should return 422."""
        resp = client.post("/api/chat", json={"wrong_field": "value"})
        assert resp.status_code == 422

    def test_chat_fallback_message(self, client):
        """When no API keys are configured, should return a helpful fallback."""
        # In test mode, API keys may not be set — the endpoint should still
        # return a fallback reply rather than crashing
        payload = {
            "messages": [
                {"role": "user", "text": "Hello"}
            ]
        }
        resp = client.post("/api/chat", json=payload)
        assert resp.status_code == 200
        reply = resp.json()["reply"]
        assert isinstance(reply, str)
        assert len(reply) > 10  # Should be a meaningful response, not empty
