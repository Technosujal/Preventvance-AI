"""
Theme configuration for the Healthcare System
Light theme with blue and white color palette for trust, calm, and peace
"""

import streamlit as st

# Color Palette - Healthcare Light & Calm Theme
THEME_COLORS = {
    # Primary Colors (Trust & Brand)
    'primary': '#0067A5',         # Deep Cerulean (Pantone 301 C)
    'primary_dark': '#004F80',    # Darker shade for hover/active
    'primary_light': '#E6F0F6',   # Very light tint for backgrounds
    
    # Secondary Colors (Calm & Support)
    'secondary': '#A0D2EB',       # Light Sky Blue
    
    # Base & Text Colors (Cleanliness & Readability)
    'background': '#FFFFFF',      # Pure White (main background)
    'surface': '#F4F7F9',        # Off-white (for content sections, cards)
    'text_primary': '#253B4A',    # Dark Slate Blue (for headings)
    'text_secondary': '#5A6D7A',  # Medium Gray (for body text)
    'border': '#DDE4E9',          # Light Gray (for borders/dividers)
    
    # Accent & Status Colors (Action & Information)
    'accent': '#007BFF',          # Active Blue (for buttons/links)
    'success': '#28A745',         # Reassuring Green
    'warning': '#FFC107',         # Soft Yellow
    'error': '#DC3545',           # Clear Red
}

def apply_light_theme():
    """Apply the enhanced light theme CSS to Streamlit."""
    st.markdown(f"""
    <style>
    /* Import Google Fonts for better typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {{
        --font-family: 'Plus Jakarta Sans', sans-serif;
        --font-family-secondary: 'Inter', sans-serif;
        
        --color-primary: {THEME_COLORS['primary']};
        --color-primary-dark: {THEME_COLORS['primary_dark']};
        --color-primary-light: {THEME_COLORS['primary_light']};
        
        --color-secondary: {THEME_COLORS['secondary']};
        
        --color-background: {THEME_COLORS['background']};
        --color-surface: {THEME_COLORS['surface']};
        --color-text-primary: {THEME_COLORS['text_primary']};
        --color-text-secondary: {THEME_COLORS['text_secondary']};
        --color-border: {THEME_COLORS['border']};
        
        --color-success: {THEME_COLORS['success']};
        --color-warning: {THEME_COLORS['warning']};
        --color-danger: {THEME_COLORS['error']};
        --color-info: {THEME_COLORS['accent']};
        
        --border-radius-sm: 0.5rem;
        --border-radius-md: 0.75rem;
        --border-radius-lg: 1rem;
        --border-radius-xl: 1.5rem;
        
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.3);
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes float {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-15px); }}
        100% {{ transform: translateY(0px); }}
    }}
    
    @keyframes rotateGradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .animate-float {{ animation: float 5s ease-in-out infinite; }}
    .animate-fade-in {{ animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}
    
    /* Global styles */
    .stApp {{
        background: linear-gradient(-45deg, rgba(248, 250, 252, 0.8), rgba(241, 245, 249, 0.8), rgba(239, 246, 255, 0.8), rgba(248, 250, 252, 0.8));
        background-size: 400% 400%;
        animation: rotateGradient 15s ease infinite;
        font-family: var(--font-family);
        color: var(--color-text-secondary);
    }}
    
    /* Background Layering Utility */
    .bg-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        opacity: 0.15;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: var(--color-text-primary);
        font-weight: 800;
        font-family: var(--font-family);
        letter-spacing: -0.04em;
    }}
    
    h1 {{ font-size: 3.5rem; line-height: 1; margin-bottom: 2rem; }}
    
    /* Main Container */
    .main .block-container {{
        padding-top: 6rem !important;
        max-width: 1400px !important;
        background: transparent !important;
    }}

    /* HIDE SIDEBAR */
    [data-testid="stSidebar"] {{ display: none; }}
    section[data-testid="stSidebar"] {{ display: none; }}
    
    /* Glass Cards with Floating */
    .glass-card {{
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: var(--border-radius-xl);
        padding: 3rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 40px 80px -12px rgba(0, 0, 0, 0.15);
    }}

    /* Premium Pillar Buttons */
    .stButton > button {{
        border-radius: 50px !important;
        font-weight: 800 !important;
        padding: 0.8rem 2.5rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        font-size: 0.8rem !important;
        border: none !important;
        height: auto !important;
    }}
    
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%) !important;
        color: white !important;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.4) !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        transform: translateY(-5px) scale(1.05) !important;
        box-shadow: 0 20px 35px -5px rgba(37, 99, 235, 0.6) !important;
        filter: brightness(1.1);
    }}
    
    .stButton > button[kind="secondary"] {{
        background: rgba(255, 255, 255, 0.9) !important;
        color: #1e3a8a !important;
        border: 1px solid rgba(37, 99, 235, 0.2) !important;
        backdrop-filter: blur(10px);
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background: #1e3a8a !important;
        color: white !important;
        transform: translateY(-3px) !important;
    }}

    /* Metric Card - Floating */
    .metric-card {{
        background: white;
        border-radius: var(--border-radius-xl);
        padding: 2.5rem;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        transition: all 0.5s ease;
        animation: float 6s ease-in-out infinite;
    }}
    
    .metric-card:hover {{
        transform: translateY(-15px) scale(1.02);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
        animation-play-state: paused;
    }}

    /* Risk Badges - Vibrant Colors */
    .risk-badge {{
        padding: 0.6rem 1.4rem;
        border-radius: 50px;
        font-weight: 800;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }}

    .risk-high {{ 
        background: #fef2f2 !important; 
        color: #dc2626 !important; 
        border: 2px solid #fee2e2 !important; 
    }}
    .risk-medium {{ 
        background: #fffbeb !important; 
        color: #d97706 !important; 
        border: 2px solid #fef3c7 !important; 
    }}
    .risk-low {{ 
        background: #f0fdf4 !important; 
        color: #16a34a !important; 
        border: 2px solid #dcfce7 !important; 
    }}
    
    .risk-high span {{ color: #ef4444; }}
    .risk-medium span {{ color: #f59e0b; }}
    .risk-low span {{ color: #10b981; }}

    /* Print Styles */
    @media print {{
        .bg-overlay, .custom-navbar, .stButton, [data-testid="stHeader"] {{
            display: none !important;
        }}
        .main .block-container {{
            padding-top: 1rem !important;
            max-width: 100% !important;
        }}
        .glass-card {{
            box-shadow: none !important;
            border: 1px solid #eee !important;
            background: white !important;
            break-inside: avoid;
        }}
        .metric-card {{
            animation: none !important;
            box-shadow: none !important;
            border: 1px solid #eee !important;
            break-inside: avoid;
        }}
        body {{
            background: white !important;
        }}
    }}

    </style>
    """, unsafe_allow_html=True)


