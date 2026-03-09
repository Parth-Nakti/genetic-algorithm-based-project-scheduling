import sys
import os
from modules.input_processing import load_project_data
from modules.scheduler import run_ga
from visualization.gantt_charts import plot_gantt
from modules.fitness import check_dependency_violations

def main():
    # 1. Configuration (Set defaults or use Command Line Arguments)
    # Usage: python main.py data/sample_project.json 15 5000
    file_path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_project.json"
    target_deadline = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    max_budget = int(sys.argv[3]) if len(sys.argv) > 3 else 6000

    # 2. Safety check for file existence
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    print(f"--- Starting Optimization for {os.path.basename(file_path)} ---")
    print(f"Constraints: Deadline = {target_deadline}d | Budget = ${max_budget}")

    # 3. Run the Genetic Algorithm
    best_schedule = run_ga(tasks=load_project_data(file_path), deadline=target_deadline)

    # 4. Final Validation Logic
    violations = check_dependency_violations(best_schedule)
    is_over_budget = best_schedule.cost > max_budget
    is_over_deadline = best_schedule.duration > target_deadline

    print("\n" + "="*55)

    # Unified Error Handling
    if violations > 0 or is_over_deadline or is_over_budget:
        print("❌ NOT POSSIBLE: No valid schedule meets your constraints.")
        
        if violations > 0:
            print(f"  - Logic Error: {violations} dependency rules broken.")
        if is_over_deadline:
            print(f"  - Time Error: Duration ({best_schedule.duration}d) exceeds deadline.")
        if is_over_budget:
            print(f"  - Financial Error: Cost (${best_schedule.cost}) exceeds budget (${max_budget}).")
        
        print("\nSUGGESTION: Increase resources, extend deadline, or reduce scope.")
    else:
        # Success State
        print("✅ SUCCESS: Optimal Schedule Found")
        print(f"Final Duration: {best_schedule.duration} days")
        print(f"Final Cost    : ${best_schedule.cost}")
        print(f"Final Risk    : {best_schedule.risk:.2f}")
        print("-" * 55)
        
        for i, t in enumerate(best_schedule.order, 1):
            print(f"{i}. {t['name']:<25} | Duration: {t['duration']}d | Cost: ${t['cost']}")
        
        plot_gantt(best_schedule)

    print("="*55 + "\n")

if __name__ == "__main__":
    main()