# 🤖 AI Interview & Communication Analysis Platform

> Powered by Google Gemini AI — Built for the future of recruitment

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)
![Gemini](https://img.shields.io/badge/Google-Gemini_AI-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Project Overview

An intelligent interview simulation platform that uses Google Gemini AI to:
- Analyze candidate CVs automatically
- Generate personalized interview questions
- Evaluate interview answers with scores
- Detect emotional state from answers
- Display performance analytics on a dashboard

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔐 Login/Signup | Secure authentication with hashed passwords |
| 📄 CV Analysis | Upload PDF CV and get instant AI analysis |
| ❓ Question Generation | AI generates personalized interview questions |
| 🎤 Answer Evaluation | Scored on communication, technical and confidence |
| 🎭 Emotion Detection | AI detects emotional state from your answers |
| 📊 Analytics Dashboard | Beautiful charts and performance visualization |
| 📋 Interview History | All sessions saved to database |
| 🏆 Competition Mode | Two candidates battle — AI picks the winner |
| 💼 Job Role Matcher | AI matches your CV to best job roles |
| 🌍 Multi-Language | Practice in English, Arabic, Somali, Turkish |
| 📄 PDF Report | Download full interview report as PDF |
| 🐙 GitHub Analysis | AI analyzes your code and interviews you about it |
---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Backend | Python 3.11 |
| AI Engine | Google Gemini API |
| PDF Processing | PyPDF2 |
| Charts | Plotly |
| Database | SQLite |

---

## 📁 Project Structure
ai_interview_system/
│
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── database.db           # SQLite database
│
└── modules/
├── cv_parser.py       # PDF text extraction
├── ai_questions.py    # CV analysis & question generation
├── emotion_detector.py # Emotion detection
├── evaluator.py       # Answer evaluation & scoring
├── database.py        # Database operations
└── charts.py          # Analytics charts
---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/shibile-dev/ai-interview-system.git

# Go to project folder
cd ai-interview-system

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

---

## 🔑 Configuration

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Add your API key in these files:
   - `modules/ai_questions.py`
   - `modules/evaluator.py`
   - `modules/emotion_detector.py`

---

## 📊 System Architecture
User
↓
Streamlit UI
↓
Python Backend
├── PyPDF2 (CV Parsing)
├── Gemini API (AI Analysis)
├── Plotly (Charts)
└── SQLite (Database)
↓
Dashboard + AI Report
---

## 👨‍💻 Developer

**Mohamud Yusud Said**
- GitHub: [@shibile-dev](https://github.com/shibile-dev)
- Department: Software Engineering
- University: OSTİM Technical University
- Year: 2026

---

## 📄 License

This project is licensed under the MIT License.
