"""
VedDrishti - Streamlit Cloud Demo Version
Lightweight demo showing UI and capabilities
Note: Full AI analysis requires local deployment (see sidebar)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="VedDrishti - AI Course Survival Agent (Demo)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 1rem;
        font-size: 1rem;
    }
    
    .demo-badge {
        background: #f0f2f6;
        border-radius: 0.5rem;
        padding: 0.5rem;
        text-align: center;
        margin: 1rem 0;
        border-left: 4px solid #ff6b6b;
    }
    
    .high-prob {
        background: linear-gradient(90deg, #ff6b6b, #ee5a24);
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        color: white;
        font-weight: bold;
    }
    
    .medium-prob {
        background: linear-gradient(90deg, #ffd93d, #f39c12);
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        color: #333;
        font-weight: bold;
    }
    
    .low-prob {
        background: linear-gradient(90deg, #6bcb77, #2ecc71);
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        color: white;
        font-weight: bold;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 0.75rem;
        padding: 1rem;
        text-align: center;
        color: white;
    }
    
    .deadline-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 0.75rem;
        padding: 0.75rem;
        margin: 0.25rem;
        color: white;
        text-align: center;
    }
    
    .custom-divider {
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        margin: 1rem 0;
    }
    
    .info-box {
        background: #e8f4f8;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown('<div class="main-header">🎓 VedDrishti</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI Course Survival Agent | Demo Version</div>', unsafe_allow_html=True)

# ============================================
# SIDEBAR - Important Notice
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=80)
    st.markdown("### 🧠 VedDrishti")
    
    st.markdown("---")
    st.markdown("### ℹ️ About This Demo")
    
    st.info(
        "**This is a demonstration version** showing the UI and capabilities of VedDrishti.\n\n"
        "**Why no live AI analysis?**\n"
        "Streamlit Cloud cannot run local AI models (LLaMA 3.2 requires 4-6GB RAM).\n\n"
        "**Full version features:**\n"
        "- Analyzes YOUR past papers (PDF)\n"
        "- Processes YOUR lecture transcripts (TXT)\n"
        "- Runs LLaMA 3.2 locally on your machine\n"
        "- Complete privacy - no data leaves your computer\n\n"
        "**Run the full version:**\n"
        "```\n"
        "git clone https://github.com/yourusername/VedDrishti.git\n"
        "cd VedDrishti\n"
        "docker-compose up\n"
        "```\n"
        "Or see GitHub repo for manual setup instructions."
    )
    
    st.markdown("---")
    st.markdown("### 📊 Sample Data Stats")
    
    st.markdown("- **Past Papers:** 5 files")
    st.markdown("- **Transcripts:** 5 files")
    st.markdown("- **Deadlines:** 5 tasks")
    st.markdown("- **Final Weight:** 45%")
    
    st.markdown("---")
    st.caption("© 2026 VedDrishti | Demo Version")

# ============================================
# LOAD SAMPLE DATA (Pre-computed for demo)
# ============================================

# Sample predictions (from actual VedDrishti analysis on COMP2012)
sample_predictions = [
    {"topic": "Inheritance", "probability": 85, "priority": "🔴 HIGH", "paper_mentions": 4, "transcript_mentions": 7},
    {"topic": "Polymorphism", "probability": 82, "priority": "🔴 HIGH", "paper_mentions": 4, "transcript_mentions": 5},
    {"topic": "Virtual Functions", "probability": 78, "priority": "🔴 HIGH", "paper_mentions": 3, "transcript_mentions": 6},
    {"topic": "Dynamic Binding", "probability": 75, "priority": "🔴 HIGH", "paper_mentions": 3, "transcript_mentions": 4},
    {"topic": "Templates", "probability": 45, "priority": "🟡 MEDIUM", "paper_mentions": 2, "transcript_mentions": 2},
    {"topic": "Exception Handling", "probability": 42, "priority": "🟡 MEDIUM", "paper_mentions": 2, "transcript_mentions": 1},
    {"topic": "STL Containers", "probability": 38, "priority": "🟡 MEDIUM", "paper_mentions": 1, "transcript_mentions": 2},
    {"topic": "Operator Overloading", "probability": 25, "priority": "🟢 LOW", "paper_mentions": 1, "transcript_mentions": 0},
    {"topic": "Friend Functions", "probability": 20, "priority": "🟢 LOW", "paper_mentions": 0, "transcript_mentions": 1},
]

# Sample grading weights
grading_weights = {
    "Midterm": 25,
    "Final": 45,
    "Assignments": 20,
    "Labs": 10
}

# Sample deadlines
sample_deadlines = [
    {"task": "Assignment 1", "due_date": "2026-04-20", "weight": 15},
    {"task": "Midterm Exam", "due_date": "2026-04-28", "weight": 25},
    {"task": "Assignment 2", "due_date": "2026-05-05", "weight": 20},
    {"task": "Final Project", "due_date": "2026-05-22", "weight": 30},
    {"task": "Final Exam", "due_date": "2026-05-26", "weight": 45},
]

# Course insights
course_insights = [
    "Final exam heavily focuses on Inheritance and Polymorphism",
    "Past papers are essential for preparation",
    "Labs are time-consuming but only 10% of grade",
    "Assignment 2 is the most challenging - start early",
]

# ============================================
# DEMO NOTICE
# ============================================
st.markdown(
    '<div class="demo-badge">ℹ️ <strong>Demo Mode</strong> - Showing sample predictions from actual VedDrishti analysis.<br>For full AI analysis on YOUR course materials, run locally with Docker.</div>',
    unsafe_allow_html=True
)

# ============================================
# METRICS ROW
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="metric-card">
            <div style="font-size: 2rem;">📚</div>
            <div style="font-size: 1.5rem; font-weight: bold;">5</div>
            <div>Past Papers</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="metric-card">
            <div style="font-size: 2rem;">📝</div>
            <div style="font-size: 1.5rem; font-weight: bold;">5</div>
            <div>Transcripts</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="metric-card">
            <div style="font-size: 2rem;">📅</div>
            <div style="font-size: 1.5rem; font-weight: bold;">5</div>
            <div>Deadlines</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <div class="metric-card">
            <div style="font-size: 2rem;">🎯</div>
            <div style="font-size: 1.5rem; font-weight: bold;">45%</div>
            <div>Final Weight</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# GRADING SCHEME
# ============================================
st.markdown("### 📊 Grading Scheme")

col_grad1, col_grad2 = st.columns(2)

with col_grad1:
    grad_df = pd.DataFrame(list(grading_weights.items()), columns=["Component", "Weight (%)"])
    fig_bar = px.bar(
        grad_df,
        x="Component",
        y="Weight (%)",
        color="Component",
        color_discrete_sequence=['#667eea', '#764ba2', '#ff6b6b', '#ffd93d'],
        title="Grading Distribution (Bar Chart)"
    )
    fig_bar.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_grad2:
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(grading_weights.keys()),
        values=list(grading_weights.values()),
        hole=0.3,
        marker=dict(colors=['#ff6b6b', '#ffd93d', '#6bcb77', '#4ecdc4'])
    )])
    fig_pie.update_layout(height=350, title="Grading Distribution (Pie Chart)")
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# WORD CLOUD & TOPIC DISTRIBUTION
# ============================================
col_wc, col_pie = st.columns([2, 1])

with col_wc:
    st.markdown("### ☁️ Topic Word Cloud")
    topic_text = " ".join([p["topic"] * int(p["probability"] / 10) for p in sample_predictions])
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(topic_text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

with col_pie:
    st.markdown("### 🥧 Topic Distribution")
    fig = go.Figure(data=[go.Pie(
        labels=[p["topic"] for p in sample_predictions[:8]],
        values=[p["probability"] for p in sample_predictions[:8]],
        hole=0.4,
        marker=dict(colors=['#ff6b6b', '#ffd93d', '#6bcb77', '#4ecdc4', '#45b7d1'])
    )])
    fig.update_layout(height=400, margin=dict(t=0, l=0, r=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# EXAM PREDICTIONS
# ============================================
st.markdown("## 🔮 Exam Predictions")

min_prob = st.slider("Minimum probability filter", 0, 100, 50, 10)
filtered = [p for p in sample_predictions if p["probability"] >= min_prob]

for p in filtered:
    if p["priority"] == "🔴 HIGH":
        priority_class = "high-prob"
    elif p["priority"] == "🟡 MEDIUM":
        priority_class = "medium-prob"
    else:
        priority_class = "low-prob"
    
    st.markdown(
        f"""
        <div class="{priority_class}">
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 1.1rem;">{p['topic']}</span>
                <span style="font-size: 1.1rem;">{p['probability']}%</span>
            </div>
            <div style="background: rgba(255,255,255,0.3); border-radius: 0.3rem; margin-top: 0.3rem;">
                <div style="width: {p['probability']}%; background: rgba(255,255,255,0.5); height: 6px; border-radius: 0.3rem;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.3rem;">
                <small>📄 Appears in {p['paper_mentions']} papers</small>
                <small>📝 Mentioned in {p['transcript_mentions']} transcripts</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with st.expander("🔍 How These Predictions Are Generated (Full Version)"):
    st.markdown("""
    In the full local version, VedDrishti's Prediction Engine:
    
    1. **Extracts text** from your PDF past papers
    2. **Analyzes content** using LLaMA 3.2 (local AI)
    3. **Detects emphasis** from lecture transcripts (repetition, verbal cues)
    4. **Calculates probability** = 60% paper frequency + 40% transcript emphasis
    5. **Generates color-coded predictions** (🔴 HIGH: >70%, 🟡 MEDIUM: 40-69%, 🟢 LOW: <40%)
    
    **These sample predictions are from actual VedDrishti analysis on COMP2012 course materials.**
    """)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# GRADE MAXIMIZER
