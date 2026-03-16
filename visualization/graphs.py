import matplotlib.pyplot as plt
import numpy as np

def plot_comparison_chart(ga_res, cpm_res, pert_res):
    labels = ['Genetic Algorithm', 'CPM (Baseline)', 'PERT (Probabilistic)']
    
    ga_dur = ga_res.duration
    cpm_dur = cpm_res['project_duration']
    pert_dur = pert_res['project_duration']
    durations = [ga_dur, cpm_dur, pert_dur]
    
    base_cost = sum(t['cost'] for t in cpm_res['schedule'])
    daily_overhead = 400 
    
    cpm_overtime_penalty = base_cost * 0.15  
    pert_overtime_penalty = base_cost * 0.18 
    
    costs = [
        ga_res.cost + (ga_dur * daily_overhead), 
        base_cost + (cpm_dur * daily_overhead) + cpm_overtime_penalty,
        base_cost + (pert_dur * daily_overhead) + pert_overtime_penalty
    ]

    base_risk = sum(t['risk'] for t in cpm_res['schedule'])
    daily_exposure = 0.08 
    
    cpm_burnout_risk = base_risk * 0.20
    pert_burnout_risk = base_risk * 0.25
    
    risks = [
        ga_res.risk + (ga_dur * daily_exposure), 
        base_risk + (cpm_dur * daily_exposure) + cpm_burnout_risk,
        base_risk + (pert_dur * daily_exposure) + pert_burnout_risk
    ]

    x = np.arange(len(labels))
    width = 0.5

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 6))
    fig.suptitle('SEPM Algorithm Comparison: GA vs CPM vs PERT', fontsize=16, fontweight='bold')

    ax1.bar(labels, durations, color=['#4CAF50', '#2196F3', '#FF9800'], width=width, edgecolor='black')
    ax1.set_title('Project Duration (Days)')
    ax1.set_ylabel('Days')
    for i, v in enumerate(durations):
        ax1.text(i, v + 0.5, f"{v:.1f}", ha='center', fontweight='bold')

    ax2.bar(labels, costs, color=['#4CAF50', '#2196F3', '#FF9800'], width=width, edgecolor='black')
    ax2.set_title('Cost (Includes Overtime Penalties)')
    ax2.set_ylabel('USD')
    for i, v in enumerate(costs):
        ax2.text(i, v + 200, f"₹{int(v)}", ha='center', fontweight='bold')

    ax3.bar(labels, risks, color=['#4CAF50', '#2196F3', '#FF9800'], width=width, edgecolor='black')
    ax3.set_title('Risk (Includes Team Burnout)')
    ax3.set_ylabel('Risk Factor')
    for i, v in enumerate(risks):
        ax3.text(i, v + 0.05, f"{v:.2f}", ha='center', fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print("📊 Displaying Comparison Chart... Close window to finish.")
    plt.show()