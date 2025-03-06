from .vectors import (
    extend_vector,
    reduce_vector,
    reduced_and_extended,
    extend_matrix,
    reduce_matrix,
    __all__ as __all_vectors__
)

from .quiver import(
    one_vector_many_systems,
    many_vectors_one_system,
    many_vectors_many_systems,
    draw_axes_from_matrices,
    __all__ as __all_quiver__
)

__all__ = (
    __all_vectors__
    + __all_quiver__
)

del __all_vectors__
del __all_quiver__