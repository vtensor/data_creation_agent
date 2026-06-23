import os
import contextvars
from dotenv import load_dotenv

# Production: config is read from the real OS environment variables.
# Local dev: a .env file may supply them, but it never overrides values
# already set in the OS environment (override=False). If no .env exists
# this is a harmless no-op.
load_dotenv(override=False)

def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Required env var '{key}' is not set. Check your .env file.")
    return value

BASE_URL    = _require("BASE_URL")
USAGE_URL   = _require("USAGE_URL")
API_VERSION = os.getenv("VERSION", "v1")
PORT        = int(os.getenv("PORT", "5000"))
LOG_LEVEL   = os.getenv("LOG_LEVEL", "INFO").upper()

# ── Request-scoped user id ────────────────────────────────────────────────────
# The user id is supplied per-request via the `x-user-id` header (NOT from env).
# The route sets it at the start of each request; downstream code reads it back.
_current_user_id: "contextvars.ContextVar[str | None]" = contextvars.ContextVar(
    "current_user_id", default=None
)


def set_user_id(user_id: str) -> None:
    _current_user_id.set(user_id)


def get_user_id() -> str:
    user_id = _current_user_id.get()
    if not user_id:
        raise EnvironmentError("user id is not set for this request (missing x-user-id header)")
    return user_id