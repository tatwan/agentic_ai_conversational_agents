# Lab 11: How to measure an agent's latency and cost

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/11_Latency_Streaming_And_Cost/11_latency_streaming_and_cost.ipynb)

**CPU | API key: `OPENAI_API_KEY` | Self-study**

## Goal

Time a streamed reply to its first words, keep a ledger of every model call, and price each case from its tokens. The
moment that teaches it: the fastest case in the set, a reply about an expired download link, is fast because the
copilot never searched the handbook, and its check fails (3 of 3 runs on `gpt-4o-mini`). A timing means little until you know the
answer was right.

## What you will learn

- How to time one call with `time.perf_counter`, and a streamed reply to its first words, counting only the model's
  own text.
- How to time the Lab 10 cases with each check printed beside its seconds, and report the spread over a few runs.
- How to keep a ledger of every model call with a callback, including the summariser's calls that the saved thread
  does not show.
- How to price a call and a case from `usage_metadata` and the prices in `models.env`, with cached tokens at the cached
  price and reasoning tokens as output.
- How to tell when OpenAI's prompt cache was used, and what a `prompt_cache_key` changes.

## Coming from

Lab 10 wrote test cases for the copilot and a `check` for each; this lab times and prices the same cases. The cases
and the check are kept in `shared/eval_cases.py` and the copilot is built from `shared/`, so you can start here. It
uses Lab 03's `SummarizationMiddleware`, Lab 06's `Meter` and Lab 09's approval pause.

## What you will do

**Part A: Time one call.** `time.perf_counter` around one model call, then around one agent turn with `invoke`.
**Part B: Time a streamed reply to its first words.** Read what `stream(..., stream_mode="messages", version="v2")`
sends, catch a timer that counts the tool's JSON as the first words, fix it, and turn it into `stream_turn`.
**Part C: Time the evaluation cases with their checks.** Lab 10's seven cases plus one of your own, three runs each,
with the check beside every timing, and the failing runs printed.
**Part D: Keep a ledger of every model call.** Start from Lab 06's `Meter`, write a `Ledger` with one row per call and
every kind of token, and count a summarising conversation from the saved thread and from the ledger.
**Part E: Price a call and a case.** The prices from `models.env`, one call by hand, `call_cost`, the conversation
both ways, and every case beside its check.
**Part F: Read the prompt cache.** A short and a long prompt five times each, with and without a `prompt_cache_key`.
**Going further.** Reasoning effort and reasoning tokens on `REASONING_MODEL` (empty by default, so it is skipped), `stream_events`
(v3), tags and metadata, LangSmith, and `ModelCallLimitMiddleware`.
**Challenge.** From starter cells: make the fast case pass and time it again. Optional: a token budget per thread
with a handover; how steady the spread is over ten runs.

## Checkpoints

| After | You should see |
|---|---|
| Part A | Helena's question: three model calls, 7 invoices, 49.62 |
| Part B | a first text from the `tools` node, then the fixed timer's first text later (ours: 1.13 s from `tools`, then 2.57 s) |
| Part C | a check beside every timing; *expired link* among the fastest, with no search and a failed check (ours: *expired link* fastest at about 1 s, 0 of 3 passed) |
| Part D | fewer calls in the saved thread than in the ledger, one `summarization` (ours: 5 calls in the thread, 9 in the ledger) |
| Part E | the same cost by hand and by `call_cost`; a cost beside each case's check (ours: $0.000124 both ways; *lookup* $0.000398 a case) |
| Part F | the short prompt never cached; the long one more often with a key (ours: 0 of 5; 0 of 5 without a key, 4 of 5 with one) |

The saved outputs come from `gpt-4o-mini` on 13 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`). Seconds depend on
your network and load, and model runs vary, and differ again if `models.env` names another model: compare which cases
are fast and whether they passed, not our seconds.

## Before you start

- **Lab 00 first.** It starts the Ops API this lab uses and checks your key.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Prices:** `models.env` holds the chat model's prices with their check date. Check them on OpenAI's pricing page
  before you teach, and change them there if you change the model.
- **Optional:** the reasoning demo in Going further runs only when `REASONING_MODEL` is set (empty in `models.env`;
  set it there or in `.env` to a reasoning model your account allows, with its prices). LangSmith needs `LANGSMITH_API_KEY` and `RUN_LANGSMITH = True`.
- **Data:** `data/chinook.db`, read by the Ops API, and the policy files in `data/corpus/`, embedded on first use by
  `search_policies`. No refund is filed: every proposed write is rejected.
- **Cost:** about 130 calls to the chat model and 150,000 input tokens, about 3 US cents with `gpt-4o-mini` (counted from the run's structure). With `REASONING_MODEL` set, Going further adds 9 calls to it, about 2 US cents with `gpt-5`.

## Resources

- [LangChain: streaming](https://docs.langchain.com/oss/python/langchain/streaming): stream modes, `version="v2"`, streaming tool calls and progress
- [LangChain: event streaming](https://docs.langchain.com/oss/python/langchain/event-streaming): `stream_events(version="v3")` and its projections
- [LangChain: models, token usage](https://docs.langchain.com/oss/python/langchain/models): `usage_metadata` and `UsageMetadataCallbackHandler`
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): `SummarizationMiddleware`, `ModelCallLimitMiddleware`
- [OpenAI: latency optimization](https://developers.openai.com/api/docs/guides/latency-optimization): principles for making a model app answer sooner, streaming among them
- [OpenAI: prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching): the minimum prefix, `cached_tokens`, cache writes, `prompt_cache_key`, differences by model
- [OpenAI: reasoning models](https://developers.openai.com/api/docs/guides/reasoning): reasoning effort and `reasoning_tokens` in the usage
- [OpenAI: pricing](https://developers.openai.com/api/docs/pricing): the current price per model
- [LangSmith: observability](https://docs.langchain.com/oss/python/langchain/observability): tracing an agent with two environment variables

Next: [Lab 12, how to guard an agent against misuse and failure](../12_Guardrails_And_Injection_Test/README.md). Back to [the lab list](../README.md).
