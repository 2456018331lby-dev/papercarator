#!/usr/bin/env python3
"""Sensitivity analysis for supported model types.

Usage:
    python scripts/sensitivity_analysis.py <model_type> [--param name=value ...]

Performs parameter sweep on key model parameters and outputs
a summary table showing how results change.
"""

import argparse
import json
import sys
import numpy as np


def run_queueing_sensitivity(arrival_rates, service_rates, servers_list):
    """Sweep M/M/c parameters."""
    import math
    results = []
    for lam in arrival_rates:
        for mu in service_rates:
            for c in servers_list:
                rho = lam / (c * mu)
                if rho >= 1:
                    results.append({"lambda": lam, "mu": mu, "c": c, "rho": rho, "Lq": float("inf"), "Wq": float("inf"), "stable": False})
                    continue
                a = lam / mu
                sum_terms = sum((a ** n) / math.factorial(n) for n in range(c))
                tail_term = (a ** c) / (math.factorial(c) * (1 - rho))
                p0 = 1.0 / (sum_terms + tail_term)
                lq = p0 * ((a ** c) * rho) / (math.factorial(c) * ((1 - rho) ** 2))
                wq = lq / lam
                results.append({"lambda": lam, "mu": mu, "c": c, "rho": round(rho, 4), "Lq": round(lq, 4), "Wq": round(wq, 4), "stable": True})
    return results


def run_optimization_sensitivity():
    """Sweep optimization objective landscape."""
    from scipy.optimize import minimize
    results = []
    for x0 in np.linspace(-2, 4, 7):
        for y0 in np.linspace(-2, 4, 7):
            obj = lambda v: v[0]**2 + v[1]**2 + v[0]*v[1] - 3*v[0] - 2*v[1]
            res = minimize(obj, [x0, y0], method='BFGS')
            results.append({
                "x0": round(x0, 2), "y0": round(y0, 2),
                "x_opt": round(float(res.x[0]), 4),
                "y_opt": round(float(res.x[1]), 4),
                "obj_val": round(float(res.fun), 6),
                "converged": bool(res.success),
            })
    return results


def main():
    parser = argparse.ArgumentParser(description="Sensitivity analysis")
    parser.add_argument("model_type", choices=["queueing", "optimization", "markov_chain"])
    parser.add_argument("--param", action="append", default=[])
    parser.add_argument("--output", "-o", help="Output JSON file")
    args = parser.parse_args()

    params = {}
    for p in args.param:
        k, v = p.split("=", 1)
        try:
            params[k] = float(v)
        except ValueError:
            params[k] = v

    if args.model_type == "queueing":
        results = run_queueing_sensitivity(
            arrival_rates=[3.0, 4.0, 4.5, 5.0, 6.0],
            service_rates=[2.5, 3.0, 3.2, 4.0],
            servers_list=[1, 2, 3, 4],
        )
    elif args.model_type == "optimization":
        results = run_optimization_sensitivity()
    else:
        print(f"Sensitivity analysis for {args.model_type} not yet implemented")
        sys.exit(1)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(results[:10], indent=2, ensure_ascii=False))
        if len(results) > 10:
            print(f"... ({len(results)} total rows)")


if __name__ == "__main__":
    main()
