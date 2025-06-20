try:
    from importlib.metadata import version

    __version__ = version("moviepy")
except Exception:
    __version__ = "%VERSION%"
