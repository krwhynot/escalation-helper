"""
================================================
Escalation Helper - Web Interface
================================================
A simple search interface for the installer team.
Run with: streamlit run app.py
================================================
"""

import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
import config
import json
import logging
from datetime import datetime

# Cross-encoder reranking (optional - graceful fallback if not available)
try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False

# ================================================
# HungerRush Brand Colors
# ================================================

COLORS = {
    # Primary
    "teal": "#0E8476",        # Primary brand teal
    "navy": "#1A1346",        # Deep navy
    "gray": "#5F6369",        # Cool gray

    # Secondary
    "blue": "#35508C",        # Deep blue
    "coral": "#FF585D",       # Coral/salmon
    "ocean": "#1D8296",       # Ocean blue

    # Accent
    "green": "#479C45",       # Success green
    "orange": "#ED5C24",      # Alert orange
    "gold": "#ED9E24",        # Warning gold
    "yellow": "#EDD614",      # Highlight yellow

    # Light shades (for backgrounds)
    "teal_light": "#9FCDC7",
    "navy_light": "#A3A0B5",
    "blue_light": "#AEB8D1",
    "coral_light": "#FFBCBE",
}


# ================================================
# Page Configuration
# ================================================

st.set_page_config(
    page_title="Escalation Helper",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================================
# Custom CSS with HungerRush Branding
# ================================================

st.markdown(f"""
<style>
    /* Import Google Fonts - Anton (FatFrank alt) & Nunito Sans (FF Nort alt) */
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Nunito+Sans:wght@400;600;700&display=swap');

    /* CSS Variables for HungerRush Brand */
    :root {{
        --hr-teal: {COLORS['teal']};
        --hr-navy: {COLORS['navy']};
        --hr-cool-gray: {COLORS['gray']};
        --hr-coral: {COLORS['coral']};
        --hr-green: {COLORS['green']};
        --hr-gold: {COLORS['gold']};
        --hr-teal-light: {COLORS['teal_light']};
        --hr-ocean: {COLORS['ocean']};
        --text-primary: #F0F2F6;
    }}

    /* Typography - Body */
    body, .stApp, .stMarkdown, p, span, div {{
        font-family: 'Nunito Sans', Arial, sans-serif;
    }}

    /* Header styling - branded gradient */
    .main-header {{
        background: linear-gradient(90deg, var(--hr-teal) 0%, var(--hr-ocean) 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}

    .main-header h1 {{
        font-family: 'Anton', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: white;
        margin: 0;
        font-size: 2rem;
    }}

    .main-header p {{
        font-family: 'Nunito Sans', sans-serif;
        color: var(--hr-teal-light);
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }}

    /* Button styling - Touch-friendly (44px min) */
    .stButton > button {{
        background: var(--hr-teal);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        min-height: 44px;
        font-family: 'Nunito Sans', sans-serif;
        font-weight: 600;
        transition: all 0.2s ease;
    }}

    .stButton > button:hover {{
        background: var(--hr-teal-light);
        color: var(--hr-navy) !important;
        box-shadow: 0 4px 15px rgba(14, 132, 118, 0.4);
    }}

    .stButton > button:active {{
        transform: scale(0.98);
    }}

    /* Chat message styling */
    [data-testid="stChatMessage"] {{
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }}

    /* User messages */
    [data-testid="stChatMessage"][data-testid*="user"] {{
        background: rgba(163, 160, 181, 0.15);
    }}

    /* Assistant messages */
    [data-testid="stChatMessage"][data-testid*="assistant"] {{
        background: rgba(95, 99, 105, 0.2);
        border-left: 4px solid var(--hr-teal);
    }}

    /* Code blocks - dark with teal accent */
    .stCodeBlock {{
        background: rgba(95, 99, 105, 0.3);
        border: 1px solid var(--hr-cool-gray);
        border-radius: 8px;
    }}

    .stCodeBlock code, .stCodeBlock pre {{
        color: var(--hr-teal-light) !important;
        font-family: 'Fira Code', 'Consolas', monospace;
    }}

    /* Chat input */
    [data-testid="stChatInput"] {{
        border-color: var(--hr-teal);
    }}

    [data-testid="stChatInput"] textarea {{
        font-family: 'Nunito Sans', sans-serif;
    }}

    /* Pills/chips for quick searches */
    [data-testid="stPills"] button {{
        font-family: 'Nunito Sans', sans-serif;
        border-radius: 20px;
        min-height: 44px;
    }}

    /* Expander styling */
    .streamlit-expanderHeader {{
        font-family: 'Nunito Sans', sans-serif;
        font-weight: 600;
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background: rgba(53, 80, 140, 0.3);
    }}

    /* Focus states - Gold outline for accessibility */
    *:focus {{
        outline: 2px solid var(--hr-gold) !important;
        outline-offset: 2px;
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Status classes for responses */
    .status-success {{ border-left: 5px solid var(--hr-green) !important; }}
    .status-warning {{ border-left: 5px solid var(--hr-gold) !important; }}
    .status-error {{ border-left: 5px solid var(--hr-coral) !important; }}
</style>
""", unsafe_allow_html=True)

# ================================================
# Session State
# ================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_processed_prompt" not in st.session_state:
    st.session_state.last_processed_prompt = None


# ================================================
# Authentication
# ================================================

def check_password():
    """Simple password gate for team access."""

    if st.session_state.authenticated:
        return True

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="main-header" style="text-align: center;">
            <h1>🍕 Escalation Helper</h1>
            <p>SQL Troubleshooting Assistant</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container():
            password = st.text_input("Team Password:", type="password", key="password_input")

            if st.button("🔓 Login", use_container_width=True):
                if password == config.APP_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")

            st.caption("Contact Kyle if you need the password.")

    return False

# ================================================
# Load RAG Components
# ================================================

@st.cache_resource
def load_chroma():
    """Load ChromaDB collection."""
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=config.OPENAI_API_KEY,
        model_name=config.EMBEDDING_MODEL
    )

    client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
    collection = client.get_collection(
        name=config.COLLECTION_NAME,
        embedding_function=openai_ef
    )

    return collection

