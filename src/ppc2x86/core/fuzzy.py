"""
fuzzy.py — Fuzzy matching helpers for instruction lookup.

Public API
----------
fuzzy_match(query, candidates, max_results, threshold)
    Returns a ranked list of (mnemonic, score) pairs where score is 0.0–1.0.
    1.0 = exact match, higher is better.

levenshtein(a, b)
    Compute edit distance between two strings.
"""

from __future__ import annotations


def levenshtein(a: str, b: str) -> int:
    """Standard dynamic-programming Levenshtein distance (no external deps)."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la

    # Two-row DP to save memory
    prev = list(range(lb + 1))
    curr = [0] * (lb + 1)
    for i in range(1, la + 1):
        curr[0] = i
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,       # deletion
                curr[j - 1] + 1,   # insertion
                prev[j - 1] + cost # substitution
            )
        prev, curr = curr, prev

    return prev[lb]


def fuzzy_match(
    query: str,
    candidates: list[str],
    max_results: int = 8,
    threshold: float = 0.3,
) -> list[tuple[str, float]]:
    """
    Score each candidate against *query* and return the top matches.

    Scoring rules (applied in order, highest wins):
    1. Exact match (case-insensitive)     → 1.0
    2. Prefix match                       → 0.85 – 0.95 (longer prefix = higher)
    3. Substring match                    → 0.70
    4. Levenshtein-based similarity       → normalised 0.0–0.65

    Parameters
    ----------
    query       : search string (case-insensitive)
    candidates  : list of candidate strings
    max_results : maximum number of results to return
    threshold   : minimum score (inclusive) to include in results

    Returns
    -------
    List of (candidate, score) sorted descending by score.
    """
    q = query.lower()
    scored: list[tuple[str, float]] = []

    for cand in candidates:
        c = cand.lower()

        # 1. Exact
        if c == q:
            scored.append((cand, 1.0))
            continue

        # 2. Prefix
        if c.startswith(q):
            # Score increases with how much of the candidate the query covers
            prefix_score = 0.85 + 0.10 * (len(q) / max(len(c), 1))
            scored.append((cand, prefix_score))
            continue

        # 3. Substring (query inside candidate, or candidate inside query)
        if q in c or c in q:
            scored.append((cand, 0.70))
            continue

        # 4. Levenshtein similarity
        dist = levenshtein(q, c)
        max_len = max(len(q), len(c))
        sim = 1.0 - dist / max_len   # normalised similarity 0–1
        score = sim * 0.65           # cap levenshtein contribution below substring
        if score >= threshold:
            scored.append((cand, score))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:max_results]
