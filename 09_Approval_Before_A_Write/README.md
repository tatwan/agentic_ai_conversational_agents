# Lab 09: How to ask a person before an agent acts

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/09_Approval_Before_A_Write/09_approval_before_a_write.ipynb)

**CPU | API key: `OPENAI_API_KEY` (Part A runs without one)**

## Goal

Make an agent stop before a tool that changes something, show a person the exact call, and continue with their
decision: approve, edit or reject. The moment that teaches it: the rep asks for a refund because two tracks on
Helena's invoice 46 skip, and the copilot proposes to refund all nine tracks, 8.91 dollars (12 of 12 runs on
`gpt-4o-mini`). The reviewer changes the amount to 1.98 before anything runs, and the Ops API files 1.98.

## What you will learn

- How to file a refund request through the Ops API by hand, and which requests its rules refuse or send to a manager.
- How to stop a hand-written agent loop before a write runs, and send a person's decision back as the tool's output.
- How to write a write tool that takes the rep from the run's context, and make it wait with
  `HumanInTheLoopMiddleware`.
- How to read the waiting call from `result.interrupts` and resume the same thread with approve, edit or reject.
- How to check what a write left behind in the API's own table, not only what the reply says.
- How to build an idempotency key so that a retried request files one refund, not two.

## Coming from

Lab 01 wrote the agent loop by hand on the Responses API, Lab 03 saved a thread with a checkpointer, Lab 05 turned
the Ops API's reads into tools with the rep in the run's context and retried failing calls, and Lab 08 gave the
copilot `search_policies`. This lab adds the first write: it introduces the refund tool, the API's own rules and the
idempotency key itself, and imports `get_invoice` and `search_policies` from `shared/`, so you can start here.

## What you will do

**Part A: File a refund request by hand.** Post a 120.00 request with `httpx` (filed as `needs_manager`), a 150.00
request (refused with a 422), and read the API's table of requests.
**Part B: Stop the loop before a write.** Lab 01's Responses loop with two JSON-schema tools; the loop returns a write
instead of running it; ticket 22 stops at a 120.00 refund, and you reject it by sending the reason back as the tool's
output.
**Part C: Pause with `HumanInTheLoopMiddleware` and approve.** The write tool with a `Literal` reason and the rep from
`ToolRuntime`; the middleware, a checkpointer and a `thread_id`; ticket 23 to the pause, the interrupt read, then
approved with `Command(resume=...)`.
**Part D: Edit or reject the waiting call.** Ticket 21: change 8.91 to 1.98 before it runs; ticket 22 rejected with a
reason; `respond` in one sentence.
**Part E: Make a retry file one refund.** Lose the API's first reply, let `ToolRetryMiddleware` retry: two rows for
one approval with random keys, one row with a key built from the thread, the invoice and the amount.
**Going further.** A review screen with a `description` function; a pause kept in a SQLite file across a restart, and
a decision sent to a mistyped thread.
**Challenge.** From starter cells: a key from the refund instead of the conversation. Optional: two refunds in one
step; a rejection without a reason.

## Checkpoints

| After | You should see |
|---|---|
| Part A | 120.00 on invoice 9003: `201`, `needs_manager`; 150.00: `Not filed: Amount 150.0 exceeds invoice total 120.0`; one row in the table |
| Part B | after one `get_invoice`, the loop stops with `file_refund_request` for invoice 9003, 120; no new row; after the rejection, a reply about a replacement disc |
| Part C | the schema without `runtime`; ticket 23 pauses at `file_refund_request` with invoice 175 and 1.98; after approval, a new row: 175, 1.98, `pending_review` |
| Part D | ticket 21 proposes the full 8.91 (12 of 12 runs); after the edit, the middleware's note and a row for invoice 46 at 1.98; ticket 22 rejected: status `error`, no new row |
| Part E | random keys: one approval, two rows for invoice 9002 at 9.99; key from the request: one row, the retry answered with `"replayed":true` |

The saved outputs come from `gpt-4o-mini` on 13 Oct 2026 (Python 3.13.5, macOS, a fresh `uv sync`). Part A gives the
same values every time. Model runs vary, and differ again if `models.env` names another model: compare the calls,
the amounts and the rows in the table, not our wording.

## Before you start

- **Lab 00 first.** It starts the Ops API this lab uses and checks your key.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** `data/chinook.db`, read by the Ops API; the policy files in `data/corpus/`, embedded on first use by
  `search_policies`. Invoices 9001 to 9003 are a course fixture inside `shared/ops_api.py`. The API writes refund
  requests to a temporary database, and Going further writes `lab09_approvals.sqlite` to your temporary folder.
- **Cost:** about 25 calls to the chat model and a few embedding calls: well under one US cent with `gpt-4o-mini`.

The notebook ends with a troubleshooting table: a run that never pauses, a missing `version="v2"`, the wrong number
of decisions (and a thread stuck after it), a resume on the wrong thread, and an API that is not running.

## Resources

- [LangChain: human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop): `interrupt_on`, the four decisions, `when`, and advice on edits and rejections
- [LangGraph: interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts): how a pause is saved and resumed with `Command(resume=...)`
- [LangGraph: persistence](https://docs.langchain.com/oss/python/langgraph/persistence): threads, checkpoints and the savers for production
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): `HumanInTheLoopMiddleware` and `ToolRetryMiddleware`
- [Stripe: idempotent requests](https://docs.stripe.com/api/idempotent_requests): idempotency keys for safe retries, and how long a payments API keeps them

Next: [Lab 10: How to evaluate an agent](../10_Evaluation_Set/README.md). Back to [the lab list](../README.md).
