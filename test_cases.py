"""
Test Cases module for OdyTest - Model Evaluation Suite
Contains comprehensive test scenarios for multilingual semantic parsing
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class TestCase:
    """Single test case for model evaluation"""
    input: str
    expected_intent: str
    expected_entities: Dict[str, Any]
    language: str
    difficulty: str
    description: str
    category: str

class TestCaseGenerator:
    """Generates comprehensive test cases for model evaluation"""
    
    def __init__(self):
        self.test_cases = self._create_test_cases()
    
    def _create_test_cases(self) -> List[TestCase]:
        """Create comprehensive test case collection"""
        cases = []
        
        # Emergency replacement scenarios
        cases.extend(self._emergency_replacement_cases())
        
        # Schedule creation scenarios
        cases.extend(self._schedule_creation_cases())
        
        # Information requests
        cases.extend(self._information_request_cases())
        
        # View schedule scenarios
        cases.extend(self._view_schedule_cases())
        
        # Modification scenarios
        cases.extend(self._modification_cases())
        
        # Analysis scenarios
        cases.extend(self._analysis_cases())
        
        # Edge cases
        cases.extend(self._edge_cases())
        
        return cases
    
    def _emergency_replacement_cases(self) -> List[TestCase]:
        """Emergency replacement test cases"""
        return [
            TestCase(
                input="Anna can't work Friday evening, who can replace her?",
                expected_intent="emergency_replacement",
                expected_entities={
                    "employee_name": "Anna",
                    "shift_day": "Friday",
                    "shift_time": "Evening",
                    "urgency": "emergency"
                },
                language="English",
                difficulty="Medium",
                description="Basic emergency replacement with specific time",
                category="emergency"
            ),
            TestCase(
                input="Sarah ist krank und kann morgen nicht arbeiten",
                expected_intent="emergency_replacement",
                expected_entities={
                    "employee_name": "Sarah",
                    "time_period": "tomorrow",
                    "urgency": "emergency"
                },
                language="German",
                difficulty="Hard",
                description="German emergency with illness context",
                category="emergency"
            ),
            TestCase(
                input="Jean-Pierre ne peut pas venir dimanche matin",
                expected_intent="emergency_replacement",
                expected_entities={
                    "employee_name": "Jean-Pierre",
                    "shift_day": "Sunday",
                    "shift_time": "Morning",
                    "urgency": "emergency"
                },
                language="French",
                difficulty="Hard",
                description="French emergency with hyphenated name",
                category="emergency"
            ),
            TestCase(
                input="Marco non può lavorare martedì pomeriggio",
                expected_intent="emergency_replacement",
                expected_entities={
                    "employee_name": "Marco",
                    "shift_day": "Tuesday",
                    "shift_time": "Afternoon",
                    "urgency": "emergency"
                },
                language="Italian",
                difficulty="Hard",
                description="Italian emergency replacement scenario",
                category="emergency"
            ),
            TestCase(
                input="We need someone to cover the night shift tonight",
                expected_intent="emergency_replacement",
                expected_entities={
                    "shift_time": "Night",
                    "time_period": "today",
                    "urgency": "emergency"
                },
                language="English",
                difficulty="Medium",
                description="Emergency without specific employee name",
                category="emergency"
            )
        ]
    
    def _schedule_creation_cases(self) -> List[TestCase]:
        """Schedule creation test cases"""
        return [
            TestCase(
                input="Create next week's schedule optimizing for cost",
                expected_intent="create_schedule",
                expected_entities={
                    "time_period": "next_week",
                    "optimization_preference": "cost"
                },
                language="English",
                difficulty="Easy",
                description="Basic schedule creation with cost optimization",
                category="creation"
            ),
            TestCase(
                input="Build a schedule that makes employees happy",
                expected_intent="create_schedule",
                expected_entities={
                    "optimization_preference": "preference"
                },
                language="English",
                difficulty="Medium",
                description="Schedule creation focusing on employee satisfaction",
                category="creation"
            ),
            TestCase(
                input="Erstelle einen Schichtplan für nächste Woche",
                expected_intent="create_schedule",
                expected_entities={
                    "time_period": "next_week"
                },
                language="German",
                difficulty="Medium",
                description="German schedule creation request",
                category="creation"
            ),
            TestCase(
                input="Générer un planning équilibré pour cette semaine",
                expected_intent="create_schedule",
                expected_entities={
                    "time_period": "this_week",
                    "optimization_preference": "balanced"
                },
                language="French",
                difficulty="Hard",
                description="French balanced schedule generation",
                category="creation"
            )
        ]
    
    def _information_request_cases(self) -> List[TestCase]:
        """Information request test cases"""
        return [
            TestCase(
                input="List all available employees",
                expected_intent="information",
                expected_entities={},
                language="English",
                difficulty="Easy",
                description="Simple employee list request",
                category="information"
            ),
            TestCase(
                input="Show me the staff with training in bartending",
                expected_intent="information",
                expected_entities={},
                language="English",
                difficulty="Medium",
                description="Filtered staff information request",
                category="information"
            ),
            TestCase(
                input="Wer ist heute verfügbar?",
                expected_intent="information",
                expected_entities={
                    "time_period": "today"
                },
                language="German",
                difficulty="Medium",
                description="German availability inquiry",
                category="information"
            )
        ]
    
    def _view_schedule_cases(self) -> List[TestCase]:
        """View schedule test cases"""
        return [
            TestCase(
                input="Show me who's working this weekend",
                expected_intent="view_schedule",
                expected_entities={
                    "time_period": "this_week"
                },
                language="English",
                difficulty="Easy",
                description="Weekend schedule view request",
                category="view"
            ),
            TestCase(
                input="What's the current schedule for Monday?",
                expected_intent="view_schedule",
                expected_entities={
                    "shift_day": "Monday"
                },
                language="English",
                difficulty="Easy",
                description="Specific day schedule inquiry",
                category="view"
            ),
            TestCase(
                input="Mostra il turno di domani sera",
                expected_intent="view_schedule",
                expected_entities={
                    "time_period": "tomorrow",
                    "shift_time": "Evening"
                },
                language="Italian",
                difficulty="Hard",
                description="Italian schedule view for tomorrow evening",
                category="view"
            )
        ]
    
    def _modification_cases(self) -> List[TestCase]:
        """Schedule modification test cases"""
        return [
            TestCase(
                input="Move Sarah from Monday morning to Tuesday afternoon",
                expected_intent="modify_schedule",
                expected_entities={
                    "employee_name": "Sarah",
                    "shift_day": "Monday",
                    "shift_time": "Morning"
                },
                language="English",
                difficulty="Hard",
                description="Complex shift modification request",
                category="modification"
            ),
            TestCase(
                input="Swap Anna and Felix for Friday shifts",
                expected_intent="modify_schedule",
                expected_entities={
                    "employee_name": "Anna",
                    "shift_day": "Friday"
                },
                language="English",
                difficulty="Hard",
                description="Employee shift swap request",
                category="modification"
            )
        ]
    
    def _analysis_cases(self) -> List[TestCase]:
        """Analysis scenario test cases"""
        return [
            TestCase(
                input="What if we move Sarah from Monday morning to Tuesday afternoon?",
                expected_intent="analyze_scenario",
                expected_entities={
                    "employee_name": "Sarah",
                    "shift_day": "Monday",
                    "shift_time": "Morning"
                },
                language="English",
                difficulty="Hard",
                description="Hypothetical scenario analysis",
                category="analysis"
            ),
            TestCase(
                input="Analyze the impact of adding an extra evening shift",
                expected_intent="analyze_scenario",
                expected_entities={
                    "shift_time": "Evening"
                },
                language="English",
                difficulty="Hard",
                description="Impact analysis request",
                category="analysis"
            )
        ]
    
    def _edge_cases(self) -> List[TestCase]:
        """Edge case test scenarios"""
        return [
            TestCase(
                input="Mike",
                expected_intent="unknown",
                expected_entities={
                    "employee_name": "Mike"
                },
                language="English",
                difficulty="Hard",
                description="Single name input - ambiguous intent",
                category="edge"
            ),
            TestCase(
                input="",
                expected_intent="unknown",
                expected_entities={},
                language="English",
                difficulty="Hard",
                description="Empty input handling",
                category="edge"
            ),
            TestCase(
                input="Anna-Maria kann nur sonntags von 8-16 Uhr mit Kellner-Fähigkeiten",
                expected_intent="information",
                expected_entities={
                    "employee_name": "Anna-Maria",
                    "shift_day": "Sunday"
                },
                language="German",
                difficulty="Very Hard",
                description="Complex German input with constraints",
                category="edge"
            ),
            TestCase(
                input="Help me with something",
                expected_intent="unknown",
                expected_entities={},
                language="English",
                difficulty="Medium",
                description="Vague request without scheduling context",
                category="edge"
            ),
            TestCase(
                input="Schedule meeting for 3pm tomorrow",
                expected_intent="unknown",
                expected_entities={
                    "time_period": "tomorrow"
                },
                language="English",
                difficulty="Medium",
                description="Non-shift scheduling request",
                category="edge"
            )
        ]
    
    def get_all_test_cases(self) -> List[TestCase]:
        """Get all test cases"""
        return self.test_cases
    
    def get_test_cases_by_language(self, language: str) -> List[TestCase]:
        """Get test cases filtered by language"""
        return [case for case in self.test_cases if case.language == language]
    
    def get_test_cases_by_difficulty(self, difficulty: str) -> List[TestCase]:
        """Get test cases filtered by difficulty"""
        return [case for case in self.test_cases if case.difficulty == difficulty]
    
    def get_test_cases_by_category(self, category: str) -> List[TestCase]:
        """Get test cases filtered by category"""
        return [case for case in self.test_cases if case.category == category]
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary statistics of test cases"""
        total = len(self.test_cases)
        
        languages = {}
        difficulties = {}
        categories = {}
        
        for case in self.test_cases:
            languages[case.language] = languages.get(case.language, 0) + 1
            difficulties[case.difficulty] = difficulties.get(case.difficulty, 0) + 1
            categories[case.category] = categories.get(case.category, 0) + 1
        
        return {
            "total_cases": total,
            "by_language": languages,
            "by_difficulty": difficulties,
            "by_category": categories
        }

# Global instance for easy access
test_generator = TestCaseGenerator()

def get_test_cases() -> List[TestCase]:
    """Get all test cases"""
    return test_generator.get_all_test_cases()

def get_test_summary() -> Dict[str, Any]:
    """Get test case summary"""
    return test_generator.get_test_summary()
