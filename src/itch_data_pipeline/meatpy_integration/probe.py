from __future__ import annotations


def probe_meatpy() -> dict[str, str | bool]:
    try:
        import meatpy  # type: ignore
        version = getattr(meatpy, "__version__", "unknown")
        return {"installed": True, "version": str(version)}
    except Exception as exc:  # pragma: no cover
        return {"installed": False, "version": "not_available", "error": repr(exc)}
