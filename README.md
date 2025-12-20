[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/NdAim9o4)
# Optimizing Multi-Party Financial Settlements: A Comparative Analysis of Graph Reduction Algorithms

Took help of AI (Gemini) in brainstorming real world applications and refining the writing.

### Summary
This project explores the algorithmic challenges of Debt Simplification—the process of reducing the total number of transactions required to settle a complex web of financial obligations without altering the net position of any participant. By modeling financial relationships as a directed weighted graph, we aim to minimize edge count (transaction volume) to improve liquidity efficiency. The core of the project involves designing, implementing, and benchmarking three distinct algorithmic approaches—Mixed Integer Linear Programming (MILP), Greedy Heuristics (Max Max or Min Min or Monte Carlo Random + Max Max Custom Algo), and an approximation layered K Subset Algorithm (idea from a harvard paper link below)—to determine the optimal trade-off between computational speed and reduction accuracy across varying dataset scales.

### Real World Application
While popularized by consumer apps like Splitwise, the mathematical problem of debt simplification is fundamental to institutional finance:
* **Interbank Settlement Systems**: Major banks transact thousands of times daily. Rather than settling every trade gross (which requires massive liquidity buffers), clearinghouses use multilateral netting algorithms to settle only the net difference, freeing up billions in capital.
* **Supply Chain Finance**: In complex supply chains, "circular debt" (A owes B, B owes C, C owes A) often causes liquidity crunches. Detecting and netting these cycles improves cash flow for all vendors involved.
* **Central Counterparty Clearing (CCP)**: Derivatives and securities exchanges minimize counterparty risk by netting offsetting positions. Reducing the number of active open obligations reduces the systemic risk if one member defaults.
* **Blockchain & L2 Scaling**: Cryptocurrency "Layer 2" solutions (like the Lightning Network) rely on finding efficient paths to route payments and rebalance channels, effectively simplifying the debt graph off-chain.

### Two lists of features:
The system is built using a modular Object-Oriented architecture in Python, featuring:

#### Core System
* **Graph Data Structure**: An optimized $O(1)$ balance tracking system capable of handling high-frequency transaction ingestion.
* **Synthetic Data Generator**: A robust engine that generates connected graphs (guaranteed spanning tree + random noise) with configurable density. It includes a "75% Active Guarantee" to prevent trivial edge cases where most users have zero balances.
* **Interactive Visualization**: A PyVis-based engine that renders the financial web as an interactive force-directed graph, featuring "Focus Mode" to isolate specific sub-graphs and untangle "hairball" datasets.
* **Automated Artifact Management**: A serialization pipeline that exports timestamped datasets, CSV logs, and visual snapshots for audit trails.

#### The Algorithmic Engine (The Crux)

The project implements and compares three specific solvers:
* **The Custom Heuristic (Max-Max, Min-Min, Monte Carlo Random + Max-Max)**: This is a custom algo thought of by me where the following actions take place in a loop. First we net off any debtors and creditors having the same amount of money due. Next we net off the highest amount of debtors and creditor (we need to resort the lists every time). Some new things I think can be implemented are - use max heaps instead of resorting every time. Try lowest amount of creditor and debtor (see if that works better), Try random cancellations (similar to cross validation in ML) a lot of different times and see if that performs better.
* **The Greedy Solver**: This is an approximation algo seen from a Harvard thesis. This has been modified for our needs. First we cancel any common amounts, then find 3 people cycles, then 4 people cycles, then fall back on the Max-Max Custom Heuristic.
* **The Exact Solver (MILP)**: Uses the PuLP/Gurobipy library to formulate the problem as a Mixed Integer Linear Program. This guarantees the mathematically perfect minimum but is restricted to small clusters due to exponential time complexity.

### Description of complexity:
The problem of minimizing transactions in a debt graph is formally known as the Minimum Edge Directed Graph Problem with flow conservation constraints.

* **Theoretical Class**: It is NP-Complete.
* **The Challenge**: The trivial solution (everyone pays a central clearinghouse) requires $N-1$ transactions. To do better, the algorithm must identify disjoint subsets of participants whose net balances sum to exactly zero (The Subset Sum Problem).
* **Computational Barrier**: Finding these perfect subsets requires exploring a search space that grows exponentially ($2^N$). For small groups ($N<20$), exact solutions are possible. For institutional scales ($N=10,000+$), exact optimization is computationally intractable, necessitating advanced approximation algorithms.

### Running the Project
1. Prerequisites: You will need to install the required dependencies before running the project.
    * pip install -r requirements.txt

