import random
from models.expense_manager import ExpenseManager

def generate_connected_data(manager: ExpenseManager, num_transactions: int, min_amt=1, max_amt=100, active_threshold=0.75, isInt=True):
    """
    Generates random transactions:
    Make suree at least 75% of users have a non-zero balance. (Arbitrary number just to ensure that people have non-zero balances)
    """
    n = manager.num_users
    edges_created = 0
    
    # We want all users to be connected to each other 
    users = list(range(n))
    random.shuffle(users)
    
    # Generate initial transactions
    for i in range(n - 1):
        u = users[i]
        v = users[i+1]

        if isInt:
            amt = round(random.uniform(min_amt, max_amt), 0)
        else:
            amt = round(random.uniform(min_amt, max_amt), 2)
        
        if random.random() > 0.5:
            manager.add_transaction(u, v, amt)
        else:
            manager.add_transaction(v, u, amt)
        edges_created += 1

    # Add Random Transactions between random people
    remaining = num_transactions - edges_created
    for _ in range(remaining):
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        while u == v:
            v = random.randint(0, n - 1)
        
        if isInt:
            amt = round(random.uniform(min_amt, max_amt), 0)
        else:
            amt = round(random.uniform(min_amt, max_amt), 2)
        manager.add_transaction(u, v, amt)

    # The "75% Rule" Enforcer
    # Check how many users currently have non-zero balance
    print("Enforcing Minimum Active User Count...")
    
    while True:
        # Count active users (non-zero balance)
        active_indices = [i for i, b in enumerate(manager.net_balances) if abs(b) > 0.01]
        inactive_indices = [i for i, b in enumerate(manager.net_balances) if abs(b) <= 0.01]
        
        current_ratio = len(active_indices) / n
        if current_ratio >= active_threshold:
            print(f"Success: {current_ratio*100:.1f}% of users have non-zero balance.")
            break
            
        # If we are below threshold, force a transaction on an inactive user
        # We pick an inactive user and make them pay a random person
        if not inactive_indices:
            break
            
        u = random.choice(inactive_indices)
        v = random.randint(0, n - 1)
        while u == v: 
            v = random.randint(0, n - 1)
        
        if isInt:
            amt = round(random.uniform(min_amt, max_amt), 0)
        else:
            amt = round(random.uniform(min_amt, max_amt), 2)
        manager.add_transaction(u, v, amt)