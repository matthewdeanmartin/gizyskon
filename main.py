# Let's verify the puzzle with two interpretations and show results clearly.
# Interpretation A:
#   Map A=1..Z=26. For each position i, tail sum T_i = sum(values[i:]).
#   Output letter F_i = ((T_i + 6 - 1) % 26) + 1  (i.e., add 6 "mod 26" in 1..26 space).
# We'll (1) compute the forward map, (2) invert it deterministically to reconstruct a word
# that maps to a given target (e.g., "BULLSHIT"), and (3) check uniqueness.
#
# Interpretation B:
#   Same tail sum T_i, but first "break into digits" = sum of decimal digits of T_i,
#   then add 6, then map to letter (again in 1..26 circularly). We'll search backward for solutions.


from itertools import product
from typing import List, Optional, Tuple

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
val = {c: i+1 for i, c in enumerate(alphabet)}
letter = {i+1: c for i, c in enumerate(alphabet)}

def map_interpretation_A_tail_plus6_mod26(values: List[int]) -> List[int]:
    # produce output values (1..26) under Interpretation A
    out = []
    tail = 0
    # compute tails from end to start to avoid recomputing sums
    for x in reversed(values):
        tail += x
        y = ((tail + 6 - 1) % 26) + 1
        out.append(y)
    return list(reversed(out))

def reconstruct_interpretation_A(target_vals: List[int]) -> Optional[List[int]]:
    # Given target output y_i, reconstruct unique x_i if possible (1..26 each)
    n = len(target_vals)
    T = [None]*n  # tail sums
    x = [None]*n  # letters 1..26
    # last position: T_n must be in [1..26] and ((T_n+6-1) % 26)+1 == y_n
    yn = target_vals[-1]
    # Tn candidates in 1..26 s.t. ((t+5)%26)+1 == yn -> (t+5) % 26 == yn-1 -> t ≡ yn-6 (mod 26)
    # There is exactly one t in 1..26 for each residue class; compute it.
    residue = (yn - 6) % 26  # 0..25
    Tn = residue if residue != 0 else 26
    if not (1 <= Tn <= 26):
        return None
    T[-1] = Tn
    x[-1] = Tn  # since Tn = x_n

    # work backwards
    for i in range(n-2, -1, -1):
        yi = target_vals[i]
        # Ti must satisfy Ti % 26 ≡ yi-6 (in 1..26 space), AND Ti - T_{i+1} in [1..26]
        residue = (yi - 6) % 26
        # Generate all numbers congruent to residue in the feasible range.
        # Feasible range for Ti given Ti+1: [Ti+1 + 1, Ti+1 + 26]
        low = T[i+1] + 1
        high = T[i+1] + 26
        # Find the unique t in [low, high] with t ≡ residue (mod 26), but note that our mapping used 1..26,
        # not 0..25. For residue==0, we want numbers ≡ 0 mod 26.
        candidates = []
        # Bring low up to the first number with this residue
        if residue == 0:
            r0 = 26
        else:
            r0 = residue
        # Find the first k >= low s.t. k % 26 == r0 % 26
        start = low + ((r0 - low) % 26)
        for t in range(start, high+1, 26):
            candidates.append(t)
        if len(candidates) != 1:
            return None  # if not exactly one, no unique reconstruction
        Ti = candidates[0]
        T[i] = Ti
        xi = Ti - T[i+1]
        if not (1 <= xi <= 26):
            return None
        x[i] = xi

    return x

def to_word(values: List[int]) -> str:
    return "".join(letter[v] for v in values)

def from_word(w: str) -> List[int]:
    return [val[c] for c in w]

def map_to_word_interpretation_A(w: str) -> str:
    values = from_word(w)
    outvals = map_interpretation_A_tail_plus6_mod26(values)
    return to_word(outvals)

# Interpretation B helpers
def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(n))

def map_interpretation_B(values: List[int]) -> List[int]:
    out = []
    tail = 0
    for x in reversed(values):
        tail += x
        y = ((digit_sum(tail) + 6 - 1) % 26) + 1
        out.append(y)
    return list(reversed(out))

def reconstruct_interpretation_B_all(target_vals: List[int]) -> List[List[int]]:
    # Backtracking over tail sums with tight bounds.
    n = len(target_vals)
    sols = []

    # Precompute feasible single-letter tails for last position
    last_target = target_vals[-1]
    last_candidates = [t for t in range(1, 26+1)
                       if ((digit_sum(t) + 6 - 1) % 26) + 1 == last_target]

    def backtrack(i: int, T_next: int, acc_letters: List[int]):
        # i indexes current position from right to left (working backwards).
        # T_next is T_{i+1}; we need to choose T_i in [T_next+1, T_next+26] with correct f(T_i).
        if i < 0:
            sols.append(list(reversed(acc_letters)))  # reverse to normal order
            return
        low = T_next + 1
        high = T_next + 26
        y = target_vals[i]
        # filter candidates in [low, high] matching y
        for Ti in range(low, high+1):
            if ((digit_sum(Ti) + 6 - 1) % 26) + 1 == y:
                xi = Ti - T_next
                if 1 <= xi <= 26:
                    acc_letters.append(xi)
                    backtrack(i-1, Ti, acc_letters)
                    acc_letters.pop()

    # Start from last pos (index n-1): choose T_n from last_candidates and recurse
    for Tn in last_candidates:
        backtrack(n-2, Tn, [Tn])  # acc_letters currently has x_n = Tn
    return sols


# Target
target = "BULLSHIT"
target_vals = from_word(target)

# 1) Interpretation A: reconstruct deterministically
x_vals_A = reconstruct_interpretation_A(target_vals)
word_A = to_word(x_vals_A) if x_vals_A else None
mapped_A = map_to_word_interpretation_A(word_A) if word_A else None

print("Interpretation A results")
print("------------------------")
print("Reconstructed word:", word_A)
print("Maps to:", mapped_A)
print("Values:", x_vals_A)

# 2) Verify if unique: the reconstruction logic already enforces uniqueness;
#    if it succeeds, it's the only solution in A..Z under this rule.
print("Unique under A..Z (deterministic reconstruction):", x_vals_A is not None)

# 3) Interpretation B: search for all solutions
sols_B = reconstruct_interpretation_B_all(target_vals)
print("\nInterpretation B results")
print("------------------------")
print("Number of solutions found:", len(sols_B))
if len(sols_B) <= 5:
    for s in sols_B:
        print("Solution:", to_word(s), s)

# Additional explicit check of the claimed example (if any)
claimed = "GIZSKYON"
mapped_claimed = map_to_word_interpretation_A(claimed)
print("\nClaimed example check")
print("---------------------")
print("Claimed word:", claimed)
print("Maps to:", mapped_claimed)
