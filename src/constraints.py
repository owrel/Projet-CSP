from abc import ABC, abstractmethod
from typing import Dict, List
from .variables import SetVariable
from .logger import Logger

logger = Logger("QUIETE")


class Constraint(ABC):
    def __init__(self, negated: bool = False):
        self.negated = negated

    @abstractmethod
    def filter(self) -> bool:
        pass

    @abstractmethod
    def copy_with_new_variables(
        self, new_variables: Dict[str, SetVariable]
    ) -> "Constraint":
        pass

    @abstractmethod
    def _evaluate(self) -> bool:
        pass

    def evaluate(self) -> bool:
        result = self._evaluate()
        return not result if self.negated else result

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def get_variables(self) -> List[SetVariable]:
        pass

    def __call__(self) -> bool:
        return self.evaluate()

    def __repr__(self) -> str:
        return self.__str__()


class Subset(Constraint):
    def __init__(self, F: SetVariable, G: SetVariable, negated: bool = False):
        super().__init__(negated)
        self.F = F
        self.G = G

    def copy_with_new_variables(
        self, new_variables: Dict[str, SetVariable]
    ) -> "Subset":
        return Subset(
            new_variables[self.F.name], new_variables[self.G.name], self.negated
        )

    def _evaluate(self) -> bool:
        return self.F.lower_bound.issubset(self.G.lower_bound)

    def __str__(self) -> str:
        op = "⊈" if self.negated else "⊆"
        return f"{self.F.name} {op} {self.G.name}"

    def get_variables(self) -> List[SetVariable]:
        return [self.F, self.G]

    def filter(self) -> bool:
        changed = False
        logger.debug(
            f"\nFiltering Subset constraint between {self.F.name} and {self.G.name}"
        )

        # F↑ ← F↑ ∩ G↑
        new_F_upper = self.F.upper_bound.intersection(self.G.upper_bound)
        if new_F_upper != self.F.upper_bound:
            self.F.upper_bound = new_F_upper
            changed = True
            logger.debug(f"Updated {self.F.name} upper bound: {new_F_upper}")

        # G↓ ← F↓ ∪ G↓
        new_G_lower = self.F.lower_bound.union(self.G.lower_bound)
        if new_G_lower != self.G.lower_bound:
            self.G.lower_bound = new_G_lower
            changed = True
            logger.debug(f"Updated {self.G.name} lower bound: {new_G_lower}")

        # bGc ← max{bGc, |(F↓ ∪ G↓)|}
        new_G_min = max(
            self.G.min_card, len(self.F.lower_bound.union(self.G.lower_bound))
        )
        if new_G_min > self.G.min_card:
            self.G.min_card = new_G_min
            changed = True
            logger.debug(f"Updated {self.G.name} min card: {new_G_min}")

        # dFe ← min{dFe, |(F↑ ∩ G↑)|}
        new_F_max = min(
            self.F.max_card, len(self.F.upper_bound.intersection(self.G.upper_bound))
        )
        if new_F_max < self.F.max_card:
            self.F.max_card = new_F_max
            changed = True
            logger.debug(f"Updated {self.F.name} max card: {new_F_max}")

        return changed


class Union(Constraint):
    def __init__(
        self, H: SetVariable, F: SetVariable, G: SetVariable, negated: bool = False
    ):
        super().__init__(negated)
        self.H = H
        self.F = F
        self.G = G

    def copy_with_new_variables(self, new_variables: Dict[str, SetVariable]) -> "Union":
        return Union(
            new_variables[self.H.name],
            new_variables[self.F.name],
            new_variables[self.G.name],
            self.negated,
        )

    def _evaluate(self) -> bool:
        return self.H.lower_bound == self.F.lower_bound.union(self.G.lower_bound)

    def __str__(self) -> str:
        op = "≠" if self.negated else "="
        return f"{self.H.name} {op} {self.F.name} ∪ {self.G.name}"

    def get_variables(self) -> List[SetVariable]:
        return [self.H, self.F, self.G]

    def filter(self) -> bool:
        changed = False
        logger.debug(
            f"Filtering Union constraint between {self.H.name}, {self.F.name}, {self.G.name}"
        )

        # H↑ ← F↑ ∪ G↑
        new_H_upper = self.F.upper_bound.union(self.G.upper_bound)
        if new_H_upper != self.H.upper_bound:
            self.H.upper_bound = new_H_upper
            changed = True
            logger.debug(f"Updated {self.H.name} upper bound: {new_H_upper}")

        # H↓ ← F↓ ∪ G↓
        new_H_lower = self.F.lower_bound.union(self.G.lower_bound)
        if new_H_lower != self.H.lower_bound:
            self.H.lower_bound = new_H_lower
            changed = True
            logger.debug(f"Updated {self.H.name} lower bound: {new_H_lower}")

        # F↑ ← H↑
        new_F_upper = self.F.upper_bound.intersection(self.H.upper_bound)
        if new_F_upper != self.F.upper_bound:
            self.F.upper_bound = new_F_upper
            changed = True
            logger.debug(f"Updated {self.F.name} upper bound: {new_F_upper}")

        # G↑ ← H↑
        new_G_upper = self.G.upper_bound.intersection(self.H.upper_bound)
        if new_G_upper != self.G.upper_bound:
            self.G.upper_bound = new_G_upper
            changed = True
            logger.debug(f"Updated {self.G.name} upper bound: {new_G_upper}")

        # Update cardinalities
        new_H_min = max(
            self.H.min_card, len(self.F.lower_bound.union(self.G.lower_bound))
        )
        if new_H_min > self.H.min_card:
            self.H.min_card = new_H_min
            changed = True
            logger.debug(f"Updated {self.H.name} min card: {new_H_min}")

        new_H_max = min(
            self.H.max_card, len(self.F.upper_bound.union(self.G.upper_bound))
        )
        if new_H_max < self.H.max_card:
            self.H.max_card = new_H_max
            changed = True
            logger.debug(f"Updated {self.H.name} max card: {new_H_max}")

        return changed


