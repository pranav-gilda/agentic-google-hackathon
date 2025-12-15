"""
Orchestration System
Manages the Storyteller -> Judge -> Refinement loop with Gemini and fallback to Ollama.
"""

from typing import Dict, Optional, List
from agents import GeminiStoryteller, GeminiJudge
from mcp_client import MCPClient
from local_backup import OllamaBackup
from mcp_expander import MCPExpander
from fact_checker import FactChecker


class StoryOrchestrator:
    """Orchestrates the story generation workflow with iterative refinement."""
    
    def __init__(
        self, 
        gemini_api_key: Optional[str] = None,
        enable_mcp: bool = True,
        max_revisions: int = 3,
        quality_threshold: float = 7.0,
        parent_settings: Optional[Dict] = None,
        storyteller_temperature: Optional[float] = None,
        judge_temperature: Optional[float] = None,
        max_story_tokens: Optional[int] = None
    ):
        """
        Initialize orchestrator.
        
        Args:
            gemini_api_key: Google AI API key
            enable_mcp: Whether to enable MCP tool integration
            max_revisions: Maximum number of refinement iterations
            quality_threshold: Minimum judge score for approval
            parent_settings: Optional parent settings (persona, values, interests)
            storyteller_temperature: Optional temperature override for storyteller
            judge_temperature: Optional temperature override for judge
            max_story_tokens: Optional max output tokens for storyteller
        """
        self.enable_mcp = enable_mcp
        self.max_revisions = max_revisions
        self.quality_threshold = quality_threshold
        self.parent_settings = parent_settings or {}
        
        # Initialize components
        try:
            self.storyteller = GeminiStoryteller(
                api_key=gemini_api_key,
                parent_settings=parent_settings,
                temperature=storyteller_temperature,
                max_output_tokens=max_story_tokens
            )
            self.judge = GeminiJudge(api_key=gemini_api_key, temperature=judge_temperature)
            self.mcp_client = MCPClient() if enable_mcp else None
            self.mcp_expander = MCPExpander() if enable_mcp else None
            try:
                self.fact_checker = FactChecker(api_key=gemini_api_key) if enable_mcp else None
            except:
                self.fact_checker = None  # Fact checker optional
            self.gemini_available = True
        except Exception as e:
            print(f"⚠️  Warning: Gemini initialization failed: {e}")
            self.gemini_available = False
        
        # Initialize fallback
        self.backup = OllamaBackup()
    
    def _detect_and_fetch_facts(self, user_request: str) -> List[Dict]:
        """
        Detect educational topics in user request and fetch facts with expansion.
        Uses MCP Expander for better topic detection.
        
        Args:
            user_request: User's story request
        
        Returns:
            List of tool call dictionaries with facts and verification
        """
        if not self.mcp_expander:
            return []
        
        tool_calls = []
        
        # Use MCP Expander to detect topics
        detected_topics = self.mcp_expander.detect_topics_in_text(user_request)
        
        # Get facts for detected topics
        for topic in detected_topics:
            fact_data = self.mcp_expander.get_fact_with_expansion(topic)
            
            # Verify fact if fact checker is available
            verification = None
            if self.fact_checker:
                try:
                    verification = self.fact_checker.verify_fact(
                        fact_data['fact'],
                        fact_data['used_topic']
                    )
                except:
                    pass  # Verification optional
            
            tool_calls.append({
                "function": "get_educational_fact",
                "arguments": {"topic": fact_data['used_topic']},
                "result": fact_data['fact'],
                "original_topic": fact_data['original_topic'],
                "category": fact_data['category'],
                "expanded": fact_data['expanded'],
                "verification": verification
            })
        
        return tool_calls
    
    def generate_story_with_judge(self, user_request: str) -> Dict:
        """
        Generate a story with judge evaluation and iterative refinement.
        
        Args:
            user_request: User's story request
        
        Returns:
            Comprehensive result with story, scores, and metadata
        """
        print("\n📚 Starting story generation...")
        print(f"📝 User request: {user_request}\n")
        
        # Try Gemini first
        if self.gemini_available:
            try:
                return self._generate_with_gemini(user_request)
            except Exception as e:
                print(f"⚠️  Gemini API failed: {e}")
                print("🔄 Falling back to local Ollama model...")
                return self._generate_with_fallback(user_request)
        else:
            print("🔄 Using local Ollama fallback (Gemini not available)...")
            return self._generate_with_fallback(user_request)
    
    def _generate_with_gemini(self, user_request: str) -> Dict:
        """Generate story using Gemini with MCP integration."""
        revision_count = 0
        
        # Initial story generation
        print("✨ Generating initial story with Gemini...")
        
        try:
            if self.enable_mcp and self.mcp_client:
                # Pre-detect educational topics and fetch facts
                tool_calls = self._detect_and_fetch_facts(user_request)
                
                if tool_calls:
                    print(f"🔧 MCP enabled - fetched {len(tool_calls)} educational fact(s)")
                    
                    # Build facts text with verification status
                    facts_parts = []
                    verified_count = 0
                    for tc in tool_calls:
                        topic = tc.get('arguments', {}).get('topic', tc.get('original_topic', 'topic'))
                        fact = tc.get('result', '')
                        verification = tc.get('verification')
                        
                        if verification and verification.get('is_verified'):
                            verified_count += 1
                            facts_parts.append(f"✅ Verified fact about {topic}: {fact}")
                        else:
                            facts_parts.append(f"Educational fact about {topic}: {fact}")
                    
                    facts_text = "\n\n".join(facts_parts)
                    
                    if verified_count > 0:
                        print(f"   ✓ {verified_count} fact(s) verified by Fact Checker")
                    
                    enhanced_request = f"""{user_request}

IMPORTANT: Incorporate these educational facts naturally into the story:
{facts_text}

Make sure the story is educational while remaining engaging and age-appropriate. Use the verified facts (marked with ✓) as primary sources."""
                else:
                    print("ℹ️  No educational topics detected - generating standard story")
                    enhanced_request = user_request
                
                # Generate with enhanced prompt
                result = self.storyteller.generate_story(enhanced_request)
                story = result.get("story", "")
            else:
                # Standard generation without tools
                result = self.storyteller.generate_story(user_request)
                story = result.get("story", "")
                tool_calls = []
            
            if not result.get("is_valid", False):
                error_msg = result.get("error", "Unknown error")
                print(f"⚠️  Initial story generation failed: {error_msg}")
                print("🔄 Trying fallback...")
                return self._generate_with_fallback(user_request)
        except Exception as e:
            print(f"❌ Gemini generation error: {str(e)}")
            print("🔄 Falling back to Ollama...")
            return self._generate_with_fallback(user_request)
        
        # Iterative refinement loop
        while revision_count < self.max_revisions:
            print(f"\n🔍 Evaluating story (attempt {revision_count + 1})...")
            
            # Judge evaluation
            evaluation = self.judge.evaluate_story(story, user_request)
            
            print(f"📊 Judge score: {evaluation['overall_score']:.1f}/10")
            print(f"✅ Verdict: {evaluation['verdict']}")
            
            # Check if story meets threshold
            if evaluation["meets_threshold"]:
                print("🎉 Story approved by judge!")
                break
            
            # If not approved and we have revisions left, refine
            if revision_count < self.max_revisions - 1:
                print(f"🔄 Refining story based on feedback...")
                revision_prompt = self.judge.generate_revision_prompt(
                    story,
                    evaluation["detailed_feedback"],
                    user_request
                )
                
                # Generate revised story
                if self.enable_mcp and self.mcp_client:
                    revised_result = self.mcp_client.process_with_tools(
                        self.storyteller.model,
                        revision_prompt
                    )
                    revised_story = revised_result.get("story", "")
                else:
                    revised_result = self.storyteller.generate_story(
                        user_request,
                        revision_context=evaluation["detailed_feedback"]
                    )
                    revised_story = revised_result.get("story", "")
                
                if revised_result.get("is_valid", False):
                    story = revised_story
                    revision_count += 1
                else:
                    print("⚠️  Revised story generation failed. Using previous version.")
                    break
            else:
                print("⚠️  Maximum revisions reached. Using current version.")
                break
        
        # Final evaluation
        final_evaluation = self.judge.evaluate_story(story, user_request)
        
        return {
            "story": story,
            "user_request": user_request,
            "revision_count": revision_count,
            "judge_score": final_evaluation["overall_score"],
            "judge_feedback": final_evaluation["detailed_feedback"],
            "meets_quality_threshold": final_evaluation["meets_threshold"],
            "tool_calls": tool_calls,
            "model_used": "gemini-2.5-flash",
            "mcp_enabled": self.enable_mcp,
            "parent_settings": self.parent_settings
        }
    
    def _generate_with_fallback(self, user_request: str) -> Dict:
        """Generate story using Ollama fallback."""
        print("🔄 Generating story with Ollama fallback...")
        print("   (Gemini API unavailable - using local model)")
        
        result = self.backup.generate_story_with_fallback(user_request)
        
        if result.get("is_valid", False):
            story = result.get("story", "")
            print(f"📖 Story generated ({len(story)} characters)")
            
            # Simple validation (no judge for fallback to keep it simple)
            return {
                "story": story,
                "user_request": user_request,
                "revision_count": 0,
                "judge_score": 6.0,  # Default score for fallback
                "judge_feedback": "Story generated using local Ollama fallback. Judge evaluation skipped.",
                "meets_quality_threshold": False,
                "tool_calls": [],
                "model_used": result.get("model", "ollama"),
                "mcp_enabled": False,
                "fallback_used": True
            }
        else:
            print(f"❌ Fallback generation failed: {result.get('error', 'Unknown error')}")
            return {
                "story": "Story generation failed. Please check your API keys and Ollama installation.",
                "user_request": user_request,
                "revision_count": 0,
                "judge_score": 0.0,
                "judge_feedback": result.get("error", "Unknown error"),
                "meets_quality_threshold": False,
                "tool_calls": [],
                "model_used": "none",
                "mcp_enabled": False,
                "fallback_used": True,
                "error": result.get("error", "Generation failed")
            }

