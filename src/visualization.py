from graphviz import Digraph
import os

from src.constraints import Constraint
from src.misc import Operation, SolverMetrics
from src.solver import StateComputer
from src.variables import SetVariable


class SetTreeVisualizer:
    def __init__(self):
        self.dot = Digraph(comment="Search Tree")
        self.dot.attr(rankdir="TB", size="8,8")
        self.node_counter = 0

    def build_from_history(
        self,
        operations: list[Operation],
        solution_path: list[Operation],
        variables: dict[str, SetVariable],
        constraints: list[Constraint],
    ):
        # Create initial state node
        state_computer = StateComputer(
            SolverMetrics(), constraints=constraints, initial_variables=variables
        )
        initial_node = f"node_{self.node_counter}"
        self.node_counter += 1

        try:
            initial_state = state_computer.compute_state(())
            initial_label = "\n".join(
                f"{k}: {v.lower_bound} ⊆ X ⊆ {v.upper_bound}"
                for k, v in initial_state.items()
            )
        except ValueError as e:
            initial_label = f"Invalid state:\n{str(e)}"

        self.dot.node(initial_node, initial_label, shape="box")

        # Track nodes by their operation path
        path_nodes = {(): initial_node}
        current_path = []

        # Build tree from operations
        for op in operations:
            # Adjust path based on depth
            current_path = current_path[: op.depth] + [op]
            parent_path = tuple(current_path[:-1])
            current_path_tuple = tuple(current_path)

            # Create new node
            node_id = f"node_{self.node_counter}"
            self.node_counter += 1

            # Get state after this operation
            try:
                state = state_computer.compute_state(current_path_tuple)
                state_label = "\n".join(
                    f"{k}: {v.lower_bound} ⊆ X ⊆ {v.upper_bound}"
                    for k, v in state.items()
                )
            except ValueError as e:
                state_label = f"Invalid state:\n{str(e)}"

            # Style node with state information
            self.dot.node(node_id, state_label, shape="box")
            path_nodes[current_path_tuple] = node_id

            # Add edge from parent
            parent_id = path_nodes[parent_path]
            self.dot.edge(parent_id, node_id, str(op))

        # Highlight solution path if exists
        if solution_path:
            path = []
            for op in solution_path:
                path.append(op)
                if len(path) > 1:
                    from_id = path_nodes[tuple(path[:-1])]
                    to_id = path_nodes[tuple(path)]
                    self.dot.edge(from_id, to_id, color="green", penwidth="2")

    def save(self, filename, directory="visualizations"):
        os.makedirs(directory, exist_ok=True)
        try:
            filepath = os.path.join(directory, filename)
            self.dot.format = "pdf"
            self.dot.render(filepath, view=True, cleanup=True)
            print(f"\nVisualization saved at: {os.path.abspath(filepath)}.pdf")
        except Exception as e:
            print(f"Error generating visualization: {e}")


class ConstraintGraphVisualizer:
    def __init__(self):
        self.dot = Digraph(comment="Constraint Graph")
        self.dot.attr(rankdir="LR")
        # Use a more visually pleasing style
        self.dot.attr("node", style="filled")

    def build_graph(
        self, variables: dict[str, SetVariable], constraints: list[Constraint]
    ):
        # Create variable nodes
        for var_name, var in variables.items():
            # Create variable node with a different shape and color
            self.dot.node(
                var_name,
                f"{var_name}\n{var.lower_bound} ⊆ X ⊆ {var.upper_bound}",
                shape="ellipse",
                fillcolor="#ADD8E6",  # Light blue
                style="filled",
            )

        # Create constraint nodes and edges
        for i, constraint in enumerate(constraints):
            constraint_name = f"C{i}_{constraint.__class__.__name__}"
            # Create constraint node with a different shape and color
            self.dot.node(
                constraint_name,
                str(constraint),
                shape="box",
                fillcolor="#98FB98",  # Light green
                style="filled",
            )

            # Create edges between constraints and their variables
            for var_name in constraint.get_variables():
                self.dot.edge(var_name, constraint_name)

    def save(self, filename, directory="visualizations"):
        """Save the constraint graph visualization."""
        os.makedirs(directory, exist_ok=True)
        try:
            filepath = os.path.join(directory, filename)
            self.dot.format = "pdf"
            self.dot.render(filepath, view=True, cleanup=True)
            print(f"\nConstraint graph saved at: {os.path.abspath(filepath)}.pdf")
        except Exception as e:
            print(f"Error generating constraint graph: {e}")
