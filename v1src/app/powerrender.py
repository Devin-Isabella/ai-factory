from fastapi import APIRouter, Request
import subprocess, tempfile, os, traceback

router = APIRouter()

# Hardcoded token (replace here if needed)
TOKEN = "123456789876543212345678987654321"

def _require_token(token: str | None):
    if not TOKEN:  # if empty, skip check
        return
    if not token or token != TOKEN:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/powerrender/run")
async def run_script(request: Request):
    # Check header
    token = request.headers.get("x-pr-token")
    _require_token(token)

    try:
        body = await request.json()
    except Exception:
        body = {}

    ps = body.get("ps")

    try:
        if not ps:
            # Default check script
            result = subprocess.run(
                ["sh", "/app/scripts/powerrender.ps1"],
                capture_output=True, text=True, check=True
            )
            return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}

        # Write PS body to temp file
        with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False) as f:
            f.write(ps)
            tmp_path = f.name

        try:
            result = subprocess.run(
                ["sh", tmp_path],
                capture_output=True, text=True, check=True
            )
            return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}
        finally:
            os.remove(tmp_path)

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


