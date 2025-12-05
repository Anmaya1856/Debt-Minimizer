import heapq
from typing import Dict, List, Tuple
from collections import defaultdict

class SimpleGreedySolver:
    """
    Max Max / Min Min Greedy Hybrid Solver. 
    
    Strategy:
    1. Uses Heaps for optimisation.
        - Phase A: Global Exact Matches (O(1) Lookup).
        - Phase B: Greedy Match.
            - Pick MAX/MIN Debtor/Creditor.    
    """
    def __init__(self, strategy='max'):
        self.strategy = strategy

    def solve(self, net_balances: Dict[int, float]) -> List[Tuple[int, int, float]]:
        transactions = []

        # Setup Active Balances (Filter zero)
        active_bals = {userId: bal for userId, bal in net_balances.items() if bal != 0.0}
        # Maps for Fast Lookups: { amount: {user_ids} } 
        # This makes the default val of any new value to be an empty set
        debtor_map = defaultdict(set)
        creditor_map = defaultdict(set)
        
        for userId, bal in active_bals.items():
            val = abs(bal)
            if bal < 0: 
                debtor_map[val].add(userId)
            else:     
                creditor_map[val].add(userId)

        # Net off any EXACT MATCHES
        common_amts = set(debtor_map.keys()) & set(creditor_map.keys())
        
        for amt in common_amts:
            # For every amount while there are users on both sides set them off
            while debtor_map[amt] and creditor_map[amt]:
                d = debtor_map[amt].pop()
                c = creditor_map[amt].pop()
                transactions.append((d, c, amt))

                # Cleanup of users as they are done now
                del active_bals[d]
                del active_bals[c]
            
            # Cleanup of maps, delete the val if there is no user with that bal
            if not debtor_map[amt]: 
                del debtor_map[amt]
            if not creditor_map[amt]: 
                del creditor_map[amt]

        # BUILD HEAPS
        debtor_heap = []
        creditor_heap = []
        
        for userId, bal in active_bals.items():
            val = abs(bal)
            # Max strategy: Sort by -val (Largest first)
            # Min strategy: Sort by val (Smallest first)
            # This is because heap is min heap by default in python
            if self.strategy == 'max':
                prio = -val
            else:
                prio = val

            # Push in debtor heap if bal < 0
            if bal < 0: 
                heapq.heappush(debtor_heap, (prio, userId))
            # Push in creditor heap if bal > 0
            else:     
                heapq.heappush(creditor_heap, (prio, userId))

        # LOOP SOLVER
        while debtor_heap and creditor_heap:
            # Pop the first debtor or creditor
            debtor_id = -1
            creditor_id = -1
            
            while debtor_heap:
                amt, userId = heapq.heappop(debtor_heap)
                if userId in active_bals: 
                    debtor_id = userId
                    break
            
            creditor_id = -1
            while creditor_heap:
                amt, userId = heapq.heappop(creditor_heap)
                if userId in active_bals: 
                    creditor_id = userId
                    break
            
            if debtor_id == -1 or  creditor_id == -1: 
                break

            # Match the values
            debtor_val = abs(active_bals[debtor_id])
            creditor_val = active_bals[creditor_id]

            # Amount net off in this transaction will be the lower of the both obviously
            amt = min(debtor_val, creditor_val)
            transactions.append((debtor_id, creditor_id, amt))
            
            # Cleanup maps
            if debtor_val in debtor_map: 
                debtor_map[debtor_val].discard(debtor_id)
            if creditor_val in creditor_map: 
                creditor_map[creditor_val].discard(creditor_id)
            
            # Calc Remainders (Round to maintain precision)
            rem_debtor = round(debtor_val - amt, 2)
            rem_creditor = round(creditor_val - amt, 2)
            
            # Handle Remainders
            self._handle_remainder(debtor_id, rem_debtor, True, active_bals, debtor_map, creditor_map, debtor_heap, transactions)
            self._handle_remainder(creditor_id, rem_creditor, False, active_bals, debtor_map, creditor_map, creditor_heap, transactions)

        return transactions
    
    def _handle_remainder(self, uid, remainder, is_debtor, active_bals, d_map, c_map, heap, transactions):
        """
        Handles the logic for leftover debt/credit:
        1. Checks if settled (rem < 0.001). (exact match)
        2. Checks for Immediate Exact Match in the OPPOSITE map.
        3. Or push back to heap.
        """
        if remainder < 0.001:
            if uid in active_bals: 
                del active_bals[uid]
            return

        # Identify which maps to use
        my_map = d_map if is_debtor else c_map
        other_map = c_map if is_debtor else d_map
        
        # Check for Exact Match in the other map 
        # Essentialy means that if debtor was 100 and creditor was 120 then rem = 20
        # We check if rem = 20 exists in the debtor and if so set if off
        if remainder in other_map and other_map[remainder]:
            match_id = other_map[remainder].pop()
            
            # Create Transaction
            if is_debtor:
                transactions.append((uid, match_id, remainder)) # Debtor pays Match
            else:
                transactions.append((match_id, uid, remainder)) # Match pays Creditor
            
            # Cleanup Match
            del active_bals[uid]
            del active_bals[match_id]
            if not other_map[remainder]: 
                del other_map[remainder]
            
        else:
            # No match, add back to heap
            if is_debtor:
                active_bals[uid] = -remainder
            else:
                active_bals[uid] = remainder
                
            my_map[remainder].add(uid)
            if self.strategy == 'max':
                prio = -remainder
            else:
                prio = remainder
            heapq.heappush(heap, (prio, uid))