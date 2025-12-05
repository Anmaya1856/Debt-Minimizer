import time
import os
from models.expense_manager import ExpenseManager
from solvers import *
from utils.exporter import create_artifact_folder, export_run_artifacts, export_benchmark_stats, export_original_state

def setup_custom_scenario():
    """
    Manually constructs the specific Debtor/Creditor scenario: 
    (taken from the OH credit to Amber and Lauren for the Test Case)
    Debtors: -85, -81, -19
    Creditors: 100, 62, 23
    """
    # Total Users
    mgr = ExpenseManager(6)
    
    # User Mapping for clarity
    D1, D2, D3 = 0, 1, 2  # Debtors
    C1, C2, C3 = 3, 4, 5  # Creditors
    
    print("Setting up Custom Scenario")
    print(f"Debtors:  User {D1}: -85, User {D2}: -81, User {D3}: -19")
    print(f"Creditors: User {C1}: +100, User {C2}: +62, User {C3}: +23")
    
    # Transactions to create these exact balances
    # Logic: Payee gets negative balance (Debtor), Payer gets positive (Creditor)
    
    # C1 (+100) needs to lend 100 total
    mgr.add_transaction(C1, D1, 85.0) # C1: +85, D1: -85 (D1 Done)
    mgr.add_transaction(C1, D3, 15.0) # C1: +100 (Done), D3: -15
    
    # 2. C2 (+62) needs to lend 62 total
    mgr.add_transaction(C2, D2, 62.0) # C2: +62 (Done), D2: -62
    
    # 3. C3 (+23) needs to lend 23 total
    mgr.add_transaction(C3, D2, 19.0) # C3: +19, D2: -62-19 = -81 (D2 Done)
    mgr.add_transaction(C3, D3, 4.0)  # C3: +23 (Done), D3: -15-4 = -19 (D3 Done)
    
    return mgr

def main():
    # Setup
    mgr = setup_custom_scenario()
    mgr.validate_integrity()
    active_balances = mgr.get_active_balances()
    

    print("\n--- Verified Net Balances ---")
    for u, b in active_balances.items():
        print(f"User {u}: {b:.2f}")
        
    # Solvers
    contestants = [
        ("Layered Solver k4", LayeredSolver(k4 = True), "layered_solver_k4"),
        ("Layered Solver", LayeredSolver(k4 = False), "layered_solver"),
        ("Max-Max Greedy", SimpleGreedySolver(strategy='max'), "max_max"),
        ("Min-Min Greedy", SimpleGreedySolver(strategy='min'), "min_min"),
        ("Hybrid Greedy Monte Carlo", HybridSolver(iterations=1000, greedy_probability=0.98), "hybrid_best"),
        ("Exact MILP Gurobi", MilpSolverGurobi(time_limit=30), "exact_milp_gurobi"),
        # ("Exact MILP", MilpSolver(time_limit=30), "exact_milp"),
    ]
    
    theo_best = 4

    # Run & Compare
    print(f"\n{'ALGORITHM':<60} | {'TXs':<6} | {'TIME':<8}")
    print("-" * 60)
    print(f"{'Theoretical Best Case':<60} | {theo_best:<6} | -")
    
    stats = []
    folder = create_artifact_folder(r"D:\CMU\Mini 2\Financial Computing\fc2-final-project-Anmaya1856\artifacts_custom") # Saves to local artifacts folder
    export_original_state(folder, mgr, 6, 5)
    
    for name, solver, suffix in contestants:
        start = time.time()
        txs = solver.solve(active_balances)
        dur = time.time() - start
        count = len(txs)
        
        stats.append({"name": name, "count": count, "time": dur})
        print(f"{name:<60} | {count:<6} | {dur:.4f}s")
        
        # Export so we can inspect the specific transactions chosen
        export_run_artifacts(folder, f"custom_{suffix}", txs, mgr)

    export_benchmark_stats(folder, stats, active_balances)
    print("-" * 40)
    print(f"Check {folder} for detailed transaction lists.")

if __name__ == "__main__":
    main()