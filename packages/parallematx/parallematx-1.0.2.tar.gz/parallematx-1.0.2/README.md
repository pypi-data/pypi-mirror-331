# ParallelMatX

This project is developed as part of the **240-123 Data Structure Algorithm and Programming Module** in my concurrency assignment

## Overview

ParallelMatX is an open-source Python library designed for parallel matrix multiplication.

It utilizes parallel processing techniques to optimize performance, competible with large-scale matrix computation

## Getting Started

### Installation

To install ParallelMatX, use pip:

```
pip install parallematx==1.0
```

### Usage Example

Here's a basic example demonstrating how to use ParallelMatX for parallel matrix multiplication:

```python
import parallelmatx
import numpy as np

if __name__ == "__main__": # Need main to run parallel
    A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    B = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    result = parallelmatx.cross_product(A, B)
    print("Result:\n", result)
```

## How It Works

## Benchmarking
