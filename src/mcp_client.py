"""
MCP Client Integration
Connects Gemini agents to the MCP server for tool calling.
"""

from typing import Dict, Optional, List
import google.generativeai as genai
from mcp_server import _get_educational_fact_impl


class MCPClient:
    """Client for integrating MCP tools with Gemini."""
    
    def __init__(self):
        """Initialize MCP client with available tools."""
        self.tools = self._create_tools()
    
    def _create_tools(self) -> List:
        """
        Create Gemini-compatible tool definitions from MCP functions.
        
        Returns:
            List of tool definitions for Gemini
        """
        # Define the educational fact tool for Gemini
        educational_fact_tool = {
            "function_declarations": [
                {
                    "name": "get_educational_fact",
                    "description": "Retrieves an educational fact about a given topic (e.g., Mars, T-Rex, Elephants, Space, Dinosaurs, Animals). Use this tool when the user mentions real-world topics to ground the story in accurate educational information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The topic to get an educational fact about (e.g., 'Mars', 'T-Rex', 'Elephants', 'Space', 'Dinosaurs')"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            ]
        }
        
        return [educational_fact_tool]
    
    def execute_tool_call(self, function_name: str, arguments: Dict) -> str:
        """
        Execute an MCP tool call.
        
        Args:
            function_name: Name of the function to call
            arguments: Arguments for the function
        
        Returns:
            Result from the tool execution
        """
        if function_name == "get_educational_fact":
            topic = arguments.get("topic", "")
            return _get_educational_fact_impl(topic)
        else:
            return f"Unknown tool: {function_name}"
    
    def process_with_tools(
        self, 
        model: genai.GenerativeModel,
        prompt: str,
        max_iterations: int = 3
    ) -> Dict:
        """
        Process a prompt with tool calling support.
        Handles the loop: Prompt -> Tool Call -> Execute -> Feed back to model.
        
        Args:
            model: Gemini model instance
            prompt: User prompt
            max_iterations: Maximum number of tool call iterations
        
        Returns:
            Dictionary with final story and tool call history
        """
        conversation_history = []
        tool_call_history = []
        
        current_prompt = prompt
        
        for iteration in range(max_iterations):
            try:
                # Generate content with tools
                if iteration == 0:
                    print("   Calling Gemini API...")
                response = model.generate_content(
                    current_prompt,
                    tools=self.tools,
                    generation_config={
                        "temperature": 0.8,
                        "max_output_tokens": 2000,
                    }
                )
                
                # Check if the response contains function calls
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    
                    # Check for function calls
                    function_calls = []
                    text_parts = []
                    
                    # Handle different response structures
                    if hasattr(candidate, 'content') and candidate.content:
                        parts = candidate.content.parts
                        
                        # Check if parts is not None and is iterable
                        if parts is not None:
                            for part in parts:
                                if hasattr(part, 'function_call') and part.function_call:
                                    function_calls.append(part.function_call)
                                elif hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                    
                    # Also check for function_calls directly on candidate
                    if hasattr(candidate, 'function_calls') and candidate.function_calls:
                        function_calls.extend(candidate.function_calls)
                    
                    # If no parts but we have text, use response.text
                    if not text_parts and not function_calls and hasattr(response, 'text') and response.text:
                        text_parts = [response.text]
                        
                        # If we have function calls, execute them
                        if function_calls:
                            tool_results = []
                            
                            for func_call in function_calls:
                                try:
                                    # Handle different function call structures
                                    if hasattr(func_call, 'name'):
                                        func_name = func_call.name
                                    elif isinstance(func_call, dict):
                                        func_name = func_call.get('name', 'unknown')
                                    else:
                                        func_name = str(func_call)
                                    
                                    # Extract arguments
                                    if hasattr(func_call, 'args'):
                                        func_args = dict(func_call.args) if func_call.args else {}
                                    elif isinstance(func_call, dict):
                                        func_args = func_call.get('args', {})
                                    else:
                                        func_args = {}
                                    
                                    print(f"   🔧 Calling MCP tool: {func_name} with topic: {func_args.get('topic', 'N/A')}")
                                    
                                    # Execute the tool
                                    result = self.execute_tool_call(func_name, func_args)
                                    
                                    tool_results.append({
                                        "function_name": func_name,
                                        "arguments": func_args,
                                        "result": result
                                    })
                                    
                                    tool_call_history.append({
                                        "iteration": iteration + 1,
                                        "function": func_name,
                                        "arguments": func_args,
                                        "result": result
                                    })
                                except Exception as e:
                                    print(f"   ⚠️  Error executing tool: {str(e)}")
                                    tool_results.append({
                                        "function_name": func_name if 'func_name' in locals() else 'unknown',
                                        "arguments": func_args if 'func_args' in locals() else {},
                                        "result": f"Error: {str(e)}"
                                    })
                            
                            # Create follow-up prompt with tool results
                            results_text = "\n\n".join([
                                f"Tool '{r['function_name']}' returned: {r['result']}"
                                for r in tool_results
                            ])
                            
                            current_prompt = f"""{prompt}

Here are the educational facts I retrieved:
{results_text}

Please now generate the story incorporating these facts naturally into the narrative."""
                            
                            # Continue to next iteration
                            continue
                        else:
                            # No function calls, we have the final story
                            if text_parts:
                                final_story = " ".join(text_parts)
                            elif hasattr(response, 'text') and response.text:
                                final_story = response.text
                            else:
                                final_story = "Story generation completed."
                            
                            return {
                                "story": final_story,
                                "tool_calls": tool_call_history,
                                "iterations": iteration + 1,
                                "is_valid": True
                            }
                    else:
                        # No content.parts, try direct text access
                        if hasattr(response, 'text') and response.text:
                            return {
                                "story": response.text,
                                "tool_calls": tool_call_history,
                                "iterations": iteration + 1,
                                "is_valid": True
                            }
                        else:
                            # Try to get text from candidate
                            if hasattr(candidate, 'text') and candidate.text:
                                return {
                                    "story": candidate.text,
                                    "tool_calls": tool_call_history,
                                    "iterations": iteration + 1,
                                    "is_valid": True
                                }
                else:
                    # Fallback to text response
                    if hasattr(response, 'text') and response.text:
                        return {
                            "story": response.text,
                            "tool_calls": tool_call_history,
                            "iterations": 1,
                            "is_valid": True
                        }
                    else:
                        return {
                            "story": "Error: Could not extract story from response",
                            "tool_calls": tool_call_history,
                            "iterations": 1,
                            "is_valid": False,
                            "error": "No text in response"
                        }
                    
            except Exception as e:
                return {
                    "story": f"Error during tool processing: {str(e)}",
                    "tool_calls": tool_call_history,
                    "error": str(e),
                    "is_valid": False
                }
        
        # If we've exhausted iterations, return the last response
        return {
            "story": "Story generation completed with tool assistance.",
            "tool_calls": tool_call_history,
            "iterations": max_iterations,
            "is_valid": True
        }

