import json

def load_project_data(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data["tasks"]


def validate_dependencies(tasks):

    task_ids = [t["id"] for t in tasks]

    for t in tasks:
        for d in t["dependencies"]:
            if d not in task_ids:
                raise Exception("Invalid dependency detected")