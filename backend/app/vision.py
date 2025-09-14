import os
import json
import httpx
import base64
import mimetypes

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

def _headers():
    return {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

def _to_data_url(content: bytes, mime: str) -> str:
    b64 = base64.b64encode(content).decode("ascii")
    return f"data:{mime};base64,{b64}"

async def _ensure_data_url(image_ref: str) -> str:
    # If it already looks like a data URL, keep it
    if image_ref.startswith("data:"):
        return image_ref
    # Otherwise assume it's an http(s) URL and fetch
    mime, _ = mimetypes.guess_type(image_ref)
    if not mime:
        mime = "image/jpeg"
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        r = await client.get(image_ref)
        r.raise_for_status()
        return _to_data_url(r.content, mime)

def _extract_json(text: str):
    # Try direct JSON
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try fenced code blocks
    if "```" in text:
        parts = text.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("{") and p.endswith("}"):
                try:
                    return json.loads(p)
                except Exception:
                    continue
            if p.lower().startswith("json"):
                body = p[4:].strip()
                try:
                    return json.loads(body)
                except Exception:
                    continue
    # Last resort: naive bracket extraction
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except Exception:
            pass
    return None

async def _chat_vision(data_url: str, model: str):
    prompt = (
        "You are an auto damage estimator. Analyze the photo and return JSON:\n"
        "{\n"
        "  \"damaged_parts\": [{\"part\": string, \"severity\": \"minor|moderate|severe\", \"notes\": string}],\n"
        "  \"cost_low\": number,\n"
        "  \"cost_high\": number,\n"
        "  \"notes\": string\n"
        "}\n"
        "Be conservative if uncertain. Do not include any text outside JSON."
    )

    body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        "temperature": 0,
        "max_tokens": 400,
    }

    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post("https://api.openai.com/v1/chat/completions", headers=_headers(), json=body)
        # If the model can’t do vision or we shaped it wrong, raise for caller to try fallback
        r.raise_for_status()
        data = r.json()
        txt = data["choices"][0]["message"]["content"]
        parsed = _extract_json(txt) or {}
        # Normalize shape
        damaged = parsed.get("damaged_parts", [])
        low = parsed.get("cost_low", 0)
        high = parsed.get("cost_high", 0)
        notes = parsed.get("notes", "")
        return {
            "damaged_parts": damaged,
            "cost_low": low,
            "cost_high": high,
            "notes": notes,
            "raw": txt,
        }

async def detect_damage(image_ref: str, model: str = "gpt-4o-mini"):
    """
    image_ref: data: URL OR http(s) URL.
    Returns dict with damaged_parts, cost_low, cost_high, notes.
    """
    # Ensure data URL to avoid hotlink issues
    data_url = await _ensure_data_url(image_ref)

    # Try primary
    try:
        return await _chat_vision(data_url, model)
    except httpx.HTTPStatusError as e:
        # Fallback to gpt-4o if the mini variant rejects
        if e.response is not None and e.response.status_code in (400, 404, 415):
            try:
                return await _chat_vision(data_url, "gpt-4o")
            except Exception as e2:
                raise e2
        raise
