"""A meta-registry for ontologies, controlled vocabularies, and semantic spaces."""

from .api import hello, square

# being explicit about exports is important!
__all__ = [
    "hello",
    "square",
]
