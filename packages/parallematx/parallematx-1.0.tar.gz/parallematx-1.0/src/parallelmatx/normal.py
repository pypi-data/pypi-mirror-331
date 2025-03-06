def normal_matrix_multiplication(
    A: list[list[float]], B: list[list[float]]
) -> list[list[float]]:
    """
    Performs standard (non-parallel) matrix multiplication

    Algorithm:
        This function computes the product of two matrices using the traditional
        nested loop approach

    Complexity (assume square matrices of size n × n):
        - Time Complexity: O(n^3), as each element requires O(n) multiplications and summations.
        - Space Complexity: O(n^2), since the result matrix requires storage for n^2 elements.

    Args:
        A (list[list[float]]): The first matrix, represented as a 2D list
        B (list[list[float]]): The second matrix, represented as a 2D list

    Returns:
        list[list[float]]: The resulting matrix after multiplication

    Raises:
        ValueError: If the matrices have incompatible dimensions for multiplication

    """
    # Handle matrix size not competible
    if len(A[0]) != len(B):
        raise ValueError("Matrix dimensions are incompatible for multiplication.")

    # Computes
    return [
        [sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
        for i in range(len(A))
    ]
