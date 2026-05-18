import streamlit as st
import re
from modules.cv_parser import extract_text_from_pdf
from modules.ai_questions import analyze_cv, generate_interview_questions
from modules.emotion_detector import detect_emotion
from modules.evaluator import evaluate_answer
from modules.database import init_db, save_interview, get_all_interviews, get_average_scores
from modules.charts import create_score_radar_chart, create_emotion_pie_chart, create_score_bar_chart

# Initialize database
init_db()

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
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📄 CV Analysis", "🎤 Interview", "📊 Dashboard", "📋 History", "🏆 Competition"]
)

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
            <div class='big-score'>5</div>
            <p>Core Features</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='score-card'>
            <h2>📊</h2>
            <div class='big-score'>4</div>
            <p>Score Metrics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='score-card'>
            <h2>🎯</h2>
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
                client = genai.Client(api_key="AIzaSyDlMmHZCCuNls9WC71K6IJFsxixHBQ_jFg")
                
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
                    client = genai.Client(api_key="AIzaSyDlMmHZCCuNls9WC71K6IJFsxixHBQ_jFg")
                    
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