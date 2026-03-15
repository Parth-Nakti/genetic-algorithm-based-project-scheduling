import matplotlib.pyplot as plt

def plot_gantt(schedule):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    finish_times = {}

    for task in schedule.order:
       
        start = 0
        if task["dependencies"]:
            start = max([finish_times.get(d, 0) for d in task["dependencies"]])
        
        duration = task["duration"]
        finish = start + duration
        finish_times[task["id"]] = finish
        

        ax.barh(task["name"], duration, left=start, color='skyblue', edgecolor='black')
        

        ax.text(start + duration/2, task["name"], f'{duration}d', 
                va='center', ha='center', color='black', fontweight='bold')

    ax.set_xlabel("Timeline (Days)")
    ax.set_title("Optimized Project Gantt Chart (Logically Valid)")
    ax.invert_yaxis()  
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()