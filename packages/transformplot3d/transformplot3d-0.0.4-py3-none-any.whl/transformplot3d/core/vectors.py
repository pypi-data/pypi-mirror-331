r"""\
Vectors
=======
This module contains very basic methods to expand and contract vectors and matrices.
The only reason these functions exist is to avoid repetition and complexity in some of the methods
in quiver, and because they turn to be useful defining vectors.
"""

import numpy as np

def extend_vector(vector: list):
    """
    Returns the input list with a 1 appended at the end.
    """
    return vector.append(1)

def reduce_vector(vector: list):
    """
    Returns the input list without the last element.
    """
    return vector[:-1]

def reduced_and_extended(vector: list):
    """
    Returns the input vector and a reduced version of it (without the last element)
    """
    return reduce_vector(vector),vector

def extend_matrix(matrix: list):
    """
    Returns an extension of the input with the form `[[matrix, zeros],[zeros,1]]`. 
    """
    M = matrix.tolist() if type(matrix) != list else matrix
    newMat = []
    for row in range(len(M)):
        newRow = []
        for item in range(len(M[row])):
            newRow.append(M[row][item])
        newRow.append(0)
        newMat.append(newRow)
    lastRow = [0]*len(M[-1])
    lastRow.append(1)
    newMat.append(lastRow)
    return np.matrix(newMat)

def reduce_matrix(matrix: list):
    """
    Returns the input matrix without the last row and last column.
    """
    M = matrix.tolist() if type(matrix) != list else matrix
    newMat = []
    for row in range(len(M)-1):
        newRow = []
        for item in range(len(M[0])-1):
            newRow.append(M[row][item])
        newMat.append(newRow)
    return np.matrix(newMat)

__all__ = [
    "extend_vector",
    "reduce_vector",
    "reduced_and_extended",
    "extend_matrix",
    "reduce_matrix",
]
 