# Steiner triple systems via SAT

This is a project for Propositional and Predicate Logic (NAIL062). The Python script `steiner_sat.py` encodes the problem of finding a Steiner triple system ([CSPLib, problem 044](https://www.csplib.org/Problems/prob044/)) into a CNF formula, solves it with a SAT solver and decodes the result back into a list of triples.

The SAT solver used is [Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1). I compiled it from the source code using

```
cmake .
make
```

This creates the executables `glucose-simp` (the sequential solver) and `glucose-syrup` (the parallel one). The script uses `glucose-simp` and expects it in the same directory as the script, but another path can be given with `-s`. Everything was tested on macOS (it should also work on Linux; on Windows I recommend WSL). Only the Python standard library is used.

The problem is already a decision problem: for a given number $n$, we ask whether a Steiner triple system of order $n$ exists. If it does, the script also prints one.

# Documentation

## Problem description

We have $n$ points $V = \{1, 2, \ldots, n\}$. A *Steiner triple system* of order $n$ is a set $B$ of 3-element subsets of $V$ (called triples) such that **every pair of distinct points is contained in exactly one triple** of $B$.

- Parameter: a positive integer $n$.
- Question: does there exist a set $B \subseteq \binom{V}{3}$ such that for every pair $\{i, j\} \subseteq V$ with $i \neq j$ there is exactly one triple $t \in B$ with $\{i, j\} \subseteq t$?

CSPLib states the problem a bit differently: find $n(n-1)/6$ triples such that any two triples have at most one point in common. This is the same thing. Two triples sharing two points would share a pair, so "at most one common point" means that no pair is covered twice. Then $n(n-1)/6$ triples cover $3 \cdot n(n-1)/6 = \binom{n}{2}$ different pairs, which is all of them. In the other direction, if every pair is covered exactly once, there must be $\binom{n}{2}/3 = n(n-1)/6$ triples.

It is known (Kirkman, 1847) that a Steiner triple system of order $n$ exists if and only if $n \equiv 1$ or $3 \pmod 6$. The "only if" part is easy: the number of triples $n(n-1)/6$ has to be an integer, and every point $p$ is in $n-1$ pairs which are split into triples through $p$ two at a time, so $n-1$ has to be even. The script does **not** use this fact; the SAT solver has to find the answer on its own. This means we know the correct answer for every instance in advance, which is useful for testing.

An example of the input format is a file containing just the order:

```
7
```

## Encoding

For every triple $a < b < c$ of points we have a variable $x_{a,b,c}$, which is true if and only if the triple $\{a, b, c\}$ is in $B$. This gives $\binom{n}{3}$ variables. They are numbered from 1 in lexicographic order of the triples, i.e. $x_{1,2,3} = 1$, $x_{1,2,4} = 2$, and so on.

For a pair $i < j$ let $T(i,j)$ be the set of the $n-2$ triples that contain both $i$ and $j$. We use the following constraints:

- Every pair is covered by at least one chosen triple

    $\bigvee_{t \in T(i,j)} x_t$ for each $i < j$

- Every pair is covered by at most one chosen triple

    $\neg x_s \vee \neg x_t$ for each $i < j$ and each two different triples $s, t \in T(i,j)$

A satisfying assignment gives a Steiner triple system (take the triples whose variables are true), and a Steiner triple system gives a satisfying assignment (set exactly its triples to true), so the formula is satisfiable if and only if the answer is yes.

The formula has $\binom{n}{3}$ variables and $\binom{n}{2}\left(1 + \binom{n-2}{2}\right)$ clauses, so the number of clauses grows like $n^4/8$. For example, $n = 67$ gives 47,905 variables and 4,601,091 clauses. Two special cases: for $n = 1$ there are no pairs, so the formula is empty and satisfiable (the empty set of triples works). For $n = 2$ the only pair $\{1,2\}$ has no triple containing it, so the "at least one" clause is the empty clause (a line with just `0` in DIMACS) and the formula is unsatisfiable.

### Alternatives

The script can also use two other options.

- **Sequential counter** (`-e sequential`). The "at most one" constraint with pairwise clauses needs $\binom{k}{2}$ clauses for $k$ triples. The sequential counter ([Sinz, 2005](https://www.carstensinz.de/papers/CP-2005.pdf)) adds helper variables $s_1, \ldots, s_{k-1}$, where $s_m$ means "one of the first $m$ triples is chosen", and uses the clauses

    $\neg x_1 \vee s_1$, $\quad \neg x_k \vee \neg s_{k-1}$, $\quad$ and for $1 < m < k$: $\neg x_m \vee s_m$, $\neg s_{m-1} \vee s_m$, $\neg x_m \vee \neg s_{m-1}$.

    This is only $3k - 4$ clauses but $k - 1$ new variables per pair. For $n = 67$ we get 189,409 variables and 424,512 clauses, so the CNF file is about 10 times smaller.

- **Symmetry breaking** (`--symmetry`). If we rename the points of a Steiner triple system, we get another one. Point 1 lies in $(n-1)/2$ triples, and these split the points $2, \ldots, n$ into pairs. After renaming we can assume that these triples are $\{1,2,3\}, \{1,4,5\}, \{1,6,7\}, \ldots$, so we add them as unit clauses. This does not change whether the formula is satisfiable, but the solver has much less to search.

- **CSPLib formulation.** We could also directly say "choose exactly $n(n-1)/6$ triples and no two chosen triples share two points". The second part gives the same clauses as our "at most one" constraint, and the first part needs a cardinality constraint (e.g. a counter over all $\binom{n}{3}$ variables), so it is bigger and more complicated. I did not implement it.

## User documentation

Basic usage:

```
steiner_sat.py [-h] [-i INPUT] [-n ORDER] [-o OUTPUT] [-s SOLVER] [-v {0,1}] [-e {pairwise,sequential}] [--symmetry] [-p]
```

Command-line options:

* `-h`, `--help`: Show a help message and exit.
* `-i INPUT`, `--input INPUT`: The instance file. Default: "input.in".
* `-n ORDER`, `--order ORDER`: The order $n$ given directly on the command line (then no input file is read).
* `-o OUTPUT`, `--output OUTPUT`: Output file for the DIMACS format (i.e. the CNF formula). Default: "formula.cnf".
* `-s SOLVER`, `--solver SOLVER`: The SAT solver to be used. Default: "./glucose-simp".
* `-v {0,1}`, `--verb {0,1}`: Verbosity. With `-v 1` the script prints the whole output of Glucose (including its statistics about the search) and then the size of the formula and the encoding and solving times. Default: 0.
* `-e {pairwise,sequential}`, `--encoding {pairwise,sequential}`: The encoding of the "at most one" constraints. Default: "pairwise".
* `--symmetry`: Add the symmetry breaking clauses.
* `-p`, `--print-cnf`: Print the CNF formula in DIMACS format to the standard output.

The input file contains one positive integer, the order $n$. For example:

```
python3 steiner_sat.py -i instances/sts-7.in
python3 steiner_sat.py -n 9 -v 1
python3 steiner_sat.py -i instances/sts-6.in -p
```

The output for `instances/sts-7.in` looks like this:

```
##################################################################
#########[ Human readable result: Steiner triple system ]#########
##################################################################

SAT: a Steiner triple system of order 7 exists.
It has 7 triples:

  {1, 2, 4}  {1, 3, 6}  {1, 5, 7}  {2, 3, 5}  {2, 6, 7}  {3, 4, 7}
  {4, 5, 6}

Check: every pair of points is in exactly one triple - OK
```

Each `{a, b, c}` is one triple of the system. The last line is a check done in Python directly on the decoded triples. It takes the three pairs inside every triple, sorts them and compares the result with the list of all pairs, so every pair has to be there exactly once. This check does not depend on the encoding being correct. If there is no solution, the script prints `UNSAT: there is no Steiner triple system of order n.`

## Example instances

* `sts-1.in`, `sts-2.in`: The two special cases from above (empty formula, SAT; empty clause, UNSAT).
* `sts-6.in`: A small unsatisfiable instance (20 variables, 105 clauses). It is easy to see why by hand: point 1 is in 5 pairs, every triple containing point 1 covers exactly 2 of them, and 5 is odd.
* `sts-7.in`: A small satisfiable instance (35 variables, 231 clauses). The solution is the Fano plane with 7 triples, and it is easy to check by hand that all 21 pairs are covered exactly once (see the output above).
* `sts-9.in`: A small satisfiable instance with $n \equiv 3 \pmod 6$ (12 triples).