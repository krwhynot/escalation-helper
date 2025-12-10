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
# Follow-up Question Configuration
# ================================================

FOLLOWUP_THRESHOLD = 0.30  # Distance > this triggers follow-up (70% similarity)
MAX_FOLLOWUPS = 4  # Maximum follow-up questions before showing results

CATEGORY_KEYWORDS = {
    "printer": ["print", "printer", "receipt", "kitchen print", "ticket", "label", "paper"],
    "payment": ["payment", "card", "credit", "debit", "charge", "batch", "tip", "refund", "terminal"],
    "employee": ["employee", "clock", "pin", "schedule", "staff", "server", "cashier", "manager", "driver"],
    "order": ["order", "void", "comp", "total", "tax", "check", "ticket", "close", "reopen"],
    "menu": ["menu", "item", "price", "modifier", "topping", "size", "coupon", "product", "category"],
    "cash": ["cash", "drawer", "drop", "safe", "over", "short", "reconcile", "till", "deposit"]
}

FOLLOWUP_QUESTIONS = {
    "printer": {
        "question": "What's happening with the printer?",
        "options": [
            "Not printing at all",
            "Printing to wrong printer/station",
            "Double printing",
            "Partial or garbled output",
            "Slow or delayed"
        ],
        "hint": "Including the printer name (like 'Printer1' or 'kitchen printer') helps narrow it down.",
        "query_enrichment": {
            "Not printing at all": "printer not printing no output offline",
            "Printing to wrong printer/station": "printer routing wrong station destination",
            "Double printing": "printer duplicate double print twice",
            "Partial or garbled output": "printer partial garbled cut off corrupt",
            "Slow or delayed": "printer slow delay queue backed up"
        }
    },
    "payment": {
        "question": "What's the payment issue?",
        "options": [
            "Card declined but customer charged",
            "Card charged twice",
            "Payment not recording on order",
            "Batch won't settle",
            "Wrong amount charged"
        ],
        "hint": "If you have the last 4 digits of the card or an order number, include those.",
        "query_enrichment": {
            "Card declined but customer charged": "credit card declined charged anyway ghost",
            "Card charged twice": "double charge duplicate payment transaction",
            "Payment not recording on order": "payment missing order unpaid not applied",
            "Batch won't settle": "credit card batch settle close end day",
            "Wrong amount charged": "payment amount wrong incorrect total tip"
        }
    },
    "employee": {
        "question": "What's happening with the employee?",
        "options": [
            "Can't clock in (says already clocked in)",
            "PIN not working",
            "Missing from POS/schedule",
            "Hours showing wrong",
            "Can't perform an action (void, comp, etc.)"
        ],
        "hint": "Knowing the employee's role (cashier, manager, driver) helps since permissions vary.",
        "query_enrichment": {
            "Can't clock in (says already clocked in)": "employee clock in already stuck timeclock",
            "PIN not working": "employee PIN login password access denied",
            "Missing from POS/schedule": "employee not showing missing POS schedule",
            "Hours showing wrong": "time clock hours incorrect wrong punch",
            "Can't perform an action (void, comp, etc.)": "employee permission denied can't void comp security"
        }
    },
    "order": {
        "question": "What's wrong with the order?",
        "options": [
            "Order won't close/complete",
            "Can't void or comp items",
            "Wrong total or tax",
            "Missing items",
            "Order stuck or disappeared"
        ],
        "hint": "Having the order number or business date helps find the exact records.",
        "query_enrichment": {
            "Order won't close/complete": "order stuck won't close complete finalize",
            "Can't void or comp items": "void comp order item permission manager",
            "Wrong total or tax": "order total tax wrong incorrect calculation",
            "Missing items": "order items missing disappeared deleted",
            "Order stuck or disappeared": "order missing stuck lost can't find search"
        }
    },
    "menu": {
        "question": "What's the menu issue?",
        "options": [
            "Item not showing on POS",
            "Wrong price displaying",
            "Modifier options missing",
            "Item in wrong category",
            "New item not syncing"
        ],
        "hint": "Knowing the exact item name helps find its configuration.",
        "query_enrichment": {
            "Item not showing on POS": "menu item not showing missing button hidden",
            "Wrong price displaying": "menu price wrong incorrect amount",
            "Modifier options missing": "modifier topping option missing unavailable",
            "Item in wrong category": "menu item group category wrong location",
            "New item not syncing": "menu sync new item not appearing update"
        }
    },
    "cash": {
        "question": "What's the cash drawer issue?",
        "options": [
            "Drawer over or short",
            "Can't reconcile/close drawer",
            "Wrong employee assigned",
            "Drop not recorded",
            "Multiple employees on same drawer"
        ],
        "hint": "The drawer name (like 'Drawer 1') and business date help find records.",
        "query_enrichment": {
            "Drawer over or short": "cash drawer over short variance count",
            "Can't reconcile/close drawer": "cash drawer close reconcile stuck end day",
            "Wrong employee assigned": "cash drawer employee assignment wrong",
            "Drop not recorded": "cash drop safe missing not recorded",
            "Multiple employees on same drawer": "cash drawer shared multiple employees assignment"
        }
    },
    "default": {
        "question": "What category best describes your issue?",
        "options": [
            "Orders & checkout",
            "Payments & credit cards",
            "Printing & receipts",
            "Employees & time clock",
            "Menu & items",
            "Cash drawers",
            "Delivery",
            "Something else"
        ],
        "hint": "Pick the closest match and I'll ask a more specific question.",
        "query_enrichment": {
            "Orders & checkout": "order",
            "Payments & credit cards": "payment credit card",
            "Printing & receipts": "printer receipt",
            "Employees & time clock": "employee time clock",
            "Menu & items": "menu item",
            "Cash drawers": "cash drawer",
            "Delivery": "delivery driver dispatch",
            "Something else": ""
        }
    }
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

# Follow-up question session state
if "followup_active" not in st.session_state:
    st.session_state.followup_active = False
if "original_query" not in st.session_state:
    st.session_state.original_query = ""
if "followup_count" not in st.session_state:
    st.session_state.followup_count = 0
if "enriched_context" not in st.session_state:
    st.session_state.enriched_context = []
if "pending_followup" not in st.session_state:
    st.session_state.pending_followup = None
if "cached_matches" not in st.session_state:
    st.session_state.cached_matches = []

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
# Follow-up Question Functions
# ================================================

def detect_category(query: str) -> str:
    """
    Detect the most likely category from the query using keyword matching.

    Args:
        query: User's search query

    Returns:
        Category key (printer, payment, etc.) or "default" if no clear match
    """
    query_lower = query.lower()
    category_scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score > 0:
            category_scores[category] = score

    if not category_scores:
        return "default"

    return max(category_scores, key=category_scores.get)


def should_trigger_followup(matches: list) -> bool:
    """
    Check if search results have low enough confidence to trigger follow-up questions.

    Args:
        matches: List of search results with 'distance' field

    Returns:
        True if follow-up should be triggered
    """
    if not matches:
        return False

    top_distance = matches[0].get('distance')
    if top_distance is None:
        return False

    return top_distance > FOLLOWUP_THRESHOLD


def build_enriched_query(original: str, enrichments: list) -> str:
    """
    Combine original query with enrichment terms.

    Args:
        original: Original user query
        enrichments: List of enrichment terms from follow-up selections

    Returns:
        Enriched query string
    """
    if not enrichments:
        return original

    enrichment_str = " ".join(enrichments)
    return f"{original} {enrichment_str}"


def reset_followup_state():
    """Reset all follow-up related session state variables."""
    st.session_state.followup_active = False
    st.session_state.original_query = ""
    st.session_state.followup_count = 0
    st.session_state.enriched_context = []
    st.session_state.pending_followup = None
    st.session_state.cached_matches = []


def get_followup_data(category: str) -> dict:
    """
    Get the follow-up question and options for a category.

    Args:
        category: Category key or "default"

    Returns:
        Dict with 'question', 'options', 'hint', 'query_enrichment' keys
    """
    if category not in FOLLOWUP_QUESTIONS:
        return FOLLOWUP_QUESTIONS["default"]
    return FOLLOWUP_QUESTIONS[category]


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

    # Helper function to display follow-up question
    def display_followup_question(category, matches):
        """Display a follow-up question with options."""
        followup_data = get_followup_data(category)
        top_similarity = round((1 - matches[0]['distance']) * 100, 1) if matches else 0

        st.info(f"I found some results ({top_similarity}% match), but let me ask a quick question to find something more specific:")

        st.markdown(f"**{followup_data['question']}**")

        # Radio buttons for options
        selected = st.radio(
            "Select an option:",
            options=followup_data["options"],
            key=f"followup_{st.session_state.followup_count}",
            label_visibility="collapsed"
        )

        st.caption(f"Tip: {followup_data['hint']}")

        # Action buttons
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Search with this selection", key=f"search_btn_{st.session_state.followup_count}", use_container_width=True):
                return selected, "search"
        with col2:
            if st.button("Skip", key=f"skip_btn_{st.session_state.followup_count}", use_container_width=True):
                return None, "skip"

        return selected, "waiting"

    # Check if we have a pending follow-up to process
    if st.session_state.pending_followup is not None:
        category = st.session_state.pending_followup
        matches = st.session_state.cached_matches

        with st.chat_message("assistant"):
            selected, action = display_followup_question(category, matches)

            if action == "search" and selected:
                # Get enrichment for selection
                followup_data = get_followup_data(category)
                enrichment = followup_data["query_enrichment"].get(selected, "")

                # Persist follow-up Q&A to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**{followup_data['question']}**\n\nTip: {followup_data['hint']}"
                })
                st.session_state.messages.append({
                    "role": "user",
                    "content": selected
                })

                # Check if this is a category redirect (from default question)
                if category == "default" and enrichment in FOLLOWUP_QUESTIONS and enrichment != "default":
                    # User selected a category, show that category's question
                    st.session_state.pending_followup = enrichment
                    st.session_state.followup_count += 1
                    st.rerun()
                elif enrichment:
                    # Add enrichment and re-search
                    st.session_state.enriched_context.append(enrichment)
                    enriched_query = build_enriched_query(
                        st.session_state.original_query,
                        st.session_state.enriched_context
                    )

                    with st.spinner("Searching with more context..."):
                        new_matches = search_knowledge_base(enriched_query, collection)

                    st.session_state.followup_count += 1

                    # Check if results improved or max follow-ups reached
                    if not should_trigger_followup(new_matches) or st.session_state.followup_count >= MAX_FOLLOWUPS:
                        # Good enough or max reached - show results
                        reset_followup_state()
                        if new_matches:
                            display_results(new_matches, enriched_query, openai_client)
                        else:
                            st.warning("I couldn't find any relevant results. Try rephrasing your question.")
                            st.session_state.messages.append({"role": "assistant", "content": "No results found.", "sources": []})
                        st.rerun()
                    else:
                        # Still low confidence, ask another question
                        st.session_state.cached_matches = new_matches
                        new_category = detect_category(enriched_query)
                        st.session_state.pending_followup = new_category
                        st.rerun()
                else:
                    # Empty enrichment (e.g., "Something else") - just show current results
                    reset_followup_state()
                    if matches:
                        display_results(matches, st.session_state.original_query, openai_client)
                    st.rerun()

            elif action == "skip":
                # User wants to skip - show results with current matches
                # Persist skip action to chat history
                followup_data = get_followup_data(category)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**{followup_data['question']}**\n\nTip: {followup_data['hint']}"
                })
                st.session_state.messages.append({
                    "role": "user",
                    "content": "[Skipped - showing available results]"
                })

                original_query = st.session_state.original_query
                reset_followup_state()
                if matches:
                    display_results(matches, original_query, openai_client)
                else:
                    st.warning("I couldn't find any relevant results.")
                    st.session_state.messages.append({"role": "assistant", "content": "No results found.", "sources": []})
                st.rerun()

    elif prompt:
        # New query from user
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
            elif should_trigger_followup(matches) and st.session_state.followup_count < MAX_FOLLOWUPS:
                # Low confidence - initiate follow-up flow
                st.session_state.followup_active = True
                st.session_state.original_query = prompt
                st.session_state.cached_matches = matches
                st.session_state.followup_count = 1

                # Detect category
                category = detect_category(prompt)
                st.session_state.pending_followup = category

                # Display follow-up question
                selected, action = display_followup_question(category, matches)

                if action == "skip":
                    # User clicked skip immediately
                    reset_followup_state()
                    display_results(matches, prompt, openai_client)
                    st.rerun()
            else:
                # High confidence - show results directly
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
            reset_followup_state()
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
            reset_followup_state()
            st.rerun()

# ================================================
# Run Application
# ================================================

if __name__ == "__main__":
    main()
