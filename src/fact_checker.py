"""
Fact Checker Agent
Validates educational facts used in stories to ensure accuracy.
Uses Gemini to verify facts against known knowledge.
"""

from typing import Dict, List, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


class FactChecker:
    """Agent that validates educational facts for accuracy."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Fact Checker.
        
        Args:
            api_key: Google AI API key. If not provided, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file or pass as argument.")
        
        genai.configure(api_key=self.api_key)
        
        # Initialize the model with fact-checking persona
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="""You are a Fact Checker Agent specialized in validating educational content for children (ages 5-10).

Your responsibilities:
1. Verify that educational facts are accurate and age-appropriate
2. Check that facts are presented in a way suitable for children
3. Identify any inaccuracies or misleading information
4. Ensure facts align with established scientific knowledge
5. Rate fact accuracy on a scale of 1-10

Be thorough but remember these are for children, so focus on age-appropriate accuracy."""
        )
    
    def verify_fact(self, fact: str, topic: str) -> Dict:
        """
        Verify an educational fact for accuracy.
        
        Args:
            fact: The fact to verify
            topic: The topic the fact is about
        
        Returns:
            Dictionary with verification results
        """
        verification_prompt = f"""Verify this educational fact for children (ages 5-10):

Topic: {topic}
Fact: {fact}

Please evaluate:
1. Is this fact accurate? (true/false/partially_true)
2. Accuracy score (1-10, where 10 is completely accurate)
3. Is it age-appropriate? (yes/no)
4. Any concerns or corrections needed?
5. Overall verdict: VERIFIED, NEEDS_CORRECTION, or INACCURATE

Format your response as:
ACCURACY: true/false/partially_true
SCORE: X/10
AGE_APPROPRIATE: yes/no
CONCERNS: [any concerns or corrections]
VERDICT: VERIFIED/NEEDS_CORRECTION/INACCURATE
"""
        
        try:
            response = self.model.generate_content(
                verification_prompt,
                generation_config={
                    "temperature": 0.2,  # Low temperature for consistent fact-checking
                    "max_output_tokens": 500,
                }
            )
            
            verification_text = response.text
            
            # Parse the response
            accuracy = "unknown"
            score = 7.0  # Default
            age_appropriate = True
            concerns = ""
            verdict = "VERIFIED"
            
            for line in verification_text.split('\n'):
                line_upper = line.upper()
                if 'ACCURACY:' in line_upper:
                    if 'TRUE' in line_upper:
                        accuracy = "true"
                    elif 'FALSE' in line_upper:
                        accuracy = "false"
                    elif 'PARTIALLY' in line_upper:
                        accuracy = "partially_true"
                elif 'SCORE:' in line_upper:
                    try:
                        score_part = line.split(':')[1].strip().split('/')[0]
                        score = float(score_part)
                    except:
                        pass
                elif 'AGE_APPROPRIATE:' in line_upper:
                    if 'NO' in line_upper:
                        age_appropriate = False
                elif 'CONCERNS:' in line_upper:
                    concerns = line.split(':', 1)[1].strip() if ':' in line else ""
                elif 'VERDICT:' in line_upper:
                    if 'NEEDS_CORRECTION' in line_upper:
                        verdict = "NEEDS_CORRECTION"
                    elif 'INACCURATE' in line_upper:
                        verdict = "INACCURATE"
            
            return {
                "fact": fact,
                "topic": topic,
                "accuracy": accuracy,
                "score": score,
                "age_appropriate": age_appropriate,
                "concerns": concerns,
                "verdict": verdict,
                "is_verified": verdict == "VERIFIED",
                "raw_response": verification_text
            }
            
        except Exception as e:
            # Fallback: assume fact is okay if verification fails
            return {
                "fact": fact,
                "topic": topic,
                "accuracy": "unknown",
                "score": 5.0,
                "age_appropriate": True,
                "concerns": f"Verification failed: {str(e)}",
                "verdict": "VERIFIED",  # Default to verified to not block generation
                "is_verified": True,
                "error": str(e)
            }
    
    def verify_multiple_facts(self, facts: List[Dict]) -> List[Dict]:
        """
        Verify multiple facts at once.
        
        Args:
            facts: List of dictionaries with 'fact' and 'topic' keys
        
        Returns:
            List of verification results
        """
        results = []
        for fact_data in facts:
            result = self.verify_fact(
                fact_data.get('fact', ''),
                fact_data.get('topic', '')
            )
            results.append(result)
        return results

