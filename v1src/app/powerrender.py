from fastapi import APIRouter
import subprocess, os, traceback

router = APIRouter()

@router.post("/powerrender/run")
def run_script():
    try:
        result = subprocess.run(
            ["sh", "/app/scripts/powerrender.ps1"],
            capture_output=True, text=True, check=True
        )
        return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"ok": False, "error": e.stderr or str(e)}
    except Exception as e:
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}
