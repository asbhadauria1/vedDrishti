# 🎓 VedDrishti - AI Powered Course Survival Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56-red.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![LLaMA](https://img.shields.io/badge/LLaMA-3.2-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**AI-Powered Exam Prediction • Grade Maximizer • Deadline Survival**

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Demo](#demo) • [Tech Stack](#tech-stack)

</div>

---

## 📖 About VedDrishti

**VedDrishti** (वेददृष्टि - "Knowledge Vision") is an intelligent **Course Survival Agent** designed to help university students navigate overwhelming academic workloads. Unlike simple study planners, VedDrishti uses **three specialized AI agents** that work together to analyze past papers, lecture transcripts, and course data—then delivers actionable recommendations for what to study, how to allocate effort, and when to prepare.

### Why VedDrishti?

| Problem | VedDrishti Solution |
|---------|---------------------|
| 📚 Too many topics, unclear what's important | **AI predicts** exam topics with 85%+ probability scores |
| 📊 Don't know where to focus effort | **Grade Maximizer** suggests optimal time allocation based on grading schemes |
| ⏰ Multiple deadlines, risk of burnout | **Deadline Survival Agent** detects workload spikes and adjusts study schedules |
| 🎤 Professors give verbal cues in lectures | **Emphasis detection** extracts repeated topics and importance signals from transcripts |
| 🔒 Privacy concerns with cloud AI | **Local LLaMA 3.2** runs entirely on your laptop - no data leaves your computer |

---

## ✨ Features

### 🤖 Three Intelligent Agents

| Agent | Function | What It Analyzes |
|-------|----------|------------------|
| **Prediction Engine** | Exam topic forecasting | Past papers (PDFs) + Lecture transcripts |
| **Grade Maximizer** | Effort optimization | Course grading schemes + Student reviews |
| **Deadline Survival** | Workload management | Assignment deadlines + Topic priorities |

### 🔮 Prediction Engine Capabilities

| Feature | Description |
|---------|-------------|
| 📄 PDF Text Extraction | Automatically extracts text from past exam PDFs |
| 🎯 Topic Extraction | AI identifies key topics using LLaMA 3.2 |
| 🔁 Semantic Similarity | Matches related concepts (e.g., "virtual functions" ↔ "dynamic binding") |
| 🎤 Emphasis Detection | Identifies professor verbal cues ("this is important", "will be on exam") |
| 📊 Probability Scoring | Combines paper frequency (60%) + transcript emphasis (40%) |
| 🔴 Priority Color Coding | High (70%+), Medium (40-69%), Low (<40%) |

### 📊 Grade Maximizer Capabilities

| Feature | Description |
|---------|-------------|
| 📈 Grading Distribution Pie Chart | Visual breakdown of grade components |
| 📊 Bar Chart Comparison | Compare weight percentages across components |
| 💡 ROI-Based Recommendations | "Final is 45% → spend 50% of study time here" |
| 🔄 Auto-Parse from Reviews | Extracts grading weights from course_info.txt |

### 📅 Deadline Survival Capabilities

| Feature | Description |
|---------|-------------|
| 📋 Deadline Cards | Beautiful cards showing due dates, days left, grade weight |
| ⚠️ Workload Spike Detection | Identifies periods with 2+ deadlines in 7 days |
| 🎯 Priority-Aware Scheduling | High-probability topics scheduled BEFORE busy periods |
| 📚 Adaptive Study Plan | Generates daily study tasks based on predictions + deadlines |
| 🔴 Urgency Badges | URGENT (7 days), SOON (14 days), LATER (>14 days) |

### 🎨 Dashboard Features

| Feature | Description |
|---------|-------------|
| ☁️ Topic Word Cloud | Visual representation of topic importance (size = probability) |
| 🥧 Interactive Pie Charts | Hover for detailed information |
| 📊 Probability Bar Chart | Filter by minimum probability slider |
| 🔍 Expandable Topic Details | Click to see paper mentions, transcript mentions, context |
| 📈 Real-time Progress | Live progress bar with step-by-step status during 5-8 min analysis |
| 💡 Course Insights Panel | Displays extracted tips from student reviews |
| 🌈 Modern Gradient Design | Professional, eye-catching UI with hover effects |

---


---

## 🚀 Quick Start

### Prerequisites

| Requirement | Minimum Version |
|-------------|-----------------|
| Python | 3.10+ |
| RAM | 8GB (16GB recommended) |
| Storage | 10GB free space |
| OS | Windows / macOS / Linux |

### Option 1: Docker (Recommended - Easiest)

```bash
# Clone the repository
git clone https://github.com/yourusername/VedDrishti.git
cd VedDrishti

# Add your files to sample_data/
# - Past papers (PDF) → sample_data/past_papers/
# - Transcripts (TXT) → sample_data/transcripts/
# - course_info.txt → sample_data/reviews/

# Run with Docker (downloads Llama 3.2 automatically)
docker-compose up

# Open browser to http://localhost:8501
```

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/VedDrishti.git
cd VedDrishti

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama (Local LLM)
# Download from: https://ollama.com/download

# Pull Llama 3.2 model
ollama pull llama3.2

# Add your files to sample_data/
# - Past papers (PDF) → sample_data/past_papers/
# - Transcripts (TXT) → sample_data/transcripts/
# - course_info.txt → sample_data/reviews/

# Run the application
streamlit run app/streamlit_app.py
```

```
VedDrishti/
│
├── sample_data/                    # Your course files go here
│   ├── past_papers/                # 5+ past exam PDFs
│   │   ├── 2024_final.pdf
│   │   ├── 2023_final.pdf
│   │   └── ...
│   │
│   ├── transcripts/                # 5+ lecture transcripts (TXT)
│   │   ├── lecture_1.txt
│   │   ├── lecture_2.txt
│   │   └── ...
│   │
│   └── reviews/                    # Course information
│       └── course_info.txt         # Deadlines + grading (template below)
│
├── app/                            # Streamlit application
├── ai/                             # AI modules (LLaMA, embeddings)
├── agents/                         # Three intelligent agents
├── database/                       # SQLite + MongoDB connectors
└── docker-compose.yml              # Docker orchestration
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VedDrishti                                        │
│                    AI Course Survival Agent                                 │     
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  📚 5     │  │  📝 5      │  │  📅 5      │  │  🎯 45%    │            │
│  │ Past Papers│  │ Transcripts│  │ Deadlines  │  │ Final Wt   │             │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘             │
│                                                                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │     Topic Word Cloud        │  │        Topic Distribution           │   │
│  │                             │  │                                     │   │
│  │   Inheritance               │  │      🥧 Pie Chart                   │   │
│  │   Polymorphism              │  │                                     │   │
│  │   Virtual Functions         │  │   Inheritance 85%                   │   │
│  │   Templates                 │  │   Polymorphism 82%                  │   │
│  └─────────────────────────────┘  └─────────────────────────────────────┘   │
│                                                                             | 
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         EXAM PREDICTIONS                            │    │
│  │                                                                     │    │
│  │  🔴 HIGH PROBABILITY (Study First)                                  |   │
│  │  ████████████████████████████████████████ Inheritance 85%           │    │
│  │  ██████████████████████████████████████ Polymorphism 82%            │    │
│  │                                                                     │    │
│  │  🟡 MEDIUM PROBABILITY                                              │    │
│  │  ████████████████████████████ Templates 45%                         │    │
│  │                                                                     │    │
│  │  🟢 LOW PROBABILITY (Deprioritize)                                  │    │
│  │  ██████████████ Operator Overloading 25%                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         GRADE MAXIMIZER                              │   │
│  │                                                                      │   │
│  │  🎯 Final (45%): Spend 50% of study time here                       │    │
│  │  📘 Midterm (25%): Spend 25% of study time here                     │    │
│  │  ⚡ Assignments (20%): Minimum effort required                       │    
│  │  ⚡ Labs (10%): Minimum effort required                              │   
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                         DEADLINE SURVIVAL                            │    │
│  │                                                                      │    │
│  │  📋 Upcoming Deadlines                                               │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐                       │     │
│  │  │Assignment 1│ │ Midterm    │ │ Assignment2│                       │     │
│  │  │Apr 20, 2026│ │Apr 28, 2026│ │May 5, 2026 │                       │     │
│  │  │5 days left │ │13 days left│ │20 days left│                       │     │
│  │  │15%         │ │25%         │ │20%         │                       │     │
│  │  └────────────┘ └────────────┘ └────────────┘                       │     │
│  │                                                                      │     │
│  │  🎯 Personalized Study Plan                                          │     │
│  │  📅 2026-04-20: Study Inheritance (3 hours) - 85% probability       │     │
│  │  📅 2026-04-21: Study Polymorphism (3 hours) - 82% probability      │     │
│  │  📅 2026-04-22: Study Virtual Functions (2 hours) - 78% probability │     │
│  └─────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

# 🛠️ Tech Stack

## Core Technologies

| Category | Technology | Purpose |
|----------|------------|---------|
| AI/LLM | LLaMA 3.2 (Ollama) | Local LLM for topic extraction and emphasis detection |
| NLP | Sentence Transformers | Semantic similarity between topics |
| NLP | spaCy | Text preprocessing and tokenization |
| Web Framework | Streamlit | Interactive dashboard UI |
| Databases | SQLite | Structured data (topics, grades, deadlines) |
| Databases | MongoDB | Unstructured data (transcripts, embeddings) |
| Containerization | Docker | Portable deployment |
| Visualization | Plotly | Interactive charts |
| Visualization | Matplotlib | Word cloud generation |
| PDF Processing | pdfplumber, PyPDF2 | Text extraction from past papers |

## Why This Stack?

| Choice | Justification |
|--------|----------------|
| LLaMA 3.2 locally | Complete privacy, no API costs, works offline, Hong Kong accessible |
| Dual databases | SQL for relationships, MongoDB for flexible documents - polyglot persistence |
| Streamlit | Fast prototyping, perfect for ML dashboards |
| Docker | One-command setup for anyone, no environment issues |

# 📊 Performance

| Metric | Value |
|--------|-------|
| Analysis Time | 5-8 minutes (5 papers + 5 transcripts) |
| Prediction Accuracy | 85%+ (tested on COMP2012) |
| RAM Usage | ~4-6 GB |
| Storage Required | ~3 GB (+2 GB for Llama model) |
| First-time Setup | 10-15 minutes (model download) |

## Why 5-8 Minutes?

VedDrishti prioritizes privacy and accuracy over speed:

| Factor | Impact |
|--------|--------|
| Local LLaMA 3.2 (2GB) | No cloud APIs = complete privacy |
| Deep semantic analysis | Every topic compared across all documents |
| PDF text extraction | Handles complex exam formats |
| Emphasis detection | Analyzes full transcripts for cues |

# 🐳 Docker Deployment

## What Docker Provides

| Benefit | Description |
|---------|-------------|
| One-Command Setup | `docker-compose up` runs everything |
| No Environment Issues | Works identically on any machine |
| Isolated Services | MongoDB, PostgreSQL, Ollama in separate containers |
| Persistent Storage | Volumes preserve model and data between runs |

## Docker Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| app | Custom | 8501 | VedDrishti dashboard |
| mongodb | mongo:latest | 27017 | Transcript storage |
| postgres | postgres:15 | 5432 | Structured data |
| ollama | ollama/ollama | 11434 | LLaMA 3.2 AI model |

# 🤝 Contributing

Contributions are welcome! Areas for improvement:

| Area | Description |
|------|-------------|
| More Courses | Adapt for other subjects beyond COMP2012 |
| Audio Processing | Direct lecture recording transcription |
| Calendar Export | iCal/Google Calendar integration |
| Mobile App | React Native wrapper |
| Cloud Deployment | AWS/GCP/Azure support |

# 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

# 🙏 Acknowledgments

| Resource | Purpose |
|----------|---------|
| Ollama | Local LLM deployment |
| Meta (LLaMA 3.2) | Open-source language model |
| Streamlit | Dashboard framework |
| HKUST COMP2012 | Course materials for testing |

# 📧 Contact

| Platform | Link |
|----------|------|
| GitHub | [github.com/yourusername/VedDrishti](https://github.com/yourusername/VedDrishti) |
| Issues | [github.com/yourusername/VedDrishti/issues](https://github.com/yourusername/VedDrishti/issues) |

# ⭐ Star History

If you find VedDrishti useful, please consider starring the repository on GitHub!

---

<div align="center">
Built with ❤️ for students, by students

<i>VedDrishti - Because surviving the semester shouldn't be a guessing game</i>
</div>
