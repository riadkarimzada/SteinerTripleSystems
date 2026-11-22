import subprocess
import sys
from argparse import ArgumentParser
from itertools import combinations

def create_triples(n):
    triples = list(combinations(range(1, n + 1), 3))
    return triples, {t: i for i, t in enumerate(triples, 1)}

def triples_with_pair(i, j, n, triple_to_id):
    return [triple_to_id[tuple(sorted((i, j, k)))] for k in range(1, n + 1) if k not in (i, j)]

def at_most_one_pairwise(ids):
    return [[-a, -b, 0] for a, b in combinations(ids, 2)]

def encode(n):
    triples, triple_to_id = create_triples(n)
    nr_vars = len(triples)
    cnf = []

    for i, j in combinations(range(1, n + 1), 2):
        ids = triples_with_pair(i, j, n, triple_to_id)

        cnf.append(ids + [0])

        cnf.extend(at_most_one_pairwise(ids))

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

    return [triples[v - 1] for v in model if v > 0]

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
    args = parser.parse_args()

    # get the input instance
    #the instance file contains a single number: the order n (the number of points)
    n = args.order if args.order is not None else int(open(args.input).read().split()[0])
    if n < 1:
        sys.exit("The order n has to be a positive integer.")

    cnf, nr_vars, triples = encode(n)
    write_dimacs(cnf, nr_vars, args.output)

    result = call_solver(args.output, args.solver, args.verb)
    if args.verb == 1:
        print(result.stdout, end="")

    if result.returncode == 10:
        print("SAT")
        print(decode(result, triples))
    elif result.returncode == 20:
        print("UNSAT")
    else:
        print("The solver did not give an answer (return code " + str(result.returncode) + ").")