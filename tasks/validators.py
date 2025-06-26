"""
Task validation utilities for checking correctness of outputs using reference-based scoring.
"""
import re
import ast
import os
from typing import Dict, List, Any, Tuple, Set
from .task_definitions import Task


class ReferenceBasedValidator:
    """Validates task outputs against gold standard references with discriminative scoring."""
    
    def __init__(self):
        """Initialize validator and load reference outputs."""
        self._load_references()
    
    def _load_references(self):
        """Load the gold standard reference outputs."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Load reference code
        try:
            with open(os.path.join(base_dir, 'best_code.py'), 'r') as f:
                self.reference_code = f.read()
        except FileNotFoundError:
            self.reference_code = ""
            
        # Load reference itinerary
        try:
            with open(os.path.join(base_dir, 'best_itinerary.md'), 'r') as f:
                self.reference_itinerary = f.read()
        except FileNotFoundError:
            self.reference_itinerary = ""
            
        # Load reference procedure
        try:
            with open(os.path.join(base_dir, 'best_procedure.md'), 'r') as f:
                self.reference_procedure = f.read()
        except FileNotFoundError:
            self.reference_procedure = ""
    
    def _extract_code_features(self, code_text: str) -> Dict[str, Any]:
        """Extract structural and semantic features from code."""
        features = {
            'has_main_guard': '__name__ == "__main__"' in code_text,
            'has_grid_class': False,
            'has_step_method': False,
            'has_neighbor_counting': False,
            'has_proper_rules': False,
            'has_display_method': False,
            'has_command_line_args': False,
            'has_type_hints': False,
            'has_docstrings': False,
            'syntactically_valid': False,
            'class_count': 0,
            'method_count': 0,
            'line_count': len(code_text.split('\n'))
        }
        
        # Check syntax validity
        try:
            ast.parse(code_text)
            features['syntactically_valid'] = True
        except SyntaxError:
            pass
        
        # Analyze AST for deeper features
        try:
            tree = ast.parse(code_text)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    features['class_count'] += 1
                    if 'grid' in node.name.lower():
                        features['has_grid_class'] = True
                        # Check methods in Grid class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                features['method_count'] += 1
                                if 'step' in item.name.lower() or 'advance' in item.name.lower():
                                    features['has_step_method'] = True
                                if 'neighbor' in item.name.lower() or 'count' in item.name.lower():
                                    features['has_neighbor_counting'] = True
                                if 'display' in item.name.lower() or '__str__' in item.name:
                                    features['has_display_method'] = True
                elif isinstance(node, ast.FunctionDef):
                    features['method_count'] += 1
        except:
            pass
        
        # Check for Game of Life rules (2,3 survival, 3 birth)
        if re.search(r'[^0-9]2[^0-9].*3[^0-9]|[^0-9]3[^0-9].*2[^0-9]', code_text):
            if 'neighbor' in code_text.lower() and ('live' in code_text.lower() or 'alive' in code_text.lower()):
                features['has_proper_rules'] = True
        
        # Check for advanced features
        features['has_command_line_args'] = 'argparse' in code_text or 'ArgumentParser' in code_text
        features['has_type_hints'] = bool(re.search(r':\s*\w+\s*=|:\s*\w+\s*->', code_text))
        features['has_docstrings'] = '"""' in code_text or "'''" in code_text
        
        return features
    
    def _score_code_against_reference(self, output: str) -> Tuple[float, List[str]]:
        """Score code output against the reference implementation."""
        issues = []
        scores = {}
        
        # Extract code from output (handle both raw code and markdown code blocks)
        code_blocks = re.findall(r'```python\n(.*?)\n```', output, re.DOTALL)
        if code_blocks:
            code_text = code_blocks[0]
        else:
            # Try to extract the main code part
            code_text = output
        
        features = self._extract_code_features(code_text)
        ref_features = self._extract_code_features(self.reference_code)
        
        # Core functionality scoring (60 points total)
        scores['syntax'] = 15 if features['syntactically_valid'] else 0
        if not features['syntactically_valid']:
            issues.append("Code contains syntax errors")
        
        scores['grid_class'] = 15 if features['has_grid_class'] else 0
        if not features['has_grid_class']:
            issues.append("Missing Grid class implementation")
        
        scores['game_rules'] = 15 if features['has_proper_rules'] else 0
        if not features['has_proper_rules']:
            issues.append("Game of Life rules not properly implemented")
        
        scores['neighbor_logic'] = 15 if features['has_neighbor_counting'] else 0
        if not features['has_neighbor_counting']:
            issues.append("Missing neighbor counting functionality")
        
        # Structure and completeness (25 points total)
        scores['main_guard'] = 10 if features['has_main_guard'] else 0
        if not features['has_main_guard']:
            issues.append("Missing if __name__ == '__main__' guard")
        
        scores['step_method'] = 10 if features['has_step_method'] else 0
        if not features['has_step_method']:
            issues.append("Missing step/advance method")
        
        scores['display'] = 5 if features['has_display_method'] else 0
        if not features['has_display_method']:
            issues.append("Missing display functionality")
        
        # Code quality and sophistication (15 points total)
        scores['command_args'] = 5 if features['has_command_line_args'] else 0
        scores['type_hints'] = 5 if features['has_type_hints'] else 0  
        scores['documentation'] = 5 if features['has_docstrings'] else 0
        
        # Penalty for being too short (realistic implementation should be substantial)
        if features['line_count'] < 50:
            scores['length_penalty'] = -10
            issues.append("Implementation too brief for a complete solution")
        else:
            scores['length_penalty'] = 0
        
        total_score = sum(scores.values())
        return max(0, min(100, total_score)), issues
    
    
    def _extract_itinerary_features(self, text: str) -> Dict[str, Any]:
        """Extract structural and content features from itinerary."""
        features = {
            'has_daily_structure': False,
            'covers_all_cities': False,
            'has_budget_breakdown': False,
            'has_transportation': False,
            'has_specific_times': False,
            'has_activities': False,
            'has_backup_plans': False,
            'has_cost_details': False,
            'cities_mentioned': set(),
            'day_count': 0,
            'word_count': len(text.split()),
            'has_table_format': False,
            'detail_level': 'low'
        }
        
        text_lower = text.lower()
        
        # Check for daily structure
        day_patterns = [r'day\s*\d+', r'day\s+one|two|three|four|five|six|seven', 
                       r'\d+\s*[–-]\s*\w+', r'sunday|monday|tuesday|wednesday|thursday|friday|saturday']
        features['day_count'] = sum(len(re.findall(pattern, text_lower)) for pattern in day_patterns)
        features['has_daily_structure'] = features['day_count'] >= 6
        
        # Check cities
        required_cities = ['london', 'paris', 'amsterdam', 'berlin']
        for city in required_cities:
            if city in text_lower:
                features['cities_mentioned'].add(city)
        features['covers_all_cities'] = len(features['cities_mentioned']) == len(required_cities)
        
        # Transportation indicators
        transport_terms = ['train', 'eurostar', 'thalys', 'ice', 'flight', 'rail', 'plane']
        features['has_transportation'] = any(term in text_lower for term in transport_terms)
        
        # Time specifications
        time_patterns = [r'\d{1,2}:\d{2}', r'\d{1,2}\s*am|\d{1,2}\s*pm', 
                        r'morning|afternoon|evening|night']
        features['has_specific_times'] = any(re.search(pattern, text_lower) for pattern in time_patterns)
        
        # Budget and cost tracking
        budget_indicators = ['$', '€', '£', 'cost', 'budget', 'price', 'total', 'usd', 'euro']
        features['has_budget_breakdown'] = any(indicator in text_lower for indicator in budget_indicators)
        cost_counts = sum(text_lower.count(indicator) for indicator in ['$', '€', '£'])
        features['has_cost_details'] = cost_counts >= 10
        
        # Activities and attractions
        activity_terms = ['museum', 'tour', 'visit', 'see', 'explore', 'walk', 'gallery', 'cathedral', 'palace']
        features['has_activities'] = sum(text_lower.count(term) for term in activity_terms) >= 8
        
        # Backup plans
        backup_indicators = ['backup', 'fallback', 'alternative', 'rain', 'weather', 'indoor']
        features['has_backup_plans'] = any(indicator in text_lower for indicator in backup_indicators)
        
        # Format sophistication
        features['has_table_format'] = '|' in text and ('---' in text or '====' in text)
        
        # Detail level assessment
        if features['word_count'] > 800 and features['has_table_format']:
            features['detail_level'] = 'high'
        elif features['word_count'] > 400:
            features['detail_level'] = 'medium'
        
        return features
    
    def _score_itinerary_against_reference(self, output: str) -> Tuple[float, List[str]]:
        """Score itinerary output against the reference implementation."""
        issues = []
        scores = {}
        
        features = self._extract_itinerary_features(output)
        ref_features = self._extract_itinerary_features(self.reference_itinerary)
        
        # Core requirements (50 points total)
        scores['city_coverage'] = 15 if features['covers_all_cities'] else len(features['cities_mentioned']) * 3
        if not features['covers_all_cities']:
            missing = {'london', 'paris', 'amsterdam', 'berlin'} - features['cities_mentioned']
            issues.append(f"Missing required cities: {list(missing)}")
        
        scores['daily_structure'] = 15 if features['has_daily_structure'] else min(features['day_count'] * 2, 10)
        if not features['has_daily_structure']:
            issues.append("Missing proper 7-day structure")
        
        scores['budget_compliance'] = 10 if features['has_budget_breakdown'] else 0
        if not features['has_budget_breakdown']:
            issues.append("Missing budget breakdown or cost information")
        
        scores['transportation'] = 10 if features['has_transportation'] else 0
        if not features['has_transportation']:
            issues.append("Missing transportation details")
        
        # Detail and sophistication (30 points total)
        scores['time_specificity'] = 10 if features['has_specific_times'] else 0
        if not features['has_specific_times']:
            issues.append("Missing specific times and scheduling")
        
        scores['activities'] = 10 if features['has_activities'] else 0
        if not features['has_activities']:
            issues.append("Insufficient activity details")
        
        scores['cost_detail'] = 10 if features['has_cost_details'] else 0
        if not features['has_cost_details']:
            issues.append("Missing detailed cost breakdown")
        
        # Advanced features (20 points total)
        scores['backup_plans'] = 10 if features['has_backup_plans'] else 0
        scores['table_format'] = 5 if features['has_table_format'] else 0
        scores['detail_level'] = {'high': 5, 'medium': 3, 'low': 0}[features['detail_level']]
        
        # Length penalty for insufficient detail
        if features['word_count'] < 300:
            scores['length_penalty'] = -15
            issues.append("Response too brief for a complete 7-day itinerary")
        else:
            scores['length_penalty'] = 0
        
        total_score = sum(scores.values())
        return max(0, min(100, total_score)), issues
    
    def _extract_procedure_features(self, text: str) -> Dict[str, Any]:
        """Extract structural and content features from procedure."""
        features = {
            'has_numbered_steps': False,
            'has_clear_sequence': False,
            'has_verification_points': False,
            'has_rollback_plan': False,
            'has_responsibilities': False,
            'has_backup_strategy': False,
            'has_notification_step': False,
            'has_documentation_step': False,
            'step_count': 0,
            'word_count': len(text.split()),
            'has_code_examples': False,
            'has_checkpoints': False,
            'detail_level': 'low'
        }
        
        text_lower = text.lower()
        
        # Step structure analysis
        step_patterns = [r'step\s*\d+', r'\d+\.', r'\d+\)', r'###\s*\d+']
        step_matches = []
        for pattern in step_patterns:
            step_matches.extend(re.findall(pattern, text_lower))
        features['step_count'] = len(step_matches)
        features['has_numbered_steps'] = features['step_count'] >= 8
        
        # Sequential flow indicators
        sequence_words = ['first', 'second', 'third', 'next', 'then', 'after', 'before', 'finally']
        features['has_clear_sequence'] = sum(text_lower.count(word) for word in sequence_words) >= 5
        
        # Verification and validation
        verification_terms = ['verify', 'check', 'confirm', 'validate', 'test', 'ensure']
        features['has_verification_points'] = sum(text_lower.count(term) for term in verification_terms) >= 3
        
        # Error handling and rollback
        rollback_terms = ['rollback', 'revert', 'undo', 'restore', 'back out']
        features['has_rollback_plan'] = any(term in text_lower for term in rollback_terms)
        
        # Backup and safety
        backup_terms = ['backup', 'snapshot', 'copy', 'save', 'dump']
        features['has_backup_strategy'] = any(term in text_lower for term in backup_terms)
        
        # Communication and responsibilities
        responsibility_terms = ['responsible', 'owner', 'team', 'role', 'who', 'assign']
        features['has_responsibilities'] = any(term in text_lower for term in responsibility_terms)
        
        notification_terms = ['notify', 'alert', 'inform', 'communicate', 'announce']
        features['has_notification_step'] = any(term in text_lower for term in notification_terms)
        
        documentation_terms = ['document', 'record', 'log', 'changelog', 'update']
        features['has_documentation_step'] = any(term in text_lower for term in documentation_terms)
        
        # Technical sophistication
        features['has_code_examples'] = '```' in text or 'ansible' in text_lower or 'docker' in text_lower
        
        # Checkpoints and validation
        checkpoint_indicators = ['checkpoint', '✅', 'confirm', 'verify']
        features['has_checkpoints'] = any(indicator in text_lower for indicator in checkpoint_indicators)
        
        # Detail level assessment
        if features['word_count'] > 600 and features['has_code_examples']:
            features['detail_level'] = 'high'
        elif features['word_count'] > 300:
            features['detail_level'] = 'medium'
        
        return features
    
    def _score_procedure_against_reference(self, output: str) -> Tuple[float, List[str]]:
        """Score procedure output against the reference implementation."""
        issues = []
        scores = {}
        
        features = self._extract_procedure_features(output)
        ref_features = self._extract_procedure_features(self.reference_procedure)
        
        # Core structure (40 points total)
        scores['step_structure'] = 15 if features['has_numbered_steps'] else min(features['step_count'] * 1.5, 10)
        if not features['has_numbered_steps']:
            issues.append("Missing clear numbered step structure")
        
        scores['sequence_flow'] = 10 if features['has_clear_sequence'] else 0
        if not features['has_clear_sequence']:
            issues.append("Missing clear sequential flow indicators")
        
        scores['verification'] = 15 if features['has_verification_points'] else 0
        if not features['has_verification_points']:
            issues.append("Missing verification and validation steps")
        
        # Safety and error handling (30 points total)
        scores['backup_strategy'] = 10 if features['has_backup_strategy'] else 0
        if not features['has_backup_strategy']:
            issues.append("Missing backup strategy")
        
        scores['rollback_plan'] = 15 if features['has_rollback_plan'] else 0
        if not features['has_rollback_plan']:
            issues.append("Missing rollback/recovery plan")
        
        scores['checkpoints'] = 5 if features['has_checkpoints'] else 0
        
        # Communication and governance (20 points total)
        scores['responsibilities'] = 5 if features['has_responsibilities'] else 0
        scores['notification'] = 10 if features['has_notification_step'] else 0
        if not features['has_notification_step']:
            issues.append("Missing team notification step")
        
        scores['documentation'] = 5 if features['has_documentation_step'] else 0
        
        # Technical sophistication (10 points total)
        scores['code_examples'] = 5 if features['has_code_examples'] else 0
        scores['detail_level'] = {'high': 5, 'medium': 3, 'low': 0}[features['detail_level']]
        
        # Length penalty for insufficient detail
        if features['word_count'] < 200:
            scores['length_penalty'] = -15
            issues.append("Response too brief for a complete deployment procedure")
        else:
            scores['length_penalty'] = 0
        
        total_score = sum(scores.values())
        return max(0, min(100, total_score)), issues
    
    
    def validate_task_output(self, task: Task, output: str) -> Tuple[bool, List[str], float]:
        """Validate task output based on task type using reference-based scoring."""
        if task.task_type == "code_generation":
            score, issues = self._score_code_against_reference(output)
        elif task.task_type == "itinerary_planning":
            score, issues = self._score_itinerary_against_reference(output)
        elif task.task_type == "procedure_structuring":
            score, issues = self._score_procedure_against_reference(output)
        else:
            return False, ["Unknown task type"], 0.0
        
        # More stringent pass threshold - only truly good outputs should pass
        is_valid = score >= 70  # Raised from 50 to make scoring more discriminative
        return is_valid, issues, score
    
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


# Create a singleton instance for backward compatibility
task_validator = ReferenceBasedValidator()


class TaskValidator:
    """Legacy wrapper for backward compatibility."""
    
    @staticmethod
    def validate_task_output(task: Task, output: str) -> Tuple[bool, List[str], float]:
        """Validate task output - delegates to reference-based validator."""
        return task_validator.validate_task_output(task, output)
    
    @staticmethod
    def format_output_preview(output: str, max_length: int = 200) -> str:
        """Format output for preview display."""
        return ReferenceBasedValidator.format_output_preview(output, max_length)
