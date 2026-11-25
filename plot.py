import csv
import matplotlib.pyplot as plt

solved_n, solved_t, timeout_n = [], [], []
with open("results/sat.csv") as file:
    for row in csv.DictReader(file):
        if row["result"] == "TIMEOUT":
            timeout_n.append(int(row["n"]))
        elif float(row["solver time (s)"]) > 0:
            solved_n.append(int(row["n"]))
            solved_t.append(float(row["solver time (s)"]))

plt.figure(figsize=(7, 4))
plt.plot(solved_n, solved_t, "o-", label="solved")
plt.plot(timeout_n, [120] * len(timeout_n), "rx", markersize=9, label="timeout (120 s)")
plt.axhline(10, color="gray", linestyle="--", linewidth=1)
plt.yscale("log")
plt.xlabel("order n")
plt.ylabel("Glucose time (s)")
plt.title("Satisfiable orders, pairwise encoding")
plt.legend()
plt.grid(True, which="both", alpha=0.3)
plt.tight_layout()
plt.savefig("plot.png", dpi=120)