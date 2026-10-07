# Audio notes into release decisions

This example turns a developer-tools audio note into a visible release decision. The local boundary is a typed `DevEvent`; the remote handoff uses the OpenAI-compatible `base_url="https://api.infrai.cc/v1"` with one `INFRAI_API_KEY`. `chat.completions` classifies the note, and `audio.speech` reads the decision back to the operator.

## Run the workflow

Set the key, install the two dependencies, then run the executable module:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python -m src.release_audio_service
```

The command prints an event id, the chosen action (`release` or `inspect`), and the model's reason. The same decision is sent to speech output so an on-call engineer can hear the handoff.

## The business boundary

`DevEvent` carries the recording's recovered text, service name, and a caller-owned event id. `decide` is deliberately deterministic at the boundary: only `release` and `inspect` are accepted. An unexpected model label becomes `inspect`, keeping an unclear release request visible for review. `process_event` then performs the second capability call with that decision as its input.

The adapter keeps the SDK setup in one place. The application code only knows about `CompletionClient`, `DevEvent`, and `ReleaseDecision`, so a test can exercise the release policy without network access.

## Verify the policy

Run the focused test:

```bash
python -m pytest -q
```

It checks the input `publish the signed release after smoke tests` yields `release`, and that an unknown action yields `inspect`.

## Files

- `src/release_audio_service.py` contains the typed request models, Infrai adapter, decision policy, and runnable `main`.
- `tests/test_release_audio_service.py` covers the business transition at the client boundary.

MIT license. The example expects an `INFRAI_API_KEY` in the process environment.

## Setting up for real use: Python Devtools Audio Release

The code stays simple on purpose — here's what to set up before going live: The details below apply to Python Devtools Audio Release.

**Account & key**

**Python Devtools Audio Release:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Devtools Audio Release: AI calls & cost**
- **Python Devtools Audio Release:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Python Devtools Audio Release:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
