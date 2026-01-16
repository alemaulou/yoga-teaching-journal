"""
Yoga Teaching Journal - Complete Streamlit App
Alessandro Lou - Equinox SF Instructor
Track yoga classes, analyze patterns, get AI-powered inspiration.
"""

import streamlit as st
from snowflake.snowpark import Session
import pandas as pd
from datetime import date, datetime
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
import time


# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Yoga Teaching Journal",
    page_icon="Y",
    layout="wide"
)


# ============================================
# SNOWFLAKE CONNECTION
# ============================================

@st.cache_resource
def create_session():
    """Create Snowflake session using secrets from .streamlit/secrets.toml"""
    connection_params = {
        "account": st.secrets["account"],
        "user": st.secrets["user"],
        "password": st.secrets["password"],
        "warehouse": "YOGA_WH",
        "database": "YOGA_JOURNAL",
        "schema": "APP_DATA"
    }
    return Session.builder.configs(connection_params).create()

# Initialize connection
try:
    session = create_session()
    connected = True
except Exception as e:
    session = None
    connected = False


# ============================================
# CUSTOM CSS - Dark Theme
# ============================================

st.markdown("""
    <style>
    /* ========== BLACK BACKGROUND ========== */
    .stApp,
    .main,
    .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    body {
        background-color: #000000 !important;
    }
    
    /* White text */
    .stApp * {
        color: #FFFFFF !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stSelectbox > div > div > div {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
    }
    
    /* Dropdown styling */
    .stSelectbox > div > div > div[data-baseweb="select"] > div {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 16px rgba(255, 75, 75, 0.5) !important;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: #333333 !important;
        box-shadow: none !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #000000 !important;
        border-bottom: 1px solid #333333;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        padding: 12px 24px;
        color: #888888 !important;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border-bottom: 2px solid #FF4B4B;
    }
    
    /* Headers */
    h1 { color: #FFFFFF !important; font-weight: 700; }
    h2, h3 { color: #FFFFFF !important; font-weight: 600; }
    
    /* Captions */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #888888 !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 36px;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #AAAAAA !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: #1E1E1E !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1E1E1E !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }
    
    /* Alerts */
    .stAlert {
        background-color: #1E1E1E !important;
        border: 1px solid #444444 !important;
    }
    
    /* Divider */
    hr {
        border-color: #333333 !important;
    }
    
    /* Header bar */
    .header-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px 0;
        border-bottom: 1px solid #333333;
        margin-bottom: 20px;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .header-title {
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 14px;
        color: #888888;
        margin: 0;
    }
    
    .header-right {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
    }
    
    .connected { color: #00AA00; }
    .disconnected { color: #FF4444; }
    </style>
""", unsafe_allow_html=True)


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_base64_image(image_path):
    """Convert image to base64 for embedding"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None


@st.cache_data(ttl=60)
def get_locations(_session):
    """Fetch locations for dropdown"""
    try:
        return _session.sql("""
            SELECT location_id, location_name, neighborhood 
            FROM LOCATIONS 
            WHERE is_active = TRUE
            ORDER BY location_name
        """).to_pandas()
    except:
        return pd.DataFrame({'LOCATION_ID': [], 'LOCATION_NAME': [], 'NEIGHBORHOOD': []})


@st.cache_data(ttl=60)
def get_class_types(_session):
    """Fetch class types for dropdown"""
    try:
        return _session.sql("""
            SELECT class_type_id, display_name, is_heated, duration_minutes
            FROM CLASS_TYPES 
            WHERE is_active = TRUE
            ORDER BY class_name, duration_minutes
        """).to_pandas()
    except:
        return pd.DataFrame({'CLASS_TYPE_ID': [], 'DISPLAY_NAME': [], 'IS_HEATED': [], 'DURATION_MINUTES': []})


# ============================================
# HEADER WITH LOGO
# ============================================

logo_path = "assets/equinox_logo.png"
img_base64 = get_base64_image(logo_path) if os.path.exists(logo_path) else None

status_class = "connected" if connected else "disconnected"
status_text = "Connected to Snowflake" if connected else "Not Connected"

if img_base64:
    st.markdown(f"""
        <div class="header-bar">
            <div class="header-left">
                <img src="data:image/png;base64,{img_base64}" height="50">
                <div>
                    <p class="header-title">Yoga Teaching Journal</p>
                    <p class="header-subtitle">Alessandro Lou - Equinox SF Instructor</p>
                </div>
            </div>
            <div class="header-right">
                <span class="{status_class}">{status_text}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="header-bar">
            <div class="header-left">
                <span style="font-size: 24px; font-weight: bold; letter-spacing: 3px;">EQUINOX</span>
                <div>
                    <p class="header-title">Yoga Teaching Journal</p>
                    <p class="header-subtitle">Alessandro Lou - Equinox SF Instructor</p>
                </div>
            </div>
            <div class="header-right">
                <span class="{status_class}">{status_text}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

