import os
os.environ.setdefault('ADMIN_EMAIL','devinisabella1@gmail.com')
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Core routers (always available)
from .routes import store, owner, safety, publish, adopt, publisher, auth, admin, metrics, feedback

# Optional admin router (import only if present)
try:
    from .routes import admin
    _HAVE_ADMIN = True
except Exception:
    _HAVE_ADMIN = False
from .routes import monitor

app = FastAPI(
# --- ROUTER_HARDLINK_V1 ---
try:
    from .routes import builder as _b
    app.include_router(_b.router)
except Exception:
    pass
try:
    from .routes import admin as _a
    app.include_router(_a.router)
except Exception:
    pass
try:
    from .routes import monitor as _m
    app.include_router(_m.router)
except Exception:
    pass
# --- END ROUTER_HARDLINK_V1 ---

# --- ROUTER RESCUE ---
import os, sys, importlib, importlib.util, json
from fastapi import APIRouter

# /debug/routes
try:
    _dbg_router = APIRouter(prefix="/debug", tags=["debug"])
    @_dbg_router.get("/routes")
    def _debug_routes():
        try:
            return {"routes":[{"path":getattr(r,'path',None),"name":getattr(r,'name',None)} for r in app.routes]}
        except Exception as e:
            return {"error": str(e)}
    app.include_router(_dbg_router)
except Exception:
    pass

# /debug/env
try:
    _dbg2 = APIRouter(prefix="/debug", tags=["debug"])
    @_dbg2.get("/env")
    def _debug_env():
        try:
            here = os.path.dirname(__file__)
            routes_dir = os.path.join(here, "routes")
            return {
                "__name__": __name__,
                "__file__": __file__,
                "here": here,
                "routes_dir": routes_dir,
                "exists": os.path.isdir(routes_dir),
                "routes_list": sorted(os.listdir(routes_dir)) if os.path.isdir(routes_dir) else None,
                "sys_path": sys.path,
            }
        except Exception as e:
            return {"error": str(e)}
    app.include_router(_dbg2)
except Exception:
    pass

# Hard file-loader fallback (builder/admin/monitor)
def _load_by_file(pyfile):
    try:
        if not os.path.isfile(pyfile): return None
        name = "dyn_" + os.path.basename(pyfile).replace(".py","")
        spec = importlib.util.spec_from_file_location(name, pyfile)
        if not spec or not spec.loader: return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None

try:
    _here = os.path.dirname(__file__)
    _routes = os.path.join(_here, "routes")
    for _name in ("builder","admin","monitor"):
        try:
            _py = os.path.join(_routes, f"{_name}.py")
            _mod = _load_by_file(_py)
            if _mod and hasattr(_mod, "router"):
                app.include_router(getattr(_mod, "router"))
        except Exception:
            pass
except Exception:
    pass
# --- END ROUTER RESCUE ---
title="AI Factory", version="0.1.0")



app.include_router(builder.router)
# --- BOT_BRAIN_V2: builder wiring (idempotent) ---
try:
    from .routes import builder as _builder_routes
except Exception:
    try:
        from app.routes import builder as _builder_routes
    except Exception:
        _builder_routes = None
if _builder_routes:
    try:
        app.include_router(_builder_routes.router)
    except Exception:
        pass
# --- END BOT_BRAIN_V2 builder wiring ---
# --- BOT_BRAIN_V2: monitor wiring (robust, idempotent) ---
try:
    from .routes import monitor as _monitor_routes
except Exception:
    try:
        from app.routes import monitor as _monitor_routes  # absolute import fallback
    except Exception as _e:
        _monitor_routes = None
if _monitor_routes:
    try:
        app.include_router(_monitor_routes.router)
    except Exception:
        pass
# --- END BOT_BRAIN_V2 monitor wiring ---
app.include_router(monitor.router)
# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(store.router)
app.include_router(owner.router)
app.include_router(safety.router)
app.include_router(publish.router)
app.include_router(adopt.router)
app.include_router(publisher.router)
if _HAVE_ADMIN:
    app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(metrics.router)
app.include_router(feedback.router)

# Simple health endpoint (kept stable for scripts)
@app.get("/health")
def health():
    return {"status": "ok"}



