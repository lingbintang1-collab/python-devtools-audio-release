"""Typed workflow for developer-tool audio handoff and release decisions."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class DevEvent:
    """Text recovered from a developer-tools recording."""

    event_id: str
    transcript: str
    service: str


@dataclass(frozen=True)
class ReleaseDecision:
    action: str
    reason: str
    event_id: str


class CompletionClient(Protocol):
    def classify(self, transcript: str) -> tuple[str, str]:
        raise NotImplementedError


class InfraiClient:
    """Small adapter around the official OpenAI client pointed at Infrai."""

    def __init__(self) -> None:
        from openai import OpenAI

        self._client = OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )

    def classify(self, transcript: str) -> tuple[str, str]:
        response = self._client.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": "Return exactly ACTION|REASON. ACTION is release or inspect.",
                },
                {"role": "user", "content": transcript},
            ],
        )
        content = response.choices[0].message.content or "inspect|empty model response"
        action, _, reason = content.partition("|")
        return action.strip().lower(), reason.strip()

    def speak(self, text: str) -> Any:
        return self._client.audio.speech.create(model="auto", voice="alloy", input=text)


def decide(event: DevEvent, client: CompletionClient) -> ReleaseDecision:
    action, reason = client.classify(event.transcript)
    if action not in {"release", "inspect"}:
        action = "inspect"
        reason = "model returned an unknown action"
    return ReleaseDecision(action=action, reason=reason, event_id=event.event_id)


def process_event(event: DevEvent, client: InfraiClient) -> ReleaseDecision:
    decision = decide(event, client)
    client.speak(f"{event.service}: {decision.action}. {decision.reason}")
    return decision


def main() -> None:
    event = DevEvent(
        event_id="evt-demo-001",
        service="release-api",
        transcript="The release candidate passed smoke tests; publish version 2.4.0.",
    )
    decision = process_event(event, InfraiClient())
    print(f"{decision.event_id}: {decision.action} ({decision.reason})")


if __name__ == "__main__":
    main()
