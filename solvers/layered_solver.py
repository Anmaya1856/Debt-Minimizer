from typing import Dict, List, Tuple
from collections import defaultdict
from .simple_greedy_solver import SimpleGreedySolver

# Inspired by this thesis paper 
# https://dash.harvard.edu/server/api/core/bitstreams/bf76bfed-1f76-4d7f-837b-a5828232d539/content

class LayeredSolver():
    """
    Layered Approximation Solver (k-Set Packing).
    
    Strategy:
    1. k=2: Find all exact pairs (1 Debtor, 1 Creditor). Using 2 Sum algo for this
    2. k=3: Find all exact triplets (2 Debtors -> 1 Creditor OR 1 Debtor -> 2 Creditors). Using 3 sum algo for this
    3. k=4: Find at exact quads (4 people who sum up to 0). Modified the data to solve it using a 2 sum
    4. Fallback: Use SimpleGreedySolver (Max-Max) for the rest.

    While it might seem like 2 sum and 3 sum are easy algos, the real challenge was thinking that the problem could be
    converted into these algos. Moreover, converting the data so that I can use these algos was also a big challenge.
    Unlike leetcode, I can't reuse a value once and I also have duplicates. So, I had to ensure multiple Data Structs
    work simultaneously.
    """
    def __init__(self, k4=True):
        self.k4 = k4

    def solve(self, net_balances: Dict[int, float]) -> List[Tuple[int, int, float]]:
        pool = {userId: bal for userId, bal in net_balances.items() if abs(bal) > 0}
        transactions = []
        
        # EXACT PAIRS (k=2) Removes simple 1 to 1 matches
        txs_k2 = self._solve_k2(pool)
        transactions.extend(txs_k2)
        
        # EXACT TRIPLES (k=3) Removes 3 person zero sum loops
        txs_k3 = self._solve_k3(pool)
        transactions.extend(txs_k3)
        
        # EXACT QUADS (k=4) Removes 4 person zero sum loops
        if self.k4:
            transactions.extend(self._solve_k4(pool))

        # GREEDY FALLBACK
        if pool:
            # Pass the remaining dict to the custom Max-Max Greedy solver
            greedy = SimpleGreedySolver(strategy='max')
            cleanup_txs = greedy.solve(pool)
            transactions.extend(cleanup_txs)
            
        return transactions

    def _solve_k2(self, pool: Dict[int, float]) -> List[Tuple]:
        """
        Finds all A + B = 0 pairs.
        Updates 'pool' in-place by deleting matched users.
        """
        txs = []
        d_map = defaultdict(list)
        c_map = defaultdict(list)
        
        for userId, bal in pool.items():
            if bal < 0: 
                d_map[abs(bal)].append(userId)
            else:     
                c_map[abs(bal)].append(userId)
            
        common = set(d_map.keys()) & set(c_map.keys())
        
        for amt in common:
            while d_map[amt] and c_map[amt]:
                d = d_map[amt].pop()
                c = c_map[amt].pop()
                txs.append((d, c, amt))
                
                # Remove from pool
                del pool[d]
                del pool[c]
                
        # print("2 cycles ", len(txs))
        return txs

    def _solve_k3(self, pool: Dict[int, float]) -> List[Tuple]:
        """
        Finds A + B + C = 0 using Two Pointers.
        Simplified unified logic.
        Using the 3 sum logic here
        """
        txs = []
        
        # Flatten to list of (balance, user_id) and Sort
        entries = sorted([(bal, userId) for userId, bal in pool.items()], key=lambda x: x[0])
        n = len(entries)
        used = set()
        
        # 3-SUM Loop    
        for i, entry in enumerate(entries):
            if entry[1] in used or entry[0] > 0:
                continue

            l, r = i + 1, len(entries) - 1
            while l < r:
                # Skip used users in inner loop
                if entries[l][1] in used:
                    l += 1
                    continue
                if entries[r][1] in used:
                    r -= 1
                    continue
                
                currSum = entry[0] + entries[l][0] + entries[r][0]
                if currSum > 0:
                    r -= 1
                elif currSum < 0:
                    l += 1
                else:
                    # UserIDs of the people in the triplet
                    group = {entry[1], entries[l][1], entries[r][1]}
                    
                    # Resolve this closed group locally using Greedy
                    # Doing this because we don't know if there are 2 creditors or 2 debtors
                    sub_bal = {u: pool[u] for u in group}
                    sub_txs = SimpleGreedySolver(strategy='max').solve(sub_bal)
                    txs.extend(sub_txs)
                    
                    # Update used, using update since it allows me to add more than 1 element in the set
                    used.update(group)
                    break 

        # Cleanup Pool
        for u in used:
            del pool[u]

        # print("3 cycles ", len(txs))
        return txs
    
    def _solve_k4(self, pool: Dict[int, float]) -> List[Tuple]:
        """
        Finds A + B + C + D = 0 
        We convert the problem to 2 sum.
        """
        txs = []
        users = list(pool.keys())
        n = len(users)
        
        # Build Pair Sum Map
        # key: Sum, value: list of sets {u1, u2}
        pair_sums = defaultdict(list)
        
        # Generate all pairs
        for i in range(n):
            for j in range(i + 1, n):
                u1, u2 = users[i], users[j]
                s = round(pool[u1] + pool[u2], 2)
                pair_sums[s].append({u1, u2})

        used = set()

        # Find 2 sum of pairs (Sum X and Sum -X) by iterating through unique sum values
        sums = list(pair_sums.keys())
        
        for s in sums:
            # Only look at positive sums to match with negative sums (can do it other way round as well)
            if s <= 0: 
                continue 
            
            target = -s
            if target in pair_sums:
                list_a = pair_sums[s]
                list_b = pair_sums[target]
                
                # Match the lists of pairs
                for pair1 in list_a:
                    # Skip if users already cleared
                    # Using intersection here cause we need to check for pair so this is faster
                    if pair1.intersection(used): 
                        continue
                    
                    for pair2 in list_b:
                        # Same skip if users already used
                        if pair2.intersection(used): 
                            continue
                        
                        group = pair1.union(pair2)
                        # Ensure all 4 users are distinct
                        if len(group) == 4:
                            # Execute using greedy logic on just this group
                            # A quad can be solved in 3 transactions optimally
                            sub_bal = {u: pool[u] for u in group}
                            sub_txs = SimpleGreedySolver(strategy='max').solve(sub_bal)
                            txs.extend(sub_txs)
                            
                            used.update(group)
                            break # Move to next p1
                    
        # Cleanup
        for u in used: 
            if u in pool: 
                del pool[u]
            
        # print("4 cycles ", len(txs))
        return txs