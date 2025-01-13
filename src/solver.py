import time
import signal
import sys
import random
from enum import Enum

from src.constraints import Constraint
from src.misc import Operation, OperationType, SolverMetrics, StateComputer
from src.variables import SetVariable
from .visualization import SetTreeVisualizer, ConstraintGraphVisualizer


class Restarting(Exception): ...


class VariableStrategy(Enum):
    FIRST = "first"
    SMALLEST_DOMAIN = "smallest_domain"
    LEAST_CONSTRAINED = "least_constrained"
    MOST_CONSTRAINED = "most_constrained"
    RANDOM = "random"
    CUSTOM_ORDER = "custom_order"


class VariableValueStrategy(Enum):
    SIMPLE = "simple"
    RANDOM = "random"
    LOWEST_FREQUENCY = "lowest_frequency"


class RestartingStrategy(Enum):
    RANDOM = "random"
    NEXT = "next"
    CONSTRAINED_RANDOM = "constrained_random"


class SetSolver:
    def __init__(
        self,
        variable_strategy: VariableStrategy = VariableStrategy.SMALLEST_DOMAIN,
        value_strategy: VariableValueStrategy = VariableValueStrategy.RANDOM,
        restarting_strategy: RestartingStrategy = RestartingStrategy.CONSTRAINED_RANDOM,
        custom_order: list[str] | None = None,
        visualize: bool = False,
    ) -> None:
        self.variable_strategy = variable_strategy
        self.value_strategy = value_strategy
        self.restarting_strategy = restarting_strategy
        self.custom_order = custom_order or []
        self.visualize = visualize

        self.variables: dict[str, SetVariable] = {}
        self.constraints: list[Constraint] = []
        self.metrics = SolverMetrics()
        self.visualizer: SetTreeVisualizer | None = (
            SetTreeVisualizer() if visualize else None
        )
        self.operation_history: list[Operation] = []
        self.solution_path: list[Operation] = []
        self.visited_states: set[tuple[Operation, ...]] = set()
        self.state_computer: StateComputer
        self.restarting = False

        signal.signal(signal.SIGINT, self.handle_interrupt)

    def add_variable(self, variable: SetVariable) -> None:
        self.variables[variable.name] = variable
        for value in variable._upper_bound:
            if variable.name not in self.metrics.var_value_frequency:
                self.metrics.var_value_frequency[variable.name] = {}
            self.metrics.var_value_frequency[variable.name][value] = 0

    def add_constraint(self, constraint: Constraint) -> None:
        self.constraints.append(constraint)

    def get_variable_constraints(self, var_name: str) -> int:
        return sum(
            1
            for c in self.constraints
            if var_name
            in [
                getattr(c, attr) for attr in dir(c) if isinstance(getattr(c, attr), str)
            ]
        )

    def visualize_constraint_graph(self):
        constraint_viz = ConstraintGraphVisualizer()
        constraint_viz.build_graph(self.variables, self.constraints)
        constraint_viz.save(f"constraint_graph_{time.strftime('%Y%m%d_%H%M%S')}")

    def choose_variable(
        self, variables: dict[str, SetVariable]
    ) -> tuple[str, SetVariable] | None:
        undetermined = [
            (name, var) for name, var in variables.items() if not var.is_determined()
        ]
        if not undetermined:
            return None

        if self.variable_strategy == VariableStrategy.CUSTOM_ORDER:
            ordered_vars = []
            for var_name in self.custom_order:
                for name, var in undetermined:
                    if name == var_name:
                        ordered_vars.append((name, var))
                        break
            remaining_vars = [
                (name, var)
                for name, var in undetermined
                if name not in self.custom_order
            ]
            ordered_vars.extend(remaining_vars)

            if not ordered_vars:
                return None

            if (
                len(ordered_vars) <= 1
                or self.metrics.random_choices >= 10 * self.metrics.restart_count
            ):
                return ordered_vars[0]
            else:
                print("random choice")
                self.metrics.random_choices += 1
                self.metrics.global_random_choices += 1

                if self.restarting_strategy == RestartingStrategy.NEXT:
                    return ordered_vars[
                        self.metrics.restart_count % (len(ordered_vars) - 1)
                    ]
                elif self.restarting_strategy == RestartingStrategy.RANDOM:
                    return random.choice(ordered_vars)
                elif self.restarting_strategy == RestartingStrategy.CONSTRAINED_RANDOM:
                    return random.choice(
                        ordered_vars[
                            min(
                                len(ordered_vars) - 1, self.metrics.restart_count
                            ) : min(len(ordered_vars), self.metrics.restart_count * 2)
                        ]
                    )

        elif self.variable_strategy == VariableStrategy.RANDOM:
            return random.choice(undetermined)
        elif self.variable_strategy == VariableStrategy.FIRST:
            return undetermined[0]
        else:
            sorted_vars = None
            if self.variable_strategy == VariableStrategy.SMALLEST_DOMAIN:
                sorted_vars = sorted(
                    undetermined, key=lambda x: len(x[1].upper_bound - x[1].lower_bound)
                )

            elif self.variable_strategy == VariableStrategy.LEAST_CONSTRAINED:
                sorted_vars = sorted(
                    undetermined, key=lambda x: self.get_variable_constraints(x[0])
                )

            elif self.variable_strategy == VariableStrategy.MOST_CONSTRAINED:
                sorted_vars = sorted(
                    undetermined,
                    key=lambda x: self.get_variable_constraints(x[0]),
                    reverse=True,
                )
            else:
                return undetermined[0]

            if not sorted_vars:
                return None
            if (
                len(sorted_vars) <= 1
                or self.metrics.random_choices >= 10 * self.metrics.restart_count
            ):
                return sorted_vars[0]
            else:
                print("random choice")
                self.metrics.random_choices += 1
                self.metrics.global_random_choices += 1
                if self.restarting_strategy == RestartingStrategy.NEXT:
                    return sorted_vars[
                        self.metrics.restart_count % (len(sorted_vars) - 1)
                    ]
                elif self.restarting_strategy == RestartingStrategy.RANDOM:
                    return random.choice(sorted_vars)
                elif self.restarting_strategy == RestartingStrategy.CONSTRAINED_RANDOM:
                    return random.choice(
                        sorted_vars[
                            min(len(sorted_vars) - 1, self.metrics.restart_count) : min(
                                len(sorted_vars), self.metrics.restart_count * 2
                            )
                        ]
                    )
                else:
                    print("EROORORORO")

    def handle_interrupt(self, signum: int, frame: object) -> None:
        self.metrics.pretty_print(interrupted=True)
        if self.visualizer:
            self.visualizer.build_from_history(
                self.operation_history,
                self.solution_path,
                self.variables,
                self.constraints,
            )
            self.visualizer.save(f"search_tree_{time.strftime('%Y%m%d_%H%M%S')}")
        sys.exit(1)

    def solve(self) -> dict[str, set] | None:
        self.state_computer = StateComputer(
            self.metrics, constraints=self.constraints, initial_variables=self.variables
        )

        try:
            while not self.restarting:
                try:
                    self.restarting = False

                    solution = self._solve([])

                    if self.visualizer:
                        self.visualizer.build_from_history(
                            self.operation_history,
                            self.solution_path,
                            self.variables,
                            self.constraints,
                        )
                        self.visualizer.save(
                            f"search_tree_{time.strftime('%Y%m%d_%H%M%S')}"
                        )
                    self.metrics.pretty_print(interrupted=False)
                    return solution
                except Restarting:
                    ...
        except KeyboardInterrupt:

            if self.visualizer:
                self.visualizer.build_from_history(
                    self.operation_history,
                    self.solution_path,
                    self.variables,
                    self.constraints,
                )
                self.visualizer.save(f"search_tree_{time.strftime('%Y%m%d_%H%M%S')}")
            self.metrics.pretty_print(interrupted=True)
            return None

    def _restart(self, current_path):
        if self.metrics.max_depth_hits >= 10 + self.metrics.max_depth:
            self.metrics.current_depth = 0
            self.metrics.max_depth = 0
            self.metrics.max_depth_hits = 0
            self.visited_states.clear()
            self.operation_history.clear()
            self.solution_path.clear()
            self.metrics.restart_count += 1
            self.metrics.random_choices = 0
            raise Restarting()
        return False

    def _choose_value(self, var: SetVariable) -> list[int]:
        undetermined = list(var.upper_bound - var.lower_bound)

        if self.value_strategy == VariableValueStrategy.RANDOM:
            random.shuffle(undetermined)
            return undetermined

        elif self.value_strategy == VariableValueStrategy.LOWEST_FREQUENCY:
            return sorted(
                undetermined,
                key=lambda x: self.metrics.var_value_frequency.get(var.name, {}).get(
                    x, 0
                ),
            )
        return undetermined

    def _solve(self, current_path: list[Operation]) -> dict[str, set] | None:
        try:
            if not self.restarting:
                self.metrics.branches += 1
            print(
                f"Branches: {self.metrics.branches:,d} | "
                f"Max Depth: {self.metrics.max_depth} | "
                f"Current Depth: {self.metrics.current_depth} | "
                f"Max Depth Hits: {self.metrics.max_depth_hits}",
            )

            if self._restart(current_path):
                self.metrics.current_depth = len(current_path)
                return None
            path_tuple = tuple(current_path)

            if path_tuple in self.visited_states:
                return None
            self.visited_states.add(path_tuple)

            try:
                current_state = self.state_computer.compute_state(path_tuple)
            except ValueError:
                return None

            self.metrics.current_depth = len(current_path)
            if self.metrics.current_depth > self.metrics.max_depth:
                self.metrics.max_depth_hits = 0
                self.metrics.max_depth = self.metrics.current_depth
                if self.metrics.global_max_depth < self.metrics.max_depth:
                    self.metrics.global_max_depth = self.metrics.max_depth

            if all(
                constraint.evaluate(current_state) for constraint in self.constraints
            ):
                solution = {
                    name: var.lower_bound for name, var in current_state.items()
                }
                self.metrics.solution = solution
                self.solution_path = current_path.copy()
                return solution

            var_tuple = self.choose_variable(current_state)
            if var_tuple is None:
                return None

            var_name, var = var_tuple
            elements = self._choose_value(var)

            for element in elements:
                if not self.restarting:
                    self.metrics.var_value_frequency[var_name][element] += 1
                add_op = Operation(
                    var_name, OperationType.ADD, element, len(current_path)
                )
                self.operation_history.append(add_op)
                solution = self._solve(current_path + [add_op])

                if solution:
                    return solution

                remove_op = Operation(
                    var_name, OperationType.REMOVE, element, len(current_path)
                )
                self.operation_history.append(remove_op)
                solution = self._solve(current_path + [remove_op])

                if solution:
                    return solution

            if self.metrics.current_depth == self.metrics.max_depth:
                self.metrics.max_depth_hits += 1

            self.metrics.current_depth -= 1
            return None

        except KeyboardInterrupt:
            if self.visualizer:
                self.visualizer.build_from_history(
                    self.operation_history,
                    self.solution_path,
                    self.variables,
                    self.constraints,
                )
                self.visualizer.save(f"search_tree_{time.strftime('%Y%m%d_%H%M%S')}")
            self.metrics.pretty_print(interrupted=True)
            sys.exit(1)
