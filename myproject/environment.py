"""Read configuration from native processes or Cloudflare Worker bindings."""
import os
import sys

IS_WORKER = sys.platform == "emscripten"


def env(name, default=""):
    if IS_WORKER:
        from workers import env as bindings

        value = getattr(bindings, name, None)
        return default if value is None else str(value)
    return os.environ.get(name, default)


def flag(name, default=False):
    return env(name, "1" if default else "0").strip().lower() in {"1", "true", "yes", "on"}


def csv(name, default=""):
    return [item.strip() for item in env(name, default).split(",") if item.strip()]
