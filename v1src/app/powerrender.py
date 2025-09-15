from fastapi import APIRouter
import subprocess, sys

router = APIRouter()

@router.post("/powerrender/run")
def run_script():
    """
    Minimal runner that executes a tiny Python command inside the container.
    You can expand this later to accept a script/body and do more.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-c", "print('powerrender ok')"],
            capture_output=True, text=True, timeout=20, check=True
        )
        return {"ok": True, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    except Exception as e:
        return {"ok": False, "error": str(e)}
