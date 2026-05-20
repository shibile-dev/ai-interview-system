import streamlit as st
import re
from modules.cv_parser import extract_text_from_pdf
from modules.ai_questions import analyze_cv, generate_interview_questions
from modules.emotion_detector import detect_emotion
from modules.evaluator import evaluate_answer
from modules.database import init_db, save_interview, get_all_interviews, get_average_scores, register_user, login_user
from modules.charts import create_score_radar_chart, create_emotion_pie_chart, create_score_bar_chart
from modules.report_generator import generate_interview_report

# Initialize database
init_db()
# Session state
if 'cv_text' not in st.session_state:
    st.session_state.cv_text = ""
if 'cv_analysis' not in st.session_state:
    st.session_state.cv_analysis = ""
if 'questions' not in st.session_state:
    st.session_state.questions = ""
if 'emotions' not in st.session_state:
    st.session_state.emotions = []
if 'scores' not in st.session_state:
    st.session_state.scores = {}
if 'candidate_name' not in st.session_state:
    st.session_state.candidate_name = ""
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'language' not in st.session_state:
    st.session_state.language = "🇬🇧 English"
if 'competition_questions' not in st.session_state:
    st.session_state.competition_questions = ""
if 'lang_questions' not in st.session_state:
    st.session_state.lang_questions = ""
if 'lang_selected' not in st.session_state:
    st.session_state.lang_selected = "English"
if 'github_repo' not in st.session_state:
    st.session_state.github_repo = None
if 'github_questions' not in st.session_state:
    st.session_state.github_questions = ""

