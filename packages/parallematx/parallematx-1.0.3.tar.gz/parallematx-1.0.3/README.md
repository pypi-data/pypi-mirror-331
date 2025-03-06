# ParallelMatX

This project is developed as part of the **240-123 Data Structure Algorithm and Programming Module** in my concurrency assignment

## Overview

ParallelMatX is an open-source Python library designed for parallel matrix multiplication.

It utilizes parallel processing techniques to optimize performance, competible with large-scale matrix computation

## Getting Started

### Installation

To install ParallelMatX, use pip:

```
pip install parallematx
```

### Usage Example

Here's a basic example demonstrating how to use ParallelMatX for parallel matrix multiplication:

```python
import parallelmatx
import numpy as np

if __name__ == "__main__": # Need main to run parallel
    A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    B = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    result = parallelmatx.parallel_matrix_multiplication(A, B)
    print("Result:\n", result)

    # result:
    # [[ 30.  36.  42.]
    # [ 66.  81.  96.]
    # [102. 126. 150.]]
```

## How It Works
### Understanding how matrix multiplication
Matrix multiplication is a binary operation that produces a matrix from two matrices. For matrix multiplication, the number of columns in the first matrix must be equal to the number of rows in the second matrix. The resulting matrix, known as the matrix product (ref: https://en.wikipedia.org/wiki/Matrix_multiplication)

![image](https://github.com/user-attachments/assets/41defda7-09d3-4742-8a83-98914758ff18)

### Problem of calculation
**Iterative algorithm** is most basic multiplication algorithmn. Its easy to understand how each row operation. 
The problem is its slowness, In computer science we can analyze the time complexity for time and space. This is analysis of this approch (assume we have matrix n x n)

Time Complexity: O(n<sup>3</sup>)

Space Complexity: O(n<sup>2</sup>)

![image](https://github.com/user-attachments/assets/0361c4e9-b355-463c-a3d9-a1b742876bd6)

Its slow because we have to do multiplication for each element. You can see from this picture how we traverse along matrix

![Row_and_column_major_order svg](https://github.com/user-attachments/assets/34141298-1f81-4ffd-bcec-43489bc2a779)

### Optimization
We can see that each role have independent result, So we can do parallel calculation for each row. Then we combine together 

![image](https://github.com/user-attachments/assets/755bf4c0-e8a5-4e7b-be77-105694d8080d)

After we analysis new complexity we got this

**Time Complexity**
- Worst Case (No Parallelism, max_workers = 1): O(n<sup>3</sup>), equivalent to traditional matrix multiplication.
- Average Case (When max_workers is moderate ) : O(n<sup>3</sup>/logn) ≈ O(n<sup>2.5</sup>)
- Best Case (Full Parallelism, max_workers = n): O(n<sup>2</sup>), where row computations are fully distributed.

**Space Complexity**: O(n<sup>2</sup>), as the final result matrix requires n<sup>2</sup> storage.

### Implementation
Using ProcessPoolExecutor from concurrnt.future library from python
```py
def compute_row(A: np.ndarray, B: np.ndarray, row_index: int) -> np.ndarray:
    return np.array([np.dot(A[row_index], B[:, col]) for col in range(B.shape[1])])


def parallel_matrix_multiplication(
    A: list | np.ndarray, B: list | np.ndarray, max_workers: int | None = None
) -> np.ndarray:
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
```

## Benchmarking
You can run benchmark that I have provided on `src/parallelmatx/performance.py` you can chose options and select which range you want to test. However, pleas careful about range its may cause your computer lagging

### 1. Testing traditional approch vs parallel approch

We can take a look that in long range square matrix size from 100 to 1000. Its seem like on the start point parallel took slower than traditional approch because its more time to split & manage task. Also for retriving all answer 

![481434274_533566232605712_3499873268860801680_n](https://github.com/user-attachments/assets/88f91a68-9164-4199-99e8-43d9609aa526)


### 2. Testing max-workers 

In ProcessPoolExcutor we can limit max-workers. However, In terms of optimization, It's not always better performance with more max-workers. 

There some technical factor behind this

1. Overhead of Process Creation and Management
2. CPU Core Limitations
3. Memory Bandwidth Bottleneck

As you can see from the figure, incress number of max-workers don't have significant changes, So just leave your computer select how much max-workers

![Figure_1](https://github.com/user-attachments/assets/0e99d172-63f9-4c5e-b65b-0a94bae736f2)
