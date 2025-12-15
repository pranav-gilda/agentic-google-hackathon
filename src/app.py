"""
Streamlit UI for Agentic Bedtime Story Generator
Provides User View, Story History, and Debug View with MCP integration.
Kid-friendly storybook design with bedtime theme.
"""

import streamlit as st
import os
import html
from datetime import datetime
from dotenv import load_dotenv
from orchestration import StoryOrchestrator
from mcp_server import EDUCATIONAL_FACTS, _get_educational_fact_impl
from mcp_expander import MCPExpander
from fact_checker import FactChecker
from parent_config import PERSONAS, VALUES, INTERESTS, DEFAULT_PARENT_SETTINGS
from config import STORY_CONFIG, JUDGE_CONFIG, GUARDRAIL_CONFIG
from database import StoryDatabase

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🌙 Bedtime Story Generator",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for storybook theme
st.markdown("""
<style>
    /* Storybook Theme - Kid-friendly but bedtime appropriate */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One:wght@400&family=Comfortaa:wght@300;400;500;600;700&family=Patrick+Hand&display=swap');
    
    /* Main background - soothing bedtime colors (darker for readability) */
    .stApp {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 25%, #1a202c 50%, #2d3748 75%, #4a5568 100%);
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Story container - storybook page (softer, more readable) */
    .story-container {
        background: linear-gradient(to bottom, #f7f3e9 0%, #ede8d8 100%);
        border-radius: 20px;
        padding: 40px;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        border: 3px solid #d4af37;
        position: relative;
        font-family: 'Comfortaa', cursive;
    }
    
    .story-container::before {
        content: "📖";
        position: absolute;
        top: -15px;
        left: 20px;
        font-size: 40px;
        background: #f7f3e9;
        padding: 5px 15px;
        border-radius: 50%;
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
    }
    
    /* Story text styling (blue bedtime text) */
    .story-text {
        font-family: 'Comfortaa', cursive;
        font-size: 1.3em;
        line-height: 1.8;
        color: #2c5282; /* Blue bedtime text color */
        text-align: justify;
        padding: 20px;
        background: transparent; /* Use cream from parent container */
        border-radius: 15px;
    }
    
    .story-text p {
        color: #2c5282; /* Blue bedtime text color */
        margin-bottom: 1em;
    }
    
    /* Headers (better contrast) */
    h1 {
        font-family: 'Fredoka One', cursive !important;
        color: #f7fafc !important;
        text-shadow: 3px 3px 8px rgba(0,0,0,0.5);
        font-size: 3em !important;
        margin-bottom: 10px !important;
    }
    
    h2 {
        font-family: 'Fredoka One', cursive !important;
        color: #f7fafc !important;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.5);
        font-size: 2em !important;
    }
    
    h3 {
        font-family: 'Comfortaa', cursive !important;
        color: #e2e8f0 !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
        font-size: 1.5em !important;
    }
    
    /* Buttons (softer, more readable) */
    .stButton > button {
        font-family: 'Comfortaa', cursive !important;
        font-weight: 600 !important;
        font-size: 1.2em !important;
        background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%) !important;
        color: #ffffff !important;
        border: 2px solid #4c51bf !important;
        border-radius: 25px !important;
        padding: 15px 40px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4) !important;
    }
    
    /* Cards and containers */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar (darker for contrast) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%) !important;
        border-right: 3px solid #d4af37;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        font-family: 'Comfortaa', cursive !important;
        font-size: 1.1em !important;
        color: #f7fafc !important;
        font-weight: 500 !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    
    /* Text inputs (cream background with black text) */
    .stTextArea > div > div > textarea {
        font-family: 'Comfortaa', cursive !important;
        font-size: 1.1em !important;
        border-radius: 15px !important;
        border: 2px solid #d4af37 !important;
        background: #f7f3e9 !important;
        color: #1a202c !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #4a5568 !important;
        opacity: 0.7 !important;
    }
    
    /* Text input labels */
    .stTextArea label {
        font-family: 'Comfortaa', cursive !important;
        font-weight: 600 !important;
        color: #f7fafc !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    
    /* Text input (single line) */
    .stTextInput > div > div > input {
        font-family: 'Comfortaa', cursive !important;
        font-size: 1.1em !important;
        border-radius: 15px !important;
        border: 2px solid #d4af37 !important;
        background: #f7f3e9 !important;
        color: #1a202c !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #4a5568 !important;
        opacity: 0.7 !important;
    }
    
    .stTextInput label {
        font-family: 'Comfortaa', cursive !important;
        font-weight: 600 !important;
        color: #f7fafc !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    
    /* Select boxes (better contrast) */
    .stSelectbox label {
        font-family: 'Comfortaa', cursive !important;
        font-weight: 600 !important;
        color: #f7fafc !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Fredoka One', cursive !important;
        font-size: 2em !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Comfortaa', cursive !important;
        font-weight: 600 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-family: 'Comfortaa', cursive !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
    }
    
    /* Info boxes (better contrast) */
    .stInfo {
        background: linear-gradient(135deg, #bee3f8 0%, #cbd5e0 100%) !important;
        border-left: 5px solid #5a67d8 !important;
        border-radius: 10px !important;
        font-family: 'Comfortaa', cursive !important;
        color: #1a202c !important;
    }
    
    /* Success boxes (better contrast) */
    .stSuccess {
        background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%) !important;
        border-left: 5px solid #38a169 !important;
        border-radius: 10px !important;
        font-family: 'Comfortaa', cursive !important;
        color: #1a202c !important;
    }
    
    /* Warning boxes (better contrast) */
    .stWarning {
        background: linear-gradient(135deg, #fefcbf 0%, #faf089 100%) !important;
        border-left: 5px solid #d69e2e !important;
        border-radius: 10px !important;
        font-family: 'Comfortaa', cursive !important;
        color: #1a202c !important;
    }
    
    /* Error boxes (better contrast) */
    .stError {
        background: linear-gradient(135deg, #fed7d7 0%, #fc8181 100%) !important;
        border-left: 5px solid #e53e3e !important;
        border-radius: 10px !important;
        font-family: 'Comfortaa', cursive !important;
        color: #1a202c !important;
    }
    
    /* Story display special styling (softer, more readable) */
    .story-display {
        background: linear-gradient(to bottom, #f7f3e9 0%, #ede8d8 50%, #e8e0c8 100%);
        border-radius: 25px;
        padding: 50px;
        margin: 30px 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.4);
        border: 4px solid #d4af37;
        position: relative;
        font-family: 'Comfortaa', cursive;
    }
    
    .story-display::before {
        content: "✨";
        position: absolute;
        top: -20px;
        left: 30px;
        font-size: 50px;
        background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%);
        padding: 10px 20px;
        border-radius: 50%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
        border: 2px solid #4c51bf;
    }
    
    .story-display::after {
        content: "🌙";
        position: absolute;
        top: -20px;
        right: 30px;
        font-size: 50px;
        background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%);
        padding: 10px 20px;
        border-radius: 50%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
        border: 2px solid #4c51bf;
    }
    
    .story-content {
        font-family: 'Comfortaa', cursive;
        font-size: 1.4em;
        line-height: 2;
        color: #2c5282; /* Blue bedtime text color */
        text-align: justify;
        padding: 30px;
        background: transparent; /* Remove white background, use cream from parent */
        border-radius: 20px;
        margin-top: 20px;
        width: 100%;
        box-sizing: border-box;
        overflow-wrap: break-word;
        word-wrap: break-word;
    }
    
    .story-content p {
        color: #2c5282; /* Blue bedtime text color */
        margin-bottom: 1em;
        font-size: 1.2em;
        line-height: 1.8;
    }
    
    /* Decorative elements */
    .star-decoration {
        font-size: 2em;
        animation: twinkle 2s infinite;
    }
    
    @keyframes twinkle {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Comfortaa', cursive !important;
        font-weight: 600 !important;
        color: white !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    """Get or create database instance."""
    return StoryDatabase()

db = get_database()

# Initialize session state
if "stories" not in st.session_state:
    # Load stories from database
    try:
        st.session_state.stories = db.get_all_stories()
    except Exception as e:
        st.session_state.stories = []
        st.warning(f"⚠️ Could not load stories from database: {e}")

if "parent_settings" not in st.session_state:
    st.session_state.parent_settings = DEFAULT_PARENT_SETTINGS.copy()
if "tuning_config" not in st.session_state:
    st.session_state.tuning_config = {
        "storyteller_temperature": STORY_CONFIG["storyteller_temperature"],
        "judge_temperature": JUDGE_CONFIG["judge_temperature"],
        "max_tokens": STORY_CONFIG["max_story_tokens"],
        "strictness": JUDGE_CONFIG["strictness_level"],
        "min_score": JUDGE_CONFIG["minimum_acceptance_score"]
    }

def main():
    """Main Streamlit application."""
    
    # Sidebar for mode selection
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 2em; margin-bottom: 10px;">🌙✨</h1>
        <h2 style="font-size: 1.5em; margin-bottom: 5px;">Story Magic</h2>
        <p style="font-size: 0.9em; opacity: 0.9;">Powered by AI 🚀</p>
    </div>
    """, unsafe_allow_html=True)
    
    mode = st.sidebar.radio(
        "📖 Choose Your Adventure",
        ["👤 Create Story", "📚 Story Library", "🔧 Story Lab"],
        help="Create Story: Make new stories\nStory Library: Read past stories\nStory Lab: Advanced settings"
    )
    
    # Map to internal names
    mode_map = {
        "👤 Create Story": "👤 User View",
        "📚 Story Library": "📚 Story History",
        "🔧 Story Lab": "🔧 Debug Tuning"
    }
    actual_mode = mode_map.get(mode, mode)
    
    # Sidebar info
    with st.sidebar.expander("✨ About This Magic"):
        st.markdown("""
        **🌟 Features:**
        - ✨ Smart AI Storytelling
        - 🔧 Educational Facts
        - 🔄 Always Works
        - 🎯 Perfect Stories
        - 🎨 Kid-Friendly Design
        """)
    
    if actual_mode == "👤 User View":
        user_view()
    elif actual_mode == "📚 Story History":
        story_history_view()
    else:
        debug_view()

