from typing import Optional
from dataclasses import dataclass


@dataclass
class SetVariable:
    name: str
    lower_bound: set[int]  # F↓
    upper_bound: set[int]  # F↑
    min_card: int  # bFc
    max_card: int  # dFe


class SetSolver:
    def __init__(self):
        self.variables: dict[str, SetVariable] = {}
        self.constraints: list[tuple] = []
        self.universe: set[int] = set()

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
        self.variables[name] = var
        self.universe.update(upper)
        return var

    def add_constraint(self, constraint_type: str, *args):
        self.constraints.append((constraint_type, args))

    def _filter_union(self, H: SetVariable, F: SetVariable, G: SetVariable) -> bool:
        changed = False

        # Update bounds
        new_H_lower = F.lower_bound.union(G.lower_bound)
        if new_H_lower != H.lower_bound:
            H.lower_bound = new_H_lower
            changed = True

        new_H_upper = F.upper_bound.union(G.upper_bound)
        if new_H_upper != H.upper_bound:
            H.upper_bound = new_H_upper
            changed = True

        #cardinality

        return changed

    def _filter_intersection(
        self, H: SetVariable, F: SetVariable, G: SetVariable
    ) -> bool:
        changed = False

        # Update bounds
        new_H_lower = F.lower_bound.intersection(G.lower_bound)
        if new_H_lower != H.lower_bound:
            H.lower_bound = new_H_lower
            changed = True

        new_H_upper = F.upper_bound.intersection(G.upper_bound)
        if new_H_upper != H.upper_bound:
            H.upper_bound = new_H_upper
            changed = True



        return changed

    def _filter_subset(self, F: SetVariable, G: SetVariable) -> bool:
        changed = False

        # F↑ ← F↑ ∩ G↑
        new_F_upper = F.upper_bound.intersection(G.upper_bound)
        if new_F_upper != F.upper_bound:
            F.upper_bound = new_F_upper
            changed = True

        # G↑ ← G↑ (no change needed)

        # F↓ ← F↓ (no change needed)

        # G↓ ← F↓ ∪ G↓
        new_G_lower = F.lower_bound.union(G.lower_bound)
        if new_G_lower != G.lower_bound:
            G.lower_bound = new_G_lower
            changed = True

        # bFc ← bFc (no change needed)

        # bGc ← max{bGc, |(F↓ ∪ G↓)|}
        new_G_min = max(G.min_card, len(F.lower_bound.union(G.lower_bound)))
        if new_G_min > G.min_card:
            G.min_card = new_G_min
            changed = True

        # dFe ← min{dFe, |(F↑ ∩ G↑)|}
        new_F_max = min(F.max_card, len(F.upper_bound.intersection(G.upper_bound)))
        if new_F_max < F.max_card:
            F.max_card = new_F_max
            changed = True

        # dGe ← dGe (no change needed)

        return changed

    def _filter_difference(
        self, H: SetVariable, F: SetVariable, G: SetVariable
    ) -> bool:
        changed = False

        # H↑ ← (H↑ ∩ F↑) \ G↓
        new_H_upper = (H.upper_bound.intersection(F.upper_bound)).difference(
            G.lower_bound
        )
        if new_H_upper != H.upper_bound:
            H.upper_bound = new_H_upper
            changed = True

        # F↑ ← F↑ ∩ (H↑ ∪ G↑)
        new_F_upper = F.upper_bound.intersection(H.upper_bound.union(G.upper_bound))
        if new_F_upper != F.upper_bound:
            F.upper_bound = new_F_upper
            changed = True

        # G↑ ← G↑ \ H↓
        new_G_upper = G.upper_bound.difference(H.lower_bound)
        if new_G_upper != G.upper_bound:
            G.upper_bound = new_G_upper
            changed = True

        # H↓ ← H↓ ∪ (F↓ \ G↑)
        new_H_lower = H.lower_bound.union(F.lower_bound.difference(G.upper_bound))
        if new_H_lower != H.lower_bound:
            H.lower_bound = new_H_lower
            changed = True

        # F↓ ← H↓ ∪ F↓
        new_F_lower = H.lower_bound.union(F.lower_bound)
        if new_F_lower != F.lower_bound:
            F.lower_bound = new_F_lower
            changed = True

        # Update cardinalities
        # bHc ← max{bHc, |(H↓ ∪ (F↓ \ G↑))|}
        new_H_min = max(
            H.min_card,
            len(H.lower_bound.union(F.lower_bound.difference(G.upper_bound))),
        )
        if new_H_min > H.min_card:
            H.min_card = new_H_min
            changed = True

        # bFc ← max{bFc, |(H↓ ∪ F↓)|}
        new_F_min = max(F.min_card, len(H.lower_bound.union(F.lower_bound)))
        if new_F_min > F.min_card:
            F.min_card = new_F_min
            changed = True

        # dHe ← min{dHe, |((F↑ ∩ H↑) \ G↓)|}
        new_H_max = min(
            H.max_card,
            len((F.upper_bound.intersection(H.upper_bound)).difference(G.lower_bound)),
        )
        if new_H_max < H.max_card:
            H.max_card = new_H_max
            changed = True

        # dFe ← min{dFe, |(F↑ ∩ (H↑ ∪ G↑))|}
        new_F_max = min(
            F.max_card,
            len(F.upper_bound.intersection(H.upper_bound.union(G.upper_bound))),
        )
        if new_F_max < F.max_card:
            F.max_card = new_F_max
            changed = True

        # dGe ← min{dGe, |(G↑ \ H↓)|}
        new_G_max = min(G.max_card, len(G.upper_bound.difference(H.lower_bound)))
        if new_G_max < G.max_card:
            G.max_card = new_G_max
            changed = True

        return changed

    def propagate(self) -> bool:
        changed = True
        while changed:
            changed = False
            for constraint_type, args in self.constraints:
                if constraint_type == "subset":
                    changed = changed or self._filter_subset(
                        self.variables[args[0]], self.variables[args[1]]
                    )
                elif constraint_type == "difference":
                    changed = changed or self._filter_difference(
                        self.variables[args[0]],
                        self.variables[args[1]],
                        self.variables[args[2]],
                    )
                elif constraint_type == "union":
                    changed = changed or self._filter_union(
                        self.variables[args[0]],
                        self.variables[args[1]],
                        self.variables[args[2]],
                    )
                elif constraint_type == "intersection":
                    changed = changed or self._filter_intersection(
                        self.variables[args[0]],
                        self.variables[args[1]],
                        self.variables[args[2]],
                    )

            # Check consistency
            for var in self.variables.values():
                if not self._is_consistent(var):
                    return False
        return True

    def _is_consistent(self, var: SetVariable) -> bool:
        return (
            var.lower_bound.issubset(var.upper_bound)
            and len(var.lower_bound) <= var.max_card
            and len(var.upper_bound) >= var.min_card
            and var.min_card <= var.max_card
        )


def subset_example():
    solver = SetSolver()

    X = solver.create_set_variable(
        name="X",
        lower={1, 2},  # must contain 1 and 2
        upper={1, 2, 3, 4},  # can contain up to 4
        min_card=2,
        max_card=3,
    )

    Y = solver.create_set_variable(
        name="Y",
        lower={2},  # must contain 2
        upper={1, 2, 3, 4, 5},  # can contain up to 5
        min_card=1,
        max_card=4,
    )

    solver.add_constraint("subset", "X", "Y")

    solver.propagate()

    print("\nAfter propagation:")
    print(f"X must contain: {X.lower_bound}, can contain: {X.upper_bound}")
    print(f"Y must contain: {Y.lower_bound}, can contain: {Y.upper_bound}")