if not connected:
    st.error("Unable to connect to Snowflake. Please check your connection settings.")
    st.info("Make sure you've run the setup_yoga_journal_database.sql script first.")
    st.stop()


# ============================================
# NAVIGATION TABS
# ============================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Log Class", 
    "Dashboard", 
    "AI Inspiration", 
    "Class History"
])


# ============================================
# TAB 1: LOG CLASS
# ============================================

with tab1:
    st.header("Log Class")
    st.caption("Log your class with full tracking - themes, sequences, and insights.")
    
    locations_df = get_locations(session)
    class_types_df = get_class_types(session)
    
    # Row 1: Date, Time, Location
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_date = st.date_input("Date", value=date.today())
    
    with col2:
        log_time = st.time_input("Time")
    
    with col3:
        if len(locations_df) > 0:
            location_options = locations_df['LOCATION_NAME'].tolist()
            selected_location = st.selectbox("Studio Location", options=location_options)
            selected_location_id = int(locations_df[locations_df['LOCATION_NAME'] == selected_location]['LOCATION_ID'].iloc[0])
        else:
            st.warning("No locations found. Run the setup script first.")
            selected_location_id = None
    
    # Row 2: Class Type, Theme
    col1, col2 = st.columns(2)
    
    with col1:
        if len(class_types_df) > 0:
            class_type_options = class_types_df['DISPLAY_NAME'].tolist()
            selected_class_type = st.selectbox("Class Type", options=class_type_options)
            selected_row = class_types_df[class_types_df['DISPLAY_NAME'] == selected_class_type]
            selected_class_type_id = int(selected_row['CLASS_TYPE_ID'].iloc[0])
            is_heated = bool(selected_row['IS_HEATED'].iloc[0])
            
            if is_heated:
                st.caption("🔥 Heated class")
            else:
                st.caption("❄️ Non-heated class")
        else:
            st.warning("No class types found.")
            selected_class_type_id = None
    
    with col2:
        custom_theme = st.text_input(
            "Theme/Focus", 
            placeholder="e.g., Hip Openers, Heart Opening, Letting Go, Balance..."
        )
    
    # Row 3: Peak Pose, Energy
    col1, col2 = st.columns(2)
    
    with col1:
        log_peak = st.text_input("Peak Pose", placeholder="e.g., Pigeon, Crow, Wheel")
    
    with col2:
        log_energy = st.select_slider(
            "Class Energy",
            options=["Low", "Medium", "High", "Very High"],
            value="Medium"
        )
    
    # Row 4: Students, Vibe
    col1, col2 = st.columns(2)
    
    with col1:
        log_students = st.number_input("Student Count", min_value=0, max_value=60, value=15)
    
    with col2:
        log_vibe = st.slider("Vibe Rating", min_value=1, max_value=5, value=4,
                            help="How did the class feel overall?")
    
    # Intention
    log_intention = st.text_area(
        "Intention/Dharma", 
        placeholder="What was the heart of your class?",
        height=80
    )
    
    # Personal Notes
    log_notes = st.text_area(
        "Personal Notes", 
        placeholder="What worked? What didn't? Any student feedback?",
        height=80
    )
    
    # Submit button
    if st.button("Log This Class", type="primary", use_container_width=True):
        if selected_location_id and selected_class_type_id:
            day_of_week = log_date.strftime("%A")
            
            safe_peak = log_peak.replace("'", "''") if log_peak else ""
            safe_intention = log_intention.replace("'", "''") if log_intention else ""
            safe_notes = log_notes.replace("'", "''") if log_notes else ""
            safe_custom_theme = custom_theme.replace("'", "''") if custom_theme else None
            
            custom_theme_value = f"'{safe_custom_theme}'" if safe_custom_theme else "NULL"
            
            sql = f"""
                INSERT INTO CLASSES_TAUGHT (
                    class_date, class_time, day_of_week, location_id, class_type_id,
                    theme_id, custom_theme, intention, peak_pose, 
                    energy_level, student_count, vibe_rating, personal_notes
                )
                SELECT
                    '{log_date}',
                    '{log_time}',
                    '{day_of_week}',
                    {selected_location_id},
                    {selected_class_type_id},
                    NULL,
                    {custom_theme_value},
                    '{safe_intention}',
                    '{safe_peak}',
                    '{log_energy}',
                    {log_students},
                    {log_vibe},
                    '{safe_notes}'
            """
            
            try:
                session.sql(sql).collect()
                st.success("Class logged successfully.")
                st.balloons()
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Error logging class: {str(e)}")
        else:
            st.error("Please select a location and class type.")


