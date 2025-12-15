"""
Setup Verification Script
Run this script to verify your environment is properly configured before running main.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_python_version():
    """Check if Python version is 3.8+."""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} (Required: 3.8+)")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (Required: 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print_header("Checking Dependencies")
    required_packages = {
        'google.generativeai': 'google-generativeai',
        'fastmcp': 'fastmcp',
        'streamlit': 'streamlit',
        'dotenv': 'python-dotenv',
        'ollama': 'ollama'
    }
    
    all_installed = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            print_info(f"  Install with: pip install {package}")
            all_installed = False
    
    return all_installed

def check_env_file():
    """Check if .env file exists and has GEMINI_API_KEY."""
    print_header("Checking .env File")
    
    # Check if .env exists in src directory
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print_error(f".env file not found at: {env_path}")
        print_info("Creating .env file template...")
        try:
            with open(env_path, 'w') as f:
                f.write("# Google Gemini API Key\n")
                f.write("GEMINI_API_KEY=your_key_here\n")
            print_success(f".env file created at: {env_path}")
            print_warning("Please edit .env and add your GEMINI_API_KEY")
            return False
        except Exception as e:
            print_error(f"Could not create .env file: {e}")
            return False
    
    print_success(f".env file found at: {env_path}")
    
    # Load and check for API key
    load_dotenv(env_path)
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_key_here":
        print_error("GEMINI_API_KEY not set or is placeholder")
        print_info("Edit .env file and set: GEMINI_API_KEY=your_actual_key")
        return False
    else:
        # Mask the key for display
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print_success(f"GEMINI_API_KEY is set: {masked_key}")
        return True

def check_gemini_api():
    """Test Gemini API connection."""
    print_header("Testing Gemini API")
    
    try:
        import google.generativeai as genai
        load_dotenv(Path(__file__).parent / '.env')
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key or api_key == "your_key_here":
            print_warning("Skipping Gemini API test (no API key)")
            return False
        
        genai.configure(api_key=api_key)
        
        # Try to list models (lightweight test)
        try:
            models = genai.list_models()
            print_success("Gemini API connection successful")
            print_info(f"Available models: {len(list(models))} models")
            return True
        except Exception as e:
            print_error(f"Gemini API test failed: {str(e)}")
            print_info("This might be due to:")
            print_info("  - Invalid API key")
            print_info("  - Network connectivity issues")
            print_info("  - API quota exceeded")
            return False
            
    except ImportError:
        print_error("google-generativeai not installed")
        return False
    except Exception as e:
        print_error(f"Error testing Gemini API: {str(e)}")
        return False

def check_ollama():
    """Check if Ollama is installed and running."""
    print_header("Checking Ollama Fallback")
    
    # Check if ollama Python package is installed
    try:
        import ollama
        print_success("ollama Python package is installed")
    except ImportError:
        print_error("ollama Python package is NOT installed")
        print_info("Install with: pip install ollama")
        print_warning("Ollama fallback will not work without this package")
        return False
    
    # Check if Ollama service is running
    try:
        models_response = ollama.list()
        print_success("Ollama service is running")
        
        # Parse model list - ollama.list() returns a ListResponse object with a 'models' attribute
        model_names = []
        if hasattr(models_response, 'models'):
            # It's a ListResponse object
            model_list = models_response.models
            if isinstance(model_list, list) and len(model_list) > 0:
                # Each item is a Model object with a 'model' attribute (the name)
                for model_obj in model_list:
                    if hasattr(model_obj, 'model'):
                        model_name = model_obj.model
                        # Remove ':latest' suffix if present for cleaner display
                        if ':latest' in model_name:
                            model_name = model_name.replace(':latest', '')
                        model_names.append(model_name)
        elif isinstance(models_response, dict):
            # Fallback for dict format
            if 'models' in models_response:
                model_list = models_response['models']
                if isinstance(model_list, list) and len(model_list) > 0:
                    for model in model_list:
                        if isinstance(model, dict) and 'model' in model:
                            model_name = model['model']
                            if ':latest' in model_name:
                                model_name = model_name.replace(':latest', '')
                            model_names.append(model_name)
                        elif isinstance(model, dict) and 'name' in model:
                            model_name = model['name']
                            if ':latest' in model_name:
                                model_name = model_name.replace(':latest', '')
                            model_names.append(model_name)
        
        if model_names:
            print_info(f"Available models: {', '.join(model_names[:5])}")
            
            # Check for llama3.2 (default) - check both with and without :latest
            has_llama = any('llama3.2' in name.lower() for name in model_names)
            if has_llama:
                print_success("Default model 'llama3.2' is available")
            else:
                print_warning("Default model 'llama3.2' not found")
                print_info("Install with: ollama pull llama3.2")
            
            # Test generation with first available model (use full name with :latest if needed)
            test_model = models_response.models[0].model if hasattr(models_response, 'models') and len(models_response.models) > 0 else (model_names[0] if model_names else 'llama3.2')
            try:
                response = ollama.generate(
                    model=test_model,
                    prompt="Test",
                    options={'num_predict': 5}
                )
                print_success("Ollama generation test successful")
                return True
            except Exception as e:
                print_warning(f"Ollama generation test failed: {str(e)}")
                print_info("Ollama service may need to be restarted or model needs to be pulled")
                return False
        else:
            print_warning("No models found in Ollama")
            print_info("Install a model with: ollama pull llama3.2")
            return False
            
    except Exception as e:
        print_error(f"Ollama service is not running: {str(e)}")
        print_info("To start Ollama:")
        print_info("  1. Install Ollama from https://ollama.ai")
        print_info("  2. Start the Ollama service")
        print_info("  3. Pull a model: ollama pull llama3.2")
        return False

def check_mcp_server():
    """Check if MCP server can be imported."""
    print_header("Checking MCP Server")
    
    try:
        from mcp_server import _get_educational_fact_impl, EDUCATIONAL_FACTS, mcp
        print_success("MCP server module can be imported")
        
        # Test the core implementation function (not the decorated one)
        test_result = _get_educational_fact_impl("Mars")
        if test_result and "Mars" in test_result:
            print_success("MCP tool 'get_educational_fact' works correctly")
            print_info(f"Knowledge base contains {len(EDUCATIONAL_FACTS)} categories")
            
            # Test that the MCP server is properly configured
            try:
                # Check if the tool is registered with the MCP server
                tools = mcp.list_tools() if hasattr(mcp, 'list_tools') else []
                if tools or hasattr(mcp, 'tools'):
                    print_success("MCP server is properly configured")
                else:
                    print_warning("MCP server tools may not be registered")
            except:
                # If we can't check tools, that's okay - the function works
                pass
            
            return True
        else:
            print_warning("MCP tool returned unexpected result")
            return False
    except ImportError as e:
        print_error(f"Cannot import MCP server: {e}")
        return False
    except Exception as e:
        print_error(f"Error testing MCP server: {e}")
        return False

def check_file_structure():
    """Check if all required files exist."""
    print_header("Checking File Structure")
    
    required_files = [
        'main.py',
        'orchestration.py',
        'agents.py',
        'mcp_server.py',
        'mcp_client.py',
        'local_backup.py'
    ]
    
    all_exist = True
    src_dir = Path(__file__).parent
    
    for file in required_files:
        file_path = src_dir / file
        if file_path.exists():
            print_success(f"{file} exists")
        else:
            print_error(f"{file} is missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all checks."""
    print_header("🌙 Agentic Bedtime Story Generator - Setup Verification")
    
    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "File Structure": check_file_structure(),
        ".env File": check_env_file(),
        "MCP Server": check_mcp_server(),
        "Gemini API": check_gemini_api(),
        "Ollama Fallback": check_ollama()
    }
    
    # Summary
    print_header("Setup Summary")
    
    all_passed = True
    for check_name, passed in results.items():
        if passed:
            print_success(f"{check_name}: OK")
        else:
            print_error(f"{check_name}: FAILED")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print_success("All checks passed! You're ready to run main.py")
        print_info("Run with: python main.py")
    else:
        print_warning("Some checks failed. Please fix the issues above.")
        print_info("After fixing, run this script again to verify.")
    print("="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