class Intersection(Constraint):
    def __init__(
        self, H: SetVariable, F: SetVariable, G: SetVariable, negated: bool = False
    ):
        super().__init__(negated)
        self.H = H
        self.F = F
        self.G = G

    def copy_with_new_variables(
        self, new_variables: Dict[str, SetVariable]
    ) -> "Intersection":
        return Intersection(
            new_variables[self.H.name],
            new_variables[self.F.name],
            new_variables[self.G.name],
            self.negated,
        )

    def _evaluate(self) -> bool:
        return self.H.lower_bound == self.F.lower_bound.intersection(self.G.lower_bound)

    def __str__(self) -> str:
        op = "≠" if self.negated else "="
        return f"{self.H.name} {op} {self.F.name} ∩ {self.G.name}"

    def get_variables(self) -> List[SetVariable]:
        return [self.H, self.F, self.G]

    def filter(self) -> bool:
        changed = False
        logger.debug(
            f"Filtering Intersection constraint between {self.H.name}, {self.F.name}, {self.G.name}"
        )

        # H↑ ← F↑ ∩ G↑
        new_H_upper = self.F.upper_bound.intersection(self.G.upper_bound)
        if new_H_upper != self.H.upper_bound:
            self.H.upper_bound = new_H_upper
            changed = True
            logger.debug(f"Updated {self.H.name} upper bound: {new_H_upper}")

        # H↓ ← F↓ ∩ G↓
        new_H_lower = self.F.lower_bound.intersection(self.G.lower_bound)
        if new_H_lower != self.H.lower_bound:
            self.H.lower_bound = new_H_lower
            changed = True
            logger.debug(f"Updated {self.H.name} lower bound: {new_H_lower}")

        # F↓ must contain H↓
        new_F_lower = self.F.lower_bound.union(self.H.lower_bound)
        if new_F_lower != self.F.lower_bound:
            self.F.lower_bound = new_F_lower
            changed = True
            logger.debug(f"Updated {self.F.name} lower bound: {new_F_lower}")

        # G↓ must contain H↓
        new_G_lower = self.G.lower_bound.union(self.H.lower_bound)
        if new_G_lower != self.G.lower_bound:
            self.G.lower_bound = new_G_lower
            changed = True
            logger.debug(f"Updated {self.G.name} lower bound: {new_G_lower}")

        # Update cardinalities
        new_H_min = max(
            self.H.min_card, len(self.F.lower_bound.intersection(self.G.lower_bound))
        )
        if new_H_min > self.H.min_card:
            self.H.min_card = new_H_min
            changed = True
            logger.debug(f"Updated {self.H.name} min card: {new_H_min}")

        new_H_max = min(
            self.H.max_card, len(self.F.upper_bound.intersection(self.G.upper_bound))
        )
        if new_H_max < self.H.max_card:
            self.H.max_card = new_H_max
            changed = True
            logger.debug(f"Updated {self.H.name} max card: {new_H_max}")

        return changed


