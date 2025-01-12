from src import (
    SetSolver,
    CardinalityConstraint,
    IntersectionConstraintCardinality,
    SetVariable,
    Different,
)
from src.constraints import Subset


def solve_social_golfer(num_groups, group_size, num_weeks):
    total_golfers = num_groups * group_size
    all_players = set(range(total_golfers))

    solver = SetSolver(options={"visualize": False})

    # Initialize group sets for each week
    week_groups = {}
    for week in range(num_weeks):
        for group_idx in range(num_groups):
            group_name = f"W{week}G{group_idx}"
            group = SetVariable(
                group_name, lower_bound=set(), upper_bound=all_players.copy()
            )
            week_groups[group_name] = group
            solver.add_variable(group)

    # Set fixed group sizes
    for g in week_groups.values():
        solver.add_constraint(CardinalityConstraint(g.name, group_size))

    # No player can be in multiple groups in same week
    for w in range(num_weeks):
        week_members = [f"W{w}G{i}" for i in range(num_groups)]

        for i, g1 in enumerate(week_members[:-1]):
            for g2 in week_members[i + 1 :]:
                solver.add_constraint(IntersectionConstraintCardinality(g1, g2, 0))

    # Players can't be grouped together more than once
    for w1, w2 in [
        (i, j) for i in range(num_weeks - 1) for j in range(i + 1, num_weeks)
    ]:
        for g1, g2 in [(i, j) for i in range(num_groups) for j in range(num_groups)]:
            g1_name = f"W{w1}G{g1}"
            g2_name = f"W{w2}G{g2}"
            solver.add_constraint(
                IntersectionConstraintCardinality(g1_name, g2_name, 1)
            )
    # solver.visualize_constraint_graph()
    result = solver.solve()
    print(solver.metrics.pretty_print())
    print(result)
    return result


def print_solution(solution):
    if solution is None:
        print("No solution found")
        return

    weeks = {}
    for var_name, group in solution.items():
        week = int(var_name[1])
        if week not in weeks:
            weeks[week] = []
        weeks[week].append(sorted(group))

    for week, groups in sorted(weeks.items()):
        print(f"\nWeek {week + 1}:")
        for i, group in enumerate(groups, 1):
            print(f"  Group {i}: {group}")


def test_strategies():
    # Create a larger universe

    results = {}

    for strategy in [
        "first",
        "smallest_domain",
        "most_constrained",
        "least_constrained",
    ]:
        print(f"\nTesting strategy: {strategy}")

        solver = SetSolver({"variable_strategy": strategy, "visualize": True})

        # Create variables with significantly different domain sizes
        v1 = SetVariable("V1", lower_bound=set(), upper_bound={1, 2, 3, 4, 5})
        v2 = SetVariable("V2", lower_bound=set(), upper_bound={4, 5, 6, 7, 8, 9})
        v3 = SetVariable("V3", lower_bound={7}, upper_bound={7, 8})
        v4 = SetVariable("V4", lower_bound=set(), upper_bound={1, 2, 3, 4, 5})
        v5 = SetVariable("V5", lower_bound=set(), upper_bound={5, 6, 7, 8, 9})

        # Add variables
        for v in [v1, v2, v3, v4, v5]:
            solver.add_variable(v)

        # Add more varied constraints
        # V1 subset V2
        solver.add_constraint(Subset(v1.name, v2.name))

        # V3 different from V4
        solver.add_constraint(Different(v3.name, v4.name))

        # V4 subset V5
        solver.add_constraint(Subset(v4.name, v5.name))

        # Add cardinality constraints with different sizes
        solver.add_constraint(CardinalityConstraint(v1.name, 1))
        solver.add_constraint(CardinalityConstraint(v2.name, 3))
        solver.add_constraint(CardinalityConstraint(v3.name, 2))
        solver.add_constraint(CardinalityConstraint(v4.name, 1))
        solver.add_constraint(CardinalityConstraint(v5.name, 4))

        # Solve and store results
        solution = solver.solve()
        results[strategy] = {
            "solution": solution,
            "branches": solver.metrics.branches,
            "max_depth": solver.metrics.max_depth,
        }

    # Compare results
    print("\nComparison of strategies:")
    for strategy, data in results.items():
        print(f"\n{strategy.upper()}:")
        print(f"Branches explored: {data['branches']}")
        print(f"Max depth: {data['max_depth']}")
        if data["solution"]:
            print("\nSolution:")
            for var, val in data["solution"].items():
                print(f"{var}: {val}")


if __name__ == "__main__":
    solve_social_golfer(group_size=2, num_groups=3, num_weeks=2)
    # test_strategies()
