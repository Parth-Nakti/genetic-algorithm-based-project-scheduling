import matplotlib.pyplot as plt

def plot_gantt(schedule):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # We need to recalculate start and finish times for the visualization
    finish_times = {}
    
    # Track task bars for the legend or coloring
    for task in schedule.order:
        # Start time is the maximum of all dependency finish times
        # If no dependencies, start at 0
        start = 0
        if task["dependencies"]:
            start = max([finish_times.get(d, 0) for d in task["dependencies"]])
        
        duration = task["duration"]
        finish = start + duration
        finish_times[task["id"]] = finish
        
        # Draw the bar
        ax.barh(task["name"], duration, left=start, color='skyblue', edgecolor='black')
        
        # Add duration text on the bar
        ax.text(start + duration/2, task["name"], f'{duration}d', 
                va='center', ha='center', color='black', fontweight='bold')

    ax.set_xlabel("Timeline (Days)")
    ax.set_title("Optimized Project Gantt Chart (Logically Valid)")
    ax.invert_yaxis()  # Put the first task at the top
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()