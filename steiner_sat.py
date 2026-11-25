import subprocess
import sys
from argparse import ArgumentParser
from itertools import combinations
import time

def create_triples(n):
    triples = list(combinations(range(1, n + 1), 3))
    return triples, {t: i for i, t in enumerate(triples, 1)}

def triples_with_pair(i, j, n, triple_to_id):
    return [triple_to_id[tuple(sorted((i, j, k)))] for k in range(1, n + 1) if k not in (i, j)]

def at_most_one_pairwise(ids):
    return [[-a, -b, 0] for a, b in combinations(ids, 2)]

def at_most_one_sequential(ids, nr_vars):
    k = len(ids)
    if k <= 1:
        return [], nr_vars
    s = [nr_vars + 1 + i for i in range(k - 1)]

    clauses = [[-ids[0], s[0], 0]]
    for i in range(1, k - 1):
        clauses.append([-ids[i], s[i], 0])
        clauses.append([-s[i - 1], s[i], 0])
        clauses.append([-ids[i], -s[i - 1], 0])
    clauses.append([-ids[k - 1], -s[k - 2], 0])
    return clauses, nr_vars + k - 1

def encode(n, encoding, symmetry):
    triples, triple_to_id = create_triples(n)
    nr_vars = len(triples)
    cnf = []

    for i, j in combinations(range(1, n + 1), 2):
        ids = triples_with_pair(i, j, n, triple_to_id)

        cnf.append(ids + [0])

        if encoding == "pairwise":
            cnf.extend(at_most_one_pairwise(ids))
        else:
            clauses, nr_vars = at_most_one_sequential(ids, nr_vars)
            cnf.extend(clauses)

    if symmetry:
        for a in range(2, n, 2):
            cnf.append([triple_to_id[(1, a, a + 1)], 0])

    return cnf, nr_vars, triples

def write_dimacs(cnf, nr_vars, output_name):
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + "\n")
        for clause in cnf:
            file.write(" ".join(str(lit) for lit in clause) + "\n")

def call_solver(output_name, solver_name, verbosity):
    return subprocess.run([solver_name, "-model", "-verb=" + str(verbosity), output_name],
                          stdout=subprocess.PIPE, text=True)

def decode(result, triples):
    model = []
    for line in result.stdout.splitlines():
        if line.startswith("v"):
            model.extend(int(v) for v in line.split()[1:])

    return [triples[v - 1] for v in model if 0 < v <= len(triples)]

def check_solution(n, chosen):
    return sorted(p for t in chosen for p in combinations(t, 2)) == list(combinations(range(1, n + 1), 2))

def print_result(n, result, chosen):
    print()
    print("##################################################################")
    print("#########[ Human readable result: Steiner triple system ]#########")
    print("##################################################################")
    print()

    if result.returncode == 20:
        print("UNSAT: there is no Steiner triple system of order " + str(n) + ".")
        return
    if result.returncode != 10:
        print("The solver did not give an answer (return code " + str(result.returncode) + ").")
        return

    print("SAT: a Steiner triple system of order " + str(n) + " exists.")
    print("It has " + str(len(chosen)) + " triples:")
    print()
    width = len(str(n))
    cells = ["{" + ", ".join(str(p).rjust(width) for p in triple) + "}" for triple in chosen]
    if not cells:
        print("  (no triples needed, there are no pairs to cover)")
    for start in range(0, len(cells), 6):
        print("  " + "  ".join(cells[start:start + 6]))
    print()
    if check_solution(n, chosen):
        print("Check: every pair of points is in exactly one triple - OK")
    else:
        print("Check FAILED: the decoded triples are not a Steiner triple system!")

if __name__ == "__main__":

    parser = ArgumentParser(description="Steiner triple systems (CSPLib prob044) solved with Glucose.")
    parser.add_argument("-i", "--input", default="input.in", type=str,
                        help="The instance file (contains the order n).")
    parser.add_argument("-n", "--order", type=int,
                        help="The order n given directly (then the input file is not read).")
    parser.add_argument("-o", "--output", default="formula.cnf", type=str,
                        help="Output file for the DIMACS format (i.e. the CNF formula).")
    parser.add_argument("-s", "--solver", default="./glucose-simp", type=str,
                        help="The SAT solver to be used.")
    parser.add_argument("-v", "--verb", default=0, type=int, choices=range(0, 2),
                        help="Verbosity: 1 prints the solver's output and statistics.")
    parser.add_argument("-e", "--encoding", default="pairwise", choices=["pairwise", "sequential"],
                        help="Encoding of the 'at most one' constraints.")
    parser.add_argument("--symmetry", action="store_true",
                        help="Add symmetry breaking (fix the triples containing point 1).")
    parser.add_argument("-p", "--print-cnf", action="store_true",
                        help="Print the CNF formula in DIMACS format.")
    args = parser.parse_args()

    n = args.order if args.order is not None else int(open(args.input).read().split()[0])
    if n < 1:
        sys.exit("The order n has to be a positive integer.")

    start = time.perf_counter()
    cnf, nr_vars, triples = encode(n, args.encoding, args.symmetry)
    write_dimacs(cnf, nr_vars, args.output)
    encode_time = time.perf_counter() - start

    if args.print_cnf:
        with open(args.output, "r") as file:
            print(file.read(), end="")

    start = time.perf_counter()
    result = call_solver(args.output, args.solver, args.verb)
    solve_time = time.perf_counter() - start

    if args.verb == 1:
        print(result.stdout, end="")
        print("c order n = " + str(n) + ", encoding = " + args.encoding + ", symmetry breaking = " + str(args.symmetry))
        print("c variables = " + str(nr_vars) + ", clauses = " + str(len(cnf)))
        print("c encoding time = %.2f s, solver time = %.2f s" % (encode_time, solve_time))

    chosen = decode(result, triples) if result.returncode == 10 else []
    print_result(n, result, chosen)