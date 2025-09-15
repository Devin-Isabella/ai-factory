from fastapi import APIRouter, Header, HTTPException
import subprocess, tempfile, os

router = APIRouter()

def _require_token(token: str | None):
    env_token = os.getenv("POWERRENDER_TOKEN", "")
    if not env_token:
        return  # if you forgot to set it, we skip check to avoid lockout (EXP only)
    if not token or token != env_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/powerrender/run")
def run_script(body: dict | None = None, x_pr_token: str | None = Header(default=None)):
    _require_token(x_pr_token)
    ps = (body or {}).get("ps", None)

    # If no script was provided, run the default placeholder (kept for quick checks)
    if not ps:
        try:
            result = subprocess.run(
                ["pwsh", "/app/scripts/powerrender.ps1"],
                capture_output=True, text=True, check=True
            )
            return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": e.stderr or str(e)}

    # If a script was provided, write to a temp file and execute
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False) as f:
            f.write(ps)
            tmp_path = f.name
        try:
            result = subprocess.run(
                ["pwsh", tmp_path],
                capture_output=True, text=True, check=True
            )
            return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": e.stderr or str(e), "stdout": e.stdout, "stderr": e.stderr}
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    except Exception as e:
        return {"ok": False, "error": str(e)}