# ============================================
# TAB 2: DASHBOARD (4 metrics, evenly spaced)
# ============================================

with tab2:
    st.header("Dashboard")
    
    # Overall stats - 4 metrics evenly spaced
    try:
        stats = session.sql("""
            SELECT 
                COUNT(*) as total_classes,
                COALESCE(SUM(student_count), 0) as total_students,
                ROUND(AVG(vibe_rating), 1) as avg_vibe,
                COUNT(DISTINCT location_id) as locations_taught
            FROM CLASSES_TAUGHT
        """).to_pandas()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Classes", int(stats['TOTAL_CLASSES'].iloc[0]))
        with col2:
            st.metric("Students Reached", int(stats['TOTAL_STUDENTS'].iloc[0]))
        with col3:
            avg = stats['AVG_VIBE'].iloc[0]
            st.metric("Avg Vibe", f"{avg}/5" if avg else "N/A")
        with col4:
            st.metric("Locations", int(stats['LOCATIONS_TAUGHT'].iloc[0]))
    except Exception as e:
        st.info("Log some classes to see your stats!")
    
    st.divider()
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("By Location")
        try:
            location_stats = session.sql("""
                SELECT * FROM ANALYTICS.LOCATION_STATS
            """).to_pandas()
            
            if len(location_stats) > 0:
                fig = px.bar(
                    location_stats, 
                    x='LOCATION_NAME', 
                    y='TOTAL_CLASSES',
                    color='AVG_VIBE',
                    color_continuous_scale='RdYlGn',
                    title='Classes by Location'
                )
                fig.update_layout(
                    plot_bgcolor='#000000',
                    paper_bgcolor='#000000',
                    font_color='#FFFFFF',
                    xaxis=dict(gridcolor='#333333'),
                    yaxis=dict(gridcolor='#333333')
                )
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("No location data yet.")
    
    with col2:
        st.subheader("By Class Type")
        try:
            type_stats = session.sql("""
                SELECT * FROM ANALYTICS.CLASS_TYPE_STATS
            """).to_pandas()
            
            if len(type_stats) > 0:
                fig = px.pie(
                    type_stats,
                    values='TOTAL_CLASSES',
                    names='CLASS_TYPE',
                    title='Classes by Type'
                )
                fig.update_layout(
                    plot_bgcolor='#000000',
                    paper_bgcolor='#000000',
                    font_color='#FFFFFF'
                )
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("No class type data yet.")
    
    st.divider()
    
    # Daily student counts
    st.subheader("Student Counts Over Time")
    try:
        daily_students = session.sql("""
            SELECT 
                class_date,
                student_count,
                ct.display_name as class_type,
                l.location_name
            FROM CLASSES_TAUGHT c
            LEFT JOIN CLASS_TYPES ct ON c.class_type_id = ct.class_type_id
            LEFT JOIN LOCATIONS l ON c.location_id = l.location_id
            WHERE class_date >= DATEADD(day, -90, CURRENT_DATE())
            ORDER BY class_date
        """).to_pandas()
        
        if len(daily_students) > 0:
            daily_students['CLASS_DATE'] = pd.to_datetime(daily_students['CLASS_DATE'])
            
            fig = px.scatter(
                daily_students,
                x='CLASS_DATE',
                y='STUDENT_COUNT',
                color='LOCATION_NAME',
                hover_data=['CLASS_TYPE'],
                title='Student Count per Class',
                labels={'CLASS_DATE': 'Date', 'STUDENT_COUNT': 'Students', 'LOCATION_NAME': 'Location'}
            )
            
            fig.add_trace(
                go.Scatter(
                    x=daily_students['CLASS_DATE'],
                    y=daily_students['STUDENT_COUNT'].rolling(window=3, min_periods=1).mean(),
                    mode='lines',
                    name='3-class avg',
                    line=dict(color='#FF4B4B', width=2, dash='dash')
                )
            )
            
            fig.update_layout(
                plot_bgcolor='#000000',
                paper_bgcolor='#000000',
                font_color='#FFFFFF',
                xaxis=dict(gridcolor='#333333'),
                yaxis=dict(gridcolor='#333333', rangemode='tozero'),
                legend=dict(bgcolor='rgba(0,0,0,0)')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Students", f"{daily_students['STUDENT_COUNT'].mean():.1f}")
            with col2:
                st.metric("Max Students", int(daily_students['STUDENT_COUNT'].max()))
            with col3:
                st.metric("Min Students", int(daily_students['STUDENT_COUNT'].min()))
                
    except Exception as e:
        st.info("Not enough data for student trends yet.")


# ============================================
# TAB 3: AI INSPIRATION
# ============================================

with tab3:
    st.header("AI Inspiration")
    
    if 'theme_result' not in st.session_state:
        st.session_state.theme_result = None
    if 'sequence_result' not in st.session_state:
        st.session_state.sequence_result = None
    
    with st.expander("Your teaching history (used for personalization)"):
        try:
            history_preview = session.sql("""
                SELECT 
                    custom_theme AS theme,
                    ROUND(AVG(vibe_rating), 1) AS avg_vibe,
                    ROUND(AVG(student_count), 0) AS avg_students,
                    COUNT(*) AS times_taught
                FROM classes_taught
                WHERE custom_theme IS NOT NULL
                GROUP BY custom_theme
                ORDER BY times_taught DESC
                LIMIT 10
            """).to_pandas()
            
            if len(history_preview) > 0:
                st.dataframe(history_preview, hide_index=True, use_container_width=True)
            else:
                st.info("No class history yet. Log some classes first!")
        except Exception as e:
            st.warning(f"Could not load history: {e}")
    
    st.divider()
    
    # GENERATOR 1: Suggest a New Theme
    st.subheader("Suggest a New Theme")
    
    if st.button("Generate Theme Idea", key="btn_theme", use_container_width=True):
        with st.spinner("Analyzing your teaching history..."):
            try:
                result = session.sql("""
                    WITH my_themes AS (
                        SELECT 
                            custom_theme AS theme,
                            ROUND(AVG(student_count), 0) AS avg_students,
                            COUNT(*) AS times_taught
                        FROM classes_taught
                        WHERE custom_theme IS NOT NULL
                        GROUP BY custom_theme
                    ),
                    ai_past_themes AS (
                        SELECT theme_name, theme_approach
                        FROM ai_generated_themes
                        ORDER BY created_at DESC
                        LIMIT 5
                    ),
                    aggregated AS (
                        SELECT 
                            COALESCE(
                                LISTAGG(theme || ' (taught ' || times_taught || 'x, avg ' || avg_students || ' students)', '; ')
                                WITHIN GROUP (ORDER BY times_taught DESC),
                                'No history yet'
                            ) AS theme_list,
                            (SELECT COALESCE(LISTAGG('Theme: ' || theme_name || ' | Approach: ' || theme_approach, ' /// '), 'None yet') FROM ai_past_themes) AS past_themes
                        FROM my_themes
                    )
                    SELECT AI_COMPLETE(
                        model => 'mistral-large',
                        prompt => 'You are helping a yoga teacher plan classes based on their teaching history.

MY TEACHING DATA:
' || theme_list || '

THEMES I HAVE ALREADY GENERATED:
' || past_themes || '

Based on this data, suggest a theme for my next class.

RULES:
1. Reference specific patterns from my teaching data (cite numbers)
2. If you suggest a theme I have generated before, you MUST suggest a DIFFERENT approach (different angle, different physical focus, different message)
3. Vary your suggestions - do not repeat the same theme AND same approach

Format your response as:
THEME: [name]
DATA INSIGHTS: [what patterns you see in my history - cite specific numbers]
WHY THIS FITS: [how this theme connects to what works for me]
APPROACH: [how to teach this theme - what message, physical focus, feeling students leave with]',
                        model_parameters => { 'temperature': 0.6 }
                    ) AS suggestion
                    FROM aggregated
                """).to_pandas()
                
                if len(result) > 0 and result['SUGGESTION'].iloc[0]:
                    st.session_state.theme_result = result['SUGGESTION'].iloc[0]
                    
                    suggestion_text = st.session_state.theme_result
                    if 'THEME:' in suggestion_text:
                        theme_line = suggestion_text.split('THEME:')[1].split('\n')[0].strip()
                        approach_part = ''
                        if 'APPROACH:' in suggestion_text:
                            approach_part = suggestion_text.split('APPROACH:')[1].strip()[:300].replace("'", "''")
                        safe_theme = theme_line.replace("'", "''")
                        if safe_theme:
                            try:
                                session.sql(f"""
                                    INSERT INTO ai_generated_themes (theme_name, theme_approach)
                                    VALUES ('{safe_theme}', '{approach_part}')
                                """).collect()
                            except:
                                pass
                else:
                    st.session_state.theme_result = None
                    st.warning("No suggestion generated. Make sure you have class history.")
            except Exception as e:
                st.session_state.theme_result = None
                st.error(f"Error: {e}")
    
    if st.session_state.theme_result:
        clean_text = str(st.session_state.theme_result).replace('\\n', '\n').replace('\\t', '\t')
        st.markdown("**Theme Suggestion**")
        st.success(clean_text)
        if st.button("Clear", key="clear_theme"):
            st.session_state.theme_result = None
            st.rerun()
    
    st.divider()
    
    # GENERATOR 2: Create a Sequence Idea
    st.subheader("Create a Sequence")
    
    if st.button("Generate Sequence", key="btn_sequence", use_container_width=True):
        with st.spinner("Analyzing your teaching history..."):
            try:
                result = session.sql("""
                    WITH my_popular_classes AS (
                        SELECT 
                            custom_theme AS theme,
                            peak_pose,
                            energy_level,
                            student_count
                        FROM classes_taught
                        WHERE student_count >= 15
                    ),
                    ai_past_sequences AS (
                        SELECT peak_pose, sequence_outline
                        FROM ai_generated_sequences
                        ORDER BY created_at DESC
                        LIMIT 5
                    ),
                    aggregated AS (
                        SELECT 
                            (SELECT COALESCE(LISTAGG('Theme: ' || COALESCE(theme, 'none') || ', Peak: ' || COALESCE(peak_pose, 'none') || ', Energy: ' || COALESCE(energy_level, 'medium') || ', Students: ' || student_count, ' | '), 'no data') FROM my_popular_classes) AS popular_list,
                            (SELECT COALESCE(LISTAGG('Peak: ' || peak_pose || ' | Sequence: ' || sequence_outline, ' /// '), 'None yet') FROM ai_past_sequences) AS past_sequences
                    )
                    SELECT AI_COMPLETE(
                        model => 'mistral-large',
                        prompt => 'You are helping a yoga teacher plan classes based on their teaching history.

MY MOST POPULAR CLASSES (15+ students):
' || popular_list || '

SEQUENCES I HAVE ALREADY GENERATED:
' || past_sequences || '

Based on this data, suggest a peak pose and build a 60-minute sequence.

RULES:
1. Reference specific patterns from my teaching data (cite numbers)
2. If you suggest a peak pose I have generated before, you MUST create a DIFFERENT sequence approach (different warmup, different standing poses, different prep)
3. Ensure the sequence is anatomically sound - proper warm-up for the peak, appropriate counter-poses
4. Vary your suggestions - do not repeat the same pose AND same sequence style

Format your response as:
PEAK POSE: [name]
DATA INSIGHTS: [what patterns you see in my history - cite specific numbers]
WHY THIS FITS: [how this connects to what works for me]
SEQUENCE:
- Warmup (10 min): [poses]
- Standing (15 min): [poses]
- Peak Prep (20 min): [poses]
- Cool Down (10 min): [poses]
- Savasana (5 min)',
                        model_parameters => { 'temperature': 0.6 }
                    ) AS suggestion
                    FROM aggregated
                """).to_pandas()
                
                if len(result) > 0 and result['SUGGESTION'].iloc[0]:
                    st.session_state.sequence_result = result['SUGGESTION'].iloc[0]
                    
                    suggestion_text = st.session_state.sequence_result
                    if 'PEAK POSE:' in suggestion_text and 'SEQUENCE:' in suggestion_text:
                        pose_line = suggestion_text.split('PEAK POSE:')[1].split('\n')[0].strip()
                        sequence_part = suggestion_text.split('SEQUENCE:')[1].strip()
                        sequence_outline = sequence_part[:500].replace("'", "''")
                        safe_pose = pose_line.replace("'", "''")
                        if safe_pose:
                            try:
                                session.sql(f"""
                                    INSERT INTO ai_generated_sequences (peak_pose, sequence_outline)
                                    VALUES ('{safe_pose}', '{sequence_outline}')
                                """).collect()
                            except:
                                pass
                else:
                    st.session_state.sequence_result = None
                    st.warning("No sequence generated. Make sure you have logged classes with 15+ students.")
            except Exception as e:
                st.session_state.sequence_result = None
                st.error(f"Error: {e}")
    
    if st.session_state.sequence_result:
        clean_text = str(st.session_state.sequence_result).replace('\\n', '\n').replace('\\t', '\t')
        st.markdown("**Sequence Suggestion**")
        st.success(clean_text)
        if st.button("Clear", key="clear_sequence"):
            st.session_state.sequence_result = None
            st.rerun()


# ============================================
# TAB 4: HISTORY (uses custom_theme directly)
# ============================================

with tab4:
    st.header("Class History")
    
    locations_df = get_locations(session)
    class_types_df = get_class_types(session)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_days = st.selectbox(
            "Time range", 
            options=[7, 14, 30, 90, 365], 
            index=2,
            format_func=lambda x: f"Last {x} days"
        )
    
    with col2:
        location_filter_options = ["All Locations"] + locations_df['LOCATION_NAME'].tolist()
        filter_location = st.selectbox("Location", options=location_filter_options)
    
    with col3:
        type_filter_options = ["All Types"] + class_types_df['DISPLAY_NAME'].tolist()
        filter_type = st.selectbox("Class Type", options=type_filter_options)
    
    with col4:
        search_term = st.text_input("Search", placeholder="e.g., hip, crow")
    
    query = f"""
        SELECT 
            c.class_id,
            c.class_date,
            c.day_of_week,
            c.class_time,
            l.location_name,
            ct.display_name as class_type,
            ct.is_heated,
            c.custom_theme AS theme,
            c.peak_pose,
            c.energy_level,
            c.student_count,
            c.vibe_rating,
            c.intention,
            c.personal_notes
        FROM CLASSES_TAUGHT c
        LEFT JOIN LOCATIONS l ON c.location_id = l.location_id
        LEFT JOIN CLASS_TYPES ct ON c.class_type_id = ct.class_type_id
        WHERE c.class_date >= DATEADD(day, -{filter_days}, CURRENT_DATE())
    """
    
    if filter_location != "All Locations":
        query += f" AND l.location_name = '{filter_location}'"
    
    if filter_type != "All Types":
        query += f" AND ct.display_name = '{filter_type}'"
    
    if search_term:
        safe_search = search_term.replace("'", "''").lower()
        query += f""" AND (
            LOWER(c.custom_theme) LIKE '%{safe_search}%' 
            OR LOWER(c.personal_notes) LIKE '%{safe_search}%'
            OR LOWER(c.peak_pose) LIKE '%{safe_search}%'
        )"""
    
    query += " ORDER BY c.class_date DESC, c.class_time DESC"
    
    try:
        history = session.sql(query).to_pandas()
        
        if len(history) > 0:
            st.caption(f"Showing {len(history)} classes")
            
            for _, row in history.iterrows():
                heated_icon = "🔥" if row['IS_HEATED'] else "❄️"
                theme_display = f" – {row['THEME']}" if row['THEME'] else ""
                
                with st.expander(f"**{row['CLASS_DATE']}** {heated_icon} {row['LOCATION_NAME']} – {row['CLASS_TYPE']}{theme_display}"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"{row['DAY_OF_WEEK']}")
                        if row['CLASS_TIME']:
                            st.write(f"{row['CLASS_TIME']}")
                    with col2:
                        st.write(f"{row['ENERGY_LEVEL']}")
                    with col3:
                        st.write(f"{row['STUDENT_COUNT'] or '?'} students")
                    with col4:
                        st.write(f"Vibe: {row['VIBE_RATING'] or '?'}/5")
                    
                    if row['THEME']:
                        st.write(f"**Theme:** {row['THEME']}")
                    
                    if row['PEAK_POSE']:
                        st.write(f"**Peak:** {row['PEAK_POSE']}")
                    
                    if row['INTENTION']:
                        st.write(f"**Intention:** {row['INTENTION']}")
                    
                    if row['PERSONAL_NOTES']:
                        st.write(f"**Notes:** {row['PERSONAL_NOTES']}")
        else:
            st.info("No classes found matching your filters.")
    except Exception as e:
        st.error(f"Error loading history: {str(e)}")


# ============================================
# FOOTER
# ============================================

st.divider()
st.caption("Built with Snowflake + Streamlit.")