class Difference(Constraint):
    def __init__(
        self, H: SetVariable, F: SetVariable, G: SetVariable, negated: bool = False
    ):
        super().__init__(negated)
        self.H = H
        self.F = F
        self.G = G

    def copy_with_new_variables(
        self, new_variables: Dict[str, SetVariable]
    ) -> "Difference":
        return Difference(
            new_variables[self.H.name],
            new_variables[self.F.name],
            new_variables[self.G.name],
            self.negated,
        )

    def _evaluate(self) -> bool:
        return self.H.lower_bound == self.F.lower_bound.difference(self.G.lower_bound)

    def __str__(self) -> str:
        op = "≠" if self.negated else "="
        return f"{self.H.name} {op} {self.F.name} \\ {self.G.name}"

    def get_variables(self) -> List[SetVariable]:
        return [self.H, self.F, self.G]

    def filter(self) -> bool:
        changed = False
        logger.debug(
            f"Filtering Difference constraint between {self.H.name}, {self.F.name}, {self.G.name}"
        )

        # H↑ ← (H↑ ∩ F↑) \ G↓
        new_H_upper = (self.H.upper_bound.intersection(self.F.upper_bound)).difference(
            self.G.lower_bound
        )
        if new_H_upper != self.H.upper_bound:
            self.H.upper_bound = new_H_upper
            changed = True
            logger.debug(f"Updated {self.H.name} upper bound: {new_H_upper}")

        # F↑ ← F↑ ∩ (H↑ ∪ G↑)
        new_F_upper = self.F.upper_bound.intersection(
            self.H.upper_bound.union(self.G.upper_bound)
        )
        if new_F_upper != self.F.upper_bound:
            self.F.upper_bound = new_F_upper
            changed = True
            logger.debug(f"Updated {self.F.name} upper bound: {new_F_upper}")

        # G↑ ← G↑ \ H↓
        new_G_upper = self.G.upper_bound.difference(self.H.lower_bound)
        if new_G_upper != self.G.upper_bound:
            self.G.upper_bound = new_G_upper
            changed = True
            logger.debug(f"Updated {self.G.name} upper bound: {new_G_upper}")

        # H↓ ← H↓ ∪ (F↓ \ G↑)
        new_H_lower = self.H.lower_bound.union(
            self.F.lower_bound.difference(self.G.upper_bound)
        )
        if new_H_lower != self.H.lower_bound:
            self.H.lower_bound = new_H_lower
            changed = True
            logger.debug(f"Updated {self.H.name} lower bound: {new_H_lower}")

        # F↓ ← H↓ ∪ F↓
        new_F_lower = self.H.lower_bound.union(self.F.lower_bound)
        if new_F_lower != self.F.lower_bound:
            self.F.lower_bound = new_F_lower
            changed = True
            logger.debug(f"Updated {self.F.name} lower bound: {new_F_lower}")

        # Update cardinalities
        # bHc ← max{bHc, |(H↓ ∪ (F↓ \ G↑))|}
        new_H_min = max(
            self.H.min_card,
            len(
                self.H.lower_bound.union(
                    self.F.lower_bound.difference(self.G.upper_bound)
                )
            ),
        )
        if new_H_min > self.H.min_card:
            self.H.min_card = new_H_min
            changed = True
            logger.debug(f"Updated {self.H.name} min card: {new_H_min}")

        # bFc ← max{bFc, |(H↓ ∪ F↓)|}
        new_F_min = max(
            self.F.min_card, len(self.H.lower_bound.union(self.F.lower_bound))
        )
        if new_F_min > self.F.min_card:
            self.F.min_card = new_F_min
            changed = True
            logger.debug(f"Updated {self.F.name} min card: {new_F_min}")

        # dHe ← min{dHe, |((F↑ ∩ H↑) \ G↓)|}
        new_H_max = min(
            self.H.max_card,
            len(
                (self.F.upper_bound.intersection(self.H.upper_bound)).difference(
                    self.G.lower_bound
                )
            ),
        )
        if new_H_max < self.H.max_card:
            self.H.max_card = new_H_max
            changed = True
            logger.debug(f"Updated {self.H.name} max card: {new_H_max}")

        # dFe ← min{dFe, |(F↑ ∩ (H↑ ∪ G↑))|}
        new_F_max = min(
            self.F.max_card,
            len(
                self.F.upper_bound.intersection(
                    self.H.upper_bound.union(self.G.upper_bound)
                )
            ),
        )
        if new_F_max < self.F.max_card:
            self.F.max_card = new_F_max
            changed = True
            logger.debug(f"Updated {self.F.name} max card: {new_F_max}")

        # dGe ← min{dGe, |(G↑ \ H↓)|}
        new_G_max = min(
            self.G.max_card, len(self.G.upper_bound.difference(self.H.lower_bound))
        )
        if new_G_max < self.G.max_card:
            self.G.max_card = new_G_max
            changed = True
            logger.debug(f"Updated {self.G.name} max card: {new_G_max}")

        return changed