@st.cache_resource
def load_openai():
    """Load OpenAI client."""
    return OpenAI(api_key=config.OPENAI_API_KEY)

@st.cache_resource
def load_cross_encoder():
    """Load cross-encoder model for reranking (cached)."""
    if not CROSS_ENCODER_AVAILABLE:
        return None

    model_name = getattr(config, 'CROSS_ENCODER_MODEL', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
    if model_name is None:
        return None

    try:
        return CrossEncoder(model_name)
    except Exception as e:
        st.warning(f"Cross-encoder model load failed: {e}. Using vector search only.")
        return None

# ================================================
# Feedback Logging
# ================================================

def log_feedback(query, response, sentiment):
    """Log user feedback to JSON file."""
    feedback_file = "feedback.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "response": response[:500],
        "helpful": sentiment == 1  # 1=thumbs up, 0=thumbs down
    }
    try:
        with open(feedback_file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    data.append(entry)
    with open(feedback_file, "w") as f:
        json.dump(data, f, indent=2)

# ================================================
# Search Function
# ================================================

def search_knowledge_base(query, collection, use_reranking=True):
    """
    Search for relevant content with optional cross-encoder reranking.

    Two-stage pipeline:
    1. Retrieve candidates from ChromaDB (fast, approximate)
    2. Rerank with cross-encoder (accurate, slower)

    Args:
        query: User's search query
        collection: ChromaDB collection
        use_reranking: Whether to apply cross-encoder reranking

    Returns:
        List of matching documents with relevance info
    """
    retrieve_k = getattr(config, 'RETRIEVE_K', 20)
    return_k = getattr(config, 'RETURN_K', 3)
    distance_threshold = getattr(config, 'DISTANCE_THRESHOLD', 0.40)

    # Stage 1: Retrieve candidates from ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=retrieve_k,
        include=["documents", "metadatas", "distances"]
    )

    if not results['documents'] or not results['documents'][0]:
        return []

    # Build candidate list with pre-filtering
    # Use slightly higher threshold before reranking (let reranker decide)
    pre_rerank_threshold = min(distance_threshold + 0.10, 0.60)

    candidates = []
    for i, doc in enumerate(results['documents'][0]):
        distance = results['distances'][0][i] if results['distances'] else None

        # Pre-filter by relaxed threshold
        if distance is not None and distance > pre_rerank_threshold:
            continue

        candidates.append({
            'content': doc,
            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
            'distance': distance,
            'similarity_pct': round((1 - distance) * 100, 1) if distance else None
        })

    if not candidates:
        return []

    # Stage 2: Cross-encoder reranking (if available and requested)
    cross_encoder = load_cross_encoder() if use_reranking else None

    if cross_encoder is not None and len(candidates) > 1:
        # Prepare query-document pairs for cross-encoder
        pairs = [[query, c['content']] for c in candidates]

        try:
            scores = cross_encoder.predict(pairs)

            # Add cross-encoder scores to candidates
            for i, candidate in enumerate(candidates):
                candidate['cross_encoder_score'] = float(scores[i])

            # Sort by cross-encoder score (higher = more relevant)
            candidates = sorted(
                candidates,
                key=lambda x: x.get('cross_encoder_score', 0),
                reverse=True
            )
        except Exception as e:
            logging.error(f"Cross-encoder reranking failed: {e}", exc_info=True)
            # Fallback to vector distance ordering is implicit

    # Apply final distance threshold and limit results
    final_matches = []
    for c in candidates[:return_k]:
        if c['distance'] is not None and c['distance'] <= distance_threshold:
            final_matches.append(c)
        elif c['distance'] is None:
            final_matches.append(c)

    return final_matches

# ================================================
# Generate Response
# ================================================

