# Lab 10: How to evaluate an agent

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/10_Evaluation_Set/10_evaluation_set.ipynb)

**CPU | API key: `OPENAI_API_KEY`**

## Goal

Write test cases that say what the agent should do and what it must not do, and check each one from what the agent
did: the tools it called, their arguments, the write it paused on and what the Ops API recorded. The moment that
teaches it: asked what to do about a double charge, the copilot gives the right rule with the right citation, and
the case still fails, because it also called `find_customer` with the name `'<ticket>'`, a lookup nobody asked for
(15 of 16 runs on `gpt-4o-mini` made a lookup like it). Asked to file a refund for Helena without an invoice number,
it proposes a refund on an invoice it picked itself (11 of 16 runs).

## What you will learn

- How to write a test case as a dict: the input, the tools the agent must call and with which arguments, the tools
  it must never call, and what the reply must say.
- How to read the tool calls and their arguments from the agent's messages, and check a case with a plain function.
- How to cover seven kinds of case: answerable, not in the documents, read-only lookup, missing argument, action not
  approved, tool failure and out of scope.
- How to check a write from the approval pause and the Ops API's table instead of the reply.
- How to label each run yourself before any check, and ask a model judge whether a reply is grounded in what the tools
  returned.
- How to note tokens and time per case beside its result.

## Coming from

Lab 05 turned the Ops API into tools, Lab 08 gave the copilot `search_policies`, and Lab 09 put the refund tool behind
`HumanInTheLoopMiddleware`. This lab builds that copilot from `shared/` and tests it; you can start here.

## What you will do

**Part A: Write one case and run it.** Helena's invoices as a dict; the copilot with its five tools and the approval
pause; one run, read as a trace.
**Part B: Check the case from the messages.** `tool_calls`, `check_calls` and `check_reply` as plain functions; the
double-charge question, whose reply passes and whose trace fails.
**Part C: Write the seven kinds of case.** Five more dicts; `run_case`, which rejects every proposed write, can take
the Ops API down, and reads the API's table before and after.
**Part D: Label the runs, then score them.** Your labels first (the cell stops until every case has one), then the
check on all seven, case by case, with a write that never paused failed.
**Part E: Ask a model judge whether each reply is grounded.** A rubric, a structured verdict, the tool results as
evidence, one judge call per case beside your label.
**Part F: Note tokens and time per case.** One row per case: check, judge, label, model calls, tokens, seconds.
**Going further.** The judge's quotes checked in code; the judge three times per case; the packaged versions of
this loop.
**Challenge.** From starter cells: test one proposed improvement on the whole set, and say whether the evidence
supports keeping it. Optional: a case of your own; an approved action that must leave one row.

## Checkpoints

| After | You should see |
|---|---|
| Part A | five tools; a trace with `find_customer` for *Helena Holý*, `get_customer_invoices` for customer 6, a reply with 7 invoices and 49.62 |
| Part B | `check(lookup, messages)` returns `[]`; the double-charge reply cites `[policy_refunds.md]` and passes `check_reply`; the full check lists a lookup nobody asked for (most runs) |
| Part C | seven traces; *not approved* paused on `file_refund_request` with invoice 9002 and 9.99; no new row in the table |
| Part D | seven labels and seven check results; ours agree on all seven: *answerable*, *not in docs*, *missing argument* (a refund proposed on invoice 404) and *out of scope* fail |
| Part E | *not in docs* fails with the invented price-matching rule listed; seven verdicts beside your labels (ours match five, two of them for a wrong reason; the judge fails *not approved* over a claim the rejection supports and passes the poem, which it cannot see) |
| Part F | one row per case with model calls, tokens and seconds (ours: the poem cheapest at one call and 918 tokens, *missing argument* dearest at five calls and 6,877 tokens) |

The saved outputs come from `gpt-4o-mini` on 13 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`). Model runs vary,
and differ again if `models.env` names another model: compare which case failed and why, not our counts.

## Before you start

- **Lab 00 first.** It starts the Ops API this lab uses and checks your key.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** `data/chinook.db`, read by the Ops API; the policy files in `data/corpus/`, embedded on first use by
  `search_policies`. Invoices 9001 and 9002 (ticket 14) are a course fixture inside `shared/ops_api.py`. No refund is
  filed: every proposed write is rejected.
- **Cost:** about 26 calls to the chat model, 8 to the judge (21 more in Going further) and a few
  embedding calls: well under one US cent with `gpt-4o-mini`.

The notebook ends with a troubleshooting table: a missing label, tools left pointing at the stopped API, a check that
disagrees with your label, a judge that disagrees with you, and a missing key.

## Resources

- [LangChain: agent evals](https://docs.langchain.com/oss/python/langchain/test/evals): evaluators over an agent's trajectory, trajectory match modes and an LLM judge
- [LangSmith: evaluation concepts](https://docs.langchain.com/langsmith/evaluation-concepts): offline and online evaluation, datasets, code evaluators, LLM-as-judge and human review
- [LangSmith: how to evaluate an agent's intermediate steps](https://docs.langchain.com/langsmith/evaluate-on-intermediate-steps): scoring what happened inside a run, not only its output
- [OpenAI: evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): eval design for single agents, function call accuracy, and how to set up and validate an LLM judge
- [OpenAI: trace grading](https://developers.openai.com/api/docs/guides/trace-grading): grading an agent's whole trace of model and tool calls
- [Zheng et al., Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (2023)](https://arxiv.org/abs/2306.05685): position, verbosity and self-enhancement bias in model judges

Next: [Lab 11, how to measure an agent's latency and cost](../11_Latency_Streaming_And_Cost/README.md). Back to [the lab list](../README.md).
