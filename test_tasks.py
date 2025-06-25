#!/usr/bin/env python3
"""
Quick test of the task definitions
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tasks import TaskGenerator
    
    # Test task loading
    tg = TaskGenerator()
    all_tasks = tg.get_all_tasks()
    
    print("✅ Task loading test:")
    total_tasks = 0
    for task_type, tasks in all_tasks.items():
        print(f"  {task_type}: {len(tasks)} tasks")
        total_tasks += len(tasks)
        for task in tasks:
            print(f"    - {task.id}: {task.title}")
    
    print(f"\nTotal tasks: {total_tasks}")
    
    # Test quick experiment calculation
    frameworks = ['react', 'cot', 'tot']
    print(f"\n🧠 Frameworks: {len(frameworks)}")
    print(f"📋 Quick test (code_001 only): {len(frameworks)} × 1 task × 1 run = {len(frameworks) * 1 * 1} experiments")
    print(f"📋 Full test (all tasks): {len(frameworks)} × {total_tasks} tasks × 3 runs = {len(frameworks) * total_tasks * 3} experiments")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
