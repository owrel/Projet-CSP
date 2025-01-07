from dataclasses import dataclass
from typing import Set


@dataclass
class SetVariable:
    name: str
    lower_bound: set[int]  # F↓
    upper_bound: set[int]  # F↑
    min_card: int  # bFc
    max_card: int  # dFe

    @property
    def undetermined(self) -> Set[int]:
        return self.upper_bound - self.lower_bound

    def __str__(self):
        return (
            f"{self.name}: must contain {self.lower_bound}, "
            f"can contain {self.undetermined}, "
            f"card [{self.min_card}, {self.max_card}]"
        )

    def copy(self):
        return SetVariable(
            self.name,
            lower_bound=set(self.lower_bound),
            upper_bound=set(self.upper_bound),
            min_card=self.min_card,
            max_card=self.max_card,
        )

    def __hash__(self):
        return hash(self.name)

    def is_consistent(self) -> bool:
        if not self.lower_bound.issubset(self.upper_bound):
            return False

        if len(self.lower_bound) > self.max_card:
            return False

        if len(self.upper_bound) < self.min_card:
            return False

        if self.min_card > self.max_card:
            return False

        return True

    def is_valid(self) -> bool:
        if not self.is_consistent():
            return False

        if len(self.lower_bound) < self.min_card:
            return False

        return True

    def __copy__(self):
        return self.copy()
