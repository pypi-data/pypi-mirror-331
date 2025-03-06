import time
import numpy as np
import matplotlib.pyplot as plt
from normal import normal_matrix_multiplication
from parallel import parallel_matrix_multiplication
import multiprocessing
from tqdm import tqdm


def get_user_input(prompt, default):
    """
    Helper function to get user input with a default value.

    Args:
        prompt (str): The input prompt message.
        default (int): The default value if the user enters nothing.

    Returns:
        int: The user-provided or default integer value.
    """
    user_input = input(f"{prompt} (default: {default}): ").strip()
    return int(user_input) if user_input.isdigit() else default


def measure_time(func, A, B, *args):
    """Measure execution time of a function."""
    start = time.time()
    func(A, B, *args)
    end = time.time()
    return end - start


def test_performance_between_normal_and_parallel(start_size, end_size, distance):
    """Compare execution time of normal vs parallel matrix multiplication with progress tracking."""
    matrix_sizes = list(range(start_size, end_size + distance, distance))

    normal_times = []
    parallel_times = []

    print("\nRunning Normal vs Parallel Multiplication Tests...\n")

    for size in tqdm(matrix_sizes, desc="Processing Matrices", unit="test"):
        A = np.random.rand(size, size)
        B = np.random.rand(size, size)

        normal_time = measure_time(normal_matrix_multiplication, A.tolist(), B.tolist())
        parallel_time = measure_time(
            parallel_matrix_multiplication, A.tolist(), B.tolist()
        )

        normal_times.append(normal_time)
        parallel_times.append(parallel_time)

        print(
            f"\nSize {size}x{size} → Normal: {normal_time:.4f}s, Parallel: {parallel_time:.4f}s"
        )

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(matrix_sizes, normal_times, marker="o", linestyle="-", label="Normal")
    plt.plot(matrix_sizes, parallel_times, marker="s", linestyle="-", label="Parallel")
    plt.xlabel("Matrix Size (NxN)")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Performance Comparison: Normal vs Parallel Multiplication")
    plt.legend()
    plt.grid(True)
    plt.show()


def test_parallel_performance_with_different_workers(start_size, end_size, distance):
    """Compare parallel matrix multiplication with different max_workers using progress tracking."""
    matrix_sizes = list(range(start_size, end_size + distance, distance))
    max_cores = multiprocessing.cpu_count()
    worker_counts = [w for w in [1, 2, 4, 8, 16] if w <= max_cores]

    performance_data = {workers: [] for workers in worker_counts}

    print("\nRunning Parallel Multiplication with Different max_workers...\n")

    with tqdm(total=len(matrix_sizes), desc="Processing Matrices", unit="test") as pbar:
        for size in matrix_sizes:
            A = np.random.rand(size, size)
            B = np.random.rand(size, size)

            for workers in worker_counts:
                exec_time = measure_time(
                    parallel_matrix_multiplication, A.tolist(), B.tolist(), workers
                )
                performance_data[workers].append(exec_time)

                # Ensure output is correctly formatted without breaking tqdm
                tqdm.write(f"Size {size}x{size} → Workers {workers}: {exec_time:.4f}s")

            pbar.update(1)  # Update progress bar

    # Plot results
    plt.figure(figsize=(10, 6))
    for workers, times in performance_data.items():
        plt.plot(
            matrix_sizes,
            times,
            marker="o",
            linestyle="-",
            label=f"max_workers={workers}",
        )

    plt.xlabel("Matrix Size (NxN)")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Parallel Multiplication Performance: Different max_workers")
    plt.legend()
    plt.grid(True)
    plt.show()


def performance():
    START_SIZE = 100
    MAX_SIZE = 500
    DISTANCE = 100
    while True:
        print("\nSelect a Performance Test to Run:")
        print("[1] - Compare Normal vs Parallel Multiplication")
        print("[2] - Compare Parallel Multiplication with Different max_workers")
        print("[q] - Exit")

        choice = input("Enter your choice (1/2/q): ").strip()

        if choice in ["1", "2"]:
            print("\nEnter matrix size range (or press Enter to use defaults):")
            start_size = get_user_input("Start size", START_SIZE)
            end_size = get_user_input("End size", MAX_SIZE)
            distance = get_user_input("Step size (distance)", DISTANCE)

            if choice == "1":
                test_performance_between_normal_and_parallel(
                    start_size, end_size, distance
                )
            elif choice == "2":
                test_parallel_performance_with_different_workers(
                    start_size, end_size, distance
                )
        elif choice == "q" or choice == "":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or q.")


if __name__ == "__main__":
    performance()
