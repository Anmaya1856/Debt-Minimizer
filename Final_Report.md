# Final Report (Financial Computing 2): Optimizing Multi-Party Financial Settlements: A Comparative Analysis of Graph Reduction Algorithms (Splitwise)

**Author:** Anmaya Agarwal
**Date:** December 11, 2025  

## 1. Project Overview and Background

This project implements a financial settlement engine designed to tackle the Debt Simplification Problem. In graph theory terms, this is the "Minimum Edge Directed Graph" problem with flow conservation constraints. Given a complex network of financial obligations (nodes representing users, weighted edges representing debts), the goal is to produce an equivalent graph with the same net balances for every user but the minimum possible number of edges (transactions).

While popular consumer applications like Splitwise tackle this problem, the underlying optimization is NP-Complete (specifically the Zero-Sum Set Packing problem). This project explores the trade-offs between computational tractability and mathematical optimality by implementing and benchmarking four to five distinct solvers ranging from simple greedy, greedy with monte carlo, layered solver and mixed integer linear programming.

## 2. Program Workflow and Features

### Important Video Link Note:

While the video requirement typically focuses on demonstrating user-facing features without code, the core value of this project lies in its algorithmic complexity and performance optimization rather than a traditional GUI workflow. To effectively demonstrate the project's impact, the video focuses on a comparative analysis of the implemented algorithms (Exact MILP, Hybrid Monte Carlo, Greedy, and Layered Solver). This approach allows for a meaningful discussion of the trade-offs between computational speed and mathematical optimality, which are the central findings of this research.

### 2.1 MVP 

#### **Project Flow**

The core application follows a linear pipeline designed to ingest raw financial data, process it through interchangeable algorithmic strategies, and output simplified transaction lists.Data Ingestion/Generation: 
* The system initializes an ExpenseManager which can either ingest manual transaction lists (need to enter manually) or generate synthetic data. The MVP relied on random float/int generation.
* **Net Balance Calculation:** The system reduces the raw transaction log into a net balance vector ($O(N)$), identifying Debtors (negative balance) and Creditors (positive balance).
* **Solver Execution:** Used various algorithms like Greedy Solver (Max-Max and Min-Min), Monte Carlo Greedy, Layered Solver and MILP to resolve the net balances into a new list of simplified transactions.
* **Output:** The simplified transactions are printed to the console, exported to CSV, and a HTML graph with for visualisation is exported to the selected folder.

### MVP Basic Features 

* **Simple Greedy Solver**: A baseline algorithm using a "Max-Max" strategy (matching the largest debtor to the largest creditor, after netting off common amounts) to ensure debts are settled efficiently, though not optimally.

* **Second Algorithm (Hybrid Heuristic)**: A custom monte carlo designed to outperform the greedy baseline by using randomization to escape local optima by randomly setting off people with a probability param that can be tweaked. I run this 1000 times and select the best answer.

* **Basic Visualization**: A mechanism to generate a visual representation of the debt graph (nodes and edges) to verify connectivity and complexity. (This project is very algorithmicly complex to more than make up for completeness part, even which is executed more than agreed upon in the MVP by the way of the analysis dashboard)


### 2.2 Additional Features (Complexity & Completeness)

* **Exact MILP Solver (Gurobi/PuLP)**: An exact solver that formulates the problem as a Mixed Integer Linear Program (MILP). It uses binary variables to represent edge existence and continuous variables for flow, guaranteeing the mathematically optimal solution for small $N$.

* **Layered "Thesis" Solver**: An advanced approximation algorithm based on research into the $k$-set packing problem. It iteratively removes zero-sum cycles of size $k=2, 3, 4$ before falling back to greedy methods.

* **Automated Benchmarking Suite**: A comprehensive analysis pipeline that runs simulations across varying $N$ ($10$ to $1000+$), calculating specific metrics like the "Optimality Gap" and "Time Complexity," and exporting results to an interactive HTML dashboard.

* **Interactive Dashboard**: A Plotly-based visualization suite allowing users to filter results, zoom into data points, and view time-complexity trade-offs dynamically.

