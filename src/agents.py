"""
Gemini 2.5 Flash Agent Setup
Configures Google Gemini 2.5 Flash for story generation with MCP tool integration.
"""

import os
from typing import Dict, Optional, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiStoryteller:
    """Storyteller agent using Google Gemini 2.5 Flash."""
    
    def __init__(self, api_key: Optional[str] = None, parent_settings: Optional[Dict] = None, temperature: Optional[float] = None, max_output_tokens: Optional[int] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google AI API key. If not provided, reads from GEMINI_API_KEY env var.
            parent_settings: Optional parent settings (persona, values, interests)
            temperature: Optional temperature override
            max_output_tokens: Optional max output tokens override
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file or pass as argument.")
        
        genai.configure(api_key=self.api_key)
        
        # Get temperature from parent settings or use default
        if temperature is not None:
            self.temperature = temperature
        elif parent_settings:
            from parent_config import apply_parent_settings_to_config
            tech_overrides = apply_parent_settings_to_config(parent_settings)
            self.temperature = tech_overrides.get("storyteller_temperature", 0.8)
        else:
            self.temperature = 0.8
        
        # Set max output tokens
        self.max_output_tokens = max_output_tokens if max_output_tokens is not None else 2000
        
        # Build system instruction with parent settings
        system_instruction = """You are a creative and educational Storyteller Agent specialized in generating 
age-appropriate bedtime stories (ages 5-10). 

Your responsibilities:
1. Generate engaging, age-appropriate stories based on user requests
2. When real-world topics are mentioned (space, animals, dinosaurs, science), incorporate educational facts naturally
3. Weave educational facts seamlessly into the story narrative
4. Ensure stories are positive, safe, and appropriate for children
5. Use simple vocabulary and clear sentence structure suitable for ages 5-10
6. Create stories with clear beginning, middle, and end
7. Include positive messages and values"""
        
        # Add parent settings to system instruction
        if parent_settings:
            from parent_config import get_persona_config, get_values_prompts, get_interests_prompts
            persona = get_persona_config(parent_settings.get("persona", "balanced_storyteller"))
            system_instruction += f"\n\nStory Style: {persona['name']} - {persona['description']}"
            system_instruction += f"\nTone: {persona['technical_mapping'].get('tone', 'uplifting')}"
            
            values = parent_settings.get("values", [])
            if values:
                system_instruction += f"\n\nValues to emphasize:\n{get_values_prompts(values)}"
            
            interests = parent_settings.get("interests", [])
            if interests:
                system_instruction += f"\n\nInterests to include:\n{get_interests_prompts(interests)}"
            
            if parent_settings.get("child_name"):
                system_instruction += f"\n\nConsider using the name '{parent_settings['child_name']}' for a character if appropriate."
            
            if parent_settings.get("custom_elements"):
                system_instruction += f"\n\nAdditional elements: {parent_settings['custom_elements']}"
        
        # Initialize the model with system instructions
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )
        self.parent_settings = parent_settings or {}
    
    def generate_story(
        self, 
        user_request: str, 
        revision_context: Optional[str] = None,
        tools: Optional[List] = None
    ) -> Dict:
        """
        Generate a story based on user request.
        
        Args:
            user_request: The user's story request
            revision_context: Optional context for revisions/refinements
            tools: Optional list of tools (MCP functions) to make available
        
        Returns:
            Dictionary with 'story' and 'is_valid' keys
        """
        prompt = user_request
        if revision_context:
            prompt = f"{user_request}\n\nRevision instructions: {revision_context}"
        
        try:
            # Configure generation parameters (use instance temperature and max tokens)
            generation_config = {
                "temperature": self.temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": self.max_output_tokens,
            }
            
            # Generate with tools if provided
            if tools:
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=generation_config,
                        tools=tools
                    )
                except Exception as tool_error:
                    # If tool calling fails, fall back to regular generation
                    print(f"   ⚠️  Tool calling failed: {tool_error}, using standard generation")
                    response = self.model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
            else:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
            
            # Extract text safely
            if hasattr(response, 'text') and response.text:
                story = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Try to extract from candidates
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    parts = candidate.content.parts
                    if parts:
                        text_parts = [p.text for p in parts if hasattr(p, 'text') and p.text]
                        story = " ".join(text_parts) if text_parts else "Story generation completed."
                    else:
                        story = "Story generation completed."
                else:
                    story = "Story generation completed."
            else:
                story = "Error: Could not extract story from response"
            
            return {
                "story": story,
                "is_valid": True,
                "raw_response": response
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Story generation error: {error_msg}")
            return {
                "story": f"Error generating story: {error_msg}",
                "is_valid": False,
                "error": error_msg
            }


class GeminiJudge:
    """Judge agent using Google Gemini 2.5 Flash to evaluate story quality."""
    
    def __init__(self, api_key: Optional[str] = None, temperature: Optional[float] = None, max_output_tokens: Optional[int] = None):
        """
        Initialize Gemini judge.
        
        Args:
            api_key: Google AI API key. If not provided, reads from GEMINI_API_KEY env var.
            temperature: Optional temperature override (default: 0.2 for consistent judging)
            max_output_tokens: Optional max output tokens override (default: 1000)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file or pass as argument.")
        
        genai.configure(api_key=self.api_key)
        
        # Set temperature (default 0.2 for consistent judging)
        self.temperature = temperature if temperature is not None else 0.2
        
        # Set max output tokens (default 1000 for judge responses)
        self.max_output_tokens = max_output_tokens if max_output_tokens is not None else 1000
        
        # Initialize judge model with evaluation persona
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="""You are a Story Judge Agent specialized in evaluating bedtime stories for children (ages 5-10).

Your evaluation criteria:
1. Age-appropriateness (vocabulary, themes, complexity)
2. Educational value (if applicable)
3. Narrative quality (plot, characters, flow)
4. Safety and positive messaging
5. Engagement and entertainment value
6. Story structure (beginning, middle, end)

Provide scores from 1-10 for each criterion and an overall score.
Give constructive feedback for improvement when scores are below 7."""
        )
    
    def evaluate_story(self, story: str, user_request: str) -> Dict:
        """
        Evaluate a story and provide feedback.
        
        Args:
            story: The story to evaluate
            user_request: Original user request for context
        
        Returns:
            Dictionary with scores, feedback, and verdict
        """
        evaluation_prompt = f"""Evaluate this bedtime story:

User Request: {user_request}

Story:
{story}

Please provide:
1. Overall score (1-10)
2. Scores for each criterion (age-appropriateness, educational value, narrative quality, safety, engagement, structure)
3. Detailed feedback
4. Verdict: "APPROVED" if overall score >= 7, "NEEDS_REVISION" otherwise

Format your response as:
OVERALL_SCORE: X/10
AGE_APPROPRIATENESS: X/10
EDUCATIONAL_VALUE: X/10
NARRATIVE_QUALITY: X/10
SAFETY: X/10
ENGAGEMENT: X/10
STRUCTURE: X/10
VERDICT: APPROVED/NEEDS_REVISION
FEEDBACK: [detailed feedback here]
"""
        
        try:
            response = self.model.generate_content(
                evaluation_prompt,
                generation_config={
                    "temperature": self.temperature,  # Use instance temperature
                    "max_output_tokens": self.max_output_tokens,  # Use instance max tokens
                }
            )
            
            evaluation_text = response.text
            
            # Parse the response
            overall_score = 7.0  # Default
            verdict = "APPROVED"
            detailed_feedback = evaluation_text
            
            # Try to extract score from response
            for line in evaluation_text.split('\n'):
                if 'OVERALL_SCORE' in line.upper():
                    try:
                        score_part = line.split(':')[1].strip().split('/')[0]
                        overall_score = float(score_part)
                    except:
                        pass
                if 'VERDICT' in line.upper():
                    if 'NEEDS_REVISION' in line.upper():
                        verdict = "NEEDS_REVISION"
            
            return {
                "overall_score": overall_score,
                "verdict": verdict,
                "meets_threshold": overall_score >= 7.0,
                "detailed_feedback": detailed_feedback,
                "raw_response": evaluation_text
            }
            
        except Exception as e:
            # Fallback evaluation
            return {
                "overall_score": 5.0,
                "verdict": "NEEDS_REVISION",
                "meets_threshold": False,
                "detailed_feedback": f"Error during evaluation: {str(e)}",
                "error": str(e)
            }
    
    def generate_revision_prompt(self, story: str, feedback: str, user_request: str) -> str:
        """
        Generate a revision prompt based on judge feedback.
        
        Args:
            story: Current story
            feedback: Judge feedback
            user_request: Original user request
        
        Returns:
            Revision prompt string
        """
        return f"""Please revise this story based on the judge's feedback:

Original Request: {user_request}

Current Story:
{story}

Judge Feedback:
{feedback}

Please improve the story while maintaining the core narrative and educational elements."""

