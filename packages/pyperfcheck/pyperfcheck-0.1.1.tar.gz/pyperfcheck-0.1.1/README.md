
# PyPerfCheck – Easy Benchmarking for Python Code

**PyPerfCheck** is a high-performance benchmarking library for Python. It allows you to measure and compare the execution time, CPU usage, and memory usage of Python functions. It supports synchronous, asynchronous, multi-threaded, and multi-processed functions, making it a versatile tool for performance analysis.

---

## Features

- **Benchmark Synchronous Functions**: Measure execution time, CPU usage, and memory usage.
- **Benchmark Asynchronous Functions**: Supports `async` functions for I/O-bound tasks.
- **Multi-Threading Benchmarking**: Test functions using multiple threads.
- **Multi-Processing Benchmarking**: Test functions using multiple processes.
- **Visual Reports**: Generate bar charts for execution time, CPU usage, and memory usage.
- **Easy-to-Use**: Simple API with decorators and helper methods.

---

## Installation

Install PyPerfCheck using pip:

```bash
pip install pyperfcheck
```

## Quick Start

1. **Import the library**:
   ```python
   from pyperfcheck import PyPerfCheck
   ```

2. **Benchmark a function**:  
   Use the `benchmark` decorator to measure execution time, CPU, and memory usage for any function.
   ```python
   @PyPerfCheck.benchmark
   def example_function():
       # Your code here
       time.sleep(1)
   ```

3. **Compare multiple functions**:  
   You can benchmark and compare the performance of multiple functions using `compare`.
   ```python
   def function1():
       time.sleep(1)

   def function2():
       time.sleep(2)

   PyPerfCheck.compare([function1, function2])
   ```

4. **Generate Visual Reports**:  
   PyPerfCheck can also generate bar charts to visualize the benchmark results.
   ```python
   # After calling PyPerfCheck.compare(), the visual report will be shown
   ```

---

## License

MIT License. See LICENSE for details.
