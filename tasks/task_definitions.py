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
- Make it runnable as a script that shows several generations""",
                expected_output_type="python_code",
                validation_criteria=[
                    "Contains a Grid class",
                    "Implements the four rules correctly",
                    "Has neighbor counting logic",
                    "Includes display functionality",
                    "Provides a test case"
                ]
            ),
            
            Task(
                id="code_002", 
                task_type="code_generation",
                title="Binary Search Tree Implementation",
                prompt="""Create a Binary Search Tree (BST) implementation in Python. Requirements:
- Implement a Node class and BST class
- Include methods: insert, search, delete, inorder_traversal
- Handle edge cases (empty tree, single node, etc.)
- Implement tree balancing check method
- Add a method to find the minimum and maximum values
- Include comprehensive test cases showing insertion, deletion, and traversal
- Make the code well-documented with docstrings""",
                expected_output_type="python_code", 
                validation_criteria=[
                    "Contains Node and BST classes",
                    "Implements all required methods",
                    "Handles edge cases",
                    "Includes balancing check",
                    "Has min/max finding methods",
                    "Contains test cases"
                ]
            ),
            
            Task(
                id="code_003",
                task_type="code_generation", 
                title="Text Analysis Tool",
                prompt="""Build a text analysis tool in Python that processes a text file. Requirements:
- Read text from a file or string input
- Count: words, sentences, paragraphs, characters
- Find: most common words, average word length, reading time estimate
- Implement sentiment analysis (simple positive/negative word counting)
- Create word frequency distribution
- Generate a summary report in both text and JSON formats
- Handle different file encodings and basic error cases
- Include a command-line interface""",
                expected_output_type="python_code",
                validation_criteria=[
                    "Reads text input properly",
                    "Implements all counting features",
                    "Has word frequency analysis", 
                    "Includes sentiment analysis",
                    "Outputs in multiple formats",
                    "Has CLI interface"
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
            ),
            
            Task(
                id="itin_002",
                task_type="itinerary_planning", 
                title="Business Trip Optimization",
                prompt="""Optimize a business trip itinerary. Constraints:
- Duration: 3 days
- Cities: New York, Philadelphia, Washington DC
- Meetings scheduled: NYC (Day 1, 2pm), Philadelphia (Day 2, 10am), DC (Day 3, 11am)
- Requirements: Minimize travel time, stay near meeting locations
- Budget: $1500 for accommodation and transport
- Need reliable internet for virtual meetings
- Prefer train travel when possible
- Include time for one business dinner and one cultural activity""",
                expected_output_type="structured_itinerary",
                validation_criteria=[
                    "Accommodates all meetings",
                    "Minimizes travel time",
                    "Stays within budget", 
                    "Includes business and cultural activities",
                    "Shows transportation logistics"
                ]
            ),
            
            Task(
                id="itin_003",
                task_type="itinerary_planning",
                title="Family Vacation Planning", 
                prompt="""Plan a family vacation for 2 adults and 2 children (ages 8, 12). Constraints:
- Destination: Orlando, Florida
- Duration: 5 days
- Budget: $3000 total
- Must include: Disney World (2 days), Universal Studios (1 day)
- Requirements: Family-friendly restaurants, nearby accommodation
- Special needs: One child has food allergies (nuts)
- Transportation: Flying from Chicago
- Want to include one non-theme park activity
- Create detailed daily plans with timing and alternatives""",
                expected_output_type="structured_itinerary",
                validation_criteria=[
                    "Accommodates family needs",
                    "Includes all required attractions",
                    "Considers food allergies",
                    "Stays within budget",
                    "Has detailed daily schedules"
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
            ),
            
            Task(
                id="proc_002",
                task_type="procedure_structuring",
                title="Customer Onboarding Process",
                prompt="""Convert this unclear onboarding description into a structured procedure:
"New customers need to sign up, verify their info, get set up with accounts, learn how to use the system, and start their subscription. Someone should welcome them and make sure they understand everything. We also need to collect their preferences and set up their profile properly."

Create a comprehensive onboarding procedure with clear steps, timelines, and responsibilities.""",
                expected_output_type="structured_procedure", 
                validation_criteria=[
                    "Logical step sequence",
                    "Clear timelines",
                    "Defined responsibilities",
                    "Covers all mentioned elements",
                    "Includes quality checkpoints"
                ]
            ),
            
            Task(
                id="proc_003", 
                task_type="procedure_structuring",
                title="Emergency Response Protocol",
                prompt="""Reorganize this emergency response description into a clear protocol:
"When there's a system outage, everyone needs to know what to do. First figure out what's wrong, then fix it, and tell people about it. Make sure to keep track of what happened and write it down later. Someone should be in charge and coordinate everything. Don't panic and follow the escalation rules."

Transform this into a detailed emergency response protocol with specific roles, actions, and communication procedures.""",
                expected_output_type="structured_procedure",
                validation_criteria=[
                    "Clear command structure",
                    "Specific action steps", 
                    "Communication protocols",
                    "Documentation requirements",
                    "Escalation procedures"
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
