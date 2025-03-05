import warnings

from elluminate.client import Client
from elluminate.middleware_sdk import ElluminateOpenAIMiddleware

# Issue a deprecation warning
warnings.warn(
    "Importing from 'elluminate.beta' is deprecated and will be removed in version 0.3.1. "
    "Please use 'elluminate' directly instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["Client", "ElluminateOpenAIMiddleware"]
