from __future__ import annotations

# ---- Routing & Spec Builder ----------------------------------------------

TIERS = ["tierA", "tierB", "tierC"]

# Default model choices per tier.
# - Tier A: cheap/fast (bulk traffic)
# - Tier B: mid (nuanced reasoning / quality)
# - Tier C: premium (edge cases only)
DEFAULT_MODELS = {
    "tierA": "gpt-4o-mini",       # or: "llama-3.1-70b", via your provider
    "tierB": "gpt-4o",            # or: "claude-3.5-sonnet"
    "tierC": "gpt-5",             # keep rare + optional
}

# Tasks that usually need higher tiers
HARD_KEYWORDS = [
    "multi-step", "write code", "coding", "legal", "security",
    "financial", "long plan", "complex", "debug", "architecture",
    "compliance", "privacy", "encryption", "risk"
]


def describe_task(req: dict) -> str:
    # Use description + category + name to infer difficulty
    parts = [
        (req.get("description") or ""),
        (req.get("category") or ""),
        (req.get("name") or "")
    ]
    return " ".join(p for p in parts if p).strip()


def is_hard_task(task: str) -> bool:
    t = task.lower()
    return any(k in t for k in HARD_KEYWORDS)


def choose_model(task: str, budget_guard: str) -> tuple[str, list[str]]:
    """
    Returns (primary_model, escalation_order)
    - budget_guard: "economy" | "balanced" | "premium"
    """
    tierA = DEFAULT_MODELS["tierA"]
    tierB = DEFAULT_MODELS["tierB"]
    tierC = DEFAULT_MODELS["tierC"]

    hard = is_hard_task(task)

    if budget_guard == "economy":
        primary = tierB if hard else tierA
        order = [tierB, tierC] if hard else [tierB]
        return primary, order

    if budget_guard == "premium":
        primary = tierC if hard else tierB
        order = [tierC] if not hard else []
        return primary, order

    # balanced (default)
    primary = tierB if hard else tierA
    order = [tierC] if hard else [tierB]
    return primary, order


def token_limits_for_target(target: str) -> int:
    if target in {"blog", "longform"}:
        return 1200
    if target in {"code", "analysis"}:
        return 800
    return 400


def build_agent_spec(req: dict) -> dict:
    """
    Construct the agent's routing + limits spec from the user's request.
    Expecting req to have: name, description, category, tone, target, budget_guard, needs[].
    """
    task = describe_task(req)
    budget = (req.get("budget_guard") or "balanced").lower()
    primary_model, escalation = choose_model(task, budget)

    target = req.get("target", "web")
    max_out = token_limits_for_target(target)

    spec = {
        "routing": {
            "primary": primary_model,
            "escalation": escalation,   # next-best tiers to try (in order), may be []
            "budget_guard": budget
        },
        "tone": req.get("tone", "professional"),
        "target": target,
        "tools": {
            "web_search": "web_search" in (req.get("needs") or []),
            "rag": "rag" in (req.get("needs") or []),
            "code_tools": "code_tools" in (req.get("needs") or []),
        },
        "limits": {
            "max_output_tokens": max_out,
            "max_escalations": 1
        },
        "guardrails": {
            "ethics_profile": "v1.0",
            "pii_redaction": True
        },
        "costing_assumptions": {
            "avg_input_tokens": 350,
            "avg_output_tokens": max_out
        }
    }
    return spec
