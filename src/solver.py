from typing import Optional, Dict, List
from .variables import SetVariable
from .logger import Logger
from .constraints import Constraint
from .metrics import SharedMetrics
import time
import math


class SetSolver:
    def __init__(self, log_level="INFO", shared_metrics=None):
        self.logger = Logger(log_level)
        self.variables: Dict[str, SetVariable] = {}
        self.constraints: List[Constraint] = []
        self.universe: set[int] = set()
        self.solutions: List[Dict[str, SetVariable]] = []
        self.metrics = shared_metrics if shared_metrics else SharedMetrics()
        self.failed_states = set()
        self.explored_states = {}

    def create_set_variable(
        self,
        name: str,
        lower: set[int],
        upper: set[int],
        min_card: int = 0,
        max_card: Optional[int] = None,
    ) -> SetVariable:
        if max_card is None:
            max_card = len(upper)

        var = SetVariable(name, lower, upper, min_card, max_card)
        if not var.is_consistent():
            raise ValueError(f"Attempting to create inconsistent variable {name}")
        self.variables[name] = var
        self.universe.update(upper)
        return var

    def show_state(self) -> str:
        state_str = []

        state_str.append("=== Variables ===")
        for var in self.variables.values():
            cons = "✓" if var.is_consistent() else "✗"
            validity = "✓" if var.is_valid() else "✗"

            state_str.append(
                f"{var.name}:{var.lower_bound} -> {var.undetermined} [{var.min_card}, {var.max_card}] validity : {validity} cons : {cons}"
            )

        state_str.append("=== Constraints ===")
        for constraint in self.constraints:
            is_satisfied = constraint()
            status = "✓" if is_satisfied else "✗"
            state_str.append(f"{status} {constraint}")

        return "\n".join(state_str)

    def add_constraint(self, constraint: Constraint):
        self.constraints.append(constraint)

    def filter(self) -> bool:
        start_time = time.time()
        self.metrics.filtering_rounds += 1

        queue = list(self.constraints)

        while queue:
            constraint_start = time.time()
            constraint = queue.pop(0)
            self.metrics.constraint_checks += 1
            if constraint.filter():
                constraint_end = time.time()
                self.metrics.add_filtering_time(constraint_end - constraint_start)
                affected_vars = constraint.get_variables()
                for var in affected_vars:
                    if not var.is_consistent():
                        # self.logger.error(
                        #     f"Inconsistency detected in variable {var.name}:"
                        # )
                        # self.logger.error(f"Current state: {var}")
                        # self.logger.error(self._get_inconsistency_reason(var))
                        return False

                for other_constraint in self.constraints:
                    if other_constraint == constraint:
                        continue

                    if any(
                        v in other_constraint.get_variables() for v in affected_vars
                    ):
                        if other_constraint not in queue:
                            queue.append(other_constraint)

        for var in self.variables.values():
            if var.upper_bound == set():  # Empty domain
                print("empty")
                return False
            if not var.is_consistent():
                # self.logger.error(f"Inconsistency detected in variable {var.name}:")
                # self.logger.error(f"Current state: {var}")
                # self.logger.error(self._get_inconsistency_reason(var))
                return False

        end_time = time.time()
        self.metrics.add_filtering_time(end_time - start_time)
        return True

    def _get_inconsistency_reason(self, var: SetVariable) -> str:
        reasons = []
        if not var.lower_bound.issubset(var.upper_bound):
            reasons.append(
                f"Lower bound {var.lower_bound} is not subset of upper bound {var.upper_bound}"
            )

        if len(var.lower_bound) > var.max_card:
            reasons.append(
                f"Lower bound size {len(var.lower_bound)} exceeds max cardinality {var.max_card}"
            )

        if len(var.upper_bound) < var.min_card:
            reasons.append(
                f"Upper bound size {len(var.upper_bound)} is less than min cardinality {var.min_card}"
            )

        if var.min_card > var.max_card:
            reasons.append(
                f"Min cardinality {var.min_card} exceeds max cardinality {var.max_card}"
            )

        return "\n".join(reasons)

    def _choose_variable(self) -> Optional[SetVariable]:

        unsatisfied_vars = set()
        for constraint in self.constraints:
            if not constraint.evaluate():
                unsatisfied_vars.update(constraint.get_variables())

        invalid_vars = set(var for var in self.variables.values() if not var.is_valid())

        undetermined_vars = [var for var in self.variables.values() if var.undetermined]
        if not undetermined_vars:
            return None

        priority_vars = []
        for var in undetermined_vars:
            if var in unsatisfied_vars and var in invalid_vars:
                priority_vars.append((var, 0))
            elif var in unsatisfied_vars:
                priority_vars.append((var, 1))  #
            elif var in invalid_vars:
                priority_vars.append((var, 2))
            else:
                priority_vars.append((var, 3))

        if priority_vars:
            var, _ = min(
                priority_vars, key=lambda x: (x[1], len(x[0].undetermined), x[0].name)
            )
            return var

        return min(undetermined_vars, key=lambda x: (len(x.undetermined), x.name))

    def solve(self, num_solutions: int = 1) -> List[Dict[str, SetVariable]]:
        self.metrics.start_measurement()

        self.logger.info("\nStarting filtering phase...")
        if self.filter():
            print(self.show_state())

            self.logger.info("\nStarting enumeration...")
            self.logger.info(
                f"Searching for {'all' if num_solutions == 0 else num_solutions} solutions"
            )

            solutions = self._enumerate(num_solutions)
            self.metrics.stop_measurement()
            self.logger.info(self.metrics.get_report())
            return solutions
        else:
            self.logger.error("Problem is inconsistent after initial filtering")
            self.metrics.stop_measurement()
            return []

    def _get_state_signature(self) -> tuple:
        return tuple(
            (name, frozenset(var.lower_bound), frozenset(var.upper_bound))
            for name, var in sorted(self.variables.items())
        )

    def _check_early_failure(self) -> bool:
        for constraint in self.constraints:
            if not constraint.evaluate():
                vars = constraint.get_variables()
                if all(var.undetermined for var in vars):
                    return True

        return False

    def constraints_state(self) -> list[tuple[Constraint, bool]]:
        return [(constraint, constraint.evaluate()) for constraint in self.constraints]

    def _enumerate(
        self, num_solutions: int | float = 0
    ) -> List[Dict[str, SetVariable]]:
        if num_solutions == 0:
            num_solutions = math.inf

        solutions = []
        self.failed_states = set()

        def recursive_enumerate(solver: SetSolver) -> bool:
            solver.metrics.nodes_explored += 1
            solver.metrics.update_memory_usage()

            enum_start = time.time()

            if solver._check_early_failure():
                solver.metrics.early_failures += 1
                return False

            state_sig = solver._get_state_signature()
            if state_sig in solver.failed_states:
                solver.metrics.cache_hits += 1
                return False

            all_constraints_satisfied = all(
                constraint.evaluate() for constraint in solver.constraints
            )

            all_var_valid = all(var.is_valid() for var in solver.variables.values())

            if all_constraints_satisfied and all_var_valid:
                solution = {name: var.copy() for name, var in solver.variables.items()}
                solutions.append(solution)
                solver.metrics.solutions_found += 1
                return len(solutions) >= num_solutions

            var = solver._choose_variable()
            if not var:
                solver.failed_states.add(state_sig)
                return False

            value = min(var.undetermined)

            solver_with = solver._create_branch(var.name, value, include=True)
            if solver_with:
                enum_end = time.time()
                solver.metrics.add_enumeration_time(enum_end - enum_start)
                if solver_with.filter():
                    enum_start = time.time()
                    if recursive_enumerate(solver_with):
                        solver.metrics.backtracks += 1
                        return True

            solver_without = solver._create_branch(var.name, value, include=False)
            if solver_without:
                enum_end = time.time()
                solver.metrics.add_enumeration_time(enum_end - enum_start)
                if solver_without.filter():
                    enum_start = time.time()
                    if recursive_enumerate(solver_without):
                        solver.metrics.backtracks += 1
                        return True

            solver.failed_states.add(state_sig)
            return False

        recursive_enumerate(self)
        return solutions

    def _create_branch(
        self, var_name: str, value: int, include: bool
    ) -> "SetSolver | None":
        new_solver = SetSolver(
            log_level=self.logger.log_level, shared_metrics=self.metrics
        )

        for name, var in self.variables.items():
            new_var = var.copy()
            if name == var_name:
                if include:
                    new_var.lower_bound.add(value)
                else:
                    new_var.upper_bound.remove(value)
                if not new_var.is_consistent():
                    return None
            if var.is_consistent() and not new_var.is_consistent():
                return None
            new_solver.variables[name] = new_var

        for constraint in self.constraints:
            new_solver.add_constraint(
                constraint.copy_with_new_variables(new_solver.variables)
            )

        return new_solver
