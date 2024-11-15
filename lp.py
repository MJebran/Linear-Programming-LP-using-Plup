import pytest
from pulp import LpProblem, LpVariable, LpMaximize, LpStatus, value


def max_flow_lp(graph, capacities, source, target):
    prob = LpProblem("Max_Flow", LpMaximize)

    flow_vars = {}
    for u, v in graph:
        if (u, v) in capacities:
            flow_vars[(u, v)] = LpVariable(
                f"flow_{u}_{v}", lowBound=0, upBound=capacities[(u, v)]
            )

    prob += (
        sum(flow_vars[(source, v)] for v in set(v for u, v in graph if u == source)),
        "Objective_MaxFlow",
    )

    nodes = set([u for u, v in graph] + [v for u, v in graph])
    for node in nodes:
        if node == source or node == target:
            continue
        inflow = sum(flow_vars[(u, node)] for u, v in graph if (u, node) in flow_vars)
        outflow = sum(flow_vars[(node, v)] for u, v in graph if (node, v) in flow_vars)
        prob += (inflow == outflow), f"Conservation_{node}"

    prob.solve()

    if LpStatus[prob.status] != "Optimal":
        print("No optimal solution found.")
        return None

    flow_solution = {edge: value(flow_vars[edge]) for edge in flow_vars}
    print("Solver's Flow Solution:", flow_solution)

    return flow_solution


def find_min_cut(graph, capacities, flow_solution, source):
    residual_graph = {}
    for (u, v), capacity in capacities.items():
        flow = flow_solution.get((u, v), 0)
        if capacity - flow > 0:
            residual_graph.setdefault(u, []).append(v)
        if flow > 0:
            residual_graph.setdefault(v, []).append(u)

    reachable = set()
    stack = [source]
    while stack:
        node = stack.pop()
        if node in reachable:
            continue
        reachable.add(node)
        for neighbor in residual_graph.get(node, []):
            if neighbor not in reachable:
                stack.append(neighbor)

    min_cut = []
    for u, v in graph:
        if u in reachable and v not in reachable:
            min_cut.append((u, v))

    return min_cut


GRAPH = [
    ("s", "a"),
    ("s", "b"),
    ("a", "c"),
    ("a", "d"),
    ("b", "d"),
    ("c", "e"),
    ("d", "e"),
    ("d", "t"),
    ("e", "t"),
]
CAPACITIES = {
    ("s", "a"): 4,
    ("s", "b"): 3,
    ("a", "c"): 5,
    ("a", "d"): 4,
    ("b", "d"): 2,
    ("c", "e"): 5,
    ("d", "e"): 2,
    ("d", "t"): 3,
    ("e", "t"): 5,
}
SOURCE = "s"
TARGET = "t"
EXPECTED_FLOWS = {
    ("s", "a"): 4.0,
    ("s", "b"): 2.0,
    ("a", "c"): 5.0,
    ("a", "d"): 1.5,
    ("b", "d"): 2.0,
    ("c", "e"): 5.0,
    ("d", "e"): 0.0,
    ("d", "t"): 2.5,
    ("e", "t"): 2.5,
}
EXPECTED_MAX_FLOW = 6


def test_max_flow_value():
    result = max_flow_lp(GRAPH, CAPACITIES, SOURCE, TARGET)
    total_flow = sum(
        result[(SOURCE, node)] for node in ["a", "b"] if (SOURCE, node) in result
    )
    assert total_flow == EXPECTED_MAX_FLOW, "The maximum flow value is incorrect."


def test_edge_flows():
    result = max_flow_lp(GRAPH, CAPACITIES, SOURCE, TARGET)
    for edge, expected_flow in EXPECTED_FLOWS.items():
        assert (
            pytest.approx(result[edge], 0.01) == expected_flow
        ), f"Flow on edge {edge} is incorrect."


def test_capacity_constraints():
    result = max_flow_lp(GRAPH, CAPACITIES, SOURCE, TARGET)
    for (u, v), flow in result.items():
        capacity = CAPACITIES.get((u, v), 0)
        assert flow <= capacity, f"Flow on edge ({u}, {v}) exceeds capacity."


def test_flow_conservation():
    result = max_flow_lp(GRAPH, CAPACITIES, SOURCE, TARGET)
    nodes = set([u for u, v in GRAPH] + [v for u, v in GRAPH])
    for node in nodes:
        if node == SOURCE or node == TARGET:
            continue
        inflow = sum(result[(u, node)] for u, v in GRAPH if (u, node) in result)
        outflow = sum(result[(node, v)] for u, v in GRAPH if (node, v) in result)
        assert (
            pytest.approx(inflow, 0.01) == outflow
        ), f"Flow conservation failed at node {node}"


def test_min_cut():
    flow_solution = max_flow_lp(GRAPH, CAPACITIES, SOURCE, TARGET)
    min_cut = find_min_cut(GRAPH, CAPACITIES, flow_solution, SOURCE)

    min_cut_capacity = sum(CAPACITIES[edge] for edge in min_cut)
    assert (
        min_cut_capacity == EXPECTED_MAX_FLOW
    ), "The minimum cut capacity does not match the max flow."


def test_simple_two_node_graph():
    graph = [("s", "t")]
    capacities = {("s", "t"): 10}
    source = "s"
    target = "t"

    result = max_flow_lp(graph, capacities, source, target)
    assert result == {
        ("s", "t"): 10
    }, "Flow does not match expected result in simple two-node graph."
    assert (
        sum(result.values()) == 10
    ), "Total flow should match the capacity of the single edge."


def test_disconnected_graph():
    graph = [("a", "b"), ("b", "c")]
    capacities = {("a", "b"): 5, ("b", "c"): 3}
    source = "s"
    target = "t"

    result = max_flow_lp(graph, capacities, source, target)
    assert all(
        flow == 0 for flow in result.values()
    ), "All flows should be zero in a disconnected graph."