def create_navbar(user_name, user_role, show_logout=True):
    """Create a top navigation bar for authenticated users."""
    st.markdown(f"""
        <div class="custom-navbar">
            <div style="display: flex; align-items: center; gap: 1.25rem;">
                <div style="font-size: 2.25rem; filter: drop-shadow(0 0 15px rgba(14, 165, 233, 0.3));">🩺</div>
                <div style="font-weight: 900; font-size: 1.8rem; color: #0369a1; letter-spacing: -0.06em;">
                    Health<span style="color: #0c4a6e;">Care</span><span style="color: #0ea5e9; font-weight: 400; font-size: 1rem; margin-left: 0.2rem; vertical-align: top;">AI</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 3rem;">
                <div style="text-align: right;">
                    <div style="font-weight: 800; color: #0f172a; font-size: 1.1rem; letter-spacing: -0.02em;">{user_name}</div>
                    <div style="font-size: 0.75rem; font-weight: 800; color: #0284c7; text-transform: uppercase; letter-spacing: 0.15em; opacity: 0.9;">{user_role}</div>
                </div>
            </div>
        </div>
        <div style="margin-top: 2rem;"></div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([8.5, 1, 1])
    with col3:
        if show_logout:
            if st.button("LOGOUT", key="btn_logout", type="secondary"):
                st.session_state.clear()
                st.rerun()

def create_metric_card(label, value, help_text=None, color="primary"):
    """Create a styled metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #64748b; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em; opacity: 0.7;">{label}</div>
        <div style="font-size: 3.25rem; font-weight: 900; color: #0f172a; margin: 0.75rem 0; letter-spacing: -0.05em;">{value}</div>
        {f'<div style="font-size: 0.9rem; color: #0284c7; font-weight: 700; opacity: 0.9;">{help_text}</div>' if help_text else ""}
    </div>
    """, unsafe_allow_html=True)

def create_risk_badge(level):
    """Create a styled risk level badge."""
    level_lower = str(level).lower()
    if level_lower == "high":
        return f'<span class="risk-badge risk-high animate-pulse" style="padding: 0.6rem 1.4rem; font-size: 0.8rem;"><span style="font-size: 1.2rem;">●</span> Critical Risk</span>'
    elif level_lower == "medium":
        return f'<span class="risk-badge risk-medium" style="padding: 0.6rem 1.4rem; font-size: 0.8rem;"><span style="font-size: 1.2rem;">●</span> Moderate Risk</span>'
    elif level_lower == "low":
        return f'<span class="risk-badge risk-low" style="padding: 0.6rem 1.4rem; font-size: 0.8rem;"><span style="font-size: 1.2rem;">●</span> Low Risk</span>'
    else:
        return f'<span class="risk-badge" style="background: rgba(241, 245, 249, 0.5); color: #64748b; border: 1px solid #e2e8f0; padding: 0.6rem 1.4rem; font-size: 0.8rem;">N/A</span>'