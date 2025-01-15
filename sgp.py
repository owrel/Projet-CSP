from src.constraints import (
    CardinalityConstraint,
    IntersectionConstraintCardinality,
    LexicographicOrdering,
)
from src.solver import SetSolver
from src.variables import SetVariable


def solve_social_golfer(num_groups, group_size, num_weeks):
    total_golfers = num_groups * group_size
    all_players = set(range(total_golfers))

    solver = SetSolver(visualize=False)

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

    # Add lexicographic ordering between weeks
    # This breaks symmetry between weeks
    # for w in range(num_weeks - 1):
    #     solver.add_constraint(LexicographicOrdering(f"W{w}G0", f"W{w+1}G0"))

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

    # Force player 0 to always be in first group of each week
    # This further breaks symmetry
    # for w in range(num_weeks):
    #     first_group = week_groups[f"W{w}G0"]
    #     first_group._lower_bound.add(0)

    result = solver.solve()
    print(result)
    return result


def solve_social_golfer_simple_sym_break(num_groups, group_size, num_weeks):
    total_golfers = num_groups * group_size
    all_players = set(range(total_golfers))

    solver = SetSolver(visualize=False)

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

    # Add lexicographic ordering between weeks
    # This breaks symmetry between weeks
    # for w in range(num_weeks - 1):
    #     solver.add_constraint(LexicographicOrdering(f"W{w}G0", f"W{w+1}G0"))

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

    # Force player 0 to always be in first group of each week
    # This further breaks symmetry
    # for w in range(num_weeks):
    #     first_group = week_groups[f"W{w}G0"]
    #     first_group._lower_bound.add(0)

    result = solver.solve()
    print(result)
    return result


def solve_social_golfer_advanced_sym_break(num_groups, group_size, num_weeks):
    total_golfers = num_groups * group_size
    all_players = set(range(total_golfers))

    solver = SetSolver(visualize=False)

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

    # Symmetry Breaking 1: Force player 0 to always be in first group of each week
    for w in range(num_weeks):
        first_group = week_groups[f"W{w}G0"]
        first_group._lower_bound.add(0)

    # Symmetry Breaking 2: Lexicographic ordering between groups within each week
    for w in range(num_weeks):
        for g in range(num_groups - 1):
            solver.add_constraint(LexicographicOrdering(f"W{w}G{g}", f"W{w}G{g+1}"))

    # Symmetry Breaking 3: Lexicographic ordering between weeks
    for w in range(num_weeks - 1):
        solver.add_constraint(LexicographicOrdering(f"W{w}G0", f"W{w+1}G0"))

    # Symmetry Breaking 4: Fix first week's groups to a canonical form
    # Place first group_size players in first group
    first_group = week_groups["W0G0"]
    first_group._lower_bound.update(range(group_size))

    # Place next group_size players in second group, etc.
    for g in range(1, num_groups):
        group = week_groups[f"W0G{g}"]
        group._lower_bound.update(range(g * group_size, (g + 1) * group_size))

    # Symmetry Breaking 5: Force player 1 to be in consecutive groups in consecutive weeks
    for w in range(num_weeks - 1):
        curr_week_groups = [f"W{w}G{i}" for i in range(num_groups)]
        next_week_groups = [f"W{w+1}G{i}" for i in range(num_groups)]

        # Find the group containing player 1 in current week
        for g1, g2 in zip(curr_week_groups, next_week_groups):
            solver.add_constraint(IntersectionConstraintCardinality(g1, g2, 1))

    result = solver.solve()
    print(result)
    return result
