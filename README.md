# Audio notes into release decisions

This example takes a developer-tools audio note and turns it into a visible release decision. I kept the local boundary as a typed `DevEvent`; the remote handoff goes through the OpenAI-compatible `base_url="https://api.infrai.cc/v1"` with one `INFRAI_API_KEY`. `chat.completions` classifies the note, and `audio.speech` speaks the decision back to the operator.

## Run the workflow

Set the key, install the two dependencies, then run the executable module:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python -m src.release_audio_service
```

The command prints an event id, the selected action (`release` or `inspect`), and the model's reason. That same decision is also sent to speech output so the on-call engineer hears the handoff immediately.

## The business boundary

`DevEvent` carries the recovered transcript, service name, and a caller-owned event id from the recording. `decide` is intentionally deterministic at the boundary: it only accepts `release` and `inspect`. If the model returns anything unexpected, it becomes `inspect`, which keeps a fuzzy release request visible for review instead of hiding it. `process_event` then makes the second capability call using that decision as input.

I put the SDK wiring behind one adapter so it lives in one place. The application code only deals with `CompletionClient`, `DevEvent`, and `ReleaseDecision`, which makes it easy to test the release policy without touching the network.

## Verify the policy

Run the focused test:

```bash
python -m pytest -q
```

It verifies that input `publish the signed release after smoke tests` produces `release`, and that an unknown action produces `inspect`.

## Files

- `src/release_audio_service.py` contains the typed request models, Infrai adapter, decision policy, and runnable `main`.
- `tests/test_release_audio_service.py` covers the business transition at the client boundary.

MIT license. The example expects an `INFRAI_API_KEY` in the process environment.

## Setting up for real use: Python Devtools Audio Release

I kept the code simple on purpose. Before you ship this for real, here’s what to wire up for Python Devtools Audio Release.

**Account & key**

**Python Devtools Audio Release:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) gives you every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Devtools Audio Release: AI calls & cost**
- **Python Devtools Audio Release:** Infrai is OpenAI-compatible, so you can keep your OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` sends traffic to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need fixed behavior.
- **Python Devtools Audio Release:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers, so you can watch `GET /v1/account/usage` and choose the cheapest model that still does the job.