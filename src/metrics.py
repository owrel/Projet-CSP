from time import time
from typing import Dict, List
import statistics
import psutil
import os


class SharedMetrics:
    def __init__(self):
        self.start_time: float = time()
        self.end_time: float = 0

        self.nodes_explored: int = 0
        self.backtracks: int = 0
        self.solutions_found: int = 0
        self.cache_hits: int = 0
        self.early_failures: int = 0

        self.constraint_checks: int = 0
        self.filtering_rounds: int = 0
        self.variable_updates: Dict[str, int] = {}

        self.filtering_time: List[float] = []
        self.enumeration_time: List[float] = []
        self.peak_memory: float = 0

    def start_measurement(self):
        self.start_time = time()

    def stop_measurement(self):
        self.end_time = time()

    def add_filtering_time(self, duration: float):
        self.filtering_time.append(duration)

    def add_enumeration_time(self, duration: float):
        self.enumeration_time.append(duration)

    def record_variable_update(self, var_name: str):
        self.variable_updates[var_name] = self.variable_updates.get(var_name, 0) + 1

    def update_memory_usage(self):
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        self.peak_memory = max(self.peak_memory, memory_info.rss / 1024 / 1024)

    def get_report(self) -> str:
        total_time = sum(self.filtering_time) + sum(self.enumeration_time)

        report = [
            "\n=== Performance Report ===",
            f"Total execution time: {total_time:.3f} seconds",
            "\nEnumeration Statistics:",
            f"- Nodes explored: {self.nodes_explored}",
            f"- Backtracks: {self.backtracks}",
            f"- Solutions found: {self.solutions_found}",
            f"- Cache hits: {self.cache_hits}",
            f"- Early failures: {self.early_failures}",
            "\nFiltering Statistics:",
            f"- Constraint checks: {self.constraint_checks}",
            f"- Filtering rounds: {self.filtering_rounds}",
        ]

        if self.filtering_time:
            report.extend(
                [
                    "- Filtering time statistics:",
                    f"  - Total: {sum(self.filtering_time):.3f}s",
                    f"  - Average: {statistics.mean(self.filtering_time):.3f}s",
                    f"  - Min: {min(self.filtering_time):.3f}s",
                    f"  - Max: {max(self.filtering_time):.3f}s",
                ]
            )

        if self.enumeration_time:
            report.extend(
                [
                    "- Enumeration time statistics:",
                    f"  - Total: {sum(self.enumeration_time):.3f}s",
                    f"  - Average: {statistics.mean(self.enumeration_time):.3f}s",
                    f"  - Min: {min(self.enumeration_time):.3f}s",
                    f"  - Max: {max(self.enumeration_time):.3f}s",
                ]
            )

        report.append("\nVariable Updates:")
        for var, count in sorted(
            self.variable_updates.items(), key=lambda x: x[1], reverse=True
        ):
            report.append(f"- {var}: {count} updates")

        if self.enumeration_time:
            report.extend(
                [
                    "\nTiming Breakdown:",
                    f"- Total filtering time: {sum(self.filtering_time):.3f}s ({(sum(self.filtering_time)/total_time)*100:.1f}%)",
                    f"- Total enumeration time: {sum(self.enumeration_time):.3f}s ({(sum(self.enumeration_time)/total_time)*100:.1f}%)",
                ]
            )

        report.extend(
            ["\nMemory Usage:", f"- Peak memory usage: {self.peak_memory:.1f} MB"]
        )

        return "\n".join(report)
