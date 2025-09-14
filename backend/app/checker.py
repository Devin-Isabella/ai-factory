from __future__ import annotations
import re
from typing import Dict, Any

# ---- Lightweight evaluator ------------------------------------------------
# Goal: cheap signals to decide "good enough" vs "try next tier".
# This is deliberately simple and fast for MVP.

BAD_TONE_WORDS = {"stupid", "idiot", "shut up", "useless"}
GOOD_TONE_WORDS = {"happy", "glad", "thanks", "appreciate"}
REFUSAL_MARKERS = {"i canâ€™t help", "i cannot help", "i won't help", "cannot assist"}
DANGEROUS_MARKERS = {"bomb", "make a bomb", "credit card number", "ssn", "steal"}

def score_tone(text: str) -> float:
    t = text.lower()
    bad = sum(1 for w in BAD_TONE_WORDS if w in t)
    good = sum(1 for w in GOOD_TONE_WORDS if w in t)
    return max(0.0, min(1.0, 0.5 + 0.1*good - 0.2*bad))

def looks_empty_or_vague(text: str) -> bool:
    t = text.strip()
    if len(t) < 15:  # too short
        return True
    vague = re.findall(r"\b(in conclusion|as an ai|i cannot provide specifics|varies|depends)\b", t, flags=re.I)
    return len(vague) >= 2

def contains_danger(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in DANGEROUS_MARKERS)

def contains_refusal(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in REFUSAL_MARKERS)

def basic_confidence(text: str) -> float:
    l = len(text)
    if l < 50: return 0.2
    if l < 150: return 0.5
    if l < 400: return 0.7
    return 0.8

def should_escalate_single(reply: str, task_is_hard: bool) -> bool:
    if contains_danger(reply):
        return True
    if looks_empty_or_vague(reply):
        return True
    if task_is_hard and basic_confidence(reply) < 0.6:
        return True
    return False

def run_checker(outputs: Dict[str, str]) -> Dict[str, Any]:
    passed = True
    tone_scores = {}
    for name, text in outputs.items():
        if contains_danger(text):
            passed = False
        tone_scores[name] = score_tone(text)
        if looks_empty_or_vague(text):
            passed = False

    trust = min(0.95, max(0.2, sum(tone_scores.values()) / max(1, len(tone_scores))))
    return {"passed": passed, "trust_score": trust, "tone_scores": tone_scores}

def quick_escalation_signal(reply: str, task_is_hard: bool) -> Dict[str, Any]:
    esc = should_escalate_single(reply, task_is_hard)
    return {"needs_escalation": esc, "confidence": basic_confidence(reply), "danger": contains_danger(reply)}
