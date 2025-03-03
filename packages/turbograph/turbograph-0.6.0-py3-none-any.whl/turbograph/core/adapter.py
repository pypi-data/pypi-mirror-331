"""Format raw vertex specifications into :py:class:`VertexSpecification` objects.

It provides utilities to:

- Convert raw vertex specifications into structured `VertexSpecification` objects.
- Map function call modes to their corresponding parameter kinds.
"""

from collections.abc import Iterable, Mapping
from inspect import _ParameterKind

from .constant import V
from .funccall import CallMode, CallModeError
from .specification import RawVertexSpecification, VertexSpecification

CALL_MODE_TO_PARAMETER_KINDS: dict[CallMode, Iterable[_ParameterKind]] = {
    "args": {_ParameterKind.POSITIONAL_ONLY, _ParameterKind.POSITIONAL_OR_KEYWORD},
    "kwargs": {_ParameterKind.POSITIONAL_OR_KEYWORD, _ParameterKind.KEYWORD_ONLY},
    "arg": set(),
}
"""Mapping of function call modes to the corresponding parameter kinds.

This dictionary defines which function parameter kinds are used for each call mode:

- ``"args"``: Includes positional-only and positional-or-keyword arguments.
- ``"kwargs"``: Includes positional-or-keyword and keyword-only arguments.
- ``"arg"``: Does not consider any specific argument types.
"""


def get_parameter_kinds(call_mode: CallMode) -> Iterable[_ParameterKind]:
    """Retrieve the parameter kinds with proper error handling.

    Retrieve the parameter kinds associated with a given function call mode,
    with proper error handling.
    The parameter kinds are defined in the :py:data:`CALL_MODE_TO_PARAMETER_KINDS`
    dictionary.
    """
    try:
        return CALL_MODE_TO_PARAMETER_KINDS[call_mode]
    except KeyError as error:
        raise CallModeError(call_mode) from error


def _format_specifications(
    raw_specifications: Mapping[V, RawVertexSpecification[V]],
    kinds: Iterable[_ParameterKind] = (),
) -> dict[V, VertexSpecification[V]]:
    """Convert raw vertex specifications into structured `VertexSpecification` objects.

    This function processes a mapping of raw vertex specifications and converts
    each entry into a structured :py:class:`VertexSpecification`.

    Args:
        raw_specifications: A mapping of vertex identifiers to raw vertex
            specifications.
        kinds: A sequence of `_ParameterKind` values specifying which parameters
               should be considered as predecessors when inferring dependencies.

    Returns:
        A dictionary mapping vertex identifiers to formatted
        :py:class:`VertexSpecification` objects.

    """
    return {
        vertex: VertexSpecification.from_any(specification, kinds=kinds)
        for vertex, specification in raw_specifications.items()
    }


def format_specifications(
    raw_specifications: Mapping[V, RawVertexSpecification[V]],
    call_mode: CallMode,
) -> dict[V, VertexSpecification[V]]:
    """Convert raw vertex specifications into :py:class:`VertexSpecification` objects.

    This functions formats raw vertex specifications into structured
    :py:class:`VertexSpecification` objects, based on the provided call mode.
    This function ensures that the correct parameter kinds are considered when
    formatting vertex specifications, based on the provided call mode.

    Args:
        raw_specifications: A mapping of vertex identifiers to raw vertex
            specifications.
        call_mode: The function call mode which determines how function arguments
            are interpreted.

    Returns:
        A dictionary mapping vertex identifiers
        to :py:class:`VertexSpecification` objects.

    """
    kinds = get_parameter_kinds(call_mode)
    return _format_specifications(raw_specifications, kinds=kinds)
