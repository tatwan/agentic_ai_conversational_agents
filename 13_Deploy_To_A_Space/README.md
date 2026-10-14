# Lab 13: How to put the agent on a web page

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tatwan/agentic_ai_conversational_agents/blob/main/13_Deploy_To_A_Space/13_deploy_to_a_space.ipynb)

**CPU | API key: `OPENAI_API_KEY` (Part A and the sign-in check in Part E run without one) | Hugging Face account: only for the optional push in Part F | In class**

## Goal

Serve Lab 12's guarded copilot as a chat page that several reps can use at once, each in their own conversation, and
prepare the folder a Hugging Face Space builds from. The moment comes in Part B: with one thread id for the whole page,
a second rep who asks which customer they are working on gets the first rep's customer and invoices.

## What you will learn

- How to turn a Python function into a chat page with Gradio's `ChatInterface`, and test it from code as several
  visitors with `gradio_client`.
- How to give each visitor their own conversation by using the browser session as the agent's `thread_id`.
- How to stream progress (the tool steps) and hold the reply until its check has passed.
- How to approve or reject a refund inside the chat, with a button or a typed reason.
- How to keep the key out of your files and put a password in front of a page.
- How to assemble the folder a Hugging Face Space builds from, check it, and run it the way the Space will.

## Coming from

Lab 12 guarded the copilot: moderation, a check that removes planted lines from tool results, a ticket search
filtered by rep, retries and a fallback model, with Lab 09's approval before the refund. This lab puts that copilot,
unchanged, behind a web page. It builds the copilot from `shared/`, so you can start here.

## What you will do

**Part A: Put a function behind a chat page.** An echo function behind `gr.ChatInterface`, two visitors driven from
code with `gradio_client`, the `history` Gradio passes, and the session id each visitor gets.
**Part B: Put the copilot behind the page, one thread per visitor.** Lab 12's guarded copilot behind the page, first
with one thread id for everyone, then with the visitor's session as the thread; then the same in two browser tabs.
**Part C: Stream progress, and hold the reply until its check passes.** A page that streams the reply word by word,
and one that streams the tool steps as folded messages and shows the reply after Lab 12's check; a scripted model
that always obeys ticket 16 shows what each page puts on the screen.
**Part D: Approve a refund inside the chat.** The page function that joins every piece: a waiting refund with
Approve and Reject buttons, one approval, a question while a refund waits (the page reminds the rep and leaves the
thread alone), one rejection with a typed reason, the API read back, and a reload while a refund waits.
**Part E: Keep the key secret and put a password on the page.** Where the key lives, and a sign-in checked from code.
**Part F: Prepare the folder a Space builds from.** The template in `space/` and its header, the app checked against
the notebook, the folder assembled and checked, and `app.py` run as the Space runs it, without and with a key. The
push is optional.
**Going further.** A public share link behind a password, and the folder check on a broken copy.
**Challenge.** From starter cells: keep a waiting refund across a reload with a sign-in, and read each visitor's
thread. Optional: check the reply a sentence at a time.

## Checkpoints

| After | You should see |
|---|---|
| Part A | the echo page counting 0, then 2, for one visitor and 0 for a new one; one session id per visitor |
| Part B | with one thread for everyone, rep B's reply naming Helena Holý, whom only rep A asked about (ours: 6 of 6 runs); with the session as the thread, rep B asked for a customer (0 of 6 named her) |
| Part C | word by word, the first words after a few seconds (ours: 4.3 s), and the scripted model's planted string shown before the check replaced it; with the tool steps streamed, a folded step first (ours: 1.4 s), the reply whole, and the scripted string never shown |
| Part D | ticket 14 paused with a refund for one invoice (ours: 9.99 for invoice 9002), with Approve and Reject buttons; *approve* filing it as `pending_review`; a question while it waits getting the page's reminder; *reject:* with a reason filing nothing; after a reload, nothing filed |
| Part E | without the password, 401 and `AuthenticationError`; with it, a reply that greets `jane` |
| Part F | the header with `sdk: gradio`, `sdk_version: 6.29.0`, `python_version: "3.13"`, `app_file: app.py`; seven functions the same in the notebook and `app.py`; 55 files and no problems; without a key a page that says so; with the key a reply from the folder |

The saved outputs come from `gpt-4o-mini` on 13 Oct 2026 (`omni-moderation-latest`, `text-embedding-3-small`, Gradio
6.29.0; Python 3.13.5, macOS, a fresh `uv sync`). Parts A, E and F give the same results every run; replies and
timings vary, and differ again if `models.env` names another model.

## Before you start

- **Labs 09 and 12 first** if you can: the page uses the approval step from Lab 09 and the guarded copilot from Lab 12.
- **Colab:** use the badge above. Add your OpenAI key under Secrets (the key icon in the left bar) as
  `OPENAI_API_KEY` and switch on notebook access. Run the setup cell first in a fresh session. The pages appear under
  their cells; the notebook's clients play the visitors.
- **Local:** in the repository folder, `uv sync`, then put `OPENAI_API_KEY` in `.env` (copied from `.env.example`).
  Open the notebook in JupyterLab (`uv run jupyter lab`) or VS Code and choose the `.venv` kernel. Open each page's
  address in your browser to try it by hand, in two tabs for Part B.
- **Data:** `chinook.db` and the policies and tickets in `data/corpus/`, read in place; Part F copies them into a
  folder in your system's temporary folder. The notebook starts the Ops API on your machine; the refund requests it
  files go to a temporary database, never to a real system.
- **Hugging Face:** creating a Gradio Space needs a paid plan (PRO for a personal account), checked 13 Oct 2026.
  Everything else in the lab is free.
- **Cost:** a few dozen chat calls on `CHAT_MODEL`, embedding calls for the policies and tickets, and free
  moderation calls: a few US cents on `gpt-4o-mini`.

## What is in this folder

| File | What it is |
|---|---|
| `13_deploy_to_a_space.ipynb` | the lab |
| `space/` | the Space template: `README.md` (the header), `app.py`, `requirements.txt`, `.gitignore` |
| `resources/lab13_page_flow.mmd`, `.png` | the diagram of one message through the page |

The notebook ends with a troubleshooting table: ports still in use, the page's API name, the Ops API not running, an
app that does not start, and the page on Colab.

## Resources

- [Gradio: `ChatInterface`](https://www.gradio.app/docs/gradio/chatinterface): the function's arguments, `history` and streaming
- [Gradio: `Chatbot` and `ChatMessage`](https://www.gradio.app/docs/gradio/chatbot): `metadata` for folded steps and `options` for buttons under a message
- [Gradio: agents and tool usage](https://www.gradio.app/guides/agents-and-tool-usage): an agent's tool steps as folded messages
- [Gradio: the Python client](https://www.gradio.app/guides/getting-started-with-the-python-client): `Client`, `predict`, `submit` and signing in
- [Gradio: sharing your app](https://www.gradio.app/guides/sharing-your-app): share links, `auth` and `gr.Request`
- [Hugging Face: Spaces overview](https://huggingface.co/docs/hub/en/spaces-overview): plans, secrets and variables, sleeping hardware
- [Hugging Face: Spaces configuration reference](https://huggingface.co/docs/hub/en/spaces-config-reference): every field of the README header
- [Hugging Face: the `hf` command line](https://huggingface.co/docs/huggingface_hub/en/guides/cli): `hf repos create`, `hf spaces secrets`, `hf upload`, `hf spaces wait` and `hf spaces logs`
- [LangChain: human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop): interrupts, decisions and resuming on the same thread

This is the last lab. Back to [the lab list](../README.md).
