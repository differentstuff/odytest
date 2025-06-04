"""
Prompt Manager for OdyTest - Model Evaluation Suite
Handles different prompt variants and production prompt loading
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PromptVariant:
    """Single prompt variant configuration"""
    name: str
    template: str
    description: str
    best_for: str

class PromptManager:
    """Manages different prompt variants for testing"""
    
    def __init__(self):
        self.variants = self._load_prompt_variants()
        self.production_prompt = self._load_production_prompt()
    
    def _load_production_prompt(self) -> str:
        """Load production prompt from semantic parser config"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'semantic_parser_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('parsing_prompt', {}).get('template', self._get_fallback_production_prompt())
            else:
                return self._get_fallback_production_prompt()
        except Exception:
            return self._get_fallback_production_prompt()
    
    def _get_fallback_production_prompt(self) -> str:
        """Fallback production prompt if config not available"""
        return """You are a semantic parser for a staff scheduling system. Parse the user input into structured JSON.

{context_str}User Input: "{user_input}"

Extract information and output ONLY valid JSON in this exact format:
{{
  "intent": "view_schedule" | "emergency_replacement" | "create_schedule" | "modify_schedule" | "analyze_scenario" | "information" | "unknown",
  "entities": {{
    "employee_name": "extracted name or null",
    "shift_day": "Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday or null", 
    "shift_time": "Morning|Afternoon|Evening|Night or null",
    "shift_name": "exact shift name if mentioned or null",
    "optimization_preference": "cost|preference|training|balanced or null",
    "time_period": "this_week|next_week|today|tomorrow or null",
    "urgency": "emergency|planned or null"
  }},
  "confidence": 0.0 to 1.0,
  "missing_info": ["list of missing required fields"],
  "suggested_question": "clear question to get missing info or null",
  "conversation_hint": "brief helpful context or null"
}}

Intent classification rules:
- "view_schedule": Show, display, see, what is, check current schedule or assignments
- "emergency_replacement": Someone can't work, needs replacement, cover, substitute
- "create_schedule": Create, build, optimize, generate, plan schedule for period
- "modify_schedule": Change, replace, move, swap, add, remove from existing schedule
- "analyze_scenario": What if, analyze, scenarios, alternatives, options
- "information": List employees, show available staff, general information
- "unknown": Cannot clearly classify

Entity extraction:
- employee_name: Extract proper names (Anna, Felix, Sarah Mueller, etc.)
- shift_day: Map day references to standard format
- shift_time: Map time references (morning, evening, afternoon, night)
- optimization_preference: Detect cost focus, employee satisfaction, training opportunities
- urgency: Emergency indicates immediate need, planned for future scheduling

Output ONLY the JSON, no other text:"""
    
    def _load_prompt_variants(self) -> Dict[str, PromptVariant]:
        """Load all prompt variants"""
        return {
            "production": PromptVariant(
                name="production",
                template="",  # Will be loaded separately
                description="Current production prompt from semantic parser config",
                best_for="Production baseline comparison"
            ),
            "multilingual": PromptVariant(
                name="multilingual",
                template=self._get_multilingual_prompt(),
                description="Enhanced multilingual support with examples",
                best_for="International teams, complex multilingual parsing"
            ),
            "concise": PromptVariant(
                name="concise",
                template=self._get_concise_prompt(),
                description="Streamlined prompt for faster inference",
                best_for="Speed-critical applications, simple inputs"
            ),
            "structured": PromptVariant(
                name="structured",
                template=self._get_structured_prompt(),
                description="Highly organized with clear sections",
                best_for="Consistent parsing, clear requirements"
            ),
            "chain_of_thought": PromptVariant(
                name="chain_of_thought",
                template=self._get_chain_of_thought_prompt(),
                description="Step-by-step reasoning approach",
                best_for="Complex scenarios, accuracy-critical tasks"
            )
        }
    
    def _get_multilingual_prompt(self) -> str:
        """Enhanced multilingual prompt"""
        return """Parse scheduling input to JSON. Output ONLY JSON.

Input: "{user_input}"
{context_str}

JSON Format:
{{
  "intent": "view_schedule|emergency_replacement|create_schedule|modify_schedule|analyze_scenario|information|unknown",
  "entities": {{
    "employee_name": null,
    "shift_day": null,
    "shift_time": null,
    "shift_name": null,
    "optimization_preference": null,
    "time_period": null,
    "urgency": null
  }},
  "confidence": 0.0,
  "missing_info": [],
  "suggested_question": null,
  "conversation_hint": null
}}

Intents:
- view_schedule: show, display, see, who's working
- emergency_replacement: can't work, sick, replace, emergency, cover
- create_schedule: create, build, optimize, generate schedule
- modify_schedule: change, move, swap, replace shifts
- analyze_scenario: what if, analyze, scenarios
- information: list, available, employees
- unknown: unclear input

Multilingual Keywords:
EN: can't work, sick, replace, schedule
DE: kann nicht, krank, ersetzen, Schichtplan  
FR: ne peut pas, malade, remplacer, horaire
IT: non può, malato, sostituire, turno

Examples:
"Anna can't work Friday" → {{"intent":"emergency_replacement","entities":{{"employee_name":"Anna","shift_day":"Friday","urgency":"emergency"}},"confidence":0.9,"missing_info":[],"suggested_question":null,"conversation_hint":null}}

"Sarah ist krank" → {{"intent":"emergency_replacement","entities":{{"employee_name":"Sarah","urgency":"emergency"}},"confidence":0.85,"missing_info":["shift_day","shift_time"],"suggested_question":"Which shift can't Sarah work?","conversation_hint":null}}

JSON only:"""
    
    def _get_concise_prompt(self) -> str:
        """Concise prompt for speed"""
        return """Convert to JSON. Output JSON only.

Input: "{user_input}"
{context_str}

{{
  "intent": "view_schedule|emergency_replacement|create_schedule|modify_schedule|analyze_scenario|information|unknown",
  "entities": {{
    "employee_name": null,
    "shift_day": null,
    "shift_time": null,
    "optimization_preference": null,
    "time_period": null,
    "urgency": null
  }},
  "confidence": 0.0,
  "missing_info": [],
  "suggested_question": null
}}

Intent mapping:
- show/display/see → view_schedule
- can't work/sick/emergency → emergency_replacement  
- create/build/optimize → create_schedule
- change/move/swap → modify_schedule
- what if/analyze → analyze_scenario
- list/available → information
- unclear → unknown

Extract names, days (Monday-Sunday), times (Morning/Afternoon/Evening/Night), urgency.

JSON:"""
    
    def _get_structured_prompt(self) -> str:
        """Structured prompt with clear sections"""
        return """TASK: Parse scheduling text to JSON
INPUT: "{user_input}"
{context_str}

OUTPUT FORMAT:
{{
  "intent": "emergency_replacement|create_schedule|view_schedule|modify_schedule|analyze_scenario|information|unknown",
  "entities": {{
    "employee_name": "Name or null",
    "shift_day": "Monday-Sunday or null",
    "shift_time": "Morning|Afternoon|Evening|Night or null",
    "optimization_preference": "cost|preference|training|balanced or null",
    "time_period": "this_week|next_week|today|tomorrow or null",
    "urgency": "emergency|planned or null"
  }},
  "confidence": 0.0-1.0,
  "missing_info": [],
  "suggested_question": "Question or null"
}}

CLASSIFICATION RULES:
1. emergency_replacement: "can't work", "sick", "replace", "cover", "emergency"
2. create_schedule: "create", "build", "optimize", "generate", "plan schedule"
3. view_schedule: "show", "display", "see", "who's working", "current schedule"
4. modify_schedule: "change", "move", "swap", "replace shifts"
5. analyze_scenario: "what if", "analyze", "scenarios", "alternatives"
6. information: "list", "available", "employees", "staff info"
7. unknown: Ambiguous or unclear requests

ENTITY EXTRACTION:
- Names: Capitalize first letters (anna → Anna)
- Days: Map to standard format (heute → today, vendredi → Friday)
- Times: Group into periods (8-16 → Morning, evening → Evening)
- Urgency: Emergency words indicate "emergency", planning words indicate "planned"

MULTILINGUAL: Support DE/FR/IT variations of keywords.

OUTPUT: JSON only, no text."""
    
    def _get_chain_of_thought_prompt(self) -> str:
        """Chain of thought reasoning prompt"""
        return """Parse scheduling request step by step, then output JSON.

Input: "{user_input}"
{context_str}

Steps:
1. Identify main action (show, create, emergency, etc.)
2. Extract person names (proper nouns)
3. Find time references (days, periods)
4. Detect urgency signals
5. Determine missing information

JSON Output:
{{
  "intent": "view_schedule|emergency_replacement|create_schedule|modify_schedule|analyze_scenario|information|unknown",
  "entities": {{
    "employee_name": null,
    "shift_day": null,
    "shift_time": null,
    "optimization_preference": null,
    "time_period": null,
    "urgency": null
  }},
  "confidence": 0.0,
  "missing_info": [],
  "suggested_question": null
}}

Example Process:
Input: "Anna kann nicht Freitag arbeiten"
1. Action: "kann nicht" = can't work → emergency_replacement
2. Person: "Anna" → employee_name: "Anna"  
3. Time: "Freitag" = Friday → shift_day: "Friday"
4. Urgency: "kann nicht" indicates emergency → urgency: "emergency"
5. Missing: No specific time → missing_info: ["shift_time"]

Result: {{"intent":"emergency_replacement","entities":{{"employee_name":"Anna","shift_day":"Friday","urgency":"emergency"}},"confidence":0.9,"missing_info":["shift_time"],"suggested_question":"What time on Friday can't Anna work?"}}

Process the input and output ONLY the final JSON:"""
    
    def get_prompt(self, variant_name: str, user_input: str, context_str: str = "") -> str:
        """Get formatted prompt for specific variant"""
        if variant_name == "production":
            template = self.production_prompt
        elif variant_name in self.variants:
            template = self.variants[variant_name].template
        else:
            raise ValueError(f"Unknown prompt variant: {variant_name}")
        
        return template.format(user_input=user_input, context_str=context_str)
    
    def get_available_variants(self) -> Dict[str, str]:
        """Get list of available prompt variants with descriptions"""
        variants = {"production": "Current production prompt from semantic parser config"}
        variants.update({name: variant.description for name, variant in self.variants.items() if name != "production"})
        return variants
    
    def get_variant_info(self, variant_name: str) -> Optional[PromptVariant]:
        """Get detailed information about a specific variant"""
        if variant_name == "production":
            return PromptVariant(
                name="production",
                template=self.production_prompt,
                description="Current production prompt from semantic parser config",
                best_for="Production baseline comparison"
            )
        return self.variants.get(variant_name)

# Global instance for easy access
prompt_manager = PromptManager()

def get_prompt(variant_name: str, user_input: str, context_str: str = "") -> str:
    """Get formatted prompt for specific variant"""
    return prompt_manager.get_prompt(variant_name, user_input, context_str)

def get_available_variants() -> Dict[str, str]:
    """Get list of available prompt variants"""
    return prompt_manager.get_available_variants()
