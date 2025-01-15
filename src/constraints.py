from abc import ABC, abstractmethod

from src.variables import SetVariable


class Constraint(ABC):
    @abstractmethod
    def filter_domains(self, variables: dict[str, SetVariable]) -> set[str]:
        pass

    @abstractmethod
    def evaluate(self, variables: dict[str, SetVariable]) -> bool:
        pass

    @abstractmethod
    def get_variables(self) -> list[str]:
        pass


class Union(Constraint):
    """Constraint: result = var1 ∪ var2"""

    def __init__(self, var1, var2, result):
        self.var1 = var1
        self.var2 = var2
        self.result = result

    def __str__(self):
        return f"{self.var1} ∪ {self.var2} = {self.result}"

    def filter_domains(self, variables) -> set[str]:
        changed = set()

        new_upper = variables[self.var1]._upper_bound.union(
            variables[self.var2]._upper_bound
        )
        if not variables[self.result]._upper_bound.issuperset(new_upper):
            variables[self.result]._upper_bound = new_upper
            changed.add(self.result)

        new_lower = variables[self.var1].lower_bound.union(
            variables[self.var2]._lower_bound
        )
        if not variables[self.result]._lower_bound.issuperset(new_lower):
            variables[self.result]._lower_bound = new_lower
            changed.add(self.result)

        return changed

    def evaluate(self, variables) -> bool:
        return variables[self.result].lower_bound == (
            variables[self.var1]._lower_bound.union(variables[self.var2]._lower_bound)
        )

    def get_variables(self) -> list[str]:
        return [self.var1, self.var2, self.result]


class Difference(Constraint):
    """Constraint: result = var1 - var2"""

    def __init__(self, var1, var2, result):
        self.var1 = var1
        self.var2 = var2
        self.result = result

    def __str__(self):
        return f"{self.var1} - {self.var2} = {self.result}"

    def filter_domains(self, variables) -> set[str]:
        changed = set()

        # Upper bound: var1 - var2 subset of var1
        new_upper = (
            variables[self.var1]._upper_bound - variables[self.var2]._lower_bound
        )
        if not variables[self.result]._upper_bound.issuperset(new_upper):
            variables[self.result]._upper_bound = new_upper
            changed.add(self.result)

        # Lower bound: var1 - upper_bound(var2)
        new_lower = (
            variables[self.var1]._lower_bound - variables[self.var2]._upper_bound
        )
        if not variables[self.result]._lower_bound.issuperset(new_lower):
            variables[self.result]._lower_bound = new_lower
            changed.add(self.result)

        return changed

    def evaluate(self, variables) -> bool:
        return variables[self.result].lower_bound == (
            variables[self.var1]._lower_bound - variables[self.var2]._lower_bound
        )

    def get_variables(self) -> list[str]:
        return [self.var1, self.var2, self.result]


class Intersection(Constraint):
    """Constraint: result = var1 ∩ var2"""

    def __init__(self, var1, var2, result):
        self.var1 = var1
        self.var2 = var2
        self.result = result

    def __str__(self):
        return f"{self.var1} ∩ {self.var2} = {self.result}"

    def filter_domains(self, variables) -> set[str]:
        changed = set()

        new_upper = variables[self.var1]._upper_bound.intersection(
            variables[self.var2]._upper_bound
        )
        if not variables[self.result]._upper_bound.issuperset(new_upper):
            variables[self.result]._upper_bound = new_upper
            changed.add(self.result)

        new_lower = variables[self.var1]._lower_bound.intersection(
            variables[self.var2]._lower_bound
        )
        if not variables[self.result]._lower_bound.issuperset(new_lower):
            variables[self.result]._lower_bound = new_lower
            changed.add(self.result)

        return changed

    def evaluate(self, variables) -> bool:
        return variables[self.result].lower_bound == (
            variables[self.var1]._lower_bound.intersection(
                variables[self.var2]._lower_bound
            )
        )

    def get_variables(self) -> list[str]:
        return [self.var1, self.var2, self.result]