2. Running Simulations (Random Data): To run the benchmark suite on randomly generated data, execute the main script:
    * python main.py
    * Some params you might want to experiment with - 
        * N_users (num of users in the graph), 
        * N_transactions (num of transactions you want in the graph), 
        * Export_Flag (True if you want artifacts else False), 
        * min_amt (min amount of each transaction), 
        * max_amt (max amount of each transaction), 
        * active_threshold (min percentage of people with non-zero balances), 
        * isInt (True if you want integer transaction vals, else False (decimals will be rounded to 2 places))
        * **Trials** (very important, it's at the end of the file. The num of simulations you want to run)

**Note**: You may need to adjust the ARTIFACTS_PATH variable inside main.py to match your local directory structure for output storage.

3. Running Custom Test Cases: To run the solver on specific edge cases (e.g., the -85, -81, -19 scenario), execute the custom test script:
    * python custom_test.py

**Note**: Ensure the ARTIFACTS_PATH in custom_test.py is set correctly to save your results.

4. Generating Analysis Graphs and Tables: For generating the analysis graphs after you have generated several benchmark stats for several Ns
    * python analysis.py

**Note**: Ensure the ARTIFACTS_PATH in analsis.py is the place where you have saved the files during the simulation. Also, you will need to adjust the output path with the address and name you like.

5. Project Structure: The codebase is organized into modular components:
    * models/: Core data structures representing the financial graph (Transaction and ExpenseManager).
    * solvers/: Implementation of the various algorithms used for benchmarking.
        * simple_greedy_solver (Simple Greedy) - This is the Custom Algo which works on Max-Max or Min-Min
        * hybrid_solver (Hybrid Solver) - This is the Custom Algo with Monte Carlo and Random Selection (Suggested by Prof. Lauren)
        * milp_solver_gurobi (MILP Solver Gurobi) - This is the MILP Solver using Gurobi
        * layered_solver (Layered Solver) - This is the approx algo based on the Harvard Paper modified for my purposes
        * milp_solver (MILP Solver) - This is the MILP Solver using Pulp (Not used in benchmarking later as it was very slow compared to Gurobi and consumed unnecessary time)
    * utils/: Helper utilities for data generation, graph visualization, and exporting artifacts.
    * artifacts/: The output directory where simulation results, CSV logs, and interactive HTML graphs are saved. The naming convention is as follows - artifacts/N {num of users}_{Int or Dec}/run_{YYYY-MM-DD}_{HH MM SS}
        * The HTML files show the transactions generated by the model for that test case to solve the problem
        * The graph_original HTML file is the original transactions which is basically the graph generated by the random data generator.
            * Hover over the graph nodes to get the exact balance or if you click on a node it will isolate the graph and the nodes it's connected to. Green node is positive balance and red node is negative balance. It is a directed graph.
        * The net balances CSV file is the net balances of the users as generated by the original graph (naming convention is net_balances_original_{num of users}_{num of txns})
        * The benchmark_stats CSV file is the stats for that simulation which containst the time taken for each solver, the number of transactions taken by the solver and gap from theoretical floor.
        * The transactions CSV files will show the amount of transaction and users involved in the transaction to solve the graph for the solver. Or the original transaction CSV shows the original transactions generated.
    * artifacts_custom/: The output directory where custom test case results, CSV logs, and interactive HTML graphs are saved.
        * Follows the same structure as the artifacts/ folder given above
    * analysis_results/: This contains the folder with the all the results for different Ns (100 random data generated for each N). 
        * The Static transaction pngs are for that particular N and 100 runs. 
        * The tradeoff_scatter png is the time and cost (gap) tradeoff. As N increases, more time and more cost will be there.
        * The time_complexity png is the average time taken by each solver for different Ns. The scaling is a bit off, use the HTML file and hover above it to see the actual number. 
        * The optimiality_gap png is heatmap where we see the gap from the theo floor for each solver. 0 indicates that I didn't run the algo (due to too much time or laptop getting crashed)
        * The aggregated_benchmark CSV is the benchmark stats for each N
        * The HTML file is the best part to visualise everything in an interactive manner. Try hovering over stuff to get better readability. 

Some Other Points regarding the project - 

* I also had generated a few more sovlers for example - LP approximation, Pure Monte Carlo but I chose to delete them as they were performing horribly and weren't up to the mark.
* I have capped the MILP solvers at 30 seconds meaning that they give whatever answer they have in 30 sec (might not be optimal for large Ns) to save on time. Since this is a NP Compelete/Hard problem it could run forever for large Ns.
* The theoretical min I have referenced is the max(num of creditors, num of debtors) because logically we need at least those number of transactions. For ex - if there are 7 debtors and 5 creditors then all 7 debtors need to make at least 1 payment at the minimum. As we scale up, it is highly likely that the actual min transactions for that data is more than this naive theoretical min. I can't approximate it better than this.
* I have generated the data on the following params - min amount in transaction = 1$, max amt in txn = 500$, and of integer type. These were chosen arbitrarily. If you increase max amount or use decimals then the number of cycles being formed will decrease and we won't be able to see the power of the implemented algos.


### Project Demo
[https://youtu.be/g0e16GqxRDs]
Quick video showing how to interpret the different output files in the artifacts, artifacts_custom and analysis folders.

### References:
https://dash.harvard.edu/server/api/core/bitstreams/bf76bfed-1f76-4d7f-837b-a5828232d539/content

https://stackoverflow.com/questions/57907655/how-to-use-pipreqs-to-create-requirements-txt-file (To generate requirements.txt)