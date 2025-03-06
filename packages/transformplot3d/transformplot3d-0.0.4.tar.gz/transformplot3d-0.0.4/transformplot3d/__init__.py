r"""\
Transformplot 3D
================
Transformplot 3D is a small library with useful commands that help visualize matrix transformations
with `matplotlib` plots. These matrices are from the `transformations` package.

It consists of only two main modules `vectors` and `quiver`. `vectors` offers some basic commands of
reshaping a vector or a matrix, while `quiver` offers methods of converting lists of vectors and matrices
into tuples ready to be input in matplotlib `quiver()` method. Note that matplotlib is not actually required
 for the methods in this package, but is needed to take advantage of it.
"""

from .core import(
    extend_vector,
    reduce_vector,
    reduced_and_extended,
    extend_matrix,
    reduce_matrix,

    one_vector_many_systems,
    many_vectors_one_system,
    many_vectors_many_systems,
    draw_axes_from_matrices,
    __all__ as __all_core__
)

__all__ = (
    __all_core__
)

del __all_core__