class Subset(Constraint):
    """Constraint: var1 ⊆ var2"""

    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return f"{self.var1} ⊆ {self.var2}"

    def filter_domains(self, variables) -> set[str]:
        changed = set()
        if variables[self.var2].is_determined() and not variables[
            self.var1
        ]._upper_bound.issubset(variables[self.var2]._upper_bound):
            raise ValueError(
                f"Subset constraint violated: {self.var1}={variables[self.var1]._lower_bound} not subset of {self.var2}={variables[self.var2]._upper_bound}"
            )

        new_upper1 = variables[self.var1]._upper_bound.intersection(
            variables[self.var2]._upper_bound
        )
        if new_upper1 != variables[self.var1]._upper_bound:
            variables[self.var1]._upper_bound = new_upper1
            changed.add(self.var1)

        new_lower2 = variables[self.var2]._lower_bound.union(
            variables[self.var1].lower_bound
        )
        if new_lower2 != variables[self.var2]._lower_bound:
            variables[self.var2]._lower_bound = new_lower2
            changed.add(self.var2)

        return changed

    def evaluate(self, variables) -> bool:
        return variables[self.var1].lower_bound.issubset(
            variables[self.var2].lower_bound
        )

    def get_variables(self) -> list[str]:
        return [self.var1, self.var2]


class Different(Constraint):
    """Constraint: var1 ≠ var2"""

    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return f"{self.var1} ≠ {self.var2}"

    def filter_domains(self, variables) -> set[str]:
        if (
            variables[self.var1].is_determined()
            and variables[self.var2].is_determined()
            and variables[self.var1]._lower_bound == variables[self.var2]._lower_bound
        ):
            raise ValueError(
                f"Different constraint violated: {self.var1}={variables[self.var1]._lower_bound} = {self.var2}={variables[self.var2]._lower_bound}"
            )
        return set()

    def evaluate(self, variables) -> bool:
        return variables[self.var1]._lower_bound != variables[self.var2]._lower_bound

    def get_variables(self) -> list[str]:
        return [self.var1, self.var2]


class IntersectionConstraintCardinality(Constraint):
    """Constraint: |var1 ∩ var2| ≤ n"""

    def __init__(self, var1, var2, max_intersection):
        self.var1 = var1
        self.var2 = var2
        self.max_intersection = max_intersection

    def __str__(self):
        return f"|{self.var1} ∩ {self.var2}| ≤ {self.max_intersection}"

    def filter_domains(self, variables) -> set[str]:
        changed = set()
        var1, var2 = variables[self.var1], variables[self.var2]

        # Check current lower bounds intersection
        intersection = var1._lower_bound.intersection(var2._lower_bound)
        if len(intersection) > self.max_intersection:
            raise ValueError(
                f"Intersection cardinality constraint violated: |{self.var1}={var1._lower_bound} ∩ {self.var2}={var2._lower_bound}| = {len(intersection)} > {self.max_intersection}"
            )

        # Filter upper bounds based on potential intersections
        for val in list(var1._upper_bound):
            if val not in var1._lower_bound:
                potential_intersection = len(intersection) + len(
                    {val}.intersection(var2._lower_bound)
                )
                if potential_intersection > self.max_intersection:
                    var1._upper_bound.remove(val)
                    changed.add(self.var1)

        for val in list(var2._upper_bound):
            if val not in var2._lower_bound:
                potential_intersection = len(intersection) + len(
                    {val}.intersection(var1._lower_bound)
                )
                if potential_intersection > self.max_intersection:
                    var2._upper_bound.remove(val)
                    changed.add(self.var2)

        return changed

    def evaluate(self, variables) -> bool:
        intersection = variables[self.var1]._lower_bound.intersection(
            variables[self.var2]._lower_bound
        )
        return len(intersection) <= self.max_intersection

    def get_variables(self) -> list[str]:
        return [self.var1, self.var2]


