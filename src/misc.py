from dataclasses import dataclass
from enum import Enum, auto
import time
import tracemalloc

import psutil
from src.constraints import Constraint
from src.variables import SetVariable


class OperationType(Enum):
    ADD = auto()
    REMOVE = auto()

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value > other.value


@dataclass(frozen=True)
class Operation:
    variable: str
    op_type: OperationType
    value: int
    depth: int

    def __str__(self):
        symbol = "+" if self.op_type == OperationType.ADD else "-"
        return f"{self.variable} {symbol} {self.value}"


class SolverMetrics:
    def __init__(self):
        tracemalloc.start()
        self.start_time = time.time()
        self.solution: dict[str, set[int]] = {}
        self.var_value_frequency: dict[str, dict[int, int]] = {}
        self.branches = 0
        self.max_depth = 0
        self.global_max_depth = 0
        self.current_depth = 0
        self.restart_count = 0
        self.random_choices = 0
        self.global_random_choices = 0
        self.initial_memory = psutil.Process().memory_info().rss
        self.max_depth_hits = 0
        self.cache_hits = 0

    def pretty_print(self, interrupted=False):
        print("\n=== Solver Statistics ===")
        print(f"Time elapsed: {time.time() - self.start_time:.2f} seconds")
        print(f"Number of branches: {self.branches}")
        print(f"Maximum search depth: {self.global_max_depth}")
        print(f"# of restarts: {self.restart_count}")
        print(f"Random choices made : {self.global_random_choices}")
        print(f"Cache hits : {self.cache_hits}")

        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage: {current / 10**6:.1f} MB")
        print(f"Peak memory usage: {peak / 10**6:.1f} MB")
        print(
            f"Memory increase: {(psutil.Process().memory_info().rss - self.initial_memory) / 1024 / 1024:.1f} MB"
        )

        if not interrupted and self.solution:
            print("\n=== Solution Found ===")
        elif not interrupted:
            print("\n=== No solution found ===")


class StateComputer:
    def __init__(
        self,
        metrics: SolverMetrics,
        initial_variables: dict[str, SetVariable],
        constraints: list[Constraint],
    ):
        self.metrics = metrics
        self.initial_state = initial_variables
        self.constraints = constraints
        self._cache = {}

    def compute_state(
        self, operations: tuple[Operation, ...]
    ) -> dict[str, SetVariable]:
        cache_key = tuple(
            sorted(((op.variable, op.op_type, op.value, op.depth) for op in operations))
        )

        if cache_key in self._cache:
            self.metrics.cache_hits += 1
            return self._cache[cache_key]

        current_state = {
            name: SetVariable(name, var.lower_bound, var.upper_bound)
            for name, var in self.initial_state.items()
        }

        for op in operations:
            var = current_state[op.variable]
            if op.op_type == OperationType.ADD:
                var._lower_bound.add(op.value)
            else:
                var._upper_bound.remove(op.value)

        changed = True
        while changed:
            changed = False
            for constraint in self.constraints:
                vars = constraint.get_variables()
                # values = [
                #     (
                #         var,
                #         current_state[var].lower_bound,
                #         current_state[var].upper_bound,
                #     )
                #     for var in vars
                # ]
                if constraint.filter_domains(current_state):
                    # print(constraint.__class__)
                    # print(values)
                    # print(
                    #     [
                    #         (
                    #             var,
                    #             current_state[var].lower_bound,
                    #             current_state[var].upper_bound,
                    #         )
                    #         for var in vars
                    #     ]
                    # )

                    changed = True

        self._cache[cache_key] = current_state
        return current_state