def generate_response(query, matches, client):
    """Generate a helpful response using GPT-4o-mini."""

    context_parts = []
    for i, match in enumerate(matches):
        context_parts.append(f"--- Source {i+1} ---\n{match['content']}")

    context = "\n\n".join(context_parts)

    system_prompt = """You are a helpful SQL troubleshooting assistant for HungerRush POS systems.
Your job is to help installers find the right SQL query to investigate issues.

When responding:
1. Start with a brief summary of what you found
2. Present the most relevant SQL query in a code block
3. Explain what to look for in the results
4. Keep it practical and concise

Format SQL queries using markdown code blocks with sql syntax highlighting.
If no relevant answer exists in the knowledge base, say so honestly."""

    user_prompt = f"""User's question: {query}

Relevant information from our knowledge base:

{context}

Help the user with their troubleshooting question."""

    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=1500
    )

    return response.choices[0].message.content

# ================================================
# Calculate Relevance Score
# ================================================

def get_relevance_class(distance, cross_encoder_score=None):
    """
    Convert cosine distance to relevance category for display.

    Args:
        distance: Cosine distance (0 = identical, 1 = unrelated)
        cross_encoder_score: Optional cross-encoder score (higher = better)

    Returns:
        Tuple of (css_class, label, similarity_percentage)
    """
    if distance is None:
        return "medium", "Medium", None

    similarity_pct = round((1 - distance) * 100, 1)

    # Cosine distance thresholds (lower = more similar)
    if distance < 0.20:
        return "excellent", f"Excellent ({similarity_pct}%)", similarity_pct
    elif distance < 0.35:
        return "good", f"Good ({similarity_pct}%)", similarity_pct
    elif distance < 0.50:
        return "fair", f"Fair ({similarity_pct}%)", similarity_pct
    else:
        return "weak", f"Weak ({similarity_pct}%)", similarity_pct

# ================================================
# Main Application
# ================================================

def main():
    """Main application logic."""

    # Check authentication
    if not check_password():
        return

    # Load components
    try:
        collection = load_chroma()
        openai_client = load_openai()
    except Exception as e:
        st.error(f"❌ Error loading system: {str(e)}")
        st.info("Make sure you've run `python ingest.py` first!")
        return

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🍕 Escalation Helper</h1>
        <p>Describe an issue and get the SQL query you need</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick search pills
    quick_searches = [
        "cashier can't void",
        "customer charged twice",
        "employee clocked in",
        "printer not printing",
        "order won't close"
    ]
    selected_quick = st.pills("Quick searches:", quick_searches, selection_mode="single")

    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                with st.expander(f"📚 {len(message['sources'])} Sources"):
                    for j, source in enumerate(message["sources"]):
                        st.markdown(f"**Source {j+1}**")
                        preview = source[:300] + "..." if len(source) > 300 else source
                        st.code(preview, language=None)

    # Chat input (or quick search)
    prompt = st.chat_input("Describe the issue (e.g. cashier can't void an order)...")

    # Handle quick search selection
    if selected_quick:
        prompt = selected_quick

    # Helper function to display results
    def display_results(matches, query, openai_client):
        """Display search results with LLM response."""
        with st.spinner("Generating response..."):
            response = generate_response(query, matches, openai_client)

        st.markdown(response)

        # Sources expander
        source_contents = [m['content'] for m in matches]
        with st.expander(f"Sources ({len(matches)})"):
            for j, match in enumerate(matches):
                rel_class, rel_text, sim_pct = get_relevance_class(match['distance'])
                ce_score = match.get('cross_encoder_score')
                if ce_score is not None:
                    st.markdown(f"**Source {j+1}** - Relevance: {rel_text} (CE: {ce_score:.2f})")
                else:
                    st.markdown(f"**Source {j+1}** - Relevance: {rel_text}")
                preview = match['content'][:300] + "..." if len(match['content']) > 300 else match['content']
                st.code(preview, language=None)

        # Feedback
        sentiment = st.feedback("thumbs", key=f"fb_{len(st.session_state.messages)}")
        if sentiment is not None:
            log_feedback(query, response, sentiment)
            st.toast("Thanks for your feedback!" if sentiment == 1 else "Sorry it wasn't helpful. We'll improve!")

        # Save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sources": source_contents
        })
        return response

    if prompt and prompt != st.session_state.last_processed_prompt:
        # New query from user
        st.session_state.last_processed_prompt = prompt
        # Add user message to history and display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                matches = search_knowledge_base(prompt, collection)

            if not matches:
                response = "I couldn't find any relevant results. Try rephrasing your question or use different keywords."
                st.warning(response)
                st.session_state.messages.append({"role": "assistant", "content": response, "sources": []})
            else:
                # Show results directly
                display_results(matches, prompt, openai_client)

        st.rerun()

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 1rem; background: {COLORS['teal']}; border-radius: 8px; color: white;">
            <h3 style="margin: 0;">Escalation Helper</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # Clear chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            # Keep last_processed_prompt so quick search pills don't re-trigger
            st.rerun()

        st.divider()

        # System info
        st.markdown("**System Info**")
        try:
            doc_count = collection.count()
            st.caption(f"📊 {doc_count} chunks indexed")
        except:
            pass
        st.caption(f"🤖 Model: {config.LLM_MODEL}")
        st.caption(f"💬 Messages: {len(st.session_state.messages)}")

        # Logout
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.rerun()

# ================================================
# Run Application
# ================================================

if __name__ == "__main__":
    main()
