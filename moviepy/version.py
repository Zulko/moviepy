try:
    from importlib.metadata import version

    __version__ = version("moviepy")
except Exception:
    # Fallback version if importlib.metadata is not available (e.g. running from
    # source without installing). Keep this in sync with pyproject.toml.
    __version__ = "2.2.0"
