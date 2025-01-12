class SetVariable:

    def __init__(self, name, lower_bound=None, upper_bound=None):
        self.name = name
        self._lower_bound: set[int] = set() if lower_bound is None else set(lower_bound)
        self._upper_bound: set[int] = set() if upper_bound is None else set(upper_bound)

        if not self._lower_bound.issubset(self._upper_bound):
            raise ValueError("Lower bound must be subset of upper bound")

    @property
    def lower_bound(self) -> set[int]:
        return self._lower_bound.copy()

    @property
    def upper_bound(self) -> set[int]:
        return self._upper_bound.copy()

    def is_determined(self):
        return self._lower_bound == self._upper_bound

    def __str__(self):
        return f"{self.name}: [{self._lower_bound} ⊆ X ⊆ {self._upper_bound}]"
