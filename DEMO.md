# 🎬 Demo Guide

## 📹 Demo Video

**Demo Video Link**: https://youtu.be/S0Szdqgfk5A

## Demo Script

### Introduction (0:00 - 0:30)
- Welcome to the Agentic Bedtime Story Generator
- Built for Google Agentic AI Hackathon
- Key features: Gemini 2.5 Flash, MCP integration, Ollama fallback

### Architecture Overview (0:30 - 1:00)
- Show architecture diagram
- Explain hybrid cloud + local architecture
- Highlight MCP as the innovation

### Live Demo (1:00 - 2:00)
1. Start Streamlit app
2. Enter request: "A story about a space adventure"
3. Show generation process
4. Display final story
5. Show metadata (score, revisions, tool calls)

### Live Demo - MCP Tool Calling (2:00 - 3:00)
1. Show console/logs with MCP tool calls
2. Highlight educational facts retrieved
3. Show how facts are woven into story

### Live Demo - Fallback (3:00 - 4:00)
1. Show Story Labs View
2. Show automatic fallback to Ollama
3. Generate story with local model
4. Highlight resilience feature

### Code Walkthrough (4:00 - 5:00)
- Show key files:
  - `mcp_server.py` - Educational facts tool
  - `mcp_client.py` - Tool calling integration
  - `orchestration.py` - Workflow management
  - `local_backup.py` - Fallback logic

### Conclusion (5:00 - 5:30)
- Recap key features
- Highlight innovation (MCP)
- Highlight resilience (Ollama fallback)
- Thank you

## Screenshots

Screenshots of the application are included in the repository:
- **Main Story Interface** (`images/Stories.png`): Shows the Streamlit UI with generated stories
- **MCP Observability** (`images/observability-mcp.png`): Demonstrates MCP tool calls and fact retrieval
- **Hyperparameter Tuning** (`images/hyperparameter-tuning.png`): Debug mode with advanced controls

## Key Points to Emphasize

1. **MCP Integration**: How educational facts are retrieved and used
2. **Automatic Fallback**: Seamless transition to Ollama
3. **Quality Assurance**: Judge-refinement loop in action
4. **Educational Value**: Stories grounded in real facts

---
