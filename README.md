# One-Reference Disruption Index (1D)

Code and data for

> Junming Huang and Yu Xie. Large scientific teams are more, not less, disruptive. *arXiv preprint arXiv:2610.07329* (2026)

This repository currently holds two things:

1. a toy citation network and a minimal script that computes the exact 1D on it;
2. the 1D scores of 53,162,290 OpenAlex papers (see [Data](#data)).

## What 1D is

The standard disruption index of a focal paper *F* compares the papers that cite *F* with the papers that cite *F*'s references. The more references *F* has, the larger that second group becomes, so the index falls mechanically as reference lists lengthen. 1D removes this dependence by comparing *F* with one reference at a time. For a reference *r* of *F*,

$$
1D^(r) = (N_F - N_B) / (N_F + N_B + N_R)
$$

where, among all papers in the citation network (no publication-year or citation-window filter),

- `N_F` cite *F* but not *r*,
- `N_B` cite both *F* and *r*,
- `N_R` cite *r* but not *F* (*F* itself is not counted).

The paper-level score is the plain average over `R_F`, the references of *F* for which `1D^(r)` is defined (`N_F + N_B + N_R > 0`):

$$
1D(F) = (1 / |R_F|) * sum over r in R_F of 1D^(r)
$$

A paper with no such reference has no 1D.

## Toy example

Run from the repository folder:

```shell
pip install numpy pandas
python OneD.py
```

`toy_citation_network.csv` lists 17 citations among 10 papers (`citing,cited`; a paper cites only lower-numbered papers). `OneD.py` builds the citation matrix `A` and gets every count from two matrix operations: the column sums `c` (citations of each paper) and `B = AᵀA` (papers citing both of a pair). Expected output:

```python
 paper  references  citations   oneD
     1           0          3    NaN
     2           0          2    NaN
     3           2          5 0.5500
     4           2          3 0.0250
     5           2          2 0.3333
     6           2          2 0.0000
     7           2          0 0.0000
     8           2          0 0.0000
     9           3          0 0.0000
    10           2          0 0.0000
```

For example, paper 4 cites papers 1 and 3 and is cited by papers 6, 7 and 9.
Against reference 1: paper 7 also cites 1, paper 3 cites 1 only, so `1D^(1) = (2 - 1) / (2 + 1 + 1) = 0.25`.
Against reference 3: papers 6 and 9 also cite 3, papers 5 and 8 cite 3 only, so `1D^(3) = (1 - 2) / (1 + 2 + 2) = -0.2`.
Hence `1D(4) = (0.25 - 0.2) / 2 = 0.025`.

The script uses dense matrices and is meant to be read, not scaled. The scores below were computed with the same definition on sparse, sharded matrices.

## Data

`oneD_openalex.parquet` — one row per paper, 53,162,290 rows.

| column | type | meaning |
| --- | --- | --- |
| `openalex_id` | string | OpenAlex work id, e.g. `W2100837269`; the work is `https://openalex.org/<openalex_id>` |
| `oneD_uniform_inf` | float64 | exact 1D, uniform average over references, no citation window |

Download: see the [Releases](../../releases) page of this repository.
SHA-256: `4a824adec19d2a2177fab024d8f839e12258fe995ae31d21629fd6ef79787fc2`

```python
import pandas as pd
oneD = pd.read_parquet("oneD_openalex.parquet").set_index("openalex_id")["oneD_uniform_inf"]
```

How the scores were computed:

- Citation network: the OpenAlex snapshot of February 2025. Citing and cited papers are not filtered.
- No citation window: every citing paper in the snapshot counts.
- The score is exact — every reference of every paper is enumerated; nothing is sampled.

Which papers are included. The file is deliberately conservative: a paper is listed only if it meets
all of the following, and papers whose inclusion could be argued either way are left out.

- published in or before 2019;
- at least one author, at least one reference and at least one citation recorded in OpenAlex;
- at least one citing paper inside the citation network;
- a known OpenAlex domain (from `primary_topic`);
- a defined 1D.

A paper missing from the file therefore has no published score here; it does not have a score of zero.

The released rows are the intersection of two independently written exports of the same computed
scores: a paper is kept only if both exports list it and their float64 scores agree bit for bit.
This checks the extraction and the inclusion rules; it is not a second computation of the scores.

## License

Code: MIT (see `LICENSE`). Data: CC BY 4.0. OpenAlex itself is CC0.

## Contact

Junming Huang, Princeton University.
