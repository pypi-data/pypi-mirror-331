import numpy as np
from concurrent.futures import ProcessPoolExecutor


def compute_row(A: np.ndarray, B: np.ndarray, row_index: int) -> np.ndarray:
    """
    Computes each matrix row in parallel

    Algorithm:
        Performing dot product between row of matrix A and columns of matrix B

    Args:
        A (numpy.ndarray): The first matrix operand
        B (numpy.ndarray): The second matrix operand
        row_index (int): The index of compute row

    Returns:
        numpy.ndarray: The computed row of result matrix
    """
    return np.array([np.dot(A[row_index], B[:, col]) for col in range(B.shape[1])])


def parallel_matrix_multiplication(
    A: list | np.ndarray, B: list | np.ndarray, max_workers: int | None = None
) -> np.ndarray:
    """
    Parallel matrix multiplication using ProcessPoolExecutor

    Algorithm:
        Computes cross product of matrix for improved performance

    Args:
        A (list | np.ndarray): The first matrix
        B (list | np.ndarray): The second matrix
        max_workers (int | None, optional): The maximum number of parallel processes.
            Defaults to None, which lets Python decide the optimal number of processes.

    Returns:
        np.ndarray: The result of matrix multiplication A × B.

    Raises:
        ValueError: If the matrices have incompatible dimensions for multiplication.
    """
    # Format input array
    A = np.array(A)
    B = np.array(B)

    # Check matrix compatibility
    if A.shape[1] != B.shape[0]:
        raise ValueError("Matrix dimensions are incompatible for multiplication.")

    # Initial Result Matrix
    result = np.zeros((A.shape[0], B.shape[1]))

    # Run Process Pool
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Init parallel process store
        parallel_row_results = []

        # Start parallel compute
        for i in range(A.shape[0]):
            parallel_row_results.append(executor.submit(compute_row, A, B, i))

        # Retrieving all row results
        for i, row in enumerate(parallel_row_results):
            result[i] = row.result()

    return result
