# Current Progress (Part 1, 22 Nov 2025)

## Completeness Part
Made all the relevant classes and wrote the code for generating random test cases which is very important.
Also made a visualisation tool for seeing transactions in a graph

## Completed Features
* Used classes to make transaction and main (expense manager class) simple OOP used here. It's in the models folder. (Might change later as project evolves)
* Made simple utils like exporter, visualiser and data generator (in the utils folder). Made the exporter (used to export all relevant data to csv like transactions history, net balances, benchmark stats, etc) and visulaiser (used to visualise the graph of transactions just for UI) with the help of AI. Data generator essentially is used to generate random transactions. 
* Main.py for running the code 

## Next TODO
Started working on my custom solver algo and thinking about implementing MILP (which would be the 3rd algo as discussed)
Build Custom Algo
Build MILP Solver
Build Simple Sum of Subset Solver
Exporter and compare

# Progress Report (Part 2, 2 Dec 2025)

Took help of AI (Gemini) in refining the writing and generating markdown code for tables and making it readable.

Note: New updates for Deliverable 2 are marked with [NEW] and bold text. Please check readme.md bottom portion to undertsand how to run, where to find different modules, what each module does, what does each output file mean. Also, have uploaded the demo video to explain the output generated.

## MVP Features (Agreed Upon Features)

1. Complexity Features (The Algorithms)
    * **[NEW] Exact Solver**: A method to find the mathematically perfect solution (minimum transactions) for small groups.
    * **[NEW] Heuristic/Greedy Solver**: A fast method to guess a good solution for large groups where the perfect answer takes too long.
    * **[NEW] Hybrid Solver**: Monte carlo with random selection and Max-Max Greedy (suggested by Prof. Lauren).
    * **[NEW] Layered Approximation**: Using strategies from research papers to find perfect loops of size 2, 3, and 4 before giving up and using Max-Max greedy methods.

2. Completeness Features (The System)
    * Data Structures: Code to represent Users, Transactions, and the Graph.
    * Data Generator: A tool to create fake financial data for testing.
    * Visualization: Interactive graphs that let you zoom in and click on users to see their specific debts.
    * **[NEW] Custom Test**: Wrote a code to run custom test cases.
    * **[NEW] Benchmarking Suite**: A system to run all algorithms side-by-side and create charts comparing Speed vs. Accuracy.

## Feature Status

| Feature | Status |
|---------|--------|
| Basic Data Structures (User/Transaction) | ✅ Completed |
| Interactive Visualization | ✅ Completed |
| **[NEW]** Greedy Solver (Max-Max) | ✅ Completed |
| **[NEW]** Exact MILP Solver (PuLP) | ✅ Completed |
| **[NEW]** Exact MILP Solver (Gurobi) | ✅ Completed |
| **[NEW]** Hybrid Heuristic Solver | ✅ Completed |
| **[NEW]** Layered Solver (k=2,3,4) | ✅ Completed |
| **[NEW]** Automated Benchmarking & Plotting | ✅ Completed |
| **[NEW]** Final Analysis | ✅ Completed |

## Implementation Details (Completed Features)

1. Algorithms (The "Crux")
    * **[NEW]Simple Greedy Solver**: First matches common amounts, then matches the person who owes the most/least money with the person who is owed the most/least. It repeats this until everyone is paid.
        * Code Location: solvers/simple_greedy_solver.py
    * **[NEW] Exact MILP Solver**: Transforms the problem into a math equation (Mixed Integer Linear Programming). It uses "Big-M" constraints to tell the computer "If you move money, you must pay the cost of opening a transaction."
        * Code Location: solvers/milp_solver.py (and milp_solver_gurobi.py)
    * **[NEW] Hybrid Solver (Monte Carlo)**: It runs thousands of fast trials. In each trial, it randomly matches people or uses Max-Max Greedy (with prob P) then creates "Exact Matches" (where Debt equals Credit) instantly using Hash Maps. It keeps the best result found.
        * Code Location: solvers/hybrid_solver.py
    * **[NEW] Layered Solver**: It follows the strategy from the thesis paper. First, it finds all perfect pairs ($k=2$). Then it finds all perfect triangles ($k=3$). Then it looks for groups of 4 using a "Meet-in-the-Middle" search. This cleans up the graph efficiently. Then fall back on Max Max Greedy
        * Code Location: solvers/layered_solver.py

2. Supporting Infrastructure

    * Interactive Visualization: Uses the PyVis library to generate HTML graphs. We injected custom JavaScript so you can click on a user to "Focus" on them and hide the rest of the messy graph.
        * Code Location: utils/visualizer.py
    * **[NEW] Analysis Pipeline**: A script that reads our results and creates Heatmaps, Boxplots, and Line Charts to show which algorithm is the winner.
        * Code Location: analysis.py

## Implementation Notes (Difficulties & Successes)

### What was Difficult?
1. **[NEW] The "NP-Hard" Freeze**: When running the Exact Solver (MILP) on large groups (>400 users), the computer would freeze for 45 minutes just trying to list the variables.
    * Solution: Added a "Lookahead Guard" that calculates the size of the problem before starting. If it is too big ($N > 400$), it skips the slow solver automatically.

2. **[NEW] Graph "Hairballs"**:
    * Issue: Visualizing 100 users created a messy black blob of lines that was impossible to read.
    * Solution: Added a "Click-to-Focus" feature so we can look at small groups individually.

### What was Easier than Expected?
1. **[NEW] The Hybrid Solver (Monte Carlo)**:
    * Thought the randomized solver would be difficult to implement but by having implemented the greedy solver before it became easier as I had to combine heaps and lists with monte carlo.

## Work Plan

Previous Plan (From Deliverable 1)
* Implement the basic Greedy algorithm. (Done)
* Set up the basic User/Transaction classes. (Done)
* Explore libraries for the Exact Solver. (Done - chose PuLP and Gurobi)

### **[NEW] Plan for Final Submission (Priority Order)**

**Large Scale Simulation**: Run the benchmark on $N=500, 1000, 10000$ to get the final data for our charts.

**Final Comparison Analysis**: Compare our different solver against the "Theoretical Lower Bound" (the mathematical floor) to prove how close to perfect we are (of course the theoretical lower bound might not actually be the lower bound but it will be slighly higher due to how we calculate it.).