## 3. Implementation Details

This section details the specific algorithmic logic used to implement the features listed above.

### 3.1 MVP

1. **Simple Greedy Solver:** `solvers/simple_greedy_solver.py`
    * Logic: This algorithm prioritizes minimizing the count of transactions by eliminating the largest liabilities first. I utilized Heaps (Priority Queues) to maintain sorted lists of Debtors and Creditors.
    * Complexity: Initially set off any common amounts in the debtor and creditor list. Then at every step, heappop the largest debtor and creditor ($O(\log N)$). Then execute a transaction for the minimum of their absolute balances.
    * Optimization: A critical optimization was the "Immediate Remainder Check." If a debtor paid a creditor but still owed a small remainder (e.g., $10), immediately check a Hash Map to see if another creditor needed exactly $10$. If so, settle it instantly, preventing the remainder from fragmenting the graph further.

2. **Hybrid Heuristic Solver:** `solvers/hybrid_solver.py`
    * Logic: This solver combines Monte Carlo with greedy logic. It runs $K$ iterations (e.g., 1000). In each iteration, it randomly shuffles the user list to explore different matching paths.
    * Implementation: To ensure the random trials were fast enough to run 1000 times in sub-second time, I optimized the data structures. Instead of scanning lists ($O(N)$), I maintained Hash Maps of Sets (defaultdict(set)) mapping amounts to users. This allowed $O(1)$ lookups for "Exact Matches" (where Debtor Amount == Creditor Amount), which are prioritized before random matching occurs.

3. **Basic Visualization:** `utils/visualizer.py`
    * Logic: Utilized the PyVis library to generate force-directed graphs. Nodes represented users (colored green for creditors, red for debtors), and edges represented transactions amount.
    * Implementation: Injected custom JavaScript into the generated HTML to implement a "Focus Mode." Clicking a node fades out unrelated nodes, allowing the user to inspect specific debt clusters in dense graphs ("hairballs"). 

4. **Configurable Random Data Generator:**  `utils/data_generator.py`
    * Description: A flexible data generation utility designed to create diverse financial network scenarios for stress testing. It generates random transactions based on user-defined parameters such as minimum/maximum transaction amounts, graph density, and the data type (Integer vs. Float).
    * Implementation Logic: The generator constructs a connected graph (spanning tree) to ensure solvability, then adds random "noise" edges to increase complexity. It includes a specific threshold parameter to ensure a minimum percentage of users (e.g., 75%) have non-zero balances, preventing trivial test cases where most users are inactive.
    * Note I have used min percent of users as 100 in the test to make the analysis easier to read otherwise I would have analysis for N=73,71,74 as well for N=75.

5. **Object-Oriented Code:** `models/expense_manager.py` and `models/transaction.py`
    * Description: A clean, modular OOP architecture to represent the core entities of the debt graph.
    * Implementation Logic: Designed a Transaction class to encapsulate payer/payee relationships and an ExpenseManager class to act as the central controller. The manager handles adding transactions and maintaining the net balance state in $O(1)$ time using optimized list structures, serving as the single source of truth for all downstream solvers.

### 3.2 Additional Features

1. **Exact MILP Solver:** `solvers/milp_solver_gurobi.py` and `solvers/milp_solver.py` (Uses PuLP)
    * Logic: I formulated the problem mathematically: Minimize $\sum z_{i,j}$ subject to Flow Conservation constraints.
    * Implementation: Used Big-M constraints ($x_{i,j} \le M \cdot z_{i,j}$) to link the continuous flow variable $x$ to the binary existence variable $z$. I implemented this using both the PuLP library (open source) and the Gurobi API (commercial optimization) for performance comparisons. Also, added constraints for Lower Bounds ($\max(|D|, |C|)$) to help the solver prune the Branch-and-Bound tree faster.
    * Note: I haven't used PuLP in the comparison because it performs worse than Gurobi for obvious reasons and for each N since I was generating 100 random simulations for accuracy, it took me 1.5 hours for each N > 20 (when including only Gurobi).

