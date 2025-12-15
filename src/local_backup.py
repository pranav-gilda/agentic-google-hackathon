"""
Local Backup System
Ollama fallback logic for when Gemini API fails.
"""

from typing import Dict, Optional
import subprocess
import json

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None


class OllamaBackup:
    """Fallback to local Ollama model when Gemini API fails."""
    
    def __init__(self, model_name: str = "llama3.2"):
        """
        Initialize Ollama backup.
        
        Args:
            model_name: Name of the Ollama model to use (default: llama3.2)
        """
        self.model_name = model_name
        self.ollama_available = self._check_ollama_available()
    
    def _check_ollama_available(self) -> bool:
        """
        Check if Ollama is installed and available.
        
        Returns:
            True if Ollama is available, False otherwise
        """
        # First check if ollama Python package is installed
        if not OLLAMA_AVAILABLE:
            return False
        
        # Then check if Ollama service is running
        try:
            # Try to list models - this checks both package and service
            models = ollama.list()
            # Check if our model is available
            model_names = [model['name'] for model in models.get('models', [])]
            if self.model_name not in model_names:
                print(f"⚠️  Warning: Model '{self.model_name}' not found. Available models: {', '.join(model_names[:5])}")
                print(f"   Run: ollama pull {self.model_name}")
            return True
        except Exception as e:
            # Try alternative check via subprocess
            try:
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                return False
    
    def generate_with_ollama(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None
    ) -> Dict:
        """
        Generate story using local Ollama model.
        
        Args:
            prompt: User prompt for story generation
            system_instruction: Optional system instruction
        
        Returns:
            Dictionary with story and metadata
        """
        if not self.ollama_available:
            error_msg = "Ollama is not available. "
            if not OLLAMA_AVAILABLE:
                error_msg += "Please install: pip install ollama"
            else:
                error_msg += "Please ensure Ollama service is running and model is downloaded."
            return {
                "story": error_msg,
                "is_valid": False,
                "error": "Ollama not available",
                "fallback_used": False
            }
        
        try:
            # Construct the full prompt
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            
            print(f"🤖 Using Ollama model: {self.model_name}")
            print("⏳ Generating story (this may take 10-30 seconds)...")
            
            # Use Ollama Python API
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                options={
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "num_predict": 2000
                }
            )
            
            story = response.get('response', '').strip()
            
            if story:
                print("✅ Story generated successfully with Ollama")
                return {
                    "story": story,
                    "is_valid": True,
                    "fallback_used": True,
                    "model": self.model_name
                }
            else:
                print("⚠️  Ollama returned empty response")
                return {
                    "story": "Ollama generation returned empty response.",
                    "is_valid": False,
                    "error": "Empty response",
                    "fallback_used": True
                }
                
        except Exception as e:
            print(f"❌ Ollama generation error: {str(e)}")
            return {
                "story": f"Error using Ollama fallback: {str(e)}",
                "is_valid": False,
                "error": str(e),
                "fallback_used": True
            }
    
    def generate_story_with_fallback(self, user_request: str) -> Dict:
        """
        Generate a story with Ollama, using a story-specific prompt.
        
        Args:
            user_request: User's story request
        
        Returns:
            Dictionary with story and metadata
        """
        system_instruction = """You are a creative Storyteller Agent specialized in generating 
age-appropriate bedtime stories for children (ages 5-10). 

Generate engaging, positive, and educational stories with:
- Simple vocabulary suitable for ages 5-10
- Clear beginning, middle, and end
- Positive messages and values
- Age-appropriate themes
- Engaging characters and plot"""
        
        prompt = f"Generate a bedtime story based on this request: {user_request}"
        
        return self.generate_with_ollama(prompt, system_instruction)

