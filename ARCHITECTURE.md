# 🏗️ Hybrid Agentic Architecture

## Overview

This document describes the hybrid agentic architecture of the Bedtime Story Generator, highlighting the innovative Model Context Protocol (MCP) integration and the resilient Ollama fallback system.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                       │
│  (Streamlit UI / CLI)                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                         │
│  (StoryOrchestrator)                                         │
│  - Manages workflow                                          │
│  - Handles fallback logic                                    │
│  - Coordinates tool calls                                    │
└───────┬───────────────────────────────┬─────────────────────┘
        │                               │
        ▼                               ▼
┌───────────────────┐         ┌───────────────────┐
│  Primary Path      │         │  Fallback Path     │
│  (Gemini 2.5 Flash)│         │  (Ollama Local)    │
└───────┬────────────┘         └───────┬────────────┘
        │                               │
        ▼                               │
┌───────────────────────────────────────┴──────────────┐
│              Agent Layer                               │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │ Storyteller  │  │    Judge     │                   │
│  │   Agent      │  │    Agent     │                   │
│  └──────┬───────┘  └──────┬───────┘                   │
│         │                  │                           │
│         └──────────┬───────┘                           │
│                    │                                   │
│         ┌──────────▼──────────┐                        │
│         │   Refinement Loop    │                        │
│         └──────────────────────┘                        │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Integration Layer                          │
│  ┌──────────────┐         ┌──────────────┐                │
│  │  MCP Client  │────────▶│  MCP Server  │                │
│  │  (Tool Call) │         │  (Facts DB)  │                │
│  └──────────────┘         └──────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Orchestration Layer

**File**: `src/orchestration.py`

The `StoryOrchestrator` is the central coordinator that:

- **Manages the workflow**: Coordinates Storyteller → Judge → Refinement loop
- **Handles resilience**: Catches Gemini API failures and switches to Ollama
- **Enables MCP**: Configures tool calling for educational facts
- **Controls quality**: Enforces quality threshold (≥7.0) and max revisions (3)

**Key Methods**:
- `generate_story_with_judge()`: Main entry point
- `_generate_with_gemini()`: Primary generation path with MCP
- `_generate_with_fallback()`: Resilient fallback path

### 2. Agent Layer

**File**: `src/agents.py`

#### Storyteller Agent

- **Model**: Google Gemini 2.5 Flash (`gemini-2.0-flash-exp`)
- **System Instructions**: Configured for age-appropriate storytelling (ages 5-10)
- **Tool Integration**: Uses MCP client to call `get_educational_fact` when topics are mentioned
- **Generation Config**: Temperature 0.8, max 2000 tokens

#### Judge Agent

- **Model**: Google Gemini 2.5 Flash (same model, different persona)
- **System Instructions**: Configured as a story evaluator
- **Evaluation Criteria**:
  - Age-appropriateness
  - Educational value
  - Narrative quality
  - Safety and positive messaging
  - Engagement
  - Story structure
- **Scoring**: 1-10 scale, threshold at 7.0

### 3. MCP Integration Layer

**Files**: `src/mcp_server.py`, `src/mcp_client.py`

#### MCP Server

- **Framework**: FastMCP
- **Tool**: `get_educational_fact(topic: str)`
- **Knowledge Base**: Hardcoded educational facts about:
  - Space (Mars, Moon, Sun, Stars, Planets)
  - Dinosaurs (T-Rex, Triceratops, Brachiosaurus, Stegosaurus)
  - Animals (Elephants, Whales, Penguins, Lions, Dolphins)
  - Ocean (Coral, Sharks, Octopus)

**Innovation**: This is the key differentiator - the MCP server allows the Storyteller Agent to ground narratives in real-world facts, making stories both entertaining and educational.

#### MCP Client

- **Tool Calling Loop**: 
  1. Gemini receives prompt
  2. Detects need for educational facts
  3. Calls `get_educational_fact` tool
  4. Receives fact from MCP server
  5. Incorporates fact into story generation
  6. Returns final story

- **Max Iterations**: 3 tool call iterations to handle complex requests

### 4. Fallback Layer

**File**: `src/local_backup.py`

#### Ollama Backup

