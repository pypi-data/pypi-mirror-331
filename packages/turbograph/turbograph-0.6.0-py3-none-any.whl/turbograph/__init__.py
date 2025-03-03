"""TurboGraph is a simple Python library, for quick dependency-based computation.

TurboGraph automatically builds a dependency graph from function argument names
or explicit specifications, ensuring computations run in the correct order.

Here's a simple example showing how TurboGraph automatically infers dependencies:

.. code-block:: python

    from turbograph import compute

    specifications = {
        "a": 2,
        "sum": lambda a, b: a + b,  # Depends on "a" and "b"
    }

    result = compute(specifications, ["sum"], {"b": 3})
    print(result)  # {"sum": 5}


TurboGraph analyzes the function signatures and determines that ``"sum"`` depends
on ``"a"`` and ``"b"``, executing the computations in the correct order.
"""

from importlib.metadata import version as _importlib_version

from .core import NA, RawVertexSpecification, VertexSpecification
from .run import build_graph, compute, compute_from_graph, rebuild_graph

__all__ = [
    "NA",
    "RawVertexSpecification",
    "VertexSpecification",
    "build_graph",
    "compute",
    "compute_from_graph",
    "rebuild_graph",
]

__version__ = _importlib_version(__name__)
