import csv
import subprocess
import time
from argparse import ArgumentParser

from steiner_sat import encode, write_dimacs, call_solver, decode, check_solution

def run_one(n, encoding, symmetry, solver, timeout):
    start = time.perf_counter()
    cnf, nr_vars, triples = encode(n, encoding, symmetry)
    nr_clauses = len(cnf)
    write_dimacs(cnf, nr_vars, "experiment.cnf")
    del cnf
    encode_time = time.perf_counter() - start

    start = time.perf_counter()
    try:
        result = call_solver("experiment.cnf", solver, 0, timeout)
    except subprocess.TimeoutExpired:
        return [n, encoding, symmetry, nr_vars, nr_clauses, "TIMEOUT", round(encode_time, 2), "> " + str(timeout)]
    solve_time = time.perf_counter() - start

    if result.returncode == 10:
        answer = "SAT"
        if not check_solution(n, decode(result, triples)):
            answer = "WRONG"
    elif result.returncode == 20:
        answer = "UNSAT"
    else:
        answer = "ERROR"
    return [n, encoding, symmetry, nr_vars, nr_clauses, answer, round(encode_time, 2), round(solve_time, 2)]

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-s", "--solver", default="./glucose-simp", type=str, help="The SAT solver to be used.")
    parser.add_argument("-t", "--timeout", default=120, type=int, help="Time limit for one solver run (seconds).")
    parser.add_argument("-x", "--experiment", default="sat", choices=["sat", "unsat", "encodings"],
                        help="Which experiment to run.")
    parser.add_argument("-n", "--orders", type=int, nargs="+", help="Orders to test (overrides the defaults).")
    parser.add_argument("-c", "--csv", default="results.csv", type=str, help="Where to save the results.")
    args = parser.parse_args()

    if args.experiment == "sat":
        settings = [("pairwise", False)]
        orders = [7, 9, 13, 15, 19, 21, 25, 27, 31, 33, 37, 39, 43, 45, 49, 51, 55, 57, 61, 63, 67, 69, 73, 75, 79, 81, 85]
    elif args.experiment == "unsat":
        settings = [("pairwise", False), ("pairwise", True)]
        orders = [4, 5, 6, 8, 10, 11, 12, 14, 16, 17, 18, 20, 22, 23]
    else:
        settings = [("pairwise", False), ("pairwise", True), ("sequential", False), ("sequential", True)]
        orders = [19, 31, 43, 55, 61, 67]
    if args.orders:
        orders = args.orders

    header = ["n", "encoding", "symmetry", "variables", "clauses", "result", "encoding time (s)", "solver time (s)"]
    print("| " + " | ".join(header) + " |")
    print("|" + "---:|" * len(header))

    rows = []
    for n in orders:
        for encoding, symmetry in settings:
            row = run_one(n, encoding, symmetry, args.solver, args.timeout)
            rows.append(row)
            print("| " + " | ".join(str(x) for x in row) + " |", flush=True)

    with open(args.csv, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)