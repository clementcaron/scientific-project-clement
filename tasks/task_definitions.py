"""
Task definitions for the three task types: Code Generation, Itinerary Planning, and Procedure Structuring.
"""
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class Task:
    """A single task instance."""
    id: str
    task_type: str
    title: str
    prompt: str
    expected_output_type: str
    validation_criteria: List[str]


class TaskGenerator:
    """Generates tasks for different categories."""
    
    @staticmethod
    def get_code_generation_tasks() -> List[Task]:
        """Generate code generation tasks."""
        return [
            Task(
                id="code_001",
                task_type="code_generation",
                title="Conway's Game of Life",
                prompt="""Implement Conway's Game of Life in Python. Requirements:
- Create a Grid class that can initialize with a given size
- Implement the four rules of Conway's Game of Life:
  1. Any live cell with 2-3 live neighbors survives
  2. Any dead cell with exactly 3 live neighbors becomes alive
  3. All other live cells die, all other dead cells stay dead
- Include methods to: display the grid, advance one generation, count live neighbors
- Provide a simple test case with a known pattern (e.g., blinker or glider)
- Make it runnable as a script that shows several generations

IMPORTANT: Your final answer should be a complete, runnable main.py file that can be copied and pasted directly into a file and executed. Include all necessary code in a single file with proper if __name__ == "__main__": structure.""",
                expected_output_type="complete_python_file",
                validation_criteria=[
                    "Contains a Grid class",
                    "Implements the four rules correctly", 
                    "Has neighbor counting logic",
                    "Includes display functionality",
                    "Provides a test case",
                    "Is a complete runnable file"
                ]
            )
        ]
    
    @staticmethod
    def get_itinerary_planning_tasks() -> List[Task]:
        """Generate itinerary planning tasks."""
        return [
            Task(
                id="itin_001",
                task_type="itinerary_planning",
                title="European City Tour",
                prompt="""Plan a 7-day European tour itinerary. Constraints:
- Budget: $2000 USD total
- Start and end in London
- Must visit: Paris, Amsterdam, Berlin
- Interests: Museums, historical sites, local cuisine
- Transportation: Train preferred, flights if necessary
- Accommodation: Mid-range hotels/hostels
- Travel dates: flexible, summer preferred
- Create day-by-day schedule with specific activities, costs, and travel times
- Include backup options for bad weather""",
                expected_output_type="structured_itinerary",
                validation_criteria=[
                    "Covers all 7 days",
                    "Visits all required cities",
                    "Stays within budget",
                    "Includes specific activities",
                    "Shows transportation details",
                    "Has cost breakdown"
                ]
            )
        ]
    
    @staticmethod 
    def get_procedure_structuring_tasks() -> List[Task]:
        """Generate procedure structuring tasks."""
        return [
            Task(
                id="proc_001",
                task_type="procedure_structuring",
                title="Software Deployment Process",
                prompt="""Restructure this vague deployment instruction into clear steps:
"Deploy the new version to production. Make sure to backup everything first and test it. Don't forget about the database migration and updating the configs. If something breaks, roll back. Also notify the team when done and update documentation."

Transform this into a detailed, step-by-step procedure that could be followed by any team member.""",
                expected_output_type="structured_procedure",
                validation_criteria=[
                    "Clear sequential steps",
                    "Includes all mentioned tasks",
                    "Has verification points",
                    "Covers error handling",
                    "Specifies responsibilities"
                ]
            )
        ]
    
    @classmethod
    def get_all_tasks(cls) -> Dict[str, List[Task]]:
        """Get all tasks organized by type."""
        return {
            "code_generation": cls.get_code_generation_tasks(),
            "itinerary_planning": cls.get_itinerary_planning_tasks(), 
            "procedure_structuring": cls.get_procedure_structuring_tasks()
        }
