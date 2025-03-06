import warnings

warnings.simplefilter("always", DeprecationWarning)
warnings.warn(
    "PGLW.components is deprecated, all modules moved to PGLW.main, import from PGLW.main instead",
    category=DeprecationWarning,
    stacklevel=2,
)
