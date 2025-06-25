"""
Task validation utilities for checking correctness of outputs.
"""
import re
import ast
from typing import Dict, List, Any, Tuple
from .task_definitions import Task


class TaskValidator:
    """Validates task outputs against criteria."""
    
    @staticmethod
    def validate_code_generation(task: Task, output: str) -> Tuple[bool, List[str], float]:
        """Validate code generation task output."""
        issues = []
        score = 0.0
        
        # Length check - adequate explanation/code
        if len(output) < 100:
            issues.append("Response too short - lacks detail")
            return False, issues, 10.0
        
        # Check if it's valid Python code (try to find code blocks)
        code_blocks = re.findall(r'```python\n(.*?)\n```', output, re.DOTALL)
        if not code_blocks:
            # Look for any potential code (class/def/import statements)
            if any(keyword in output for keyword in ['class ', 'def ', 'import ', 'from ']):
                score += 20  # Has code-like content
            else:
                issues.append("No identifiable Python code found")
        else:
            # Try to parse the first code block
            try:
                ast.parse(code_blocks[0])
                score += 30  # Valid syntax
            except SyntaxError as e:
                issues.append(f"Syntax error in code: {e}")
        
        # Conway's Game of Life specific validation
        if task.id == "code_001":
            # Check for key concepts (more lenient scoring)
            key_concepts = {
                'class': 25,  # Grid class
                'neighbor': 20,  # Neighbor counting
                'live': 15,   # Live cells
                'dead': 10,   # Dead cells  
                'generation': 15,  # Generation concept
                'display': 10,  # Display method
                'grid': 15    # Grid concept
            }
            
            for concept, points in key_concepts.items():
                if concept.lower() in output.lower():
                    score += points
            
            # Look for Game of Life rules (2, 3 neighbors) - more flexible
            rules_found = 0
            if '2' in output and ('live' in output.lower() or 'surviv' in output.lower()):
                rules_found += 1
            if '3' in output and ('live' in output.lower() or 'born' in output.lower()):
                rules_found += 1
            
            if rules_found >= 1:
                score += 10  # Partial credit for understanding rules
            if rules_found == 2:
                score += 5   # Bonus for both rules
            
            # Bonus for having method names that make sense
            method_indicators = ['def ', 'class ', 'init', 'display', 'count', 'advance']
            methods_found = sum(1 for indicator in method_indicators if indicator in output.lower())
            score += min(methods_found * 2, 10)  # Up to 10 bonus points
        
        return score >= 50, issues, min(score, 100)  # Lowered threshold from 60 to 50
    
    @staticmethod
    def validate_itinerary_planning(task: Task, output: str) -> Tuple[bool, List[str], float]:
        """Validate itinerary planning task output."""
        issues = []
        score = 0.0
        
        # Length check
        if len(output) < 200:
            issues.append("Response too short - lacks detail")
            return False, issues, 10.0
        
        # Structure checks
        if any(pattern in output.lower() for pattern in ['day 1', 'day 2', 'day one', 'day two']):
            score += 25
        else:
            issues.append("Missing structured daily format")
        
        # European tour specific validation (itin_001)
        if task.id == "itin_001":
            required_cities = ['london', 'paris', 'amsterdam', 'berlin']
            cities_found = sum(1 for city in required_cities if city in output.lower())
            score += cities_found * 15  # 15 points per city
            
            if cities_found < len(required_cities):
                missing = [city for city in required_cities if city not in output.lower()]
                issues.append(f"Missing cities: {missing}")
            
            # Check for budget awareness
            budget_indicators = ['$', 'cost', 'budget', 'price', 'euro', '€', 'pound', '£']
            if any(indicator in output.lower() for indicator in budget_indicators):
                score += 15
            
            # Transportation
            transport_words = ['train', 'flight', 'travel', 'transport', 'eurostar']
            if any(word in output.lower() for word in transport_words):
                score += 15
            
            # Activities
            activity_words = ['museum', 'tour', 'visit', 'see', 'activity', 'attraction']
            if any(word in output.lower() for word in activity_words):
                score += 15
        
        return score >= 50, issues, min(score, 100)  # Lowered threshold
    
    @staticmethod
    def validate_procedure_structuring(task: Task, output: str) -> Tuple[bool, List[str], float]:
        """Validate procedure structuring task output."""
        issues = []
        score = 0.0
        
        # Length check
        if len(output) < 150:
            issues.append("Response too short - lacks detail")
            return False, issues, 10.0
        
        # Step structure
        step_patterns = [
            r'step\s*\d+',
            r'\d+\.',
            r'[a-z]\)',
            r'first|second|third|next|then|finally'
        ]
        
        if any(re.search(pattern, output.lower()) for pattern in step_patterns):
            score += 30
        else:
            issues.append("Missing clear step structure")
        
        # Software deployment specific (proc_001)
        if task.id == "proc_001":
            required_elements = {
                'backup': 15,
                'test': 15, 
                'migration': 15,
                'rollback': 15,
                'notify': 10,
                'documentation': 10,
                'production': 10,
                'deploy': 10
            }
            
            for element, points in required_elements.items():
                if element in output.lower():
                    score += points
        
        # Check for responsibility assignment
        responsibility_words = ['responsible', 'assign', 'role', 'who', 'team', 'owner']
        if any(word in output.lower() for word in responsibility_words):
            score += 10
        
        return score >= 50, issues, min(score, 100)  # Lowered threshold
    
    @classmethod
    def validate_task_output(cls, task: Task, output: str) -> Tuple[bool, List[str], float]:
        """Validate task output based on task type."""
        if task.task_type == "code_generation":
            return cls.validate_code_generation(task, output)
        elif task.task_type == "itinerary_planning":
            return cls.validate_itinerary_planning(task, output)
        elif task.task_type == "procedure_structuring":
            return cls.validate_procedure_structuring(task, output)
        else:
            return False, ["Unknown task type"], 0.0
    
    @staticmethod
    def format_output_preview(output: str, max_length: int = 200) -> str:
        """Format output for preview display."""
        if len(output) <= max_length:
            return output
        
        # Try to find a natural break point
        truncated = output[:max_length]
        last_sentence = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        
        break_point = max(last_sentence, last_newline)
        if break_point > max_length * 0.7:  # If break point is reasonably close to end
            return output[:break_point + 1] + "..."
        else:
            return truncated + "..."
        if task.id == "itin_001":  # European tour
            required_cities = ["london", "paris", "amsterdam", "berlin"]
            cities_found = sum(1 for city in required_cities if city in output.lower())
            score += cities_found * 10
            
            if cities_found < len(required_cities):
                missing = [city for city in required_cities if city not in output.lower()]
                issues.append(f"Missing cities: {missing}")
        
        elif task.id == "itin_002":  # Business trip
            required_cities = ["new york", "philadelphia", "washington"]
            cities_found = sum(1 for city in required_cities if city in output.lower())
            score += cities_found * 10
            
            if "meeting" in output.lower():
                score += 15
            else:
                issues.append("Missing meeting accommodations")
        
        elif task.id == "itin_003":  # Family vacation
            if "disney" in output.lower():
                score += 10
            if "universal" in output.lower():
                score += 10
            if "allerg" in output.lower():
                score += 15
            else:
                issues.append("Didn't address food allergies")
        
        # Check for time specifications
        if re.search(r'\d+:\d+|morning|afternoon|evening', output.lower()):
            score += 15
        else:
            issues.append("Missing time specifications")
        
        return score >= 60, issues, score
    
    @staticmethod
    def validate_procedure_structuring(task: Task, output: str) -> Tuple[bool, List[str], float]:
        """Validate procedure structuring task output."""
        issues = []
        score = 0.0
        
        # Check for numbered or structured steps
        step_patterns = [
            r'step\s*\d+',
            r'\d+\.',
            r'[a-z]\)',
            r'first|second|third|next|then|finally'
        ]
        
        if any(re.search(pattern, output.lower()) for pattern in step_patterns):
            score += 25
        else:
            issues.append("Missing clear step structure")
        
        # Check for logical flow indicators
        flow_words = ["after", "before", "once", "when", "if", "then", "next"]
        flow_count = sum(1 for word in flow_words if word in output.lower())
        score += min(flow_count * 3, 15)
        
        # Check for responsibility assignment
        if any(keyword in output.lower() for keyword in ["responsible", "assign", "role", "who", "team"]):
            score += 15
        else:
            issues.append("Missing responsibility assignments")
        
        # Task-specific validation
        if task.id == "proc_001":  # Software deployment
            required_elements = ["backup", "test", "migration", "rollback", "notify"]
            elements_found = sum(1 for element in required_elements if element in output.lower())
            score += elements_found * 6
            
        elif task.id == "proc_002":  # Customer onboarding
            required_elements = ["sign up", "verify", "account", "training", "welcome"]
            elements_found = sum(1 for element in required_elements if element in output.lower())
            score += elements_found * 6
            
        elif task.id == "proc_003":  # Emergency response
            required_elements = ["identify", "escalate", "communicate", "document", "coordinate"]
            elements_found = sum(1 for element in required_elements if element in output.lower())
            score += elements_found * 6
        
        # Check for error handling or contingencies
        if any(keyword in output.lower() for keyword in ["if", "error", "fail", "problem", "backup", "alternative"]):
            score += 15
        else:
            issues.append("Missing error handling or contingencies")
        
        return score >= 60, issues, score
    
    @classmethod
    def validate_task_output(cls, task: Task, output: str) -> Tuple[bool, List[str], float]:
        """Validate task output based on task type."""
        if task.task_type == "code_generation":
            return cls.validate_code_generation(task, output)
        elif task.task_type == "itinerary_planning":
            return cls.validate_itinerary_planning(task, output)
        elif task.task_type == "procedure_structuring":
            return cls.validate_procedure_structuring(task, output)
        else:
            return False, ["Unknown task type"], 0.0
