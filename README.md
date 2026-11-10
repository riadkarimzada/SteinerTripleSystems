# Steiner triple systems via SAT

This is a project for Propositional and Predicate Logic (NAIL062). The Python script `steiner_sat.py` encodes the problem of finding a Steiner triple system ([CSPLib, problem 044](https://www.csplib.org/Problems/prob044/)) into a CNF formula, solves it with a SAT solver and decodes the result back into a list of triples.

The SAT solver used is [Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1). I compiled it from the source code using

```
cmake .
make
```

This creates the executables `glucose-simp` (the sequential solver) and `glucose-syrup` (the parallel one). The script uses `glucose-simp` and expects it in the same directory as the script, but another path can be given with `-s`. Everything was tested on macOS (it should also work on Linux; on Windows I recommend WSL). Only the Python standard library is used.

The problem is already a decision problem: for a given number $n$, we ask whether a Steiner triple system of order $n$ exists. If it does, the script also prints one.