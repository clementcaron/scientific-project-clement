#!/usr/bin/env python3

import sys
sys.path.append('.')

from tasks import TaskGenerator

print("=== TaskGenerator Test ===")
gen = TaskGenerator()
all_tasks = gen.get_all_tasks()

print("Available tasks:")
for task_type, tasks in all_tasks.items():
    print(f"  {task_type}:")
    for task in tasks:
        print(f"    - {task.id}: {task.title}")

print("\nSpecific tasks we want:", ['code_001', 'itin_001', 'proc_001'])

# Test filtering
quick_tasks = ["code_001", "itin_001", "proc_001"]
print("\nFiltered tasks:")
for task_type, tasks in all_tasks.items():
    filtered = [t for t in tasks if t.id in quick_tasks]
    if filtered:
        print(f"  {task_type}: {[t.id for t in filtered]}")
