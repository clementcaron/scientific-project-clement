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
        
        # Check if it's valid Python code
        try:
            ast.parse(output)
            score += 20  # Valid syntax
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
        
        # Check for required components based on task
        if task.id == "code_001":  # Conway's Game of Life
            if "class" in output.lower() and "grid" in output.lower():
                score += 15
            else:
                issues.append("Missing Grid class")
                
            if "neighbor" in output.lower():
                score += 15
            else:
                issues.append("Missing neighbor counting logic")
                
            if "display" in output.lower() or "print" in output.lower():
                score += 10
            else:
                issues.append("Missing display functionality")
                
            # Check for Game of Life rules
            rule_keywords = ["survive", "alive", "die", "2", "3"]
            rule_count = sum(1 for keyword in rule_keywords if keyword in output.lower())
            score += min(rule_count * 5, 25)
            
            if "test" in output.lower() or "example" in output.lower():
                score += 15
            else:
                issues.append("Missing test case")
        
        elif task.id == "code_002":  # BST
            if "class" in output.lower() and ("bst" in output.lower() or "tree" in output.lower()):
                score += 20
            else:
                issues.append("Missing BST class")
                
            required_methods = ["insert", "search", "delete", "traversal"]
            for method in required_methods:
                if method in output.lower():
                    score += 12.5
                else:
                    issues.append(f"Missing {method} method")
        
        elif task.id == "code_003":  # Text Analysis
            required_features = ["read", "count", "word", "sentence", "frequency"]
            for feature in required_features:
                if feature in output.lower():
                    score += 10
                else:
                    issues.append(f"Missing {feature} functionality")
        
        return score >= 60, issues, score
    
    @staticmethod
    def validate_itinerary_planning(task: Task, output: str) -> Tuple[bool, List[str], float]:
        """Validate itinerary planning task output."""
        issues = []
        score = 0.0
        
        # Check for structured format
        if any(keyword in output.lower() for keyword in ["day 1", "day 2", "schedule", "itinerary"]):
            score += 20
        else:
            issues.append("Missing structured daily format")
        
        # Check for cost information
        if any(keyword in output for keyword in ["$", "cost", "budget", "price"]):
            score += 15
        else:
            issues.append("Missing cost information")
        
        # Check for transportation details
        if any(keyword in output.lower() for keyword in ["train", "flight", "bus", "transport"]):
            score += 15
        else:
            issues.append("Missing transportation details")
        
        # Task-specific validation
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
