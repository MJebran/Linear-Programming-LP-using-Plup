# Linear-Programming-LP-using-Plup

# Max Flow and Min Cut Implementation

## Overview
This repository includes two methods for solving the **maximum flow** and **minimum cut** problems in a flow network using Linear Programming (LP) and Residual Graph concepts.

---

## Method: `max_flow_lp(graph, capacities, source, target)`
This method calculates the **maximum flow** in a flow network using **Linear Programming**.

### **Inputs:**
- `graph`: A list of edges in the flow network, e.g., `[(u, v), ...]`.
- `capacities`: A dictionary specifying the capacity of each edge, e.g., `{(u, v): capacity}`.
- `source`: The source node where the flow originates.
- `target`: The sink node where the flow ends.

### **Steps:**
1. **Initialize LP Problem:**
   - Creates an `LpProblem` to **maximize the flow**.

2. **Define Variables:**
   - For each edge `(u, v)` with a capacity, a decision variable `flow_{u}_{v}` is created:
     - `lowBound=0` (flow cannot be negative).
     - `upBound=capacities[(u, v)]` (flow cannot exceed edge capacity).

3. **Set Objective Function:**
   - Maximizes the total flow out of the `source` node:
     \[
     \text{maximize: } \sum (\text{flow from source to its neighbors})
     \]

4. **Flow Conservation Constraints:**
   - For each intermediate node (excluding `source` and `target`), ensures that:
     \[
     \sum (\text{flow into node}) = \sum (\text{flow out of node})
     \]

5. **Solve the Problem:**
   - Uses the solver to find an optimal solution. If no solution exists, it returns `None`.

6. **Extract and Return Solution:**
   - Constructs and returns a dictionary (`flow_solution`) containing the flow values for each edge.

### **Output:**
- A dictionary mapping edges to flow values, e.g., `{(u, v): flow_value}`.

---

## Method: `find_min_cut(graph, capacities, flow_solution, source)`
This method computes the **minimum cut** of a flow network based on the flow solution from the `max_flow_lp` method.

### **Inputs:**
- `graph`: A list of edges in the flow network, e.g., `[(u, v), ...]`.
- `capacities`: A dictionary specifying the capacity of each edge, e.g., `{(u, v): capacity}`.
- `flow_solution`: The flow values for each edge, returned by `max_flow_lp`.
- `source`: The source node where the flow originates.

### **Steps:**
1. **Build Residual Graph:**
   - Constructs a residual graph based on the remaining capacity of each edge:
     - If `capacity - flow > 0`, adds the edge `(u -> v)` to the residual graph.
     - If `flow > 0`, adds the reverse edge `(v -> u)` to allow for flow reversal.

2. **Find Reachable Nodes:**
   - Uses a **Depth-First Search (DFS)** starting from the `source` to find all nodes reachable in the residual graph.

3. **Identify Minimum Cut Edges:**
   - Iterates through all edges `(u, v)` in the original graph:
     - If `u` is in the reachable set and `v` is not, the edge `(u, v)` is part of the **minimum cut**.

4. **Return Minimum Cut:**
   - Returns a list of edges in the minimum cut.

### **Output:**
- A list of edges representing the **minimum cut**, e.g., `[(u, v), ...]`.

---

## Key Concepts
1. **Maximum Flow (Ford-Fulkerson Framework):**
   - The maximum flow is the largest amount of "flow" that can be pushed from the `source` to the `target` without exceeding edge capacities.

2. **Minimum Cut:**
   - The minimum cut is a partition of nodes into two disjoint sets (`source-side` and `sink-side`) such that the total capacity of edges crossing the partition is minimized.
   - By the **Max-Flow Min-Cut Theorem**, the value of the maximum flow equals the capacity of the minimum cut.

3. **Residual Graph:**
   - A graph representing the remaining capacity of edges after accounting for flow. It also includes reverse edges for possible flow reduction.

---

## How These Methods Work Together
- `max_flow_lp`: Computes the maximum flow in the network.
- `find_min_cut`: Uses the flow solution to determine the minimum cut edges separating the `source` from the `target`.

These methods are useful for solving problems in network routing, resource allocation, and optimization.

---

## Example Use Case
1. Define the `graph`, `capacities`, `source`, and `target`.
2. Compute the maximum flow:
   ```python
   flow_solution = max_flow_lp(graph, capacities, source, target)
