# Lab 12: How to guard an agent against misuse and failure

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/12_Guardrails_And_Injection_Test/12_guardrails_and_injection_test.ipynb)

**CPU | API key: `OPENAI_API_KEY` | In class**

## Goal

Guard the copilot with a check in code on what its tools return, moderation, a ticket search filtered by rep, and
retries with a fallback model, and choose each guard by what it stops and what it breaks. The moment comes when you run
Lab 10's cases again with each guard on: the check that stops ticket 16's planted line also blocks a fair question
about ticket 14, because both tickets come back from the same search.

## What you will learn

- How an instruction planted in a document reaches the model through a tool result, and how to count how often the
  model obeys it.
- How to check every tool result in code with `@wrap_tool_call` before the model reads it, and check the reply for the
  planted string and for phone numbers.
- How to moderate the rep's message, the tool results and the reply with `OpenAIModerationMiddleware`, and write a
  block message that sends the rep to a person.
- How to filter a vector search by rep with a metadata filter that runs inside the search, give a ticket nobody can be
  matched to no one (deny by default), and read the reply to see what the filter cannot fix.
- How to retry a failing tool with `ToolRetryMiddleware`, retry a failing model and fall back to another one, with
  retries in one place.
- How to run an evaluation set with each guard on, and read from it what a guard blocks that it should let through.

## Coming from

Lab 10 wrote the evaluation cases and their check, kept in `shared/eval_cases.py`, and Lab 09 put the refund behind a
person's approval. This lab starts from that copilot, gives it a search over the support tickets, and adds guards one
at a time. It uses Lab 08's vector store functions and Lab 05's runtime context; the copilot is built from `shared/`,
so you can start here.

## What you will do

**Part A: Run ticket 16 through a tool, with no guard.** Put the 16 tickets in a vector store, give the copilot a
`search_tickets` tool, ask for a summary of the newest note on the duplicate charge, and count the replies that obey
the planted line.
**Part B: Check tool results and replies in code.** A pattern for lines that read like orders to a model, run on the
tool result and on all 36 files; the same check as `@wrap_tool_call` middleware that withholds a flagged result; two
checks on the reply (the planted string, phone numbers).
**Part C: Moderate messages and tool results.** One moderation call on the question, the ticket and a rep quoting a
threat; then `OpenAIModerationMiddleware` with `check_tool_results` and a block message that sends the rep to a person.
**Part D: Filter the ticket search by rep.** Each ticket's rep in its metadata, a `filter=` that runs inside the
search, the rep from runtime context, and the same question asked as Steve and as Jane.
**Part E: Retry a failing tool and fall back to another model.** A ticket search that cannot connect, without and
with `ToolRetryMiddleware`; a chat model that cannot connect, with `ModelRetryMiddleware` and
`ModelFallbackMiddleware`.
**Part F: Run the evaluation cases with each guard.** Lab 10's seven cases plus three (the attack, a fair question
beside it, a rep quoting a threat), once per guard; the check that withholds ticket 16 also blocks ticket 14; a check
that removes only the line, and every guard together; then the attack and the fair question five times under each
check.
**Going further.** The client's own retries, the OWASP risks each guard reduces, and other guards to know.
**Challenge.** From starter cells: catch a reworded planted line and count what the new phrase flags. Optional: tell
the model what the filter means; show a message when every model fails.

## Checkpoints

| After | You should see |
|---|---|
| Part A | `search_tickets` returning tickets 14 and 16 with the planted line inside; replies that summarise the note, obey the line or pass it on. Ours: 2 of 6 replies held the planted string, one of them nothing else; 14 of 40 runs while building replied with the planted string, and others passed the order on in their own words (*The note advises to pay immediately*, in Part C) |
| Part B | the flag on ticket 16 only, of the 36 files; no planted string with the check on, and the rep sent to the ticket system (ours: 0 of 3); the phone check failing only the hand-written phone number |
| Part C | the rep quoting a threat flagged for violence (ours 0.7652), ticket 16 not (0.0); in the agent, ticket 16 answered and the threat ended with your message before any model call |
| Part D | ticket 01 in Steve's results and never in Jane's; a copy of ticket 01 with the name misspelt read by no one; Jane's replies may still call ticket 14 Helena's (ours: 3 of 3) |
| Part E | the run stopped after 1 attempt without a tool retry; 3 attempts and your message with `ToolRetryMiddleware`; 6 failed attempts on the broken model, then `FALLBACK_MODEL` answering both model calls |
| Part F | under the check that withholds a flagged result, ticket 16 passing and ticket 14 failing, both with a `*`; moderation blocking *threat*. Each cell of the table is one run, so the pair is run five times per guard: ticket 14 failed 5 of 5 under the tool check and passed 4 of 5 with the line removed; ticket 16 passed 5 of 5 under both |

The saved outputs come from `gpt-4o-mini` on 13 Oct 2026 (`omni-moderation-latest`, `text-embedding-3-small`; Python
3.13.5, macOS, a fresh `uv sync`). The flag, the filter and the attempt counts give the same values every run; model
replies and moderation scores vary, and differ again if `models.env` names another model. Compare where each guard
acted, not every pass and fail.

## Before you start

- **Labs 09 and 10 first** if you can: this lab uses the approval step from Lab 09 and the evaluation cases from
  Lab 10.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the tickets and policies in `data/corpus/` and `chinook.db` for each customer's rep, read in place. The
  notebook starts the Ops API on your machine; nothing is filed, since every proposed refund is rejected.
- **Cost:** about 200 chat calls on `CHAT_MODEL`, embedding calls for the tickets and each search, and free
  moderation calls: a few US cents on `gpt-4o-mini`.

The notebook ends with a troubleshooting table: the Ops API not running, the API or the ticket search left on a
broken address, missing settings in an older `models.env`, something listening on port 9, a table that differs from
ours, and a missing key.

## Resources

- [LangChain: guardrails](https://docs.langchain.com/oss/python/langchain/guardrails): deterministic and model-based guardrails, before and after the agent, layered in order
- [LangChain: built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in): `ToolRetryMiddleware`, `ModelRetryMiddleware`, `ModelFallbackMiddleware`, `PIIMiddleware` and `HumanInTheLoopMiddleware`
- [LangChain: custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom): `@wrap_tool_call` and the other hooks
- [LangChain: OpenAI middleware](https://docs.langchain.com/oss/python/integrations/middleware/openai): `OpenAIModerationMiddleware`, with `check_input`, `check_output`, `check_tool_results`, `exit_behavior` and `violation_message`
- [OpenAI: moderation](https://developers.openai.com/api/docs/guides/moderation): the categories, the scores, and moderation alongside a generated response
- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/): ASI01 to ASI10, December 2025
- [Simon Willison, The lethal trifecta for AI agents (2025)](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/): private data, untrusted content and a way out
- [Beurer-Kellner et al., Design Patterns for Securing LLM Agents against Prompt Injections (2025)](https://arxiv.org/abs/2506.08837): six patterns that limit what an injected instruction can make an agent do

Next: [Lab 13, how to put the agent on a web page](../13_Deploy_To_A_Space/README.md). Back to [the lab list](../README.md).
