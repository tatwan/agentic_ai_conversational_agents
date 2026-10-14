# Lab 07: How to search documents by meaning

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/07_FAISS_Index_Handbook/07_faiss_index_handbook.ipynb)

**CPU | API key: `OPENAI_API_KEY` (Part B runs without one) | Self-study**

## Goal

Search the support handbook by meaning, and know what a search score can and cannot tell you. The moment that teaches
it: the search returns three chunks with scores for every question, and the best score is not a reliable sign that the
handbook covers the question. *Do we take Bitcoin?*, which the payment policy answers, scores 0.3248, about the same as
*Do we match a lower price from another store?* (0.3253), which no policy covers. *Can a customer pay in monthly
instalments?*, also not covered, scores 0.4915, higher than five of the twelve covered questions.

## What you will learn

- How to compute cosine similarity by hand.
- How to split a handbook by size and by heading, and choose by where a rule lands and which file its chunk names.
- How to build, save, load and search an exact FAISS index of the handbook.
- How to predict the top file for a question, check it, and explain a miss from what each chunk holds.
- How to test, on labelled questions, whether a score can tell a covered question from an uncovered one.
- What FAISS leaves to you (the text, the metadata, a filter by rep), which a vector store takes over.

## Coming from

Until now the copilot read a policy only when it could name the file (`get_policy("refunds")`). This lab builds the
search that finds a policy from the rep's own words. It is self-study: no other lab needs it, and Lab 08 builds its own
search with LangChain's `InMemoryVectorStore`. FAISS is taught here as the fundamental, the bare vector search inside
every vector store. The lab uses only `EMBED_MODEL` from `models.env` and calls no chat model.

## What you will do

**Part A: Measure closeness with cosine similarity.** Dot product, lengths and cosine on two-number vectors, then on
three rep questions embedded with one raw OpenAI call.
**Part B: Split the handbook two ways.** By size (`RecursiveCharacterTextSplitter`) and by heading
(`MarkdownHeaderTextSplitter`), and find where the duplicate-charge rule lands in each.
**Part C: Build an exact index with FAISS.** `IndexFlatIP` on toy vectors, raw and normalised, then on the handbook's
20 chunks, and a `search` function.
**Part D: Save the index and load it back.** The index file and the chunk texts beside it.
**Part E: Predict the top file, then search.** Four rep questions, and why question 4 misses.
**Part F: Test whether a score shows the handbook covers a question.** 18 questions labelled before the search, and
four thresholds.
**Part G: Keep the text and metadata, and filter by rep.** What the index does not store, a filter after the search and
a filter inside it, and what a vector store takes over.
**Going further.** BM25 and reciprocal rank fusion by hand; approximate indexes (HNSW, IVF).
**Challenge.** From starter cells: reword question 4 and see whether the wording decides the top file. Optional:
split by heading, then by size; test a threshold on new questions.

## Checkpoints

| After | You should see |
|---|---|
| Part A | toy cosines A 1.0, B 0.7071; `(3, 1536)`, lengths 1.0; cosines 1–2 0.7059, 1–3 0.1140, 2–3 0.2407 |
| Part B | split A: 10 chunks, the rule whole in chunk 6 with `policy_returns.md` and `policy_shipping.md`; split B: 20 chunks, the rule in chunk 13 with `policy_refunds.md` |
| Part C | `ntotal 20`, `d 1536`; the bought-twice question: `policy_refunds.md` 0.4423, `policy_damaged_media.md` 0.3792, `policy_digital_downloads.md` 0.3496 |
| Part D | `handbook.faiss` 122,925 bytes; the loaded index has the same vectors and returns the same files |
| Part E | questions 1–3 rank the answering file first; question 4 ranks `policy_shipping.md` (0.3875) above `policy_international.md` (0.3680) |
| Part F | lowest covered score 0.3248 (Bitcoin), highest uncovered 0.4915 (instalments); no threshold separates them |
| Part G | filtering after the search leaves Jane Peacock no ticket; filtering inside returns Jane's one ticket, 0.2321 |
| Going further | answering file first: vector 11, BM25 10, hybrid 11 of 12 |

The saved outputs come from `text-embedding-3-small` on 12 Oct 2026 (faiss-cpu 1.15.1, Python 3.13.5, macOS, a fresh
`uv sync`). Part B and the toy steps call no model, so their values are exact. Embedding scores can move in the fourth
decimal between runs: check the order of the files.

## Before you start

- **Lab 00 first.** It checks that your key reaches OpenAI.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel.
- **Data:** the handbook in `data/handbook/support_handbook.md` and the tickets in `data/corpus/`, read in place. Your
  index is saved in `07_FAISS_Index_Handbook/my_index/`, which git ignores.
- **Cost:** about 45 embedding calls, under 10,000 tokens: well under a cent. No chat model.

The notebook ends with a troubleshooting table: a missing index file, a query embedded with another model, an array
that is not `float32`.

## Resources

- [OpenAI: embeddings guide](https://developers.openai.com/api/docs/guides/embeddings): models, vector length, cosine and dot product
- [OpenAI: retrieval guide](https://developers.openai.com/api/docs/guides/retrieval): hosted vector stores, `score_threshold`, hybrid ranking
- [LangChain: text splitters](https://docs.langchain.com/oss/python/integrations/splitters) and [split markdown by headers](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter)
- [LangChain: vector stores](https://docs.langchain.com/oss/python/integrations/vectorstores): `InMemoryVectorStore`, Qdrant, Chroma and the common interface
- [FAISS wiki: guidelines to choose an index](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index): flat indexes, HNSW and IVF
- [Anthropic: contextual retrieval](https://www.anthropic.com/news/contextual-retrieval): BM25 with embeddings, reranking, and when to send the whole knowledge base

Next: [Lab 08: How to give an agent a document search tool](../08_RAG_Citations_Abstention/README.md). Back to [the lab
list](../README.md).
