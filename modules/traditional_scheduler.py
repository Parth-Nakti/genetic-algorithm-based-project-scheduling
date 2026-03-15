import numpy as np

def run_cpm(tasks):
    """Calculates Earliest/Latest starts/finishes and identifies Critical Path."""
    id_to_task = {t['id']: t for t in tasks}
    for t in tasks:
        t['es'] = t['ef'] = t['ls'] = t['lf'] = 0

    # Forward Pass
    for t in tasks:
        if not t['dependencies']:
            t['es'] = 0
        else:
            t['es'] = max(id_to_task[dep]['ef'] for dep in t['dependencies'])
        t['ef'] = t['es'] + t['duration']

    project_duration = max(t['ef'] for t in tasks)

    # Backward Pass
    for t in reversed(tasks):
        successors = [s for s in tasks if t['id'] in s['dependencies']]
        if not successors:
            t['lf'] = project_duration
        else:
            t['lf'] = min(s['ls'] for s in successors)
        t['ls'] = t['lf'] - t['duration']

    # Identify Critical Path Tasks
    critical_tasks = [t for t in tasks if (t['lf'] - t['es'] - t['duration']) == 0]
    critical_path_names = [t['name'] for t in critical_tasks]

    return {
        "project_duration": project_duration,
        "critical_path": critical_path_names,
        "critical_tasks": critical_tasks, # New: returning full objects for cost/risk math
        "schedule": tasks
    }

def run_pert(tasks):
    """Calculates PERT duration while preserving cost and risk data."""
    pert_tasks = []
    for t in tasks:
        o = t.get('o', t['duration'] * 0.8)
        m = t.get('m', t['duration'])
        p = t.get('p', t['duration'] * 1.2)
        expected_time = (o + (4 * m) + p) / 6
        
        new_task = t.copy()
        new_task['duration'] = round(expected_time, 2)
        # Ensure cost and risk are explicitly kept
        new_task['cost'] = t.get('cost', 0)
        new_task['risk'] = t.get('risk', 0)
        pert_tasks.append(new_task)

    return run_cpm(pert_tasks)