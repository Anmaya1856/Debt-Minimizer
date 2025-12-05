import time
import os
from models.expense_manager import ExpenseManager
from utils.data_generator import generate_connected_data
from utils.exporter import create_artifact_folder, export_run_artifacts, export_benchmark_stats, export_original_state
from solvers import *
import traceback
from tqdm import tqdm
import time

# DO NOT GENERATE DECIMALS WITH N USERS >= 100,000 AND MAX AMOUNT = 500 (LAPTOP CRASHED !!!!!!!)

def main():
    N_USERS = 10000
    N_TRANSACTIONS = 2 * N_USERS
    EXPORT_FLAG = True

    # Use raw string r"" for Windows paths
    ARTIFACTS_PATH = r"D:\CMU\Mini 2\Financial Computing\fc2-final-project-Anmaya1856\artifacts\N " + str(N_USERS) + "_Int"
    # ARTIFACTS_PATH = r"D:\CMU\Mini 2\Financial Computing\fc2-final-project-Anmaya1856\artifacts"
    
    # Setup Data
    print(f"--- Initializing {N_USERS} Users ---")
    mgr = ExpenseManager(N_USERS)
    generate_connected_data(mgr, N_TRANSACTIONS, min_amt=1, max_amt=500, active_threshold=1, isInt=True)
    mgr.validate_integrity()
    active_balances = mgr.get_active_balances()
    
    # print(active_balances)

    if EXPORT_FLAG:
        # Prepare Output & Export Original Data
        folder = create_artifact_folder(ARTIFACTS_PATH)
        print(f"\n--- Saving Artifacts to: {folder} ---")
        # EXPORT ORIGINAL STATE HERE
        export_original_state(folder, mgr, N_USERS, N_TRANSACTIONS)
    
    # Define Solvers
    contestants = [
        ("Layered Solver k4", LayeredSolver(k4 = True), "layered_solver_k4"),
        ("Layered Solver", LayeredSolver(k4 = False), "layered_solver"),
        ("Max-Max Greedy", SimpleGreedySolver(strategy='max'), "max_max"),
        ("Min-Min Greedy", SimpleGreedySolver(strategy='min'), "min_min"),
        ("Hybrid Greedy Monte Carlo", HybridSolver(iterations=1000, greedy_probability=0.98), "hybrid_best"),
        ("Exact MILP Gurobi", MilpSolverGurobi(time_limit=30), "exact_milp_gurobi"),
        # ("Exact MILP", MilpSolver(time_limit=30), "exact_milp"),
    ]
    
    stats = []

    debtors = [userId for userId, bal in active_balances.items() if bal < 0]
    creditors = [userId for userId, bal in active_balances.items() if bal > 0]
    theo_worst = len(active_balances) - 1
    theo_best = max(len(debtors), len(creditors))
    
    print(f"\n{'ALGORITHM':<60} | {'TXs':<6} | {'TIME':<8}")
    print("-" * 60)
    print(f"{'Theoretical Worst Case':<60} | {theo_worst:<6} | -")
    print(f"{'Theoretical Best Case (under Optimal Conditions)':<60} | {theo_best:<6} | -")

    for name, solver, suffix in contestants:
        try:
            # Skip MILP if N is too large
            if ((name == "Exact MILP") and len(active_balances) > 400) or ((name == "Exact MILP Gurobi") and len(active_balances) > 500):
                print(f"{name:<60} | {'SKIP':<6} | {'0.0000'}s (N > {400 if name == 'Exact MILP' else 500})")
                stats.append({"name": name, "count": 0, "time": 0.0})
                continue
            if ((name == "Hybrid Greedy Monte Carlo") and len(active_balances) >= 10000):
                print(f"{name:<60} | {'SKIP':<6} | {'0.0000'}s (N >= 10000)")
                stats.append({"name": name, "count": 0, "time": 0.0})
                continue

            # Start Time
            start = time.time()
            txs = solver.solve(active_balances)
            dur = time.time() - start
            
            count = len(txs)
            stats.append({"name": name, "count": count, "time": dur})
            print(f"{name:<60} | {count:<6} | {dur:.4f}s")
            
            if txs and EXPORT_FLAG:
                export_run_artifacts(folder, suffix, txs, mgr)
                
        except Exception as e:
            traceback.print_exc() 
            print(f"{name:<60} | {'FAIL':<6} | {e}")
            # Log failure as 0/0 so it appears in CSV
            stats.append({"name": name, "count": 0, "time": 0.0})

    if EXPORT_FLAG:
        export_benchmark_stats(folder, stats, active_balances)
    print("-" * 40)
    print("Done. Check the artifacts folder.")

    if N_USERS <= 10:
        time.sleep(0.8)

if __name__ == "__main__":
    # trials = 100
    trials = 1
    for _ in tqdm(range(trials)):
        main()