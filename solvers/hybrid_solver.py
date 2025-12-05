import random
import heapq
from typing import Dict, List, Tuple
from collections import defaultdict
from tqdm import tqdm

class HybridSolver():
    """
    Monte Carlo Random + Max Max Greedy Hybrid Solver. 
    (Algo suggested by Prof. Lauren implemented by me)
    
    Strategy:
    1. Combines the efficiency of Heaps (Max-Max) with the exploration of Random Lists.
    2. Iteration Loop (Monte Carlo):
       - Phase A: Global Exact Matches (O(1) Lookup).
       - Phase B: Greedy Match.
         - With probability P (e.g. 0.7): Pick MAX Debtor/Creditor (Heap).
         - With probability 1-P (e.g. 0.3): Pick RANDOM Debtor/Creditor (List).
    
    Tried a lot of configs, having a higher P val is better (.95 seems to give good results generally)
    But P b/w 0.85 to 0.97 gives good results generally
    """
    def __init__(self, iterations=1000, greedy_probability=0.90):
        self.iterations = iterations
        self.epsilon = greedy_probability

    def solve(self, net_balances: Dict[int, float]) -> List[Tuple[int, int, float]]:
        """
        Main function to solve the problem given the algo above

        d_map = debtor map
        c_map = creditor map
        d is short for debtor
        c is short for creditor
        """
        pool_base = {userId: bal for userId, bal in net_balances.items() if bal != 0.0}
        
        best_txs = None
        min_tx_count = float('inf')

        for _ in tqdm(range(self.iterations)):
            # Copying since we work in destructive fashion and need it everytime
            active_bals = pool_base.copy()
            current_txs = []
            
            # DATA STRUCTURES
            # Maps for Exact Lookup {value : UserId}
            d_map = defaultdict(set)
            c_map = defaultdict(set)
            
            # Lists for Random Access [UserId]
            d_list = []
            c_list = []
            
            # Heaps for Greedy Access (Max-Max) (Value, UserId)
            d_heap = []
            c_heap = []
            
            # Initialise all the different Structures
            for userId, bal in active_bals.items():
                val = abs(bal)
                # bal < 0 means debtor so appending in debtor
                if bal < 0:
                    d_map[val].add(userId)
                    d_list.append(userId)
                    # Max-Heap via negation since heaps are min heap by default in python
                    heapq.heappush(d_heap, (-val, userId)) 
                # bal > 0 means creditor so appending in creditor
                else:
                    c_map[val].add(userId)
                    c_list.append(userId)
                    heapq.heappush(c_heap, (-val, userId))
            
            # Shuffle lists once for randomness order
            random.shuffle(d_list)
            random.shuffle(c_list)

            # SOLVER LOOP
            while active_bals:
                
                # Net of Common Amounts
                common = set(d_map.keys()) & set(c_map.keys())
                match_found = False
                # If there are common amounts
                if common:
                    for amt in common:
                        # For every amount while there are users on both sides set them off
                        while d_map[amt] and c_map[amt]:
                            d = d_map[amt].pop()
                            c = c_map[amt].pop()
                            current_txs.append((d, c, amt))

                            # Cleanup of users as they are done now
                            del active_bals[d]
                            del active_bals[c]
                            match_found = True

                        # Cleanup of maps, delete the val if there is no user with that bal
                        if not d_map[amt]: 
                            del d_map[amt]
                        if not c_map[amt]: 
                            del c_map[amt]
                
                if match_found: 
                    continue
                if not active_bals: 
                    break

                # Max Max or Random Selection
                # if random number is less than prob use max max greedy or use random
                use_greedy = random.random() < self.epsilon
                
                # Select Debtor
                d_u = -1
                if use_greedy:
                    # Try Heap (Max)
                    while d_heap:
                        _, u = heapq.heappop(d_heap)
                        if u in active_bals: 
                            d_u = u
                            break
                
                # Fallback to List (Random) if Heap empty or skipped
                if d_u == -1:
                    while d_list:
                        u = d_list.pop()
                        if u in active_bals: 
                            d_u = u
                            break
                
                # Select Creditor
                c_u = -1
                if use_greedy:
                    # Try Heap (Max)
                    while c_heap:
                        _, u = heapq.heappop(c_heap)
                        if u in active_bals: 
                            c_u = u
                            break
                
                # Fallback to List (Random)
                if c_u == -1:
                    while c_list:
                        u = c_list.pop()
                        if u in active_bals: 
                            c_u = u; 
                            break

                # If we can't find any debtor or creditor
                # Should never really come to this since we are checking if active bals is empty above
                # But good to have
                if d_u == -1 or c_u == -1: 
                    break

                # MATCH
                d_val = abs(active_bals[d_u])
                c_val = active_bals[c_u]
                
                # Cleanup Maps 
                # Using discard here so that keyerror doesn't occur as in remove
                if d_val in d_map: 
                    d_map[d_val].discard(d_u)
                if c_val in c_map: 
                    c_map[c_val].discard(c_u)
                
                # Amount net off in this transaction will be the lower of the both obviously
                amt = min(d_val, c_val)
                current_txs.append((d_u, c_u, amt))
                
                # Remainder amount, one of the vals will be 0 other would be non zero
                rem_d = round(d_val - amt, 2)
                rem_c = round(c_val - amt, 2)
                
                # HANDLE REMAINDERS
                self._handle_remainder(d_u, rem_d, True, active_bals, d_map, c_map, d_list, c_list, d_heap, current_txs)
                self._handle_remainder(c_u, rem_c, False, active_bals, d_map, c_map, d_list, c_list, c_heap, current_txs)

            if len(current_txs) < min_tx_count:
                min_tx_count = len(current_txs)
                best_txs = current_txs
                
        return best_txs

    def _handle_remainder(self, uid, remainder, is_debtor : bool, active_bals, d_map, c_map, d_list, c_list, heap, current_txs):
        """
        Function to handle remainders from the above function.
        
        Steps:
        1. Check if there is an exact value left in the opposing side if so match them
        2. If no exact value then push in heap, map, list.
        """
        # If remainder is negligible / 0 don't run the whole function just return
        # Always executes once since one guy would have 0 remainder
        if remainder < 0.001:
            if uid in active_bals: 
                del active_bals[uid]
            return

        # Identify Structures
        my_map = d_map if is_debtor else c_map
        other_map = c_map if is_debtor else d_map
        my_list = d_list if is_debtor else c_list

        # Check Immediate Exact Match
        if remainder in other_map and other_map[remainder]:
            match_id = other_map[remainder].pop()
            
            # If user with remainder is debtor and exact match with creditor is found
            # Then transaction to settle would be debtor pays mathced person with the rem
            if is_debtor: 
                current_txs.append((uid, match_id, remainder))
            # If user with rem is creditor and exact match with debtor is found
            # Then transaction to settle would be matched person pays creditor with the rem
            else:         
                current_txs.append((match_id, uid, remainder))
            
            # Cleanup Maps 
            if uid in active_bals: 
                del active_bals[uid]
            if match_id in active_bals: 
                del active_bals[match_id]
            if not other_map[remainder]: 
                del other_map[remainder]
        else:
            # Add back to System (All structures)
            if is_debtor: 
                active_bals[uid] = -remainder
            else:         
                active_bals[uid] = remainder
            
            my_map[remainder].add(uid)
            my_list.append(uid)           
            heapq.heappush(heap, (-remainder, uid)) 