"""Exact One-Reference Disruption Index (1D) on a toy citation network.

For a focal paper F and ONE of its references r, the single-reference score is

    1D^(r) = (N_F - N_B) / (N_F + N_B + N_R)

    N_F : papers citing F but not r
    N_B : papers citing both F and r
    N_R : papers citing r but not F   (F itself is not counted)

counted over every paper in the network (no publication-year or citation-window filter), and
1D(F) is the plain average of 1D^(r) over the references r of F for which it is defined
(N_F + N_B + N_R > 0).
This is the standard disruption index with the reference list reduced to {r}, so the size
of the comparison set no longer grows with the length of F's reference list.

Everything below is dense matrix algebra: fine for a toy network, not for 50 million papers.
"""
import numpy as np
import pandas as pd

edges = pd.read_csv("toy_citation_network.csv")            # one row per citation: citing -> cited
papers = np.unique(edges[["citing", "cited"]].to_numpy())  # sorted paper ids
index = {p: i for i, p in enumerate(papers)}
n = len(papers)

# A[i, j] = 1 if paper i cites paper j
A = np.zeros((n, n))
A[edges["citing"].map(index), edges["cited"].map(index)] = 1

c = A.sum(axis=0)   # c[j]    = number of papers citing j
B = A.T @ A         # B[f, r] = number of papers citing both f and r   (N_B)

# For every pair (F, r): N_F + N_B = c[F] and N_R + N_B = c[r] - 1 (F cites r, and is excluded)
numerator = c[:, None] - 2 * B                  # N_F - N_B
denominator = c[:, None] + c[None, :] - 1 - B   # N_F + N_B + N_R

# Keep only real citation pairs (F cites r) whose comparison set is not empty
defined = (A == 1) & (denominator > 0)
oneD_r = np.where(defined, numerator / np.where(defined, denominator, 1), np.nan)

# 1D(F) = mean of 1D^(r) over F's references; NaN if F has no reference to average over
count = defined.sum(axis=1)
oneD = np.where(count > 0, np.nansum(oneD_r, axis=1) / np.where(count > 0, count, 1), np.nan)

result = pd.DataFrame({"paper": papers, "references": A.sum(axis=1).astype(int),
                       "citations": c.astype(int), "oneD": oneD})
print(result.to_string(index=False, float_format="%.4f"))
