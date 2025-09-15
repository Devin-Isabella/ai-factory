from fastapi import APIRouter
import subprocess

router = APIRouter()

@router.post("/powerrender/run")
def run_script():
    try:
        result = subprocess.run(
            ["pwsh", "/app/scripts/powerrender.ps1"],
            capture_output=True, text=True, check=True
        )
        return {"stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr or str(e)}
