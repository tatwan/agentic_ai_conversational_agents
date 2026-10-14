# Lab 08: How to give an agent a document search tool

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/08_RAG_Citations_Abstention/08_rag_citations_abstention.ipynb)

**CPU | API key: `OPENAI_API_KEY` | In class**

## Goal

Give an agent a tool that searches the support handbook, so that it answers rule questions from the handbook, names
the file each rule came from, and says so when the handbook has no answer. The moment that teaches it: asked for a
warmer greeting, the agent does not search; asked about a duplicate charge, it searches and cites
`policy_refunds.md`; asked whether Chinook matches a lower price, which no policy covers, it searches, finds nothing
that answers, and says the handbook does not cover it (5 of 5 runs for each question on `gpt-4o-mini`).

## What you will learn

- How to load the handbook into a vector store, with each section's file and title as metadata.
- How to answer from the handbook in two steps by hand: search in your code, then one model call with the passages.
- How to give an agent the same search as a tool, and see when it decides to call it.
- How to make the agent cite its sources and say when the handbook has no answer.
- How to check citations and abstention in code, from the files the tool returned.
- How to catch a citation that does not support its claim, with a quote your code looks up.

## Coming from

Lab 01 gave the copilot `get_policy`, which needs the policy's name. This lab gives it a search that finds the policy
from the rep's own words, built in the notebook with LangChain's `InMemoryVectorStore`. The self-study Lab 07 shows
how that kind of search works inside (FAISS, scores, chunking); this lab does not need it. You reuse `create_agent`
and tools from Lab 01.

## What you will do

**Part A: Load the handbook into a vector store.** Split the handbook at its headings, keep each section's file and
title as metadata, and embed the 20 sections into `InMemoryVectorStore`.
**Part B: Search, then answer in two steps.** A plain `search` function, a shorter query that pushes the right
section down to fourth, and one model call with the passages.
**Part C: Give the agent the search as a tool.** `search_policies` returns the passages for the model and the files
and scores as an artifact for your code; the agent searches for the duplicate charge and not for the greeting.
**Part D: Cite the file each rule came from.** One prompt line adds citations; on the price question the agent
answers with a rule the handbook does not have and cites a real file.
**Part E: Say when the handbook has no answer.** One more prompt line; five runs of each question.
**Part F: Check citations and abstention in code.** Cited files against retrieved files, an abstention check, and
the made-up answer that passes the citation check.
**Part G: Catch a citation that does not support its claim.** A quote for every claim, looked up in its passage, with
the agent filling a `CitedAnswer`.
**Going further.** The whole handbook in the prompt with cached tokens counted; the same search on Qdrant.
**Challenge.** From starter cells: a score threshold that abstains before any model call. Optional: a search limited
to some sections, and new test questions.

## Checkpoints

| After | You should see |
|---|---|
| Part A | 20 sections; metadata `{'source': 'policy_refunds.md', 'section': 'Refunds'}`; 20 documents in the store |
| Part B | top 4: `policy_refunds.md` 0.4807, `policy_damaged_media.md` 0.4515, `policy_exchanges.md` 0.4124, `policy_digital_downloads.md` 0.3906; the short query puts refunds fourth (0.3391); the reply gives the duplicate-charge rule |
| Part C | the artifact lists four files with scores; one search for the duplicate charge, none for the greeting |
| Part D | the duplicate charge cites `[policy_refunds.md]`; the price question gets an answer the handbook does not give, citing `[policy_exchanges.md]` (most often *We do not match lower prices from other stores*) |
| Part E | greeting: no search, 5 of 5; duplicate charge: the rule with its citation, 5 of 5; price match: *the handbook does not cover it*, no citation, 5 of 5 |
| Part F | every run passes its checks; Part D's made-up answer passes `cited files retrieved` and fails only `abstained` |
| Part G | the invented rule's quote and a blank quote are not found; the duplicate charge's quote is found 3 of 3; the greeting names a file that does not exist (ours: 2 of 3, flagged); ours set `covered False` on price matching 3 of 3 (an earlier run, 1 of 3) |
| Going further | whole handbook about 1,698 input tokens a question, 1,536 cached (ours: all 6 calls, the cache warm from an earlier run); the search tool about 544; Qdrant returns the same four files and scores |

The saved outputs come from `gpt-4o-mini` and `text-embedding-3-small` on 13 Oct 2026 (langchain 1.4.3, Python
3.13.5, macOS, a fresh `uv sync`). Search scores can move in the fourth decimal; replies change from run to run, so
check the files, the searches and the checks, not our wording. If `models.env` names another model, your counts may
differ: the checks in Part F tell you how.

## Before you start

- **Lab 00 first.** It checks that your key reaches the chat model. Lab 01 explains tools and the agent.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the handbook in `data/handbook/support_handbook.md`, read in place. The store lives in memory and is built
  again each time you run the notebook.
- **Going further** installs `langchain-qdrant` 1.1.0 if it is missing; the rest of the lab needs nothing beyond the
  repository's requirements.
- **Cost:** about 55 `gpt-4o-mini` calls and 40 embedding calls: under one US cent.

The copilot's later labs import the same search from `shared/copilot.py` (`search_policies`), built on
`InMemoryVectorStore` from the 20 policy files.

The notebook ends with a troubleshooting table: a tool that returns only text, a missing `langchain_qdrant`, a missing
key.

## Resources

- [LangChain: retrieval](https://docs.langchain.com/oss/python/deepagents/retrieval): two-step, agentic and hybrid RAG compared
- [LangChain: semantic search](https://docs.langchain.com/oss/python/langchain/knowledge-base): documents, embeddings and `InMemoryVectorStore`
- [LangChain: vector stores](https://docs.langchain.com/oss/python/integrations/vectorstores): the common interface, Qdrant, Chroma and others
- [LangChain: messages](https://docs.langchain.com/oss/python/langchain/messages): the tool message and its `artifact`
- [LangChain: structured output](https://docs.langchain.com/oss/python/langchain/structured-output): `response_format` on `create_agent`
- [Anthropic: reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations): allow "I don't know", ground answers in quotes
- [Anthropic: contextual retrieval](https://www.anthropic.com/engineering/contextual-retrieval): better retrieval, and when to send the whole knowledge base instead
- [OpenAI: prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching): when a long, repeated prompt is cached, and `prompt_cache_key`

Next: [Lab 09: How to ask a person before an agent acts](../09_Approval_Before_A_Write/README.md). Back to [the lab
list](../README.md).