2. **Layered "Thesis" Solver:** `solvers/layered_solver.py`
    * Logic: Based on the principle that finding small zero-sum disjoint sets maximizes graph reduction. The solver runs in phases: 
        * $k=2$: Finds pairs $(A+B=0)$ using Hash Maps.
        * $k=3$: Finds triangles $(A+B+C=0)$ using an optimized 3-SUM algorithm (Sorting + Two Pointers).
        * $k=4$: Finds quads $(A+B+C+D=0)$. 
    * Implementation Note: The naive solution for $k=4$ is $O(N^4)$, which is too slow. I implemented a modified version of the 2 Sum algorithm (similar to meet-in-the-middle algo I believe, not sure). Here, I generated sums of all possible pairs $(A+B)$ and stored them in a Map ($O(N^2)$). Then looked for collisions where $\text{Sum}_{pair1} = -\text{Sum}_{pair2}$, reducing the complexity from $O(N^4)$ to $O(N^2)$.

3. **Benchmarking & Analysis:** `analyze_benchmarks.py`
    * Logic: This script crawls the artifact directories, parses CSV logs, and aggregates performance metrics.
    * Implementation: Calculated the Theoretical Floor for every test case ($\max(|Debtors|, |Creditors|)$) (Important to note that this is a very loose floor, for high number of users it is very likely the actual floor is higher than the one suggested by me). The script generates a "gap analysis" showing exactly how many extra transactions each algorithm produced compared to the mathematical limit. Used Plotly to generate interactive HTML heatmaps and scatter plots to visualize the Time vs. Accuracy trade-off.

4. **Artifact Exporter & Serialization** `utils/exporter.py`
    * Description: A system to serialize and persist all simulation inputs and outputs for auditability and reproducibility.
    * Implementation Logic: This module handles file I/O operations, creating timestamped directories for each run. It exports the raw transaction list and net balance vector as CSV files before optimization (ground truth) and saves the results of every algorithm. It also triggers the visualizer to generate and save HTML graph snapshots for both the initial and optimized states.

5. **Artifacts Folder Structure** `artificats/` and `artifacts_custom` (for custom graphs)
    * Description: A hierarchical data storage system generated by the simulation pipeline.
    * Implementation Logic: For each run, a timestamped subfolder is created containing:
        * graph_original.html: Visualization of the initial "hairball" graph before optimization.
        * transactions_original.csv: The raw input list of debts.
        * net_balances_original.csv: The calculated net positions for every user.
        * benchmark_stats.csv: A summary log of the performance (Time, Transaction Count, Gap) for every algorithm run on that specific dataset.
        * Algorithm-specific outputs: graph_{algo}.html and transactions_{algo}.csv showing the optimized results for each solver.

6. **Analysis Results Folder** `analysis_results/`
    * Description: The output destination for the aggregated research findings generated by analyze_benchmarks.py.
    * Implementation Logic: This folder contains the final research artifacts derived from parsing hundreds of individual simulation runs. It includes:
        * aggregated_benchmark_stats.csv: A master dataset summarizing mean performance metrics for every algorithm across all $N$.
        * interactive_dashboard.html: A Plotly-based HTML file containing dynamic charts (Heatmaps, Trade-off Scatter Plots) with zoom and filtering capabilities.
        * Static PNGs: High-resolution charts (time_complexity.png, optimality_gap_heatmap.png) generated via Matplotlib/Seaborn for inclusion in the final report document.

## Changes Since Presentation

No Changes really since the project has been completed (had talked to Prof. Sands regarding this in the last OH)

## Missing Features / Areas for Improvement

- Inspired by Google DeepMind's AlphaFold (which solves protein folding, another complex constraint satisfaction problem), I think that Deep Learning could offer powerful solutions for identifying optimal zero-sum sets. However, experimenting with and implementing complex neural architectures suitable for combinatorial optimization was outside the feasible scope of this two-week project given that I don't know anything about DL yet.
- Implement K=5 in the layered solver, but the algo for that would be slower I believe.