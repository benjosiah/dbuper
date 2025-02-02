try:
    from version import __version__
    print("Version:", __version__)
except ImportError as e:
    print("Import error:", e)