def user_view():
    """User-friendly interface for parents and kids."""
    # Header with emojis
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1>🌙✨ Bedtime Story Magic ✨🌙</h1>
        <p style="font-size: 1.3em; color: #f7fafc; font-family: 'Comfortaa', cursive; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            Create magical stories for children aged 5-10 🎈🎨🎭
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Tip:** Mention real-world topics (like 'Mars' 🚀, 'dinosaurs' 🦕, 'elephants' 🐘) to get educational facts woven into the story!")
    
    # Parent Settings Section
    with st.expander("🎨✨ Story Preferences (Make it Special!) ✨🎨", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Persona selection
            persona_options = {k: v["name"] + " - " + v["description"] for k, v in PERSONAS.items()}
            selected_persona = st.selectbox(
                "Story Style",
                options=list(persona_options.keys()),
                format_func=lambda x: persona_options[x],
                index=list(persona_options.keys()).index(st.session_state.parent_settings.get("persona", "balanced_storyteller"))
            )
            
            # Values selection
            value_options = {k: v["name"] for k, v in VALUES.items()}
            selected_values = st.multiselect(
                "Values to Emphasize",
                options=list(value_options.keys()),
                format_func=lambda x: value_options[x],
                default=st.session_state.parent_settings.get("values", ["kindness", "friendship"])
            )
        
        with col2:
            # Interests selection
            interest_options = {k: v["name"] for k, v in INTERESTS.items()}
            selected_interests = st.multiselect(
                "Interests to Include",
                options=list(interest_options.keys()),
                format_func=lambda x: interest_options[x],
                default=st.session_state.parent_settings.get("interests", [])
            )
            
            # Optional child name
            child_name = st.text_input(
                "Child's Name (Optional)",
                value=st.session_state.parent_settings.get("child_name", ""),
                help="If provided, may be used in character names"
            )
        
        # Custom elements
        custom_elements = st.text_area(
            "Additional Elements (Optional)",
            value=st.session_state.parent_settings.get("custom_elements", ""),
            help="Any other elements you'd like included (e.g., 'include a magical garden')",
            height=80
        )
        
        # Update session state
        st.session_state.parent_settings = {
            "persona": selected_persona,
            "values": selected_values,
            "interests": selected_interests,
            "child_name": child_name,
            "custom_elements": custom_elements
        }
    
    # Story Request Section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2>📖✨ What story would you like to hear? ✨📖</h2>
        <p style="font-size: 1.2em; color: #e2e8f0; font-family: 'Comfortaa', cursive; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">
            Tell us your dream story and we'll make it come true! 🎭🎪
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Example requests with emojis
    example_requests = [
        "🚀 A story about a child visiting Mars",
        "🦕 An adventure with dinosaurs",
        "🐋 A story about ocean animals",
        "✨ A magical space adventure",
        "🦁 A story about brave animals",
        "🏰 A princess adventure"
    ]
    
    selected_example = st.selectbox("🌟 Or choose a magical example:", [""] + example_requests)
    
    user_request = st.text_area(
        "Story Request",
        value=selected_example if selected_example else "",
        height=100,
        placeholder="Tell me what kind of story you want... (e.g., 'A story about a child visiting Mars and learning about the red planet')"
    )
    
    # Configuration
    with st.expander("⚙️ Advanced Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            enable_mcp = st.checkbox("Enable MCP (Educational Facts)", value=True, help="Automatically fetch educational facts for real-world topics")
            max_revisions = st.slider("Max Revisions", 1, 5, 3, help="Maximum refinement iterations")
        with col2:
            quality_threshold = st.slider("Quality Threshold", 1.0, 10.0, 7.0, 0.5, help="Minimum score for story approval")
    
    # Generate button with emoji
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("✨🌟 Create My Magical Story! 🌟✨", type="primary", use_container_width=True)
    
    if generate_button and user_request.strip():
        import time
        start_time = time.time()
        
        with st.spinner("✨ Creating your magical story..."):
            try:
                orchestrator = StoryOrchestrator(
                    enable_mcp=enable_mcp,
                    max_revisions=max_revisions,
                    quality_threshold=quality_threshold,
                    parent_settings=st.session_state.parent_settings,
                    storyteller_temperature=st.session_state.tuning_config.get("storyteller_temperature"),
                    judge_temperature=st.session_state.tuning_config.get("judge_temperature"),
                    max_story_tokens=st.session_state.tuning_config.get("max_tokens")
                )
                result = orchestrator.generate_story_with_judge(user_request)
                
                # Add timestamp and metadata
                result['timestamp'] = datetime.now().isoformat()
                result['storyteller_temperature'] = st.session_state.tuning_config.get("storyteller_temperature")
                result['judge_temperature'] = st.session_state.tuning_config.get("judge_temperature")
                result['max_story_tokens'] = st.session_state.tuning_config.get("max_tokens")
                result['quality_threshold'] = quality_threshold
                result['max_revisions'] = max_revisions
                result['parent_settings'] = st.session_state.parent_settings
                
                # Save to database
                try:
                    story_id = db.save_story(result)
                    result['db_id'] = story_id
                except Exception as db_error:
                    st.warning(f"⚠️ Story generated but could not save to database: {db_error}")
                
                # Save successful run
                generation_time = time.time() - start_time
                try:
                    db.save_run({
                        'timestamp': result['timestamp'],
                        'user_request': user_request,
                        'success': True,
                        'model_used': result.get('model_used', 'unknown'),
                        'generation_time_seconds': generation_time,
                        'mcp_enabled': enable_mcp,
                        'fallback_used': result.get('fallback_used', False)
                    })
                except:
                    pass  # Run saving is optional
                
                # Store in session
                st.session_state.stories.append(result)
                
                # Display story with beautiful header
                st.markdown("---")
                st.markdown("""
                <div style="text-align: center; padding: 30px;">
                    <h2>📖✨ Your Magical Story is Ready! ✨📖</h2>
                    <p style="font-size: 1.3em; color: #e2e8f0; font-family: 'Comfortaa', cursive; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">
                        Get cozy and enjoy! 🛏️💤
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Metadata with emojis
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("⭐ Quality", f"{result['judge_score']:.1f}/10")
                with col2:
                    st.metric("🔄 Revisions", result['revision_count'])
                with col3:
                    model_emoji = "🤖" if "gemini" in result.get('model_used', '').lower() else "🦙"
                    st.metric(f"{model_emoji} Model", result.get('model_used', 'unknown')[:10])
                with col4:
                    mcp_status = "✅" if result.get('mcp_enabled') else "❌"
                    st.metric("🔧 MCP", mcp_status)
                with col5:
                    fallback_emoji = "🔄" if result.get('fallback_used') else "✨"
                    st.metric("⚡ Mode", fallback_emoji)
                
                # Tool calls info with verification
                if result.get('tool_calls'):
                    verified_count = sum(1 for tc in result['tool_calls'] if tc.get('verification', {}).get('is_verified'))
                    with st.expander(f"🔧 Educational Facts Retrieved ({len(result['tool_calls'])} facts, {verified_count} verified)"):
                        for i, tool_call in enumerate(result['tool_calls'], 1):
                            topic = tool_call.get('arguments', {}).get('topic', tool_call.get('original_topic', 'N/A'))
                            verification = tool_call.get('verification')
                            
                            # Show verification badge
                            if verification and verification.get('is_verified'):
                                st.success(f"**{i}. {topic.title()}** ✓ Verified")
                            else:
                                st.info(f"**{i}. {topic.title()}**")
                            
                            # Show fact
                            fact_preview = tool_call.get('result', 'N/A')
                            st.write(f"   {fact_preview}")
                            
                            # Show verification details if available
                            if verification:
                                with st.expander(f"Verification Details for {topic}"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Accuracy Score", f"{verification.get('score', 0):.1f}/10")
                                        st.write(f"**Verdict:** {verification.get('verdict', 'N/A')}")
                                    with col2:
                                        st.write(f"**Age Appropriate:** {'✅ Yes' if verification.get('age_appropriate') else '❌ No'}")
                                        if verification.get('concerns'):
                                            st.warning(f"**Concerns:** {verification.get('concerns')}")
                            
                            st.markdown("---")
                
                # Beautiful story display - everything inside the cream/golden box
                st.markdown("---")
                
                # Format story - EXACT SAME AS HISTORY VIEW
                if result.get('story'):
                    story_escaped = html.escape(result['story'])
                    story_lines = story_escaped.split('\n')
                    story_formatted = ""
                    for line in story_lines:
                        if line.strip():
                            story_formatted += f"<p style='margin-bottom: 1em; font-size: 1.2em; line-height: 1.8; color: #2c5282;'>{line.strip()}</p>"
                        else:
                            story_formatted += "<br>"
                    
                    # Add play button for text-to-speech (only for Gemini stories)
                    is_gemini = "gemini" in result.get('model_used', '').lower()
                    if is_gemini:
                        story_id = f"story_{len(st.session_state.stories)}"
                        import json
                        story_text_js = json.dumps(result['story'])
                        
                        # Render play button first, inside the box - NO onclick, use event listeners
                        st.markdown(f"""
                        <div class="story-display">
                            <div class="story-content">
                                <div style="text-align: center; margin-bottom: 30px;">
                                    <button id="playStoryBtn_{story_id}" style="
                                        background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%);
                                        color: white;
                                        border: 2px solid #4c51bf;
                                        border-radius: 25px;
                                        padding: 15px 40px;
                                        font-family: 'Comfortaa', cursive;
                                        font-size: 1.2em;
                                        font-weight: 600;
                                        cursor: pointer;
                                        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
                                    ">
                                        ▶️ Listen to Story
                                    </button>
                                    <button id="stopStoryBtn_{story_id}" style="
                                        background: linear-gradient(135deg, #e53e3e 0%, #fc8181 100%);
                                        color: white;
                                        border: 2px solid #c53030;
                                        border-radius: 25px;
                                        padding: 15px 40px;
                                        font-family: 'Comfortaa', cursive;
                                        font-size: 1.2em;
                                        font-weight: 600;
                                        cursor: pointer;
                                        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
                                        margin-left: 10px;
                                        display: none;
                                    ">
                                        ⏹️ Stop
                                    </button>
                                </div>
                                {story_formatted}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add script for text-to-speech - use event listeners, not onclick
                        st.markdown(f"""
                        <script>
                        (function() {{
                            let synth_{story_id} = window.speechSynthesis;
                            let utterance_{story_id} = null;
                            const storyText_{story_id} = {story_text_js};
                            
                            function playStory_{story_id}() {{
                                console.log('Play button clicked');
                                if (synth_{story_id}.speaking) synth_{story_id}.cancel();
                                utterance_{story_id} = new SpeechSynthesisUtterance(storyText_{story_id});
                                utterance_{story_id}.rate = 0.9;
                                utterance_{story_id}.pitch = 1.0;
                                utterance_{story_id}.volume = 1.0;
                                let voices = synth_{story_id}.getVoices();
                                let voice = voices.find(v => v.name.includes('Google') || v.name.includes('Microsoft')) || voices.find(v => v.lang.startsWith('en')) || voices[0];
                                if (voice) utterance_{story_id}.voice = voice;
                                synth_{story_id}.speak(utterance_{story_id});
                                document.getElementById('playStoryBtn_{story_id}').style.display = 'none';
                                document.getElementById('stopStoryBtn_{story_id}').style.display = 'inline-block';
                                utterance_{story_id}.onend = function() {{
                                    document.getElementById('playStoryBtn_{story_id}').style.display = 'inline-block';
                                    document.getElementById('stopStoryBtn_{story_id}').style.display = 'none';
                                }};
                            }}
                            
                            function stopStory_{story_id}() {{
                                console.log('Stop button clicked');
                                synth_{story_id}.cancel();
                                document.getElementById('playStoryBtn_{story_id}').style.display = 'inline-block';
                                document.getElementById('stopStoryBtn_{story_id}').style.display = 'none';
                            }}
                            
                            // Wait for DOM and attach event listeners
                            function init_{story_id}() {{
                                let playBtn = document.getElementById('playStoryBtn_{story_id}');
                                let stopBtn = document.getElementById('stopStoryBtn_{story_id}');
                                if (playBtn && stopBtn) {{
                                    playBtn.addEventListener('click', playStory_{story_id});
                                    stopBtn.addEventListener('click', stopStory_{story_id});
                                }} else {{
                                    setTimeout(init_{story_id}, 100);
                                }}
                            }}
                            
                            if (document.readyState === 'loading') {{
                                document.addEventListener('DOMContentLoaded', init_{story_id});
                            }} else {{
                                init_{story_id}();
                            }}
                        }})();
                        </script>
                        """, unsafe_allow_html=True)
                    else:
                        # No play button, just story - EXACT SAME AS HISTORY VIEW
                        st.markdown(f"""
                        <div class="story-display">
                            <div class="story-content">
                                {story_formatted}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Decorative stars
                    st.markdown("""
                    <div style="text-align: center; padding: 20px;">
                        <span class="star-decoration">⭐</span>
                        <span class="star-decoration" style="animation-delay: 0.5s;">✨</span>
                        <span class="star-decoration" style="animation-delay: 1s;">🌟</span>
                        <span class="star-decoration" style="animation-delay: 1.5s;">💫</span>
                        <span class="star-decoration" style="animation-delay: 2s;">⭐</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Success indicators
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        threshold_status = "✅ Met" if result['meets_quality_threshold'] else "⚠️ Below"
                        st.success(f"Quality Threshold: {threshold_status}")
                    with col2:
                        if result.get('fallback_used'):
                            st.info("🔄 Generated with Ollama fallback")
                        else:
                            st.success("✨ Generated with Gemini")
                    with col3:
                        if result.get('mcp_enabled') and result.get('tool_calls'):
                            st.success(f"🔧 MCP: {len(result['tool_calls'])} facts used")
                        elif result.get('mcp_enabled'):
                            st.info("🔧 MCP: Enabled (no facts needed)")
                        else:
                            st.warning("🔧 MCP: Disabled")
                
            except Exception as e:
                # Save failed run
                generation_time = time.time() - start_time
                try:
                    db.save_run({
                        'timestamp': datetime.now().isoformat(),
                        'user_request': user_request,
                        'success': False,
                        'error_message': str(e),
                        'generation_time_seconds': generation_time,
                        'mcp_enabled': enable_mcp,
                        'fallback_used': False
                    })
                except:
                    pass
                
                # Display beautiful error message
                st.markdown("---")
                st.markdown("""
                <div style="text-align: center; padding: 30px;">
                    <h2>😔 Oops! Something went wrong</h2>
                    <p style="font-size: 1.2em; color: #e2e8f0; font-family: 'Comfortaa', cursive;">
                        We couldn't create your story right now. Please try again! 🌟
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🔍 Technical Details (for debugging)", expanded=False):
                    st.error(f"Error: {str(e)}")
                    st.info("💡 Tips:\n- Check your GEMINI_API_KEY in .env file\n- Ensure Ollama is running if using fallback\n- Try a simpler story request")
                
                st.stop()  # Stop execution on error
    
    elif generate_button:
        st.warning("⚠️ Please enter a story request!")

def story_history_view():
    """View past stories with search and filtering."""
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1>📚✨ Your Story Library ✨📚</h1>
        <p style="font-size: 1.3em; color: #e2e8f0; font-family: 'Comfortaa', cursive; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">
            All your magical stories in one place! 🎪🎨
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load stories from database
    try:
        db_stories = db.get_all_stories()
        # Update session state with database stories (merge, avoid duplicates)
        existing_ids = {s.get('db_id') for s in st.session_state.stories if 'db_id' in s}
        for db_story in db_stories:
            if db_story.get('id') not in existing_ids:
                db_story['db_id'] = db_story.get('id')
                st.session_state.stories.append(db_story)
    except Exception as e:
        st.warning(f"⚠️ Could not load stories from database: {e}")
    
    if not st.session_state.stories:
        st.info("📖 No stories generated yet. Generate some stories in User View first! ✨")
        return
    
    # Statistics Dashboard
    try:
        stats = db.get_statistics()
    except:
        stats = {}
    
    with st.expander("📊 Statistics Dashboard", expanded=True):
        total_stories = stats.get('total_stories', len(st.session_state.stories))
        avg_score = stats.get('average_judge_score', sum(s['judge_score'] for s in st.session_state.stories) / len(st.session_state.stories) if st.session_state.stories else 0)
        stories_meeting_threshold = sum(1 for s in st.session_state.stories if s['meets_quality_threshold'])
        avg_revisions = sum(s['revision_count'] for s in st.session_state.stories) / len(st.session_state.stories) if st.session_state.stories else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Stories", total_stories)
        with col2:
            st.metric("Average Score", f"{avg_score:.1f}/10")
        with col3:
            st.metric("Quality Threshold Met", stories_meeting_threshold)
        with col4:
            st.metric("Avg Revisions", f"{avg_revisions:.1f}")
    
    # Search and Filter
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search Stories", placeholder="Search by request or story content...")
    
    with col2:
        min_score_filter = st.slider("Minimum Score", 0.0, 10.0, 0.0, 0.5)
    
    # Filter stories
    filtered_stories = st.session_state.stories
    if search_query:
        filtered_stories = [
            s for s in filtered_stories
            if search_query.lower() in s['user_request'].lower() or search_query.lower() in s['story'].lower()
        ]
    filtered_stories = [s for s in filtered_stories if s['judge_score'] >= min_score_filter]
    
    st.markdown(f"### Found {len(filtered_stories)} Stories")
    
    # Story List
    for idx, story in enumerate(reversed(filtered_stories)):
        with st.expander(
            f"Story #{len(filtered_stories) - idx} | Score: {story['judge_score']:.1f}/10 | Model: {story.get('model_used', 'unknown')} | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            expanded=False
        ):
            # Story metadata
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Quality Score", f"{story['judge_score']:.1f}/10")
            with col2:
                st.metric("Revisions", story['revision_count'])
            with col3:
                st.metric("Model", story.get('model_used', 'unknown'))
            with col4:
                threshold_status = "✅ Met" if story['meets_quality_threshold'] else "❌ Below"
                st.metric("Quality", threshold_status)
            
            # User request
            st.markdown(f"**Original Request:** {story['user_request']}")
            
            # MCP info
            if story.get('tool_calls'):
                with st.expander(f"🔧 MCP Tool Calls ({len(story['tool_calls'])} facts)"):
                    for i, tool_call in enumerate(story['tool_calls'], 1):
                        st.json({
                            "Function": tool_call.get('function', 'unknown'),
                            "Topic": tool_call.get('arguments', {}).get('topic', 'N/A'),
                            "Result": tool_call.get('result', 'N/A')
                        })
            
            # Story text with beautiful display
            st.markdown("**📖 Story:**")
            story_escaped = html.escape(story['story'])
            story_lines = story_escaped.split('\n')
            story_formatted = ""
            for line in story_lines:
                if line.strip():
                    story_formatted += f"<p style='margin-bottom: 1em; font-size: 1.2em; line-height: 1.8; color: #2c5282;'>{line.strip()}</p>"
                else:
                    story_formatted += "<br>"
            st.markdown(f"""
            <div class="story-display">
                <div class="story-content">
                    {story_formatted}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed information
            tab1, tab2 = st.tabs(["Judge Feedback", "Metadata"])
            
            with tab1:
                judge_feedback = story.get('judge_feedback') or story.get('detailed_feedback')
                if judge_feedback:
                    st.text_area("Judge Feedback", value=judge_feedback, height=200, key=f"feedback_{idx}", disabled=True)
                else:
                    st.info("No judge feedback available for this story")
            
            with tab2:
                metadata = {
                    "Model Used": story.get('model_used', 'unknown'),
                    "MCP Enabled": story.get('mcp_enabled', False),
                    "Fallback Used": story.get('fallback_used', False),
                    "Tool Calls": len(story.get('tool_calls', [])),
                    "Revision Count": story['revision_count'],
                    "Meets Quality Threshold": story['meets_quality_threshold']
                }
                st.json(metadata)

def debug_view():
    """Debug view with observability, hyperparameter tuning, and MCP integration."""
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1>🔧✨ Story Lab ✨🔧</h1>
        <p style="font-size: 1.3em; color: #e2e8f0; font-family: 'Comfortaa', cursive; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);">
            Advanced controls for perfect stories! 🎛️⚙️
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different debug sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Generation", "⚙️ Hyperparameters", "🔧 MCP Tools", "📈 Observability", "🎯 Parent Settings"])
    
    with tab1:
        st.subheader("Story Generation with Debug Info")
        
        user_request = st.text_area(
            "Story Request",
            height=100,
            placeholder="Enter story request..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            enable_mcp = st.checkbox(
                "Enable MCP (Educational Facts)",
                value=True,
                help="Enable Model Context Protocol for educational facts"
            )
            enable_refinement = st.checkbox(
                "Enable Iterative Refinement",
                value=True,
                help="Automatically refine stories based on judge feedback"
            )
        
        with col2:
            max_revisions = st.slider(
                "Max Revisions",
                min_value=0,
                max_value=5,
                value=3
            )
            quality_threshold = st.slider(
                "Quality Threshold",
                min_value=1.0,
                max_value=10.0,
                value=7.0,
                step=0.5
            )
        
        # Get tuning config if available
        tuning_config = st.session_state.get("tuning_config", {})
        
        if st.button("🚀 Generate with Debug Info", type="primary"):
            if user_request.strip():
                with st.spinner("Generating story with debug information..."):
                    try:
                        orchestrator = StoryOrchestrator(
                            enable_mcp=enable_mcp,
                            max_revisions=max_revisions,
                            quality_threshold=quality_threshold or tuning_config.get("min_score", 7.0),
                            parent_settings=st.session_state.parent_settings,
                            storyteller_temperature=tuning_config.get("storyteller_temperature"),
                            judge_temperature=tuning_config.get("judge_temperature"),
                            max_story_tokens=tuning_config.get("max_tokens")
                        )
                        result = orchestrator.generate_story_with_judge(user_request)
                        
                        # Store in session
                        st.session_state.stories.append(result)
                        
                        # Display results
                        display_debug_results(result)
                        
                    except Exception as e:
                        st.error(f"Error generating story: {str(e)}")
            else:
                st.warning("Please enter a story request")
    
    with tab2:
        st.subheader("Hyperparameter Tuning")
        st.info("💡 Adjust these parameters to customize story generation behavior")
        
        # Store tuning values in session state
        if "tuning_config" not in st.session_state:
            st.session_state.tuning_config = {
                "storyteller_temperature": STORY_CONFIG["storyteller_temperature"],
                "judge_temperature": JUDGE_CONFIG["judge_temperature"],
                "max_tokens": STORY_CONFIG["max_story_tokens"],
                "strictness": JUDGE_CONFIG["strictness_level"],
                "min_score": JUDGE_CONFIG["minimum_acceptance_score"]
            }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Story Generation Parameters")
            
            storyteller_temp = st.slider(
                "Storyteller Temperature",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.tuning_config["storyteller_temperature"],
                step=0.05,
                help="Higher = more creative, Lower = more consistent"
            )
            st.session_state.tuning_config["storyteller_temperature"] = storyteller_temp
            
            max_tokens = st.slider(
                "Max Story Tokens",
                min_value=500,
                max_value=4000,
                value=st.session_state.tuning_config["max_tokens"],
                step=100,
                help="Maximum length of generated story"
            )
            st.session_state.tuning_config["max_tokens"] = max_tokens
            
            story_arc = st.selectbox(
                "Story Arc Type",
                options=["hero_journey", "three_act", "simple_adventure"],
                index=["hero_journey", "three_act", "simple_adventure"].index(STORY_CONFIG["story_arc_type"]),
                help="Story structure template"
            )
        
        with col2:
            st.markdown("### Judge Configuration")
            
            judge_temp = st.slider(
                "Judge Temperature",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.tuning_config["judge_temperature"],
                step=0.05,
                help="Lower = more consistent evaluation"
            )
            st.session_state.tuning_config["judge_temperature"] = judge_temp
            
            strictness = st.slider(
                "Judge Strictness",
                min_value=1,
                max_value=10,
                value=st.session_state.tuning_config["strictness"],
                help="How strict the judge is (1-10)"
            )
            st.session_state.tuning_config["strictness"] = strictness
            
            min_score = st.slider(
                "Minimum Acceptance Score",
                min_value=0.0,
                max_value=10.0,
                value=st.session_state.tuning_config["min_score"],
                step=0.5,
                help="Minimum score required to accept story"
            )
            st.session_state.tuning_config["min_score"] = min_score
        
        # Guardrail Settings
        st.markdown("### 🛡️ Guardrail Settings")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            enable_content_filter = st.checkbox(
                "Enable Content Filter",
                value=GUARDRAIL_CONFIG["enable_content_filter"],
                help="Filter prohibited content"
            )
        
        with col2:
            enable_age_check = st.checkbox(
                "Enable Age Check",
                value=GUARDRAIL_CONFIG["enable_age_check"],
                help="Validate age-appropriateness"
            )
        
        with col3:
            enable_safety_check = st.checkbox(
                "Enable Safety Check",
                value=GUARDRAIL_CONFIG["enable_safety_check"],
                help="Check for safety issues"
            )
        
        # Prohibited themes
        st.markdown("**Prohibited Themes:**")
        prohibited_display = ", ".join(GUARDRAIL_CONFIG["prohibited_themes"])
        st.info(prohibited_display)
        
        # Required elements
        st.markdown("**Required Elements:**")
        required_display = ", ".join(GUARDRAIL_CONFIG["required_elements"])
        st.success(required_display)
        
        if st.button("💾 Apply Hyperparameters", type="primary"):
            st.success("✅ Hyperparameters saved! They will be used in the next story generation.")
            st.info("Note: These settings apply to stories generated in the Debug Tuning tab.")
    
    with tab3:
        st.subheader("🔧 Model Context Protocol (MCP) Tools")
        st.markdown("**MCP Integration** - Educational Facts with Fact Checking")
        
        # MCP Knowledge Base Explorer
        st.markdown("### 📚 Educational Facts Knowledge Base")
        
        # Show available categories
        st.markdown("**Available Categories:**")
        for category, facts in EDUCATIONAL_FACTS.items():
            with st.expander(f"📁 {category.title()} ({len(facts)} facts)"):
                for topic, fact in facts.items():
                    st.markdown(f"**{topic.title()}:**")
                    st.write(fact)
                    st.markdown("---")
        
        # Test MCP Tool with Expansion
        st.markdown("### 🧪 Test MCP Tool with Expansion")
        col1, col2 = st.columns(2)
        
        with col1:
            test_topic = st.text_input("Enter a topic to test:", placeholder="e.g., Mars, T-Rex, Elephants, Red Planet")
        
        with col2:
            verify_fact = st.checkbox("Verify fact with Fact Checker", value=True)
        
        if st.button("Test Tool"):
            if test_topic:
                with st.spinner("Fetching and expanding educational fact..."):
                    try:
                        expander = MCPExpander()
                        fact_data = expander.get_fact_with_expansion(test_topic)
                        
                        st.success("✅ Tool executed successfully!")
                        st.markdown("**Result:**")
                        
                        # Show expansion info
                        if fact_data['expanded']:
                            st.info(f"📝 Topic expanded: '{fact_data['original_topic']}' → '{fact_data['used_topic']}'")
                        if fact_data['category']:
                            st.info(f"📁 Category inferred: {fact_data['category']}")
                        
                        st.write(fact_data['fact'])
                        
                        # Verify if requested
                        if verify_fact:
                            with st.spinner("Verifying fact..."):
                                try:
                                    checker = FactChecker()
                                    verification = checker.verify_fact(fact_data['fact'], fact_data['used_topic'])
                                    
                                    st.markdown("### ✓ Fact Verification")
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Accuracy Score", f"{verification.get('score', 0):.1f}/10")
                                    with col2:
                                        verdict = verification.get('verdict', 'N/A')
                                        if verdict == "VERIFIED":
                                            st.success(f"**Verdict:** {verdict}")
                                        elif verdict == "NEEDS_CORRECTION":
                                            st.warning(f"**Verdict:** {verdict}")
                                        else:
                                            st.error(f"**Verdict:** {verdict}")
                                    with col3:
                                        st.write(f"**Age Appropriate:** {'✅ Yes' if verification.get('age_appropriate') else '❌ No'}")
                                    
                                    if verification.get('concerns'):
                                        st.warning(f"**Concerns:** {verification.get('concerns')}")
                                except Exception as e:
                                    st.warning(f"Fact verification unavailable: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter a topic")
        
        # MCP Tool Usage Stats
        st.markdown("### 📊 MCP Tool Usage Statistics")
        stories_with_mcp = [s for s in st.session_state.stories if s.get('mcp_enabled') and s.get('tool_calls')]
        
        if stories_with_mcp:
            total_tool_calls = sum(len(s.get('tool_calls', [])) for s in stories_with_mcp)
            unique_topics = set()
            for story in stories_with_mcp:
                for tool_call in story.get('tool_calls', []):
                    topic = tool_call.get('arguments', {}).get('topic', '')
                    if topic:
                        unique_topics.add(topic)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Stories with MCP", len(stories_with_mcp))
            with col2:
                st.metric("Total Tool Calls", total_tool_calls)
            with col3:
                st.metric("Unique Topics", len(unique_topics))
            
            if unique_topics:
                st.markdown("**Topics Queried:**")
                st.write(", ".join(sorted(unique_topics)))
        else:
            st.info("No MCP tool calls yet. Generate stories with educational topics to see usage statistics.")
    
    with tab4:
        st.subheader("Observability Dashboard")
        
        stories_to_show = st.session_state.stories
        
        if stories_to_show:
            st.markdown(f"### Generated Stories ({len(stories_to_show)})")
            
            for idx, story_data in enumerate(reversed(stories_to_show[-5:]), 1):
                with st.expander(f"Story #{len(stories_to_show) - idx + 1} - Score: {story_data['judge_score']:.1f}/10"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Quality Score", f"{story_data['judge_score']:.1f}/10")
                        st.metric("Model", story_data.get('model_used', 'unknown'))
                    with col2:
                        st.metric("Revisions", story_data['revision_count'])
                        st.metric("MCP Enabled", "✅" if story_data.get('mcp_enabled') else "❌")
                    with col3:
                        st.metric("Fallback Used", "🔄 Yes" if story_data.get('fallback_used') else "✨ No")
                        st.metric("Tool Calls", len(story_data.get('tool_calls', [])))
                    
                    if story_data.get('tool_calls'):
                        st.markdown("**MCP Tool Calls:**")
                        for tool_call in story_data['tool_calls']:
                            st.json({
                                "Function": tool_call.get('function', 'unknown'),
                                "Topic": tool_call.get('arguments', {}).get('topic', 'N/A'),
                                "Result Preview": tool_call.get('result', 'N/A')[:100] + "..." if len(tool_call.get('result', '')) > 100 else tool_call.get('result', 'N/A')
                            })
                    
                    if 'judge_feedback' in story_data:
                        with st.expander("Judge Feedback"):
                            st.text(story_data['judge_feedback'])
                    
                    st.markdown("**📖 Story Text:**")
                    story_escaped = html.escape(story_data['story'])
                    story_lines = story_escaped.split('\n')
                    story_formatted = ""
                    for line in story_lines:
                        if line.strip():
                            story_formatted += f"<p style='margin-bottom: 1em; font-size: 1.2em; line-height: 1.8; color: #2c5282;'>{line.strip()}</p>"
                        else:
                            story_formatted += "<br>"
                    st.markdown(f"""
                    <div class="story-display">
                        <div class="story-content">
                            {story_formatted}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No stories generated yet. Generate a story to see observability data.")
    
    with tab5:
        st.subheader("Parent Settings Configuration")
        st.markdown("Configure parent-friendly settings that influence story generation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            persona_options = {k: v["name"] + " - " + v["description"] for k, v in PERSONAS.items()}
            selected_persona = st.selectbox(
                "Story Style (Persona)",
                options=list(persona_options.keys()),
                format_func=lambda x: persona_options[x],
                index=list(persona_options.keys()).index(st.session_state.parent_settings.get("persona", "balanced_storyteller")),
                help="Choose the storytelling style"
            )
            
            value_options = {k: v["name"] + " - " + v["description"] for k, v in VALUES.items()}
            selected_values = st.multiselect(
                "Values to Emphasize",
                options=list(value_options.keys()),
                format_func=lambda x: value_options[x],
                default=st.session_state.parent_settings.get("values", ["kindness", "friendship"]),
                help="Select values to incorporate into stories"
            )
        
        with col2:
            interest_options = {k: v["name"] + " - " + v["description"] for k, v in INTERESTS.items()}
            selected_interests = st.multiselect(
                "Interests to Include",
                options=list(interest_options.keys()),
                format_func=lambda x: interest_options[x],
                default=st.session_state.parent_settings.get("interests", []),
                help="Add interests that will be incorporated into stories"
            )
            
            child_name = st.text_input(
                "Child's Name (Optional)",
                value=st.session_state.parent_settings.get("child_name", ""),
                help="If provided, may be used in character names"
            )
        
        custom_elements = st.text_area(
            "Custom Elements (Optional)",
            value=st.session_state.parent_settings.get("custom_elements", ""),
            height=100,
            help="Any other elements you'd like included"
        )
        
        # Update session state
        st.session_state.parent_settings = {
            "persona": selected_persona,
            "values": selected_values,
            "interests": selected_interests,
            "child_name": child_name,
            "custom_elements": custom_elements
        }
        
        # Show technical mapping
        st.markdown("### 📋 Technical Configuration")
        from parent_config import apply_parent_settings_to_config
        tech_overrides = apply_parent_settings_to_config(st.session_state.parent_settings)
        
        st.json({
            "Persona": selected_persona,
            "Temperature": tech_overrides.get("storyteller_temperature", 0.8),
            "Story Arc": tech_overrides.get("story_arc_type", "hero_journey"),
            "Tone": tech_overrides.get("tone", "uplifting"),
            "Values": selected_values,
            "Interests": selected_interests,
            "Child Name": child_name if child_name else "Not set",
            "Custom Elements": custom_elements if custom_elements else "None"
        })
        
        # Show prompt additions
        if tech_overrides.get("custom_prompts"):
            with st.expander("📝 Generated Prompt Additions"):
                st.text(tech_overrides["custom_prompts"])

def display_debug_results(result):
    """Display detailed debug results."""
    st.markdown("---")
    st.subheader("📊 Generation Results")
    
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Quality Score", f"{result['judge_score']:.1f}/10")
    with col2:
        st.metric("Revisions", result['revision_count'])
    with col3:
        st.metric("Model", result.get('model_used', 'unknown'))
    with col4:
        st.metric("MCP Enabled", "✅" if result.get('mcp_enabled') else "❌")
    with col5:
        st.metric("Fallback", "🔄" if result.get('fallback_used') else "✨")
    
    # Story with beautiful display
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2>📖✨ Generated Story ✨📖</h2>
    </div>
    """, unsafe_allow_html=True)
    
    story_escaped = html.escape(result['story'])
    story_lines = story_escaped.split('\n')
    formatted_story = ""
    for line in story_lines:
        if line.strip():
            formatted_story += f"<p style='margin-bottom: 1em; font-size: 1.2em; line-height: 1.8; color: #2c5282;'>{line.strip()}</p>"
        else:
            formatted_story += "<br>"
    
    st.markdown(f"""
    <div class="story-display">
        <div class="story-content">
            {formatted_story}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Decorative stars
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <span class="star-decoration">⭐</span>
        <span class="star-decoration" style="animation-delay: 0.5s;">✨</span>
        <span class="star-decoration" style="animation-delay: 1s;">🌟</span>
        <span class="star-decoration" style="animation-delay: 1.5s;">💫</span>
        <span class="star-decoration" style="animation-delay: 2s;">⭐</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Tool calls
    if result.get('tool_calls'):
        st.markdown("---")
        st.subheader(f"🔧 MCP Tool Calls ({len(result['tool_calls'])})")
        for i, tool_call in enumerate(result['tool_calls'], 1):
            with st.expander(f"Tool Call #{i}: {tool_call.get('function', 'unknown')}"):
                st.json({
                    "Function": tool_call.get('function', 'unknown'),
                    "Arguments": tool_call.get('arguments', {}),
                    "Result": tool_call.get('result', 'N/A')
                })
    
    # Judge feedback
    if result.get('judge_feedback'):
        st.markdown("---")
        st.subheader("📝 Judge Feedback")
        st.text_area("", value=result['judge_feedback'], height=200, disabled=True)
    
    # Metadata
    st.markdown("---")
    st.subheader("📋 Metadata")
    metadata = {
        "User Request": result.get('user_request', 'N/A'),
        "Model Used": result.get('model_used', 'unknown'),
        "MCP Enabled": result.get('mcp_enabled', False),
        "Fallback Used": result.get('fallback_used', False),
        "Tool Calls Count": len(result.get('tool_calls', [])),
        "Revision Count": result['revision_count'],
        "Judge Score": result['judge_score'],
        "Meets Quality Threshold": result['meets_quality_threshold']
    }
    st.json(metadata)

if __name__ == "__main__":
    main()

