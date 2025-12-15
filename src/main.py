"""
Agentic Bedtime Story Generator
Entry point for the hackathon submission.
Supports both Streamlit UI and CLI modes.
"""

import os
import sys
from dotenv import load_dotenv
from orchestration import StoryOrchestrator

load_dotenv()


def print_welcome():
    """Print welcome message."""
    print("\n" + "="*60)
    print("🌙 AGENTIC BEDTIME STORY GENERATOR 🌙")
    print("   Powered by Gemini 2.5 Flash + MCP + Ollama Fallback")
    print("="*60)
    print("Features:")
    print("  ✨ Google Gemini 2.5 Flash for story generation")
    print("  🔧 Model Context Protocol (MCP) for educational facts")
    print("  🔄 Ollama fallback for resilience")
    print("  🎯 Iterative refinement with LLM judge")
    print("="*60 + "\n")


def cli_mode():
    """Run in command-line interface mode."""
    print_welcome()
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  WARNING: GEMINI_API_KEY not found.")
        print("   The system will use Ollama fallback only.")
        print("   To use Gemini, create a .env file with:")
        print("   GEMINI_API_KEY=your_key_here\n")
    
    # Initialize orchestrator
    try:
        orchestrator = StoryOrchestrator(
            enable_mcp=True,
            max_revisions=3,
            quality_threshold=7.0
        )
    except Exception as e:
        print(f"❌ Error initializing orchestrator: {e}")
        return
    
    # Get user input
    user_input = input("What kind of story do you want to hear? ")
    
    if not user_input.strip():
        print("No input provided. Using example request...")
        user_input = "A story about a child visiting Mars and learning about the red planet."
    
    # Generate story
    try:
        result = orchestrator.generate_story_with_judge(user_input)
        
        # Display final story
        print("\n" + "="*60)
        print("📖 FINAL STORY:")
        print("="*60)
        print(result["story"])
        print("="*60)
        
        # Display metadata
        print(f"\n📊 Story Quality Score: {result['judge_score']:.1f}/10")
        print(f"🔄 Revisions: {result['revision_count']}")
        print(f"✅ Meets Quality Threshold: {'Yes' if result['meets_quality_threshold'] else 'No'}")
        print(f"🤖 Model Used: {result.get('model_used', 'unknown')}")
        print(f"🔧 MCP Enabled: {'Yes' if result.get('mcp_enabled', False) else 'No'}")
        
        if result.get('tool_calls'):
            print(f"📚 Educational Facts Retrieved: {len(result['tool_calls'])}")
            for i, tool_call in enumerate(result['tool_calls'], 1):
                print(f"   {i}. {tool_call.get('function', 'unknown')} - {tool_call.get('arguments', {}).get('topic', 'N/A')}")
        
        if result.get('fallback_used'):
            print("⚠️  Fallback mode: Story generated using Ollama")
        
        # Show judge feedback summary
        if result.get('judge_feedback'):
            print("\n📝 Judge Feedback Summary:")
            feedback_lines = result['judge_feedback'].split('\n')[:5]
            for line in feedback_lines:
                if line.strip():
                    print(f"   {line}")
        
    except Exception as e:
        print(f"\n❌ Error generating story: {str(e)}")
        print("Please check your configuration and try again.")


def streamlit_mode():
    """Run in Streamlit UI mode."""
    try:
        import streamlit as st
        # Import and run the app
        from app import main
        main()
    except ImportError:
        print("Streamlit not installed. Install with: pip install streamlit")
        print("Running in CLI mode instead...")
        cli_mode()
        return


if __name__ == "__main__":
    # Check if running with streamlit
    if len(sys.argv) > 1 and sys.argv[1] == "streamlit":
        streamlit_mode()
    else:
        cli_mode()

