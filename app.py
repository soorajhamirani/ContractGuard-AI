"""
ContractGuard AI - Intelligent Contract Risk Scoring System
Main Streamlit Application

A production-grade contract analysis tool that provides AI-powered risk assessment
for legal contracts with detailed clause-by-clause analysis.
"""

import streamlit as st
import html
import os
from dotenv import load_dotenv

# Load environment variables (ensure this is done early)
load_dotenv()

from backend.analyzer import analyze_contract, validate_analysis_result
from config.settings import (
    APP_TITLE, APP_SUBTITLE, UPLOAD_HELP, ANALYZE_BUTTON_TEXT,
    RISK_LEVEL_LOW, RISK_LEVEL_MEDIUM, RISK_LEVEL_HIGH,
    COLORS, RISK_EMOJI
)


# ==================== PAGE CONFIGURATION ====================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==================== CUSTOM CSS STYLING ====================

def inject_custom_css():
    """Inject custom CSS for professional styling"""
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* Header styling */
        .app-header {
            text-align: center;
            padding: 2rem 0;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
        }
        
        .app-title {
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
            padding: 0;
        }
        
        .app-subtitle {
            font-size: 1.3rem;
            font-weight: 300;
            margin-top: 0.5rem;
            opacity: 0.95;
        }
        
        /* Risk badge styling */
        .risk-badge {
            display: inline-block;
            padding: 0.5rem 1.5rem;
            border-radius: 25px;
            font-weight: 600;
            font-size: 1.1rem;
            margin: 1rem 0;
        }
        
        .risk-low {
            background-color: #d4edda;
            color: #155724;
            border: 2px solid #28a745;
        }
        
        .risk-medium {
            background-color: #fff3cd;
            color: #856404;
            border: 2px solid #fd7e14;
        }
        
        .risk-high {
            background-color: #f8d7da;
            color: #721c24;
            border: 2px solid #dc3545;
        }
        
        /* Clause card styling */
        .clause-card {
            background-color: #ffffff;
            border-left: 4px solid #667eea;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .clause-field {
            margin-bottom: 1rem;
        }
        
        .clause-label {
            font-weight: 600;
            color: #555;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.3rem;
        }
        
        .clause-value {
            color: #333;
            line-height: 1.6;
        }
        
        /* Risk score badge in clause */
        .score-badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-weight: 700;
            font-size: 1rem;
        }
        
        .score-low {
            background-color: #28a745;
            color: white;
        }
        
        .score-medium {
            background-color: #fd7e14;
            color: white;
        }
        
        .score-high {
            background-color: #dc3545;
            color: white;
        }
        
        /* Upload section */
        .upload-section {
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            border: 2px dashed #dee2e6;
            margin: 2rem 0;
        }
        
        /* Metrics styling */
        div[data-testid="stMetricValue"] {
            font-size: 3rem;
            font-weight: 700;
        }
        
        /* Summary boxes */
        .summary-box {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin: 1rem 0;
        }
        
        .summary-stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #dee2e6;
        }
        
        .summary-stat:last-child {
            border-bottom: none;
        }
        
        /* Confidence score styling */
        .confidence-score {
            display: inline-block;
            background-color: #e7f3ff;
            color: #0056b3;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            font-size: 1.1rem;
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 8px;
            transition: transform 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button:disabled {
            background: #cccccc;
            cursor: not-allowed;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-size: 1.1rem;
            font-weight: 600;
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        
        </style>
    """, unsafe_allow_html=True)


# ==================== HELPER FUNCTIONS ====================

def get_risk_level(score: float) -> str:
    """Determine risk level based on score"""
    if RISK_LEVEL_LOW[0] <= score <= RISK_LEVEL_LOW[1]:
        return "low"
    elif RISK_LEVEL_MEDIUM[0] <= score <= RISK_LEVEL_MEDIUM[1]:
        return "medium"
    else:
        return "high"


def get_risk_label(score: float) -> str:
    """Get formatted risk label with emoji"""
    level = get_risk_level(score)
    labels = {
        "low": f"{RISK_EMOJI['low']} Low Risk",
        "medium": f"{RISK_EMOJI['medium']} Medium Risk",
        "high": f"{RISK_EMOJI['high']} High Risk"
    }
    return labels[level]


def get_risk_badge_html(score: float) -> str:
    """Generate HTML for risk level badge"""
    level = get_risk_level(score)
    label = get_risk_label(score)
    return f'<div class="risk-badge risk-{level}">{label}</div>'


def get_score_badge_html(score: float) -> str:
    """Generate HTML for score badge in clause cards"""
    level = get_risk_level(score)
    return f'<span class="score-badge score-{level}">{score}/10</span>'


def calculate_risk_distribution(clauses: list) -> dict:
    """Calculate distribution of risk levels across clauses"""
    distribution = {"low": 0, "medium": 0, "high": 0}
    for clause in clauses:
        level = get_risk_level(clause["risk_score"])
        distribution[level] += 1
    return distribution


def display_header():
    """Display application header"""
    st.markdown(f"""
        <div class="app-header">
            <h1 class="app-title">🛡️ {APP_TITLE}</h1>
            <p class="app-subtitle">{APP_SUBTITLE}</p>
        </div>
    """, unsafe_allow_html=True)


def display_upload_section():
    """Display file upload section and return uploaded file"""
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    st.markdown("### 📄 Upload Contract")
    st.markdown(UPLOAD_HELP)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload your contract in PDF format for analysis",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.success(f"✅ **File uploaded:** {uploaded_file.name}")
        st.info(f"📊 **File size:** {uploaded_file.size / 1024:.2f} KB")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return uploaded_file


def display_results_dashboard(analysis_result: dict):
    """Display comprehensive results dashboard"""
    
    # Extract data
    overall_score = analysis_result["overall_risk_score"]
    clauses = analysis_result["clauses"]
    risk_distribution = calculate_risk_distribution(clauses)
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # ========== Overall Risk Score Section ==========
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown("### Overall Risk Assessment")
        st.metric(
            label="Risk Score",
            value=f"{overall_score}/10",
            delta=None
        )
        st.markdown(get_risk_badge_html(overall_score), unsafe_allow_html=True)
    
    with col3:
        st.markdown("### Risk Distribution Summary")
        st.markdown(f"""
            <div class="summary-box">
                <div class="summary-stat">
                    <span>{RISK_EMOJI['low']} <strong>Low Risk Clauses</strong></span>
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['low']};">{risk_distribution['low']}</span>
                </div>
                <div class="summary-stat">
                    <span>{RISK_EMOJI['medium']} <strong>Medium Risk Clauses</strong></span>
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['medium']};">{risk_distribution['medium']}</span>
                </div>
                <div class="summary-stat">
                    <span>{RISK_EMOJI['high']} <strong>High Risk Clauses</strong></span>
                    <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['high']};">{risk_distribution['high']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # ========== Clause-by-Clause Analysis ==========
    st.markdown("---")
    st.markdown("## 🔍 Detailed Clause Analysis")
    st.markdown(f"**Found {len(clauses)} clauses for review**")
    
    # Sort clauses by risk score (highest first)
    sorted_clauses = sorted(clauses, key=lambda x: x["risk_score"], reverse=True)
    
    for idx, clause in enumerate(sorted_clauses, 1):
        risk_level = get_risk_level(clause["risk_score"])
        risk_emoji = RISK_EMOJI[risk_level]
        
        # Create expander title with risk indicator
        expander_title = f"{risk_emoji} Clause {idx}: {clause['risk_type']} - Risk Score: {clause['risk_score']}/10"
        
        with st.expander(expander_title, expanded=(idx <= 3)):  # Auto-expand top 3 risky clauses
            # Escape HTML in dynamic content to prevent code injection/display issues
            escaped_clause_text = html.escape(clause['clause_text'])
            escaped_risk_type = html.escape(clause['risk_type'])
            escaped_reasoning = html.escape(clause['reasoning'])
            escaped_suggested_revision = html.escape(clause['suggested_revision'])
            
            st.markdown(f"""
                <div class="clause-card">
                    <div class="clause-field">
                        <div class="clause-label">📋 Clause Text</div>
                        <div class="clause-value">"{escaped_clause_text}"</div>
                    </div>
                    
                    <div class="clause-field">
                        <div class="clause-label">⚠️ Risk Type</div>
                        <div class="clause-value"><strong>{escaped_risk_type}</strong></div>
                    </div>
                    
                    <div class="clause-field">
                        <div class="clause-label">📊 Risk Score</div>
                        <div class="clause-value">{get_score_badge_html(clause['risk_score'])}</div>
                    </div>
                    
                    <div class="clause-field">
                        <div class="clause-label">🧠 AI Reasoning</div>
                        <div class="clause-value">{escaped_reasoning}</div>
                    </div>
                    
                    <div class="clause-field">
                        <div class="clause-label">✏️ Suggested Revision</div>
                        <div class="clause-value" style="background-color: #e7f3ff; padding: 1rem; border-radius: 6px; border-left: 3px solid #0056b3;">
                            {escaped_suggested_revision}
                        </div>
                    </div>
                    
                    <div class="clause-field">
                        <div class="clause-label">🎯 Confidence Score</div>
                        <div class="clause-value">
                            <span class="confidence-score">{clause['confidence_score']:.0%} Confident</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


def display_error_message(error_type: str, message: str):
    """Display formatted error message"""
    if error_type == "invalid_response":
        st.error("❌ **Invalid Analysis Response**")
        st.warning(f"The AI returned an unexpected response format. Please try again or contact support.")
        with st.expander("🔧 Technical Details"):
            st.code(message)
    
    elif error_type == "api_failure":
        st.error("❌ **Analysis Failed**")
        st.warning("We encountered an issue analyzing your contract. Please try again in a moment.")
        with st.expander("🔧 Error Details"):
            st.code(message)
    
    elif error_type == "validation_error":
        st.error("❌ **Validation Error**")
        st.warning(message)
    
    elif error_type == "config_error":
        st.error("⚙️ **Configuration Error**")
        st.warning(message)
        st.info("💡 **Tip:** Check your .env file or environment variables.")

    else:
        st.error("❌ **Unexpected Error**")
        st.warning("An unexpected error occurred. Please try again.")
        with st.expander("🔧 Error Details"):
            st.code(message)


# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    
    # Inject custom CSS
    inject_custom_css()
    
    # Display header
    display_header()

    # Check for API Key
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("⚠️ **Google API Key Not Found**")
        st.markdown("""
        To use this app, you need to set up your Google API Key:
        1.  Get a key from [Google AI Studio](https://aistudio.google.com/).
        2.  Create a `.env` file in the project root.
        3.  Add: `GOOGLE_API_KEY=your_key_here`
        4.  Restart the app.
        """)
        return
    
    # Initialize session state
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "analyzing" not in st.session_state:
        st.session_state.analyzing = False
    
    # Upload section
    uploaded_file = display_upload_section()
    
    # Sidebar for API Key override
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key_input = st.text_input("Google API Key", type="password", help="Override the GOOGLE_API_KEY from environment")
        if api_key_input:
            # Strip whitespace to prevent copy-paste errors
            clean_key = api_key_input.strip()
            os.environ["GOOGLE_API_KEY"] = clean_key
            st.success("API Key updated! (Whitespace removed)")
            
        if st.button("Test API Connection"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
                model = genai.GenerativeModel("gemini-2.0-flash") # Use latest Flash model for test
                response = model.generate_content("Test")
                st.success(f"✅ Connection successful! Response: {response.text}")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

    # Analyze button
    st.markdown("###")  # Spacing
    analyze_disabled = uploaded_file is None
    
    if st.button(
        ANALYZE_BUTTON_TEXT,
        disabled=analyze_disabled,
        use_container_width=True,
        type="primary"
    ):
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("⚠️ Please enter your Google API Key in the sidebar to proceed.")
            return

        st.session_state.analyzing = True
        st.session_state.analysis_result = None
    
    # Processing and results
    if st.session_state.analyzing and uploaded_file:
        try:
            # Show loading state
            with st.spinner("🔄 Analyzing contract... This may take a moment."):
                # Call backend analysis function
                analysis_result = analyze_contract(uploaded_file)
                
                # Validate response
                if not validate_analysis_result(analysis_result):
                    display_error_message(
                        "invalid_response",
                        "Analysis result did not match expected schema"
                    )
                    st.session_state.analyzing = False
                else:
                    # Store result and display
                    st.session_state.analysis_result = analysis_result
                    st.session_state.analyzing = False
                    st.success("✅ **Analysis Complete!**")
        
        except ValueError as ve:
            error_str = str(ve)
            # Check if it's a config error (missing key call inside pipeline)
            if "GOOGLE_API_KEY" in error_str:
                display_error_message("config_error", error_str)
            elif "Invalid Google API Key" in error_str:
                st.error("🔑 **Invalid API Key**")
                st.warning("The API key provided is rejected by Google. Please check the sidebar ⚙️ and enter a valid key.")
                st.info("Make sure you copied the entire key and there are no extra spaces.")
                with st.expander("Show Error Details"):
                    st.code(error_str)
            else:
                # Validation errors from backend
                display_error_message("validation_error", error_str)
            st.session_state.analyzing = False
        
        except Exception as e:
            # Unexpected errors
            display_error_message("api_failure", str(e))
            st.session_state.analyzing = False
    
    # Display results if available
    if st.session_state.analysis_result:
        display_results_dashboard(st.session_state.analysis_result)
        
        # Add action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 Analyze Another Contract", use_container_width=True):
                st.session_state.analysis_result = None
                st.session_state.analyzing = False
                st.rerun()
        
        with col2:
            if st.button("📥 Export Report (Coming Soon)", use_container_width=True, disabled=True):
                st.info("Export functionality coming in next release!")
        
        with col3:
            if st.button("📧 Share Results (Coming Soon)", use_container_width=True, disabled=True):
                st.info("Share functionality coming in next release!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem 0;">
            <p>🛡️ <strong>ContractGuard AI</strong> - Powered by Advanced Legal AI</p>
            <p style="font-size: 0.9rem;">For questions or support, contact your legal team</p>
        </div>
    """, unsafe_allow_html=True)


# ==================== APPLICATION ENTRY POINT ====================

if __name__ == "__main__":
    main()
