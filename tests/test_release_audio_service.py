from src.release_audio_service import DevEvent, ReleaseDecision, decide


class StubClassifier:
    def __init__(self, result: tuple[str, str]) -> None:
        self.result = result

    def classify(self, transcript: str) -> tuple[str, str]:
        return self.result


def test_release_event_keeps_publish_action_visible() -> None:
    event = DevEvent("evt-7", "publish the signed release after smoke tests", "billing-api")
    decision = decide(event, StubClassifier(("release", "smoke tests passed")))
    assert decision == ReleaseDecision("release", "smoke tests passed", "evt-7")


def test_unknown_model_action_routes_to_inspection() -> None:
    event = DevEvent("evt-8", "the deploy signal is ambiguous", "billing-api")
    decision = decide(event, StubClassifier(("later", "needs context")))
    assert decision.action == "inspect"
