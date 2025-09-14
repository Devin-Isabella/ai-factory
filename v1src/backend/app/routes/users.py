from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

_fake_users = [
    {"id": 1, "name": "Alice", "role": "owner"},
    {"id": 2, "name": "Bob", "role": "admin"},
]


@router.get("/")
def list_users():
    """Return all users (temporary in-memory)."""
    return _fake_users


@router.get("/{user_id}")
def get_user(user_id: int):
    """Return a specific user."""
    return next((u for u in _fake_users if u["id"] == user_id), {"error": "not found"})