from fastapi import Request
from fastapi.responses import JSONResponse
@app.middleware('http')
async def error_logger(request: Request, call_next):
    try:
        resp = await call_next(request)
        return resp
    except Exception as e:
        logging.getLogger('app').exception(f'unhandled: {e}')
        return JSONResponse({'error':'unhandled'}, status_code=500)





# --- FORCED ROUTER APPEND ---
try:
    import os
    os.environ.setdefault('ADMIN_EMAIL','devinisabella1@gmail.com')
except Exception:
    pass

def _try_import(modname):
    try:
        return __import__(f".routes.{modname}", fromlist=['*'], level=1)
    except Exception:
        try:
            return __import__(f"app.routes.{modname}", fromlist=['*'])
        except Exception:
            return None

for _m in ('builder','admin','monitor'):
    try:
        _mod = _try_import(_m)
        if _mod and hasattr(_mod, 'router'):
            app.include_router(getattr(_mod, 'router'))
    except Exception:
        pass
# --- END FORCED ROUTER APPEND ---

# --- DEBUG ROUTES LIST ---
try:
    from fastapi import APIRouter
    _dbg_router = APIRouter(prefix="/debug", tags=["debug"])
    @_dbg_router.get("/routes")
    def debug_routes():
        try:
            return {"routes":[{"path":getattr(r,'path',None),"name":getattr(r,'name',None)} for r in app.routes]}
        except Exception as e:
            return {"error": str(e)}
    app.include_router(_dbg_router)
except Exception:
    pass
# --- END DEBUG ROUTES LIST ---

# --- HARD INCLUDE ROUTERS (builder/admin/monitor) ---
import importlib
def _safe_import(mods):
    for mn in mods:
        try:
            return importlib.import_module(mn)
        except Exception:
            pass
    return None
try:
    _mods = {
        "builder": _safe_import((".routes.builder","app.routes.builder","backend.app.routes.builder")),
        "admin":   _safe_import((".routes.admin","app.routes.admin","backend.app.routes.admin")),
        "monitor": _safe_import((".routes.monitor","app.routes.monitor","backend.app.routes.monitor")),
    }
    for _k,_m in _mods.items():
        try:
            if _m and hasattr(_m,"router"):
                app.include_router(getattr(_m,"router"))
        except Exception:
            pass
except Exception:
    pass
# --- END HARD INCLUDE ROUTERS ---

# --- DEBUG ENV & FILE LOADER ---
try:
    import os, sys, json, importlib, importlib.util
    from fastapi import APIRouter

    # 1) /debug/env shows paths and route-file presence
    _dbg2 = APIRouter(prefix="/debug", tags=["debug"])
    @_dbg2.get("/env")
    def debug_env():
        info = {}
        try:
            here = os.path.dirname(__file__)
            routes_dir = os.path.join(here, "routes")
            info["__name__"] = __name__
            info["__file__"] = __file__
            info["sys_path"] = sys.path
            info["here"] = here
            info["routes_dir"] = routes_dir
            info["routes_dir_exists"] = os.path.isdir(routes_dir)
            if os.path.isdir(routes_dir):
                info["routes_list"] = sorted(os.listdir(routes_dir))
            else:
                info["routes_list"] = None
        except Exception as e:
            info["error"] = str(e)
        return info
    app.include_router(_dbg2)
except Exception:
    pass

# 2) Hard file-loader fallback for routes by explicit file path
def _load_by_file(pyfile):
    try:
        if not os.path.isfile(pyfile):
            return None
        name = "dyn_" + os.path.basename(pyfile).replace(".py","")
        spec = importlib.util.spec_from_file_location(name, pyfile)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None

try:
    _here = os.path.dirname(__file__)
    _routes = os.path.join(_here, "routes")
    for _name in ("builder","admin","monitor"):
        _py = os.path.join(_routes, f"{_name}.py")
        _mod = _load_by_file(_py)
        try:
            if _mod and hasattr(_mod, "router"):
                app.include_router(getattr(_mod, "router"))
        except Exception:
            pass
except Exception:
    pass
# --- END DEBUG ENV & FILE LOADER ---


