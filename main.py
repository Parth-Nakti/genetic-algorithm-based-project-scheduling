import sys
import os
import numpy as np
from modules.input_processing import load_project_data
from modules.scheduler import run_ga
from modules.traditional_scheduler import run_cpm, run_pert
from visualization.gantt_charts import plot_gantt
from visualization.graphs import plot_comparison_chart
from modules.fitness import check_dependency_violations

def main():

    file_path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_project.json"
    target_deadline = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    max_budget = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
    max_risk = 4.0 

    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    tasks = load_project_data(file_path)
    print(f"--- Starting SEPM Analysis for {os.path.basename(file_path)} ---")

    best_ga_schedule = run_ga(tasks=tasks, deadline=target_deadline)
    cpm_result = run_cpm(tasks)
    pert_result = run_pert(tasks)

    violations = check_dependency_violations(best_ga_schedule)
    is_over_budget = best_ga_schedule.cost > max_budget
    is_over_deadline = best_ga_schedule.duration > target_deadline
    is_high_risk = best_ga_schedule.risk > max_risk

    print("\n" + "="*65)
    if violations > 0 or is_over_deadline or is_over_budget or is_high_risk:
        print("❌ GA STATUS: INFEASIBLE (Constraints Violated)")
    else:
        print("✅ GA STATUS: OPTIMIZED SUCCESS")
        print(f"GA Duration: {best_ga_schedule.duration}d | Cost: ₹{best_ga_schedule.cost} | Risk: {best_ga_schedule.risk:.2f}")

    print("-" * 65)
    print(f"📊 TRADITIONAL BASELINES:")
    print(f"CPM Duration: {cpm_result['project_duration']} days")
    print(f"PERT Expected: {pert_result['project_duration']:.2f} days")
    print(f"Critical Path: {' -> '.join(cpm_result['critical_path'])}")
    print("="*65 + "\n")

    plot_gantt(best_ga_schedule)
    plot_comparison_chart(best_ga_schedule, cpm_result, pert_result)

if __name__ == "__main__":
    main()