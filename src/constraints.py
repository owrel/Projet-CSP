from abc import ABC, abstractmethod

from src.variables import SetVariable


class Constraint(ABC):
    @abstractmethod
    def filter_domains(self, variables: dict[str, SetVariable]) -> bool:
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

    def filter_domains(self, variables) -> bool:
        changed = False

        new_upper = variables[self.var1]._upper_bound.union(
            variables[self.var2]._upper_bound
        )
        if not variables[self.result]._upper_bound.issuperset(new_upper):
            variables[self.result]._upper_bound = new_upper
            changed = True

        new_lower = variables[self.var1].lower_bound.union(
            variables[self.var2]._lower_bound
        )
        if not variables[self.result]._lower_bound.issuperset(new_lower):
            variables[self.result]._lower_bound = new_lower
            changed = True

        return changed

    def evaluate(self, variables) -> bool:
        return variables[self.result].lower_bound == (
            variables[self.var1]._lower_bound.union(variables[self.var2]._lower_bound)
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

    def filter_domains(self, variables) -> bool:
        changed = False
        new_upper1 = variables[self.var1]._upper_bound.intersection(
            variables[self.var2]._upper_bound
        )
        if new_upper1 != variables[self.var1]._upper_bound:
            variables[self.var1]._upper_bound = new_upper1
            changed = True

        new_lower2 = variables[self.var2]._lower_bound.union(
            variables[self.var1].lower_bound
        )
        if new_lower2 != variables[self.var2]._lower_bound:
            variables[self.var2]._lower_bound = new_lower2
            changed = True

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

    def filter_domains(self, variables) -> bool:
        if variables[self.var1]._lower_bound == variables[self.var2]._lower_bound:
            raise ValueError(
                f"Different constraint violated: {self.var1}={variables[self.var1]._lower_bound} equals {self.var2}={variables[self.var2]._lower_bound}"
            )
        return False

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

    def filter_domains(self, variables):
        changed = False
        intersection = variables[self.var1]._lower_bound.intersection(
            variables[self.var2]._lower_bound
        )
        if len(intersection) > self.max_intersection:
            raise ValueError(
                f"Intersection cardinality constraint violated: |{self.var1}={variables[self.var1]._lower_bound} ∩ {self.var2}={variables[self.var2]._lower_bound}| = {len(intersection)} > {self.max_intersection}"
            )

        # if len(variables[self.var1]._lower_bound) == self.max_intersection:
        #     variables[self.var1]._upper_bound = variables[self.var1]._lower_bound
        #     changed = True
        # if len(variables[self.var2]._lower_bound) == self.max_intersection:
        #     variables[self.var2]._upper_bound = variables[self.var2]._lower_bound
        #     changed = True

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

    def filter_domains(self, variables):
        changed = False
        var = variables[self.var]
        # print(self.var, var)

        if len(var._lower_bound) > self.cardinality:
            raise ValueError(
                f"Determined variable {self.var}={var._lower_bound} has wrong cardinality {len(var._lower_bound)} > {self.cardinality}"
            )

        if (
            not var.is_determined()
            and len(var._lower_bound | var._upper_bound) < self.cardinality
        ):
            raise ValueError(
                f"Determined variable {self.var}={var._lower_bound} + {var._upper_bound} has wrong cardinality {len(var._lower_bound | var._upper_bound)} < {self.cardinality}"
            )

        if (
            not var.is_determined()
            and len(var.lower_bound) == self.cardinality
            and var._upper_bound != var._lower_bound
        ):
            var._upper_bound = var._lower_bound
            changed = True

        if var.is_determined() and len(var._lower_bound) != self.cardinality:
            raise ValueError(
                f"Determined variable {self.var}={var._lower_bound} has wrong cardinality {len(var._lower_bound)} ≠ {self.cardinality}"
            )

        return changed

    def evaluate(self, variables) -> bool:
        return len(variables[self.var].lower_bound) == self.cardinality

    def get_variables(self) -> list[str]:
        return [self.var]