- **Purpose**: Resilience when Gemini API fails
- **Model**: Configurable (default: `llama3.2`)
- **Activation**: Automatic on Gemini API failure
- **Features**:
  - Checks Ollama availability
  - Generates stories with similar system instructions
  - Maintains story quality standards

**Resilience**: This ensures the system always works, even during:
- API outages
- Rate limiting
- Network issues
- API key problems

## Workflow Details

### Primary Workflow (Gemini + MCP)

1. **User Request** → Orchestrator receives story request
2. **Storyteller Activation** → Gemini Storyteller Agent activated
3. **Topic Detection** → Agent detects real-world topics (e.g., "Mars", "dinosaurs")
4. **MCP Tool Call** → Agent calls `get_educational_fact` tool
5. **Fact Retrieval** → MCP server returns educational fact
6. **Story Generation** → Agent incorporates fact into story
7. **Judge Evaluation** → Judge Agent scores story (1-10)
8. **Quality Check** → If score < 7.0, enter refinement loop
9. **Refinement** → Story refined based on judge feedback (max 3 iterations)
10. **Final Story** → Return approved story

### Fallback Workflow (Ollama)

1. **Gemini Failure** → API call fails or times out
2. **Fallback Activation** → Orchestrator switches to Ollama
3. **Local Generation** → Ollama generates story locally
4. **Simple Validation** → Basic validation (no judge for simplicity)
5. **Story Return** → Return story with fallback flag

## Design Decisions

### Why MCP?

**Innovation**: MCP allows agents to access external knowledge sources in a standardized way. For educational storytelling, this means:
- Stories are grounded in reality
- Facts are accurate and age-appropriate
- Extensible: Easy to add more knowledge sources
- Standardized: Works with any MCP-compatible agent

### Why Hybrid Architecture?

**Resilience**: Combining cloud (Gemini) and local (Ollama) provides:
- **Availability**: System works even during API outages
- **Privacy**: Local option for sensitive use cases
- **Cost**: Free tier Gemini + free local Ollama
- **Performance**: Fast local generation when needed

### Why Iterative Refinement?

**Quality**: The judge-refinement loop ensures:
- Consistent high-quality output
- Automatic improvement based on feedback
- Production-ready stories
- Educational value maintained

## Scalability Considerations

### Current Implementation

- **MCP Server**: Hardcoded facts (suitable for demo)
- **Ollama**: Single model (configurable)
- **Gemini**: Single API key (can be rate-limited)

### Future Enhancements

1. **MCP Server**:
   - Connect to external knowledge APIs (Wikipedia, educational databases)
   - Add vector database for semantic search
   - Support multiple knowledge domains

2. **Ollama**:
   - Model selection based on request complexity
   - Multiple model fallback chain
   - Model fine-tuning for storytelling

3. **Gemini**:
   - Multiple API keys for rate limit handling
   - Caching for common requests
   - Batch processing for multiple stories

## Security & Privacy

### API Keys
- Stored in `.env` file (not committed)
- Loaded via `python-dotenv`
- Never logged or exposed

### Local Fallback
- Ollama runs entirely locally
- No data sent to external services
- Privacy-preserving option

### Content Safety
- Age-appropriate system instructions
- Judge Agent validates safety
- Positive messaging enforced

## Performance Metrics

### Expected Performance

- **Gemini Generation**: ~2-5 seconds
- **MCP Tool Call**: <100ms (local)
- **Judge Evaluation**: ~1-3 seconds
- **Ollama Fallback**: ~5-15 seconds (depends on hardware)

### Optimization Opportunities

1. **Caching**: Cache common educational facts
2. **Parallel Processing**: Run judge evaluation in parallel
3. **Streaming**: Stream story generation for better UX
4. **Model Selection**: Use smaller models for simple requests

## Conclusion

This hybrid agentic architecture demonstrates:

1. **Innovation**: MCP integration for grounded, educational storytelling
2. **Resilience**: Automatic fallback ensures system availability
3. **Quality**: Iterative refinement loop ensures high-quality output
4. **Extensibility**: Modular design allows easy enhancements

The combination of cloud-based Gemini, local Ollama, and MCP tool integration creates a robust, educational, and resilient storytelling system.

