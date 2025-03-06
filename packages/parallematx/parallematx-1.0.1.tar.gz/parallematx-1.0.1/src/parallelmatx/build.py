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


def cross_product(
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


# Test cases
def test_matrix_multiplication():
    # Test Case 1: Simple square matrices
    A1 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    B1 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    numpy_result1 = np.dot(A1, B1)
    parallel_result1 = cross_product(A1, B1)

    # Detailed comparison
    print("Test Case 1 (Square Matrices):")
    print("NumPy Result:\n", numpy_result1)
    print("\nParallel Result:\n", parallel_result1)
    print("\nResults Match:", np.array_equal(numpy_result1, parallel_result1))

    # Test Case 2: Rectangular matrices
    A2 = np.array([[1, 2], [3, 4], [5, 6]])
    B2 = np.array([[1, 2, 3], [4, 5, 6]])
    numpy_result2 = np.dot(A2, B2)
    parallel_result2 = cross_product(A2, B2)
    print("\n\nTest Case 2 (Rectangular Matrices):")
    print("NumPy Result:\n", numpy_result2)
    print("\nParallel Result:\n", parallel_result2)
    print("\nResults Match:", np.array_equal(numpy_result2, parallel_result2))


if __name__ == "__main__":
    test_matrix_multiplication()
