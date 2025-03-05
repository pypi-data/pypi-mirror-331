import time
import functools
import psutil
import asyncio
import threading
import multiprocessing
import matplotlib.pyplot as plt
from tabulate import tabulate

class PyPerfCheck:
    @staticmethod
    def benchmark(func):
        """Decorator to measure execution time, CPU & memory usage."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            process = psutil.Process()
            
            start_time = time.perf_counter()
            start_cpu = process.cpu_percent(interval=None)
            start_mem = process.memory_info().rss / (1024 * 1024)  # MB

            result = func(*args, **kwargs)

            end_time = time.perf_counter()
            end_cpu = process.cpu_percent(interval=None)
            end_mem = process.memory_info().rss / (1024 * 1024)  # MB

            execution_time = end_time - start_time
            cpu_usage = end_cpu - start_cpu
            memory_usage = end_mem - start_mem

            return execution_time, cpu_usage, memory_usage, result
        return wrapper

    @staticmethod
    def compare(functions, iterations=5):
        """
        Compare execution times, CPU & memory usage of multiple functions.

        Args:
            functions (list): List of functions to benchmark.
            iterations (int): Number of times each function is run.
        """
        results = {}

        for func in functions:
            total_time, total_cpu, total_mem = 0, 0, 0
            benchmarked_func = PyPerfCheck.benchmark(func)
            
            for _ in range(iterations):
                try:
                    exec_time, cpu_usage, mem_usage, _ = benchmarked_func()
                    total_time += exec_time
                    total_cpu += cpu_usage
                    total_mem += mem_usage
                except Exception as e:
                    print(f"Error benchmarking {func.__name__}: {e}")
                    continue

            avg_time = total_time / iterations
            avg_cpu = total_cpu / iterations
            avg_mem = total_mem / iterations
            results[func.__name__] = (avg_time, avg_cpu, avg_mem)

        # Print results in a table format
        headers = ["Function", "Avg Time (s)", "Avg CPU (%)", "Avg Mem (MB)"]
        table_data = [[name, f"{time:.6f}", f"{cpu:.2f}", f"{mem:.2f}"] for name, (time, cpu, mem) in results.items()]
        
        print("\n📊 Benchmark Results:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        # Generate Visual Report
        PyPerfCheck.plot_results(results)

    @staticmethod
    def plot_results(results):
        """Generate a bar chart for execution time, CPU & memory usage."""
        functions = list(results.keys())
        times = [results[f][0] for f in functions]
        cpus = [results[f][1] for f in functions]
        mems = [results[f][2] for f in functions]

        fig, ax = plt.subplots(3, 1, figsize=(8, 10))

        ax[0].bar(functions, times, color='blue')
        ax[0].set_title("Execution Time (s)")
        ax[0].set_ylabel("Seconds")

        ax[1].bar(functions, cpus, color='red')
        ax[1].set_title("CPU Usage (%)")
        ax[1].set_ylabel("CPU %")

        ax[2].bar(functions, mems, color='green')
        ax[2].set_title("Memory Usage (MB)")
        ax[2].set_ylabel("Memory (MB)")

        plt.tight_layout()
        plt.show()

    @staticmethod
    async def bench_async(func, runs=5):
        """Benchmark an async function."""
        times = []
        for _ in range(runs):
            try:
                start = time.perf_counter_ns()
                await func()
                end = time.perf_counter_ns()
                times.append(end - start)
            except Exception as e:
                print(f"Error benchmarking {func.__name__}: {e}")
                continue
        avg_time = sum(times) / runs
        print(f"[PyPerfCheck] {func.__name__} (async): {avg_time / 1e6:.3f} ms")
        return avg_time

    @staticmethod
    def benchmark_threaded(func, num_threads=4, iterations=5):
        """
        Benchmark a function using multiple threads.

        Args:
            func: The function to benchmark.
            num_threads: Number of threads to use.
            iterations: Number of times to run the benchmark.
        """
        results = []

        def thread_task():
            for _ in range(iterations):
                exec_time, cpu_usage, mem_usage, _ = PyPerfCheck.benchmark(func)()
                results.append((exec_time, cpu_usage, mem_usage))

        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=thread_task)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        avg_time = sum(r[0] for r in results) / len(results)
        avg_cpu = sum(r[1] for r in results) / len(results)
        avg_mem = sum(r[2] for r in results) / len(results)

        print(f"[PyPerfCheck] {func.__name__} (threaded): Avg Time = {avg_time:.6f} s, Avg CPU = {avg_cpu:.2f}%, Avg Mem = {avg_mem:.2f} MB")
        return avg_time, avg_cpu, avg_mem
    
    @staticmethod
    def _process_task(func):
        """
        Helper function for multiprocessing benchmarking.
        """
        exec_time, cpu_usage, mem_usage, _ = PyPerfCheck.benchmark(func)()
        return exec_time, cpu_usage, mem_usage

    @staticmethod
    def benchmark_multiprocessed(func, num_processes=4, iterations=5):
        """
        Benchmark a function using multiple processes.

        Args:
            func: The function to benchmark.
            num_processes: Number of processes to use.
            iterations: Number of times to run the benchmark.
        """
        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.starmap(
                PyPerfCheck._process_task,
                [(func,) for _ in range(iterations)]
            )

        avg_time = sum(r[0] for r in results) / len(results)
        avg_cpu = sum(r[1] for r in results) / len(results)
        avg_mem = sum(r[2] for r in results) / len(results)

        print(f"[PyPerfCheck] {func.__name__} (multiprocessed): Avg Time = {avg_time:.6f} s, Avg CPU = {avg_cpu:.2f}%, Avg Mem = {avg_mem:.2f} MB")
        return avg_time, avg_cpu, avg_mem