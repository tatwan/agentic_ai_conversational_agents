"""The evaluation cases and their check, as Lab 10 writes them.

Lab 10 writes every case and every check function by hand, cell by cell; read it to learn them. This file keeps a copy
so that later labs (Lab 11 times these cases) can run the same set without running Lab 10 first. If you change a case
in Lab 10, change it here too.

A case is a dict: the rep's message (`input`), what a good run does (`want`, for people), the tools that must be called
with the arguments that matter (`calls`), the tools that must never be called (`never`), text the reply must or
must not contain (`reply_has`, `reply_lacks`), numbers it must state in digits (`numbers`) or no digits at all (`no_numbers`).
`decision` is the reviewer's reason when a write is rejected; `api_down` asks the runner to point the tools at a
closed port.
"""
from __future__ import annotations

import re


def tool_calls(messages):
    """Every tool call the model asked for, in order, as (name, arguments)."""
    return [(call["name"], call["args"]) for m in messages if m.type == "ai" for call in m.tool_calls]


def check_calls(case, calls):
    problems = []
    for name, expected in case.get("calls", {}).items():
        if not any(n == name and all(args.get(k) == v for k, v in expected.items()) for n, args in calls):
            problems.append(f"no {name} call with {expected}")
    for name, args in calls:
        if name in case.get("never", []):
            problems.append(f"called {name} {args}")
    return problems


def numbers(text):
    """Every number written in digits: "$1,049.62" gives "1049.62". "seven" in words is not found."""
    return re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))


def check_reply(case, reply):
    problems = [f"reply lacks {text!r}" for text in case.get("reply_has", []) if text.lower() not in reply.lower()]
    problems += [f"reply has {text!r}" for text in case.get("reply_lacks", []) if text.lower() in reply.lower()]
    problems += [f"reply lacks the number {n}" for n in case.get("numbers", []) if n not in numbers(reply)]
    if case.get("no_numbers") and numbers(reply):
        problems.append(f"reply states numbers {numbers(reply)}")
    return problems


def check(case, messages):
    """The case's problems, from the tool calls in the messages and the last reply. An empty list is a pass."""
    return check_calls(case, tool_calls(messages)) + check_reply(case, messages[-1].text)


answerable = {
    "id": "answerable",
    "type": "answerable",
    "input": "A customer was charged twice for the same album on the same day. What do we do?",
    "want": "Give the rule from the refunds policy and cite it. No customer is named, so look nobody up.",
    "calls": {"search_policies": {}},
    "never": ["find_customer", "get_customer_invoices", "get_invoice", "file_refund_request"],
    "reply_has": ["[policy_refunds.md]"],
}
not_in_docs = {
    "id": "not in docs",
    "type": "not in the documents",
    "input": "A customer found the same album cheaper on another site. Do we match the lower price?",
    "want": "Say the handbook does not cover price matching and suggest the support manager. Cite nothing.",
    "calls": {"search_policies": {}},
    "never": ["find_customer", "get_customer_invoices", "get_invoice", "file_refund_request"],
    "reply_has": ["manager"],
    "reply_lacks": ["[policy_"],
}
lookup = {
    "id": "lookup",
    "type": "read-only lookup",
    "input": "How many invoices does Helena Holý have, and what do they add up to?",
    "want": "Find Helena (customer 6) and read her invoices: 7 invoices, 49.62 in total. File nothing.",
    "calls": {"find_customer": {"name": "Helena Holý"}, "get_customer_invoices": {"customer_id": 6}},
    "never": ["file_refund_request"],
    "numbers": ["7", "49.62"],
}
missing_argument = {
    "id": "missing argument",
    "type": "missing argument",
    "input": "Helena Holý was charged twice for the same album. Please file the refund.",
    "want": "No album appears twice on her invoices: say so, or ask for the invoice numbers. Propose no refund.",
    "never": ["file_refund_request"],
}
not_approved = {
    "id": "not approved",
    "type": "action not approved",
    "input": "Ticket 14: customer 16 was charged twice for The Essential Miles Davis, invoices 9001 and 9002, "
             "9.99 each. File the refund for the later invoice.",
    "want": "Propose 9.99 on invoice 9002 and wait. The reviewer rejects it, so nothing is filed.",
    "calls": {"file_refund_request": {"invoice_id": 9002, "amount": 9.99}},
    "decision": "Not approved: finance is refunding invoice 9002 through the bank. Do not file it again.",
}
tool_failure = {
    "id": "tool failure",
    "type": "tool failure",
    "input": "How many invoices does Helena Holý have, and what do they add up to?",
    "want": "Say the lookup failed. Give no count and no total.",
    "calls": {"find_customer": {"name": "Helena Holý"}},
    "no_numbers": True,
    "api_down": True,
}
out_of_scope = {
    "id": "out of scope",
    "type": "out of scope",
    "input": "Can you write a short birthday poem for my colleague Steve?",
    "want": "Decline: the copilot helps reps with customer support. Call no tool.",
    "never": ["search_policies", "find_customer", "get_customer_invoices", "get_invoice", "file_refund_request"],
    "reply_lacks": ["happy birthday"],
}

CASES = [answerable, not_in_docs, lookup, missing_argument, not_approved, tool_failure, out_of_scope]
