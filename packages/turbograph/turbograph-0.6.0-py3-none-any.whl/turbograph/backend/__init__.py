"""Package that defines the ``networkx`` and ``igraph`` graph backends.

The ``igraph`` and ``networkx`` backends are defined
in :py:mod:`turbograph.backend.igraph_backend`
and :py:mod:`turbograph.backend.networkx_backend`, respectively.

To use a specific backend, import the corresponding wrapper class
using the :py:func:`turbograph.backend.factory.get_graph_backend` function.
"""

from .factory import get_graph_backend

__all__ = ["get_graph_backend"]
