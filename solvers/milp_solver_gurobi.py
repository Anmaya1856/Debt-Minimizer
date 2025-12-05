import gurobipy as gp
from gurobipy import GRB
from typing import Dict, List, Tuple

class MilpSolverGurobi():
    """
    Exact solver using the native Gurobi Python API.

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
    
    Using Gurobi here (Thanks to Prof. Mackey for letting us know about this optimiser.)
    """
    def __init__(self, time_limit=60):
        self.time_limit = time_limit

    def solve(self, net_balances: Dict[int, float]) -> List[Tuple[int, int, float]]:
        debtors = [u for u, b in net_balances.items() if b < -0.001]
        creditors = [u for u, b in net_balances.items() if b > 0.001]
        
        if not debtors or not creditors:
            return []

        # First four lines are for supressing output taken from
        # https://support.gurobi.com/hc/en-us/articles/360044784552-How-do-I-suppress-all-console-output-from-Gurobi
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag', 0)
            env.start()
            with gp.Model("Minimize_Transactions", env=env) as model:
                # Initialize Model
                # model = gp.Model("Minimize_Transactions")

                # Configuration
                model.setParam(GRB.Param.TimeLimit, self.time_limit)
                # Silence output (very very very long output)
                model.setParam(GRB.Param.OutputFlag, 0) 
                model.setParam(GRB.Param.LogToConsole, 0)

                # x[d,c]: Continuous flow amount
                x = dict()
                # z[d,c]: Binary existence
                z = dict()
                
                # Big M: Max possible flow
                M = sum(net_balances[c] for c in creditors)

                # Bulk create variables
                for d in debtors:
                    for c in creditors:
                        x[d, c] = model.addVar(lb=0.0, ub=M, vtype=GRB.CONTINUOUS, name=f"x_{d}_{c}")
                        z[d, c] = model.addVar(vtype=GRB.BINARY, name=f"z_{d}_{c}")

                model.update() 

                # CONSTRAINTS
                
                # 1. Big-M Link: x <= M * z (Essentially payment cant be more than the total creditor amount)
                for d in debtors:
                    for c in creditors:
                        model.addConstr(x[d, c] <= M * z[d, c], name=f"link_{d}_{c}")

                # 2. Flow Conservation (Debtors)
                for d in debtors:
                    model.addConstr(gp.quicksum(x[d, c] for c in creditors) == abs(net_balances[d]), name=f"debt_{d}")

                # 3. Flow Conservation (Creditors)
                for c in creditors:
                    model.addConstr(gp.quicksum(x[d, c] for d in debtors) == net_balances[c], name=f"credit_{c}")

                # OBJECTIVE
                # Minimize sum of z variables
                objective_expr = gp.quicksum(z[d, c] for d in debtors for c in creditors)
                model.setObjective(objective_expr, GRB.MINIMIZE)

                # Constraints for Optimising
                # Lower Bound: max(|D|, |C|)
                lower_bound = max(len(debtors), len(creditors))
                model.addConstr(objective_expr >= lower_bound, name="lower_bound_cut")

                # Upper Bound: N - 1 (Spanning Tree)
                active_count = len(debtors) + len(creditors)
                upper_bound = active_count - 1
                model.addConstr(objective_expr <= upper_bound, name="upper_bound_cut")

                # SOLVE
                model.optimize()

                # print(model.Status)
                # print(model.SolCount)

                results = []
                if model.SolCount > 0:
                    for d in debtors:
                        for c in creditors:
                            z_val = z[d, c].X
                            if z_val > 0.5:
                                amt = x[d, c].X
                                if amt > 0.001:
                                    results.append((d, c, round(amt, 2)))
                            
        return results