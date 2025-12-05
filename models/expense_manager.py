from typing import List, Dict
from .transaction import Transaction

class ExpenseManager:
    """
    Manages the graph of users and their net balances.
    Rounding to 2-decimal to prevent weird interations due to float.
    """
    def __init__(self, num_users: int):
        self.num_users = num_users
        self.net_balances: List[float] = [0.0] * num_users
        self.transactions: List[Transaction] = []

    def add_transaction(self, payer_id: int, payee_id: int, amount: float):
        # Can't have a transaction where payer and payee are the same (Doesn't make sense)
        if payer_id == payee_id:
            return
        
        # Rounding the input to 2 decimals
        curr_amount = round(amount, 2)
        
        # Create transaction
        t = Transaction(payer_id, payee_id, curr_amount)
        self.transactions.append(t)
        
        # Update balances with rounding
        # Payer gets credit (+), Payee gets debt (-)
        self.net_balances[payer_id] = round(self.net_balances[payer_id] + curr_amount, 2)
        self.net_balances[payee_id] = round(self.net_balances[payee_id] - curr_amount, 2)

    def get_active_balances(self) -> Dict[int, float]:
        """
        Returns dictionary of {user_id: balance} for users with non-zero balance.
        """
        active = {}
        for i, bal in enumerate(self.net_balances):
            # Must be at least 1 cent (Should always work since we have rounding everywhere else but good to have)
            if abs(bal) >= 0.01:
                active[i] = bal
        return active

    def validate_integrity(self):
        """
        Just checking if the sum of the net balances is = 0.00
        Basic math and accounting amount of debt = amount of credit in a group
        """
        total = round(sum(self.net_balances), 2)
        if abs(total) > 0.01:
            raise Exception(f"CRITICAL ERROR: Net sum is {total} (Should be 0.00)")
        else:
            print("Integrity OK: Zero-Sum maintained.")
            return True