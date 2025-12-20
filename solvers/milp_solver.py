import pulp
from typing import Dict, List, Tuple

class MilpSolver():
    """
    Exact solver using Mixed Integer Linear Programming (PuLP).

    Same logic as in milp_solver_gurobi.py just using PuLP here.

    The Math is as follows:
    Variables:
        x: is the amount to be transacted
        z: binary variable showing whether there is transaction between 2 people
        We create these variables for each pair of creditor and debtor so if there are 5 debtor and 5 creditors
        We will form a 5x5 matrix for each variable.
    Obj Function:
        min z
    Constraints:
        1. x <= M * z (any single transaction has to be smaller than the total debtor/creditor value)
        2. sum of x for each person has to be equal to the net balance of the user
        3. min sum of z >= max(num of debtors, creditors)
        4. max sum of z <= num of debtors + num of creditors - 1

    """
    def __init__(self, time_limit=60):
        self.time_limit = time_limit

    def solve(self, net_balances: Dict[int, float]) -> List[Tuple[int, int, float]]:
        debtors = [u for u, b in net_balances.items() if b < 0]
        creditors = [u for u, b in net_balances.items() if b > 0]
        if not debtors or not creditors: 
            return []

        # print(net_balances)
        # print(debtors)
        # print(creditors)

        prob = pulp.LpProblem("Minimize_Transactions", pulp.LpMinimize)
        
        x = dict()
        z = dict()
        M = sum(net_balances[c] for c in creditors) 

        for d in debtors:
            x[d] = dict()
            z[d] = dict()
            for c in creditors:
                x[d][c] = pulp.LpVariable(f"x_{d}_{c}", 0)
                z[d][c] = pulp.LpVariable(f"z_{d}_{c}", cat='Binary')
                prob += x[d][c] <= M * z[d][c]

        # Objective: Minimize edges
        objective = pulp.lpSum([z[d][c] for d in debtors for c in creditors])
        prob += objective

        # --- OPTIMIZATION: Lower Bound Constraint ---
        # We know the answer cannot be less than max(|Debtors|, |Creditors|)
        # Adding this helps the solver prune branches that try to go lower (impossible).
        lower_bound = max(len(debtors), len(creditors))
        prob += objective >= lower_bound

        upper_bound = len(debtors) + len(creditors) - 1
        prob += objective <= upper_bound

        # Flow Constraints
        for d in debtors:
            prob += pulp.lpSum([x[d][c] for c in creditors]) == abs(net_balances[d])
        
        for c in creditors:
            prob += pulp.lpSum([x[d][c] for d in debtors]) == net_balances[c]

        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=self.time_limit)
        prob.solve(solver)
        
        results = []
        if pulp.LpStatus[prob.status] in ["Optimal", "Feasible"]:
            for d in debtors:
                for c in creditors:
                    val_z = pulp.value(z[d][c])
                    if val_z and val_z > 0.5:
                        amt = pulp.value(x[d][c])
                        if amt and amt > 0.001:
                            results.append((d, c, round(amt, 2)))
                            
        return results