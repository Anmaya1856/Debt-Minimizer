class Transaction:
    """
    A simple Data Class representing a directed flow of money.
    """
    def __init__(self, payer_id: int, payee_id: int, amount: float):
        self.payer_id = payer_id
        self.payee_id = payee_id
        self.amount = amount

    def __repr__(self):
        return f"Trans({self.payer_id} -> {self.payee_id}: ${self.amount:.2f})"