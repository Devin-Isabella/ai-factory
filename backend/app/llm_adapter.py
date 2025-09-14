from typing import Optional, List, Dict
import os
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
# If your key is project-scoped, set OPENAI_PROJECT in .env to your project id (not the key).
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT", "").strip()

class OpenAIError(Exception):
    pass

async def _invoke_openai_legacy(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 400):
    if not OPENAI_API_KEY:
        raise OpenAIError("Missing OPENAI_API_KEY")

    url = f"{OPENAI_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    if OPENAI_PROJECT:
        headers["OpenAI-Project"] = OPENAI_PROJECT

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful, safe assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=payload)
        if r.status_code >= 400:
            raise OpenAIError(f"{r.status_code} {r.reason_phrase}: {r.text}")
        data = r.json()
        return data["choices"][0]["message"]["content"]

# --- Compatibility shim: accept messages=[...] OR prompt=str ---
def invoke_openai(
    model: str,
    messages: Optional[List[Dict]] = None,
    prompt: Optional[str] = None,
    max_tokens: int = 200,
    temperature: float = 0.7,
):
    # If a legacy implementation exists, call it; otherwise raise.
    try:
        legacy = _invoke_openai_legacy  # type: ignore[name-defined]
    except NameError as _e:
        # No legacy symbol; maybe the current impl already accepts 'prompt' only.
        # Try to call a same-name function without messages kw.
        try:
            # fall through to a local name 'invoke_openai_raw' if user has one
            legacy = invoke_openai_raw  # type: ignore[name-defined]
        except NameError:
            raise RuntimeError("No legacy OpenAI adapter found. Please keep _invoke_openai_legacy or invoke_openai_raw defined.") from _e

    # Build a text prompt from messages if provided
    if messages and not prompt:
        # Join simple role:content pairs into a compact prompt
        parts = []
        for m in messages:
            role = m.get("role","user")
            content = m.get("content","")
            # content may be list/dict in OpenAI schema; coerce simply
            if isinstance(content, list):
                content = " ".join(
                    c.get("text","") if isinstance(c, dict) else str(c)
                    for c in content
                )
            elif isinstance(content, dict):
                content = content.get("text", str(content))
            parts.append(f"{role.upper()}: {content}")
        prompt = "\n".join(parts)

    if not prompt:
        prompt = ""

    # Call legacy with a 'prompt=' signature
    return legacy(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,

    )