# ============================================
st.markdown("## 📊 Grade Maximizer Agent")

fig_pie2 = go.Figure(data=[go.Pie(
    labels=list(grading_weights.keys()),
    values=list(grading_weights.values()),
    hole=0.3,
    marker=dict(colors=['#ff6b6b', '#ffd93d', '#6bcb77', '#4ecdc4'])
)])
fig_pie2.update_layout(height=350, title="Your Grading Distribution")
st.plotly_chart(fig_pie2, use_container_width=True)

st.markdown("### 🎯 Recommended Effort Allocation")

for component, weight in sorted(grading_weights.items(), key=lambda x: x[1], reverse=True):
    if weight >= 40:
        st.success(f"🎯 **{component}** ({weight}%): Spend **50%** of your study time here")
        st.progress(50)
    elif weight >= 20:
        st.info(f"📘 **{component}** ({weight}%): Spend **25%** of your study time here")
        st.progress(25)
    else:
        st.caption(f"⚡ **{component}** ({weight}%): Minimum effort required")
        st.progress(10)

with st.expander("💡 How Grade Maximizer Works (Full Version)"):
    st.markdown("""
    The Grade Maximizer Agent:
    
    1. **Parses your course_info.txt** file for grading breakdown
    2. **Calculates ROI** (Return on Investment) for each component
    3. **Allocates study time** proportionally to grade weight
    4. **Recommends focus areas** based on highest return
    
    **Why this matters:** Spending 50% of time on a 45% weighted final is smarter than spending equal time on labs worth only 10%.
    """)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# DEADLINE SURVIVAL