class CardinalityConstraint(Constraint):
    """Constraint: |var1| = n"""

    def __init__(self, var, cardinality):
        self.var = var
        self.cardinality = cardinality

    def __str__(self):
        return f"|{self.var}| = {self.cardinality}"

    def filter_domains(self, variables) -> set[str]:
        changed = set()
        var = variables[self.var]

        # Check if lower bound is too large
        if len(var._lower_bound) > self.cardinality:
            raise ValueError(
                f"Variable {self.var} lower bound {var._lower_bound} (size={len(var._lower_bound)}) exceeds cardinality {self.cardinality}"
            )

        # Check if upper bound is too small to reach cardinality
        if len(var._upper_bound) < self.cardinality:
            raise ValueError(
                f"Variable {self.var} upper bound {var._upper_bound} (size={len(var._upper_bound)}) too small to reach cardinality {self.cardinality}"
            )

        # If lower bound reaches cardinality, fix the set
        if len(var._lower_bound) == self.cardinality:
            if var._upper_bound != var._lower_bound:
                var._upper_bound = var._lower_bound.copy()
                changed.add(self.var)
            return changed

        if len(var._upper_bound) == self.cardinality:
            if var._lower_bound != var._upper_bound:
                var._lower_bound = var._upper_bound.copy()
                changed.add(self.var)
            return changed

        remaining_needed = self.cardinality - len(var._lower_bound)
        optional_values = var._upper_bound - var._lower_bound

        if len(optional_values) == remaining_needed:
            var._lower_bound.update(optional_values)
            changed.add(self.var)

        return changed

    def evaluate(self, variables) -> bool:
        return len(variables[self.var].lower_bound) == self.cardinality

    def get_variables(self) -> list[str]:
        return [self.var]


class LexicographicOrdering(Constraint):
    """Constraint: var1 < var2 in lexicographic order"""

    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return f"{self.var1} <lex {self.var2}"

    def _compare_sets_lex(self, set1: set[int], set2: set[int]) -> bool:
        list1 = sorted(set1)
        list2 = sorted(set2)

        for i in range(min(len(list1), len(list2))):
            if list1[i] < list2[i]:
                return True
            if list1[i] > list2[i]:
                return False
        return len(list1) < len(list2)

    def _can_be_greater_lex(self, set1: set[int], set2: set[int]) -> bool:
        list1 = sorted(set1)
        list2 = sorted(set2)

        for i in range(min(len(list1), len(list2))):
            if list1[i] > list2[i]:
                return True
            if list1[i] < list2[i]:
                return False
        return len(list1) > len(list2)

    def _can_be_less_lex(self, set1: set[int], set2: set[int]) -> bool:
        list1 = sorted(set1)
        list2 = sorted(set2)

        for i in range(min(len(list1), len(list2))):
            if list1[i] < list2[i]:
                return True
            if list1[i] > list2[i]:
                return False
        return len(list1) < len(list2)

    def filter_domains(self, variables) -> set[str]:
        changed = set()
        var1, var2 = variables[self.var1], variables[self.var2]

        for val in list(var2._upper_bound):
            if not self._can_be_greater_lex(
                var2._lower_bound | {val}, var1._lower_bound
            ):
                var2._upper_bound.remove(val)
                changed.add(self.var2)

        if not self._compare_sets_lex(var1._lower_bound, var2._upper_bound):
            raise ValueError(
                f"Lexicographic ordering constraint cannot be satisfied: {self.var1}={var1._lower_bound} ≥lex {self.var2}={var2._upper_bound}"
            )

        return changed

    def evaluate(self, variables) -> bool:
        return self._compare_sets_lex(
            variables[self.var1].lower_bound, variables[self.var2].lower_bound
        )

    def get_variables(self) -> list[str]:
        return [self.var1, self.var2]