# Page config
st.set_page_config(
    page_title="AI Interview System",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #0D0A1A;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0D0A1A 0%, #1A1028 50%, #0D0A1A 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0818 0%, #150F25 100%);
        border-right: 1px solid #FFB30044;
    }
    
    /* Sidebar title */
    [data-testid="stSidebar"] h1 {
        color: #FFB300 !important;
        font-size: 20px !important;
    }
    
    /* All buttons */
    .stButton>button {
        background: linear-gradient(90deg, #FFB300, #FF8C00);
        color: #0D0A1A;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(255, 179, 0, 0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #FFC933, #FFB300);
        box-shadow: 0 6px 20px rgba(255, 179, 0, 0.5);
        transform: translateY(-2px);
    }
    
    /* Score cards */
    .score-card {
        background: linear-gradient(135deg, #1E1535, #2A1F45);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #FFB30044;
        box-shadow: 0 4px 20px rgba(255, 179, 0, 0.1);
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .score-card:hover {
        border: 1px solid #FFB300;
        box-shadow: 0 6px 25px rgba(255, 179, 0, 0.25);
        transform: translateY(-3px);
    }
    
    .score-card h2 {
        font-size: 40px;
        margin: 0;
    }
    
    .score-card h3 {
        color: #FFB300;
        font-size: 18px;
        margin: 10px 0;
    }
    
    .score-card p {
        color: #A89BC2;
        font-size: 14px;
    }
    
    /* Big score number */
    .big-score {
        font-size: 52px;
        font-weight: bold;
        color: #FFB300;
        text-shadow: 0 0 20px rgba(255, 179, 0, 0.5);
    }
    
    /* Small score label */
    .score-label {
        color: #A89BC2;
        font-size: 14px;
        margin-bottom: 5px;
    }
    
    /* Header banner */
    .header-banner {
        background: linear-gradient(90deg, #FFB30022, #9B59B622);
        border: 1px solid #FFB30044;
        border-radius: 15px;
        padding: 20px 30px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .header-banner h1 {
        color: #FFB300;
        font-size: 28px;
        margin: 0;
        text-shadow: 0 0 30px rgba(255, 179, 0, 0.4);
    }
    
    .header-banner p {
        color: #A89BC2;
        margin: 5px 0 0 0;
        font-size: 16px;
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: #E8E0F5 !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        background-color: #1E1535;
        border: 1px solid #FFB30044;
        border-radius: 10px;
        color: white;
    }
    
    .stTextArea>div>div>textarea {
        background-color: #1E1535;
        border: 1px solid #FFB30044;
        border-radius: 10px;
        color: white;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #1E1535;
        border: 2px dashed #FFB30044;
        border-radius: 15px;
        padding: 20px;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E1535, #2A1F45);
        border: 1px solid #FFB30044;
        border-radius: 10px;
        padding: 15px;
    }
    
    [data-testid="stMetricValue"] {
        color: #FFB300 !important;
        font-size: 24px !important;
    }
    
    /* Divider */
    hr {
        border-color: #FFB30022;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1E1535;
        border-radius: 10px;
        border: 1px solid #FFB30033;
        color: #FFB300 !important;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        background: linear-gradient(90deg, #FFB30022, #9B59B622);
        border: 1px solid #FFB300;
        color: #FFB300;
        margin-bottom: 20px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0D0A1A;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #FFB300;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🤖 AI Interview System")
st.sidebar.markdown("---")

if st.session_state.logged_in:
    st.sidebar.markdown(f"👤 **{st.session_state.current_user['full_name']}**")
    st.sidebar.markdown(f"📧 {st.session_state.current_user['email']}")
    st.sidebar.markdown("---")
    
    # Language selector
    language = st.sidebar.selectbox(
        "🌍 Language",
        ["🇬🇧 English", "🇸🇦 Arabic", "🇸🇴 Somali", "🇹🇷 Turkish"]
    )
    st.session_state.language = language
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📄 CV Analysis", "🎤 Interview", "📊 Dashboard", "📋 History", "🏆 Competition", "💼 Job Matcher", "🌍 Languages", "🐙 GitHub Analysis"]
)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.cv_text = ""
        st.session_state.cv_analysis = ""
        st.session_state.questions = ""
        st.session_state.emotions = []
        st.session_state.scores = {}
        st.rerun()
else:
    page = "🔐 Login"
# ============================================================
# PAGE 0 — LOGIN/SIGNUP
# ============================================================

if page == "🔐 Login":
    
    st.markdown("""
    <style>
    .login-card {
        background: linear-gradient(145deg, #1a1535, #231d40);
        border: 1px solid #FFB30044;
        border-radius: 24px;
        padding: 50px 40px;
        text-align: center;
        box-shadow: 0 0 60px rgba(255,179,0,0.1),
                    0 0 120px rgba(155,89,182,0.08);
        max-width: 480px;
        margin: 0 auto;
    }
    .login-logo-circle {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #FFB300, #FF6B00);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px auto;
        font-size: 36px;
        box-shadow: 0 0 30px rgba(255,179,0,0.4);
    }
    .login-title {
        color: white;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .login-sub {
        color: #A89BC2;
        font-size: 14px;
        margin-bottom: 30px;
    }
    .divider-line {
        display: flex;
        align-items: center;
        margin: 20px 0;
        color: #A89BC2;
        font-size: 13px;
    }
    .divider-line::before,
    .divider-line::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #FFB30033;
        margin: 0 10px;
    }
    .pill-row {
        display: flex;
        justify-content: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 25px;
    }
    .pill-tag {
        background: rgba(255,179,0,0.1);
        border: 1px solid rgba(255,179,0,0.25);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 12px;
        color: #FFB300;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.show_signup:
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div class='login-card'>
                <div class='login-logo-circle'>🤖</div>
                <div class='login-title'>AI Interview System</div>
                <div class='login-sub'>Powered by Google Gemini AI</div>
                <div class='pill-row'>
                    <span class='pill-tag'>🎯 CV Analysis</span>
                    <span class='pill-tag'>🏆 Competition</span>
                    <span class='pill-tag'>🌍 4 Languages</span>
                    <span class='pill-tag'>💼 Job Matcher</span>
                </div>
                <div class='divider-line'>Sign in to continue</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            email = st.text_input(
                "📧 Email",
                placeholder="your@email.com"
            )
            password = st.text_input(
                "🔑 Password",
                type="password",
                placeholder="••••••••"
            )
            
            st.markdown("")
            
            if st.button("🚀 Sign In"):
                if email and password:
                    success, result = login_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.current_user = result
                        st.success(f"✅ Welcome back, {result['full_name']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("⚠️ Please fill in all fields!")
            
            st.markdown("""
            <div class='divider-line'>New here?</div>
            """, unsafe_allow_html=True)
            
            if st.button("✨ Create Free Account"):
                st.session_state.show_signup = True
                st.rerun()
    
    else:
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div class='login-card'>
                <div class='login-logo-circle'>🌟</div>
                <div class='login-title'>Create Account</div>
                <div class='login-sub'>Join the future of interview preparation</div>
                <div class='divider-line'>Fill in your details</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            full_name = st.text_input(
                "👤 Full Name",
                placeholder="Mohamed Shibile"
            )
            email = st.text_input(
                "📧 Email",
                placeholder="your@email.com"
            )
            password = st.text_input(
                "🔑 Password",
                type="password",
                placeholder="Min 6 characters"
            )
            confirm_password = st.text_input(
                "🔑 Confirm Password",
                type="password",
                placeholder="Repeat password"
            )
            
            st.markdown("")
            
            if st.button("🎉 Create My Account"):
                if full_name and email and password and confirm_password:
                    if password == confirm_password:
                        if len(password) >= 6:
                            success, message = register_user(
                                full_name, email, password
                            )
                            if success:
                                st.success("✅ Account created! Please login!")
                                st.session_state.show_signup = False
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.warning("⚠️ Password must be 6+ characters!")
                    else:
                        st.error("❌ Passwords don't match!")
                else:
                    st.warning("⚠️ Please fill in all fields!")
            
            st.markdown("""
            <div class='divider-line'>Already have an account?</div>
            """, unsafe_allow_html=True)
            
            if st.button("🔐 Back to Login"):
                st.session_state.show_signup = False
                st.rerun()
# ============================================================
# PAGE 1 — HOME
# ============================================================
if page == "🏠 Home":
    
    # Header Banner
    st.markdown("""
    <div class='header-banner'>
        <h1>🤖 AI Interview & Communication Analysis Platform</h1>
        <p>Powered by Google Gemini AI — Built for the future of recruitment</p>
        <span class='status-badge'>⚡ SYSTEM ONLINE</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='score-card'>
            <h2>🧠</h2>
            <div class='big-score'>AI</div>
            <p>Powered Analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='score-card'>
            <h2>⚡</h2>
            <div class='big-score'>8</div>
            <p>Core Features</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='score-card'>
            <h2>🌍</h2>
            <div class='big-score'>4</div>
            <p>Languages</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='score-card'>
            <h2>🏆</h2>
            <div class='big-score'>∞</div>
            <p>Practice Sessions</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features section
    st.markdown("### 🚀 How It Works")
    st.markdown("")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='score-card'>
            <h2>📄</h2>
            <h3>Step 1 — Upload CV</h3>
            <p>Upload your CV in PDF format. Our AI instantly extracts and analyzes your skills, experience, and strengths using Google Gemini AI.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='score-card'>
            <h2>🎤</h2>
            <h3>Step 2 — Get Interviewed</h3>
            <p>Answer AI-generated questions tailored specifically to YOUR CV. Get scored on communication, technical knowledge, and confidence.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='score-card'>
            <h2>📊</h2>
            <h3>Step 3 — View Analytics</h3>
            <p>See detailed performance charts, emotion analysis, AI feedback, and improvement suggestions on your personal dashboard.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Technology stack
    st.markdown("### 🛠️ Technology Stack")
    st.markdown("")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class='score-card'>
            <h2>🐍</h2>
            <h3>Python</h3>
            <p>Core Backend</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='score-card'>
            <h2>🤖</h2>
            <h3>Gemini AI</h3>
            <p>Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='score-card'>
            <h2>📱</h2>
            <h3>Streamlit</h3>
            <p>Dashboard UI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='score-card'>
            <h2>📈</h2>
            <h3>Plotly</h3>
            <p>Charts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class='score-card'>
            <h2>🗄️</h2>
            <h3>SQLite</h3>
            <p>Database</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Call to action
    st.markdown("""
    <div class='header-banner'>
        <h1>👈 Start by clicking CV Analysis in the sidebar!</h1>
        <p>Upload your CV and let AI take it from there</p>
    </div>
    """, unsafe_allow_html=True)
# ============================================================
# PAGE 2 — CV ANALYSIS
# ============================================================
elif page == "📄 CV Analysis":
    st.title("📄 CV Analysis")
    st.markdown("---")
    
    st.session_state.candidate_name = st.text_input(
        "Enter Your Name",
        placeholder="Mohamed Shibile"
    )
    
    uploaded_file = st.file_uploader(
        "Upload Your CV (PDF)",
        type=["pdf"]
    )
    
    if uploaded_file is not None:
        st.success("✅ CV Uploaded Successfully!")
        
        cv_text = extract_text_from_pdf(uploaded_file)
        st.session_state.cv_text = cv_text
        
        with st.expander("📄 View Extracted CV Text"):
            st.text_area("CV Content", cv_text, height=200)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧠 Analyze CV with AI"):
                with st.spinner("Gemini AI is analyzing your CV..."):
                    analysis = analyze_cv(cv_text)
                    st.session_state.cv_analysis = analysis
                st.success("✅ Analysis Complete!")
        
        with col2:
            if st.button("❓ Generate Interview Questions"):
                with st.spinner("Generating personalized questions..."):
                    questions = generate_interview_questions(cv_text)
                    st.session_state.questions = questions
                st.success("✅ Questions Generated!")
        
        if st.session_state.cv_analysis:
            st.markdown("### 🧠 AI CV Analysis")
            st.write(st.session_state.cv_analysis)
        
        if st.session_state.questions:
            st.markdown("### ❓ Your Interview Questions")
            st.write(st.session_state.questions)
            st.info("👈 Go to Interview page to answer these questions!")

# ============================================================
# PAGE 3 — INTERVIEW
# ============================================================
elif page == "🎤 Interview":
    st.title("🎤 AI Interview Session")
    st.markdown("---")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first in the CV Analysis page!")
    else:
        st.markdown("### 📝 Answer the Interview Question Below")
        
        question = st.text_area(
            "Interview Question",
            placeholder="Paste one of your generated questions here...",
            height=100
        )
        
        answer = st.text_area(
            "Your Answer",
            placeholder="Type your answer here...",
            height=200
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎭 Detect Emotion"):
                if answer:
                    with st.spinner("AI is analyzing your emotional state..."):
                        emotion, confidence_score, reason = detect_emotion(answer)
                        st.session_state.emotions.append(emotion)
                        st.markdown(f"""
                        <div class='score-card'>
                            <h2>🎭</h2>
                            <h3>Detected Emotion</h3>
                            <div class='big-score'>{emotion}</div>
                            <p>Confidence Level: {confidence_score}/10</p>
                            <p>{reason}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Please type your answer first!")
        
        with col2:
            if st.button("🚀 Evaluate My Answer"):
                if question and answer:
                    with st.spinner("AI is evaluating your answer..."):
                        evaluation = evaluate_answer(question, answer)
                        
                        # Parse scores
                        comm_match = re.search(r'COMMUNICATION:\s*(\d+(?:\.\d+)?)/10', evaluation)
                        tech_match = re.search(r'TECHNICAL:\s*(\d+(?:\.\d+)?)/10', evaluation)
                        conf_match = re.search(r'CONFIDENCE:\s*(\d+(?:\.\d+)?)/10', evaluation)
                        overall_match = re.search(r'OVERALL:\s*(\d+(?:\.\d+)?)/10', evaluation)
                        
                        comm = float(comm_match.group(1)) if comm_match else 7.0
                        tech = float(tech_match.group(1)) if tech_match else 7.0
                        conf = float(conf_match.group(1)) if conf_match else 7.0
                        overall = float(overall_match.group(1)) if overall_match else 7.0
                        
                        st.session_state.scores = {
                            'communication': comm,
                            'technical': tech,
                            'confidence': conf,
                            'overall': overall,
                            'evaluation': evaluation
                        }
                        
                        # Save to database
                        emotion = st.session_state.emotions[-1] if st.session_state.emotions else "Neutral"
                        save_interview(
                            st.session_state.candidate_name,
                            st.session_state.cv_analysis,
                            question, answer,
                            comm, tech, conf, overall, emotion
                        )
                    
                    st.success("✅ Evaluation Complete!")
                    
                    # Show scores
                    st.markdown("### 📊 Your Scores")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class='score-card'>
                            <p>Communication</p>
                            <div class='big-score'>{comm}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class='score-card'>
                            <p>Technical</p>
                            <div class='big-score'>{tech}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class='score-card'>
                            <p>Confidence</p>
                            <div class='big-score'>{conf}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class='score-card'>
                            <p>Overall</p>
                            <div class='big-score'>{overall}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("### 💡 AI Feedback")
                    st.write(evaluation)
                    
                    # PDF Report Download
                    st.markdown("### 📄 Download Your Report")
                    
                    pdf_buffer = generate_interview_report(
                        candidate_name=st.session_state.current_user['full_name'],
                        question=question,
                        answer=answer,
                        communication_score=comm,
                        technical_score=tech,
                        confidence_score=conf,
                        overall_score=overall,
                        emotion=st.session_state.emotions[-1] if st.session_state.emotions else "Neutral",
                        evaluation_text=evaluation
                    )
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"interview_report_{st.session_state.current_user['full_name'].replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                    
                    st.info("👈 Go to Dashboard to see your charts!")
                else:
                    st.error("Please enter both a question and your answer!")

# ============================================================
# PAGE 4 — DASHBOARD
# ============================================================
elif page == "📊 Dashboard":
    st.title("📊 Analytics Dashboard")
    st.markdown("---")
    
    if not st.session_state.scores:
        st.warning("⚠️ No interview data yet! Complete an interview first.")
    else:
        scores = st.session_state.scores
        comm = scores['communication']
        tech = scores['technical']
        conf = scores['confidence']
        overall = scores['overall']
        
        st.markdown("### 🎯 Performance Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            radar = create_score_radar_chart(comm, tech, conf, overall)
            st.plotly_chart(radar, use_container_width=True)
            radar_html = radar.to_html(full_html=False)
            st.download_button(
                label="📥 Download Radar Chart",
                data=radar_html,
                file_name="radar_chart.html",
                mime="text/html"
            )
        
        with col2:
            bar = create_score_bar_chart(comm, tech, conf, overall)
            st.plotly_chart(bar, use_container_width=True)
            bar_html = bar.to_html(full_html=False)
            st.download_button(
                label="📥 Download Bar Chart",
                data=bar_html,
                file_name="bar_chart.html",
                mime="text/html"
            )
        
        if st.session_state.emotions:
            st.markdown("### 🎭 Emotion Analysis")
            pie = create_emotion_pie_chart(st.session_state.emotions)
            st.plotly_chart(pie, use_container_width=True)
            pie_html = pie.to_html(full_html=False)
            st.download_button(
                label="📥 Download Emotion Chart",
                data=pie_html,
                file_name="emotion_chart.html",
                mime="text/html"
            )
        
        # Performance summary
        st.markdown("### 📋 Performance Summary")
        if overall >= 8:
            st.success(f"🌟 Excellent Performance! Overall Score: {overall}/10")
        elif overall >= 6:
            st.info(f"👍 Good Performance! Overall Score: {overall}/10")
        else:
            st.warning(f"📈 Keep Practicing! Overall Score: {overall}/10")
# ============================================================
# PAGE 5 — HISTORY
# ============================================================
elif page == "📋 History":
    st.title("📋 Interview History")
    st.markdown("---")
    
    interviews = get_all_interviews()
    
    if not interviews:
        st.warning("No interview history yet!")
    else:
        avg_scores = get_average_scores()
        
        if avg_scores and avg_scores[0]:
            st.markdown("### 📊 Overall Averages")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg Communication", f"{avg_scores[0]:.1f}/10")
            with col2:
                st.metric("Avg Technical", f"{avg_scores[1]:.1f}/10")
            with col3:
                st.metric("Avg Confidence", f"{avg_scores[2]:.1f}/10")
            with col4:
                st.metric("Avg Overall", f"{avg_scores[3]:.1f}/10")
        
        st.markdown("### 📋 All Interviews")
        
        for interview in interviews:
            with st.expander(f"📌 {interview[1]} — {interview[10]} — Score: {interview[8]}/10"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Question:** {interview[3]}")
                    st.write(f"**Answer:** {interview[4]}")
                with col2:
                    st.write(f"**Communication:** {interview[5]}/10")
                    st.write(f"**Technical:** {interview[6]}/10")
                    st.write(f"**Confidence:** {interview[7]}/10")
                    st.write(f"**Overall:** {interview[8]}/10")
                    st.write(f"**Emotion:** {interview[9]}")
                    # ============================================================
# PAGE 6 — COMPETITION
# ============================================================
elif page == "🏆 Competition":
    st.title("🏆 AI Interview Competition Mode")
    st.markdown("---")
    
    st.markdown("""
    <div class='header-banner'>
        <h1>⚔️ Head to Head Interview Battle</h1>
        <p>Two candidates. Same questions. One winner. Let AI decide!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Step 1 - Enter candidate names
    st.markdown("### 👥 Step 1 — Enter Candidates")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='score-card'>
            <h2>🔵</h2>
            <h3>Candidate 1</h3>
        </div>
        """, unsafe_allow_html=True)
        candidate1_name = st.text_input(
            "Candidate 1 Name",
            placeholder="Enter first candidate name..."
        )
    
    with col2:
        st.markdown("""
        <div class='score-card'>
            <h2>🔴</h2>
            <h3>Candidate 2</h3>
        </div>
        """, unsafe_allow_html=True)
        candidate2_name = st.text_input(
            "Candidate 2 Name",
            placeholder="Enter second candidate name..."
        )
    
    st.markdown("---")
    
    # Step 2 - Enter interview topic
    st.markdown("### 🎯 Step 2 — Enter Interview Topic")
    topic = st.text_input(
        "Interview Topic",
        placeholder="e.g. Python Programming, Cloud Security, Machine Learning..."
    )
    
    # Generate questions button
    if st.button("⚡ Generate Competition Questions"):
        if topic:
            with st.spinner("Generating competition questions..."):
                from google import genai
                from modules.config import GEMINI_API_KEY
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                prompt = f"""
                Generate 3 challenging interview questions about: {topic}
                
                Make them:
                - Technical and specific
                - Suitable for university level
                - Progressively harder
                
                Format EXACTLY like this:
                Q1: [question]
                Q2: [question]
                Q3: [question]
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                st.session_state.competition_questions = response.text
                st.success("✅ Questions Generated!")
        else:
            st.warning("⚠️ Please enter an interview topic first!")
    
    # Show questions if generated
    if 'competition_questions' in st.session_state and st.session_state.competition_questions:
        st.markdown("### ❓ Competition Questions")
        st.info(st.session_state.competition_questions)
        
        st.markdown("---")
        
        # Step 3 - Candidates answer
        st.markdown("### 🎤 Step 3 — Candidates Answer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### 🔵 {candidate1_name or 'Candidate 1'}")
            answer1 = st.text_area(
                "Answer (Candidate 1)",
                placeholder="Type answer here...",
                height=200,
                key="answer1"
            )
        
        with col2:
            st.markdown(f"#### 🔴 {candidate2_name or 'Candidate 2'}")
            answer2 = st.text_area(
                "Answer (Candidate 2)",
                placeholder="Type answer here...",
                height=200,
                key="answer2"
            )
        
        st.markdown("---")
        
        # Step 4 - Judge
        if st.button("⚖️ JUDGE THE COMPETITION!"):
            if answer1 and answer2:
                with st.spinner("AI is judging both candidates..."):
                    from google import genai
                    from modules.config import GEMINI_API_KEY
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    
                    prompt = f"""
                    You are an expert interview judge.
                    
                    Questions asked:
                    {st.session_state.competition_questions}
                    
                    Candidate 1 ({candidate1_name}) answered:
                    {answer1}
                    
                    Candidate 2 ({candidate2_name}) answered:
                    {answer2}
                    
                    Judge both candidates fairly.
                    
                    Respond EXACTLY in this format:
                    CANDIDATE1_SCORE: [number 1-100]
                    CANDIDATE2_SCORE: [number 1-100]
                    CANDIDATE1_STRENGTHS: [one sentence]
                    CANDIDATE2_STRENGTHS: [one sentence]
                    CANDIDATE1_WEAKNESSES: [one sentence]
                    CANDIDATE2_WEAKNESSES: [one sentence]
                    WINNER: [exactly "CANDIDATE1" or "CANDIDATE2" or "TIE"]
                    WINNER_REASON: [one sentence explaining why]
                    """
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    
                    result = response.text
                    
                    # Parse results
                    c1_score = 75
                    c2_score = 75
                    c1_strengths = ""
                    c2_strengths = ""
                    c1_weaknesses = ""
                    c2_weaknesses = ""
                    winner = "TIE"
                    winner_reason = ""
                    
                    for line in result.split('\n'):
                        if 'CANDIDATE1_SCORE:' in line:
                            try:
                                c1_score = float(line.replace('CANDIDATE1_SCORE:', '').strip())
                            except:
                                c1_score = 75
                        if 'CANDIDATE2_SCORE:' in line:
                            try:
                                c2_score = float(line.replace('CANDIDATE2_SCORE:', '').strip())
                            except:
                                c2_score = 75
                        if 'CANDIDATE1_STRENGTHS:' in line:
                            c1_strengths = line.replace('CANDIDATE1_STRENGTHS:', '').strip()
                        if 'CANDIDATE2_STRENGTHS:' in line:
                            c2_strengths = line.replace('CANDIDATE2_STRENGTHS:', '').strip()
                        if 'CANDIDATE1_WEAKNESSES:' in line:
                            c1_weaknesses = line.replace('CANDIDATE1_WEAKNESSES:', '').strip()
                        if 'CANDIDATE2_WEAKNESSES:' in line:
                            c2_weaknesses = line.replace('CANDIDATE2_WEAKNESSES:', '').strip()
                        if line.strip().startswith('WINNER:'):
                            winner = line.replace('WINNER:', '').strip()
                        if 'WINNER_REASON:' in line:
                            winner_reason = line.replace('WINNER_REASON:', '').strip()
                    
                    # Show results
                    st.markdown("---")
                    st.markdown("## 🏆 COMPETITION RESULTS")
                    
                    # Score cards
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        <div class='score-card'>
                            <h2>🔵</h2>
                            <h3>{candidate1_name or 'Candidate 1'}</h3>
                            <div class='big-score'>{c1_score}/100</div>
                            <p>✅ {c1_strengths}</p>
                            <p>⚠️ {c1_weaknesses}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class='score-card'>
                            <h2>🔴</h2>
                            <h3>{candidate2_name or 'Candidate 2'}</h3>
                            <div class='big-score'>{c2_score}/100</div>
                            <p>✅ {c2_strengths}</p>
                            <p>⚠️ {c2_weaknesses}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Winner announcement
                    if winner == "CANDIDATE1":
                        winner_name = candidate1_name or "Candidate 1"
                        winner_emoji = "🔵"
                    elif winner == "CANDIDATE2":
                        winner_name = candidate2_name or "Candidate 2"
                        winner_emoji = "🔴"
                    else:
                        winner_name = "TIE"
                        winner_emoji = "🤝"
                    
                    st.markdown(f"""
                    <div class='header-banner'>
                        <h1>{winner_emoji} WINNER: {winner_name}! 🏆</h1>
                        <p>{winner_reason}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Score comparison chart
                    import plotly.graph_objects as go
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            name=candidate1_name or 'Candidate 1',
                            x=['Score'],
                            y=[c1_score],
                            marker_color='#4444FF',
                            text=[f'{c1_score}/100'],
                            textposition='auto'
                        ),
                        go.Bar(
                            name=candidate2_name or 'Candidate 2',
                            x=['Score'],
                            y=[c2_score],
                            marker_color='#FF4444',
                            text=[f'{c2_score}/100'],
                            textposition='auto'
                        )
                    ])
                    
                    fig.update_layout(
                        title="Competition Score Comparison",
                        yaxis=dict(range=[0, 100]),
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        barmode='group'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
            else:
                st.error("⚠️ Both candidates must answer before judging!")
                # ============================================================
# PAGE 7 — JOB MATCHER
# ============================================================
elif page == "💼 Job Matcher":
    st.title("💼 AI Job Role Matcher")
    st.markdown("---")
    
    st.markdown("""
    <div class='header-banner'>
        <h1>💼 Find Your Perfect Career Match</h1>
        <p>Upload your CV and AI will tell you which jobs you're best suited for!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # CV Upload
    st.markdown("### 📄 Step 1 — Upload Your CV")
    uploaded_file = st.file_uploader(
        "Upload CV (PDF)",
        type=["pdf"],
        key="job_matcher_cv"
    )
    
    if uploaded_file is not None:
        st.success("✅ CV Uploaded Successfully!")
        
        cv_text = extract_text_from_pdf(uploaded_file)
        
        st.markdown("### 🎯 Step 2 — Choose Your Field")
        field = st.selectbox(
            "Select your field",
            [
                "Software Engineering",
                "Data Science & AI",
                "Cybersecurity",
                "Web Development",
                "Mobile Development",
                "Cloud Computing",
                "DevOps",
                "Network Engineering",
                "Database Administration",
                "UI/UX Design"
            ]
        )
        
        if st.button("🚀 Find My Job Matches!"):
            with st.spinner("AI is analyzing your CV and finding best matches..."):
                from google import genai
                from modules.config import GEMINI_API_KEY
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                prompt = f"""
                You are an expert career counselor and HR specialist.
                
                Analyze this CV and find the best job matches in the {field} field.
                
                CV:
                {cv_text}
                
                Respond EXACTLY in this format:
                
                JOB1_TITLE: [job title]
                JOB1_MATCH: [match percentage 0-100]
                JOB1_REASON: [one sentence why they match]
                JOB1_SKILLS_HAVE: [skills they already have for this job]
                JOB1_SKILLS_NEED: [skills they need to learn]
                
                JOB2_TITLE: [job title]
                JOB2_MATCH: [match percentage 0-100]
                JOB2_REASON: [one sentence why they match]
                JOB2_SKILLS_HAVE: [skills they already have for this job]
                JOB2_SKILLS_NEED: [skills they need to learn]
                
                JOB3_TITLE: [job title]
                JOB3_MATCH: [match percentage 0-100]
                JOB3_REASON: [one sentence why they match]
                JOB3_SKILLS_HAVE: [skills they already have for this job]
                JOB3_SKILLS_NEED: [skills they need to learn]
                
                JOB4_TITLE: [job title]
                JOB4_MATCH: [match percentage 0-100]
                JOB4_REASON: [one sentence why they match]
                JOB4_SKILLS_HAVE: [skills they already have for this job]
                JOB4_SKILLS_NEED: [skills they need to learn]
                
                JOB5_TITLE: [job title]
                JOB5_MATCH: [match percentage 0-100]
                JOB5_REASON: [one sentence why they match]
                JOB5_SKILLS_HAVE: [skills they already have for this job]
                JOB5_SKILLS_NEED: [skills they need to learn]
                
                OVERALL_RECOMMENDATION: [2 sentences overall career advice]
                STRONGEST_SKILLS: [list 3 strongest skills from CV]
                IMPROVEMENT_AREAS: [list 3 areas to improve]
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                result = response.text
                
                # Parse results
                jobs = []
                for i in range(1, 6):
                    job = {}
                    for line in result.split('\n'):
                        if f'JOB{i}_TITLE:' in line:
                            job['title'] = line.replace(f'JOB{i}_TITLE:', '').strip()
                        if f'JOB{i}_MATCH:' in line:
                            try:
                                job['match'] = float(line.replace(f'JOB{i}_MATCH:', '').strip().replace('%', ''))
                            except:
                                job['match'] = 70
                        if f'JOB{i}_REASON:' in line:
                            job['reason'] = line.replace(f'JOB{i}_REASON:', '').strip()
                        if f'JOB{i}_SKILLS_HAVE:' in line:
                            job['skills_have'] = line.replace(f'JOB{i}_SKILLS_HAVE:', '').strip()
                        if f'JOB{i}_SKILLS_NEED:' in line:
                            job['skills_need'] = line.replace(f'JOB{i}_SKILLS_NEED:', '').strip()
                    if job:
                        jobs.append(job)
                
                # Parse overall
                overall_rec = ""
                strongest = ""
                improvement = ""
                
                for line in result.split('\n'):
                    if 'OVERALL_RECOMMENDATION:' in line:
                        overall_rec = line.replace('OVERALL_RECOMMENDATION:', '').strip()
                    if 'STRONGEST_SKILLS:' in line:
                        strongest = line.replace('STRONGEST_SKILLS:', '').strip()
                    if 'IMPROVEMENT_AREAS:' in line:
                        improvement = line.replace('IMPROVEMENT_AREAS:', '').strip()
                
                # Show results
                st.markdown("---")
                st.markdown("## 🎯 Your Job Match Results")
                
                # Job cards
                for i, job in enumerate(jobs):
                    if 'title' in job and 'match' in job:
                        match = job['match']
                        
                        # Color based on match
                        if match >= 80:
                            color = "#FFB300"
                            emoji = "🔥"
                        elif match >= 60:
                            color = "#51CF66"
                            emoji = "✅"
                        else:
                            color = "#8B9DC3"
                            emoji = "📈"
                        
                        st.markdown(f"""
                        <div class='score-card'>
                            <h2>{emoji}</h2>
                            <h3>{job.get('title', 'Job Role')}</h3>
                            <div class='big-score' style='color: {color}'>{match}%</div>
                            <p>Match Score</p>
                            <p>💡 {job.get('reason', '')}</p>
                            <p>✅ <strong>Have:</strong> {job.get('skills_have', '')}</p>
                            <p>📚 <strong>Need:</strong> {job.get('skills_need', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("")
                
                # Chart
                if jobs:
                    import plotly.graph_objects as go
                    
                    titles = [j.get('title', f'Job {i+1}') for i, j in enumerate(jobs)]
                    matches = [j.get('match', 70) for j in jobs]
                    colors = ['#FFB300' if m >= 80 else '#51CF66' if m >= 60 else '#8B9DC3' for m in matches]
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=matches,
                            y=titles,
                            orientation='h',
                            marker_color=colors,
                            text=[f'{m}%' for m in matches],
                            textposition='auto'
                        )
                    ])
                    
                    fig.update_layout(
                        title="Job Match Comparison",
                        xaxis=dict(range=[0, 100]),
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Overall recommendation
                st.markdown("---")
                st.markdown("### 💡 AI Career Advice")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class='score-card'>
                        <h2>🎯</h2>
                        <h3>Recommendation</h3>
                        <p>{overall_rec}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class='score-card'>
                        <h2>💪</h2>
                        <h3>Strongest Skills</h3>
                        <p>{strongest}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class='score-card'>
                        <h2>📚</h2>
                        <h3>Improve These</h3>
                        <p>{improvement}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    # ============================================================
# PAGE 8 — LANGUAGES
# ============================================================
elif page == "🌍 Languages":
    st.title("🌍 Multi-Language Interview Practice")
    st.markdown("---")
    
    st.markdown("""
    <div class='header-banner'>
        <h1>🌍 Practice Interviews in Any Language</h1>
        <p>English, Arabic, Somali, Turkish — AI speaks your language!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Language selection
    st.markdown("### 🗣️ Step 1 — Choose Your Language")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='score-card'>
            <h2>🇬🇧</h2>
            <h3>English</h3>
            <p>International standard</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='score-card'>
            <h2>🇸🇦</h2>
            <h3>Arabic</h3>
            <p>العربية</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='score-card'>
            <h2>🇸🇴</h2>
            <h3>Somali</h3>
            <p>Af Soomaali</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='score-card'>
            <h2>🇹🇷</h2>
            <h3>Turkish</h3>
            <p>Türkçe</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Interview topic and language
    st.markdown("### 🎯 Step 2 — Setup Your Interview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_language = st.selectbox(
            "Interview Language",
            ["English", "Arabic", "Somali", "Turkish"]
        )
    
    with col2:
        topic = st.text_input(
            "Interview Topic",
            placeholder="e.g. Python, Cloud Computing, AI..."
        )
    
    if st.button("⚡ Generate Questions in Selected Language"):
        if topic:
            with st.spinner(f"Generating questions in {selected_language}..."):
                from google import genai
                from modules.config import GEMINI_API_KEY
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                prompt = f"""
                Generate 5 professional interview questions about: {topic}
                
                IMPORTANT: Write ALL questions in {selected_language} language.
                
                If language is Arabic, write in Arabic script.
                If language is Somali, write in Somali language.
                If language is Turkish, write in Turkish language.
                If language is English, write in English.
                
                Format:
                Q1: [question in {selected_language}]
                Q2: [question in {selected_language}]
                Q3: [question in {selected_language}]
                Q4: [question in {selected_language}]
                Q5: [question in {selected_language}]
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                st.session_state.lang_questions = response.text
                st.session_state.lang_selected = selected_language
                st.success(f"✅ Questions generated in {selected_language}!")
        else:
            st.warning("⚠️ Please enter an interview topic!")
    
    # Show questions and answer
    if 'lang_questions' in st.session_state and st.session_state.lang_questions:
        st.markdown(f"### ❓ Interview Questions in {st.session_state.get('lang_selected', 'English')}")
        st.info(st.session_state.lang_questions)
        
        st.markdown("---")
        st.markdown("### 🎤 Step 3 — Answer the Questions")
        
        answer = st.text_area(
            "Your Answer",
            placeholder="Type your answer here in any language...",
            height=200,
            key="lang_answer"
        )
        
        if st.button("🚀 Evaluate My Answer"):
            if answer:
                with st.spinner("AI is evaluating your answer..."):
                    from google import genai
                from modules.config import GEMINI_API_KEY
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                prompt = f"""
                    You are an expert multilingual interview evaluator.
                    
                    The interview was conducted in {st.session_state.get('lang_selected', 'English')}.
                    
                    Questions asked:
                    {st.session_state.lang_questions}
                    
                    Candidate answered:
                    {answer}
                    
                    Evaluate the answer. Write your evaluation in {st.session_state.get('lang_selected', 'English')} language.
                    
                    Respond EXACTLY in this format:
                    COMMUNICATION: [score 1-10]
                    TECHNICAL: [score 1-10]
                    CONFIDENCE: [score 1-10]
                    OVERALL: [score 1-10]
                    FEEDBACK: [2-3 sentences of feedback in {st.session_state.get('lang_selected', 'English')}]
                    SUGGESTIONS: [3 improvement suggestions in {st.session_state.get('lang_selected', 'English')}]
                    """
                    
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                result = response.text
                    
                    # Parse scores
                comm = 7
                tech = 7
                conf = 7
                overall = 7
                feedback = ""
                suggestions = ""
                    
                for line in result.split('\n'):
                        if 'COMMUNICATION:' in line:
                            try:
                                comm = float(line.replace('COMMUNICATION:', '').strip())
                            except:
                                comm = 7
                        if 'TECHNICAL:' in line:
                            try:
                                tech = float(line.replace('TECHNICAL:', '').strip())
                            except:
                                tech = 7
                        if 'CONFIDENCE:' in line:
                            try:
                                conf = float(line.replace('CONFIDENCE:', '').strip())
                            except:
                                conf = 7
                        if 'OVERALL:' in line:
                            try:
                                overall = float(line.replace('OVERALL:', '').strip())
                            except:
                                overall = 7
                        if 'FEEDBACK:' in line:
                            feedback = line.replace('FEEDBACK:', '').strip()
                        if 'SUGGESTIONS:' in line:
                            suggestions = line.replace('SUGGESTIONS:', '').strip()
                    
                    # Show results
                st.markdown("---")
                st.markdown("## 📊 Your Results")
                    
                col1, col2, col3, col4 = st.columns(4)
                    
                with col1:
                        st.markdown(f"""
                        <div class='score-card'>
                            <p>Communication</p>
                            <div class='big-score'>{comm}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                with col2:
                        st.markdown(f"""
                        <div class='score-card'>
                            <p>Technical</p>
                            <div class='big-score'>{tech}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                with col3:
                        st.markdown(f"""
                        <div class='score-card'>
                            <p>Confidence</p>
                            <div class='big-score'>{conf}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                with col4:
                        st.markdown(f"""
                        <div class='score-card'>
                            <p>Overall</p>
                            <div class='big-score'>{overall}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                st.markdown("### 💡 AI Feedback")
                st.markdown(f"""
                    <div class='score-card'>
                        <h3>📝 Feedback</h3>
                        <p>{feedback}</p>
                        <h3>📚 Suggestions</h3>
                        <p>{suggestions}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please type your answer first!")
                # ============================================================
# PAGE 9 — GITHUB ANALYSIS
# ============================================================
elif page == "🐙 GitHub Analysis":
    st.title("🐙 GitHub Repository Analysis")
    st.markdown("---")
    
    st.markdown("""
    <div class='header-banner'>
        <h1>🐙 AI Code Interview Generator</h1>
        <p>Enter your GitHub repo URL — AI analyzes your code and interviews you about it!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🔗 Step 1 — Enter Your GitHub Repository URL")
    
    github_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repository"
    )
    
    if st.button("🔍 Analyze Repository"):
        if github_url:
            with st.spinner("Fetching and analyzing your repository..."):
                try:
                    import requests
                    
                    # Parse GitHub URL
                    parts = github_url.replace("https://github.com/", "").strip("/").split("/")
                    
                    if len(parts) >= 2:
                        owner = parts[0]
                        repo = parts[1]
                        
                        # Fetch repo info
                        api_url = f"https://api.github.com/repos/{owner}/{repo}"
                        repo_response = requests.get(api_url)
                        repo_data = repo_response.json()
                        
                        # Fetch README
                        readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
                        readme_response = requests.get(readme_url)
                        
                        readme_content = ""
                        if readme_response.status_code == 200:
                            import base64
                            readme_data = readme_response.json()
                            readme_content = base64.b64decode(
                                readme_data['content']
                            ).decode('utf-8')[:3000]
                        
                        # Fetch file tree
                        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
                        tree_response = requests.get(tree_url)
                        
                        file_list = []
                        if tree_response.status_code == 200:
                            tree_data = tree_response.json()
                            if 'tree' in tree_data:
                                file_list = [
                                    f['path'] for f in tree_data['tree']
                                    if f['type'] == 'blob'
                                    and not f['path'].startswith('.')
                                ][:50]
                        
                        # Store repo info
                        st.session_state.github_repo = {
                            'name': repo_data.get('name', repo),
                            'description': repo_data.get('description', 'No description'),
                            'language': repo_data.get('language', 'Unknown'),
                            'stars': repo_data.get('stargazers_count', 0),
                            'forks': repo_data.get('forks_count', 0),
                            'owner': owner,
                            'readme': readme_content,
                            'files': file_list,
                            'url': github_url
                        }
                        
                        st.success("✅ Repository analyzed successfully!")
                    else:
                        st.error("❌ Invalid GitHub URL format!")
                        
                except Exception as e:
                    st.error(f"❌ Error fetching repository: {str(e)}")
        else:
            st.warning("⚠️ Please enter a GitHub URL!")
    
    # Show repo info and generate questions
    if 'github_repo' in st.session_state and st.session_state.github_repo:
        repo = st.session_state.github_repo
        
        st.markdown("---")
        st.markdown("### 📊 Repository Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='score-card'>
                <h2>📁</h2>
                <h3>{repo['name']}</h3>
                <p>Repository Name</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='score-card'>
                <h2>💻</h2>
                <h3>{repo['language']}</h3>
                <p>Main Language</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='score-card'>
                <h2>⭐</h2>
                <h3>{repo['stars']}</h3>
                <p>Stars</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='score-card'>
                <h2>🍴</h2>
                <h3>{repo['forks']}</h3>
                <p>Forks</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"**Description:** {repo['description']}")
        
        if repo['files']:
            with st.expander("📂 View Project Files"):
                for f in repo['files'][:30]:
                    st.markdown(f"📄 `{f}`")
        
        st.markdown("---")
        st.markdown("### 🤖 Step 2 — Generate Interview Questions")
        
        interview_type = st.selectbox(
            "Interview Type",
            [
                "General Code Review",
                "Architecture & Design",
                "Technical Deep Dive",
                "Problem Solving",
                "Best Practices & Security"
            ]
        )
        
        if st.button("⚡ Generate Questions From My Code!"):
            with st.spinner("AI is reading your code and generating questions..."):
                from google import genai
                from modules.config import GEMINI_API_KEY
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                files_str = "\n".join(repo['files'][:30])
                
                prompt = f"""
                You are an expert technical interviewer.
                
                Analyze this GitHub repository and generate interview questions.
                
                Repository: {repo['name']}
                Language: {repo['language']}
                Description: {repo['description']}
                
                Project Files:
                {files_str}
                
                README Content:
                {repo['readme'][:2000]}
                
                Interview Type: {interview_type}
                
                Generate 5 specific technical questions about THIS project.
                Make questions specific to the actual files and technology used.
                
                Format EXACTLY:
                Q1: [specific question about their code]
                Q2: [specific question about their architecture]
                Q3: [specific question about their technology choices]
                Q4: [specific question about challenges they faced]
                Q5: [specific question about improvements]
                
                SUMMARY: [2 sentences about what this project demonstrates]
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                st.session_state.github_questions = response.text
                st.success("✅ Questions generated from your code!")
        
        # Show questions and answer
        if 'github_questions' in st.session_state and st.session_state.github_questions:
            st.markdown("### ❓ Your Code Interview Questions")
            st.info(st.session_state.github_questions)
            
            st.markdown("---")
            st.markdown("### 🎤 Step 3 — Answer the Questions")
            
            github_answer = st.text_area(
                "Your Answer",
                placeholder="Explain your code, architecture decisions, challenges...",
                height=200,
                key="github_answer"
            )
            
            if st.button("🚀 Evaluate My Answer"):
                if github_answer:
                    with st.spinner("AI is evaluating your answer..."):
                        from google import genai
                        from modules.config import GEMINI_API_KEY
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        
                        prompt = f"""
                        You are an expert code reviewer and technical interviewer.
                        
                        The candidate is being interviewed about their GitHub project:
                        Repository: {repo['name']}
                        Language: {repo['language']}
                        
                        Questions asked:
                        {st.session_state.github_questions}
                        
                        Candidate answered:
                        {github_answer}
                        
                        Evaluate their answer professionally.
                        
                        Respond EXACTLY:
                        COMMUNICATION: [1-10]
                        TECHNICAL: [1-10]
                        CODE_KNOWLEDGE: [1-10]
                        OVERALL: [1-10]
                        STRENGTHS: [what they explained well]
                        IMPROVEMENTS: [what they should explain better]
                        VERDICT: [one sentence overall verdict]
                        """
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt
                        )
                        
                        result = response.text
                        
                        # Parse scores
                        comm = 7
                        tech = 7
                        code = 7
                        overall = 7
                        strengths = ""
                        improvements = ""
                        verdict = ""
                        
                        for line in result.split('\n'):
                            if 'COMMUNICATION:' in line:
                                try:
                                    comm = float(line.replace('COMMUNICATION:', '').strip())
                                except:
                                    comm = 7
                            if 'TECHNICAL:' in line:
                                try:
                                    tech = float(line.replace('TECHNICAL:', '').strip())
                                except:
                                    tech = 7
                            if 'CODE_KNOWLEDGE:' in line:
                                try:
                                    code = float(line.replace('CODE_KNOWLEDGE:', '').strip())
                                except:
                                    code = 7
                            if 'OVERALL:' in line:
                                try:
                                    overall = float(line.replace('OVERALL:', '').strip())
                                except:
                                    overall = 7
                            if 'STRENGTHS:' in line:
                                strengths = line.replace('STRENGTHS:', '').strip()
                            if 'IMPROVEMENTS:' in line:
                                improvements = line.replace('IMPROVEMENTS:', '').strip()
                            if 'VERDICT:' in line:
                                verdict = line.replace('VERDICT:', '').strip()
                        
                        # Show results
                        st.markdown("---")
                        st.markdown("## 📊 Your Results")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown(f"""
                            <div class='score-card'>
                                <p>Communication</p>
                                <div class='big-score'>{comm}/10</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class='score-card'>
                                <p>Technical</p>
                                <div class='big-score'>{tech}/10</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class='score-card'>
                                <p>Code Knowledge</p>
                                <div class='big-score'>{code}/10</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col4:
                            st.markdown(f"""
                            <div class='score-card'>
                                <p>Overall</p>
                                <div class='big-score'>{overall}/10</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            <div class='score-card'>
                                <h2>💪</h2>
                                <h3>Strengths</h3>
                                <p>{strengths}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class='score-card'>
                                <h2>📚</h2>
                                <h3>Improve</h3>
                                <p>{improvements}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class='header-banner'>
                            <h1>🎯 Verdict</h1>
                            <p>{verdict}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Please type your answer first!")