# ============================================
st.markdown("## 📅 Deadline Survival Agent")

st.markdown("### 📋 Upcoming Deadlines")

# Display deadlines in rows of 3
for i in range(0, len(sample_deadlines), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j < len(sample_deadlines):
            d = sample_deadlines[i + j]
            due_date = datetime.strptime(d["due_date"], "%Y-%m-%d")
            days_left = (due_date - datetime.now()).days
            if days_left < 7:
                urgency = "🔴 URGENT"
            elif days_left < 14:
                urgency = "🟡 SOON"
            else:
                urgency = "🟢 LATER"
            
            col.markdown(
                f"""
                <div class="deadline-card">
                    <div style="font-weight: bold;">📌 {d['task']}</div>
                    <div>📅 {d['due_date']}</div>
                    <div>⏰ {days_left} days left</div>
                    <div>📊 {d['weight']}%</div>
                    <div style="font-size: 0.7rem; margin-top: 0.3rem;">{urgency}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("### 🎯 Personalized Study Plan")

# Sample study plan based on predictions
sample_study_plan = [
    {"date": "2026-04-20", "topic": "Inheritance", "priority": "HIGH", "hours": 3, "reason": "85% exam probability - Study BEFORE midterm"},
    {"date": "2026-04-21", "topic": "Polymorphism", "priority": "HIGH", "hours": 3, "reason": "82% exam probability"},
    {"date": "2026-04-22", "topic": "Virtual Functions", "priority": "HIGH", "hours": 2, "reason": "78% exam probability"},
    {"date": "2026-04-23", "topic": "Dynamic Binding", "priority": "HIGH", "hours": 2, "reason": "75% exam probability"},
    {"date": "2026-04-29", "topic": "Templates", "priority": "MEDIUM", "hours": 2, "reason": "45% exam probability - Study AFTER midterm"},
]

for plan in sample_study_plan:
    if plan["priority"] == "HIGH":
        priority_icon = "🔴"
    else:
        priority_icon = "🟡"
    
    st.markdown(
        f"""
        <div style="background: #f0f2f6; border-radius: 0.5rem; padding: 0.75rem; margin: 0.5rem 0;">
            <div style="display: flex; justify-content: space-between;">
                <span style="font-weight: bold;">📅 {plan['date']}</span>
                <span>{priority_icon} {plan['priority']} Priority</span>
            </div>
            <div style="margin: 0.5rem 0;">📖 <b>{plan['topic']}</b></div>
            <div style="display: flex; justify-content: space-between;">
                <small>⏰ {plan['hours']} hours</small>
                <small>{plan['reason']}</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with st.expander("📅 How Deadline Survival Works (Full Version)"):
    st.markdown("""
    The Deadline Survival Agent:
    
    1. **Reads deadlines** from your course_info.txt file
    2. **Detects workload spikes** (2+ deadlines within 7 days)
    3. **Prioritizes study** based on exam probabilities from Prediction Engine
    4. **Schedules high-priority topics BEFORE busy periods**
    5. **Schedules low-priority topics AFTER deadlines**
    
    **The result:** You study what matters most when you have time, not during exam week panic.
    """)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# COURSE INSIGHTS
# ============================================
st.markdown("## 💡 Course Insights")

for insight in course_insights:
    st.markdown(f'<div class="info-box">📌 {insight}</div>', unsafe_allow_html=True)

# ============================================
# FOOTER WITH LOCAL RUN INSTRUCTIONS
# ============================================
st.markdown("---")
st.markdown(
    """
### 🚀 Run the Full Version on Your Machine

# Clone the repository
git clone https://github.com/yourusername/VedDrishti.git
cd VedDrishti

# Add your course files to sample_data/
# - Past papers (PDF) -> sample_data/past_papers/
# - Transcripts (TXT) -> sample_data/transcripts/
# - course_info.txt -> sample_data/reviews/

# Run with Docker (easiest)
docker-compose up

# Or manual setup
pip install -r requirements.txt
ollama pull llama3.2
streamlit run app/streamlit_app.py
"""
)
