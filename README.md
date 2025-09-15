# LangGraph_Chatbot
Resume Screening chatbot 
# AI Interview Screening Agent

This project implements an **AI-powered interview screening agent** using **LangGraph** and **LangChain**.  
It simulates an automated first-round interview: asking dynamic questions, evaluating answers, and generating structured feedback and recommendations.

---

## 🚀 Features
- **Automated Question Generation**: Dynamically generates role-specific questions from a job description.
- **Answer Evaluation**: Scores candidate answers (0–5) with feedback for experience, technical, problem-solving, and cultural fit questions.
- **Conversation Flow with LangGraph**: Handles state, branching, and checkpointing via SQLite.
- **Session Tracking**: Saves messages, evaluations, and final summaries in a local database.
- **Final Report**: Provides an evaluation summary with average score and recommendation.

---

## 🛠️ Tech Stack
- **Python 3.10+**
- **LangChain + LangGraph**
- **SQLite (for checkpointing and session storage)**

---

## 📂 Project Structure
db.py              # Database utilities
graph_builder.py   # Builds the LangGraph state machine
nodes.py           # Defines question/answer nodes and evaluation logic
tools.py           # Tools for question generation and answer evaluation
