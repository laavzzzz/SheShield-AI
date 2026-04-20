<div align="center">

# 🛡️ SheShield AI

### AI-Powered Women Safety Assistant

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=for-the-badge)](https://www.langchain.com)
[![Groq](https://img.shields.io/badge/Groq-Llama--3.1--8B-F55036?style=for-the-badge)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**A real-time AI-powered safety assistant designed to help women with risk detection, emotional support, emergency guidance, and location-aware responses.**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Demo](#-demo) • [Project Structure](#-project-structure) • [Roadmap](#-roadmap)

</div>

---

## 🎯 The Problem

Women often face unsafe situations where:
- Immediate guidance is unavailable  
- Panic leads to poor decisions  
- Awareness of legal rights is limited  
- Emotional distress reduces response clarity  

There is no **instant, intelligent assistant** that:
- Understands the situation  
- Assesses risk  
- Provides actionable guidance  

---

## 💡 The Solution

SheShield AI is a **real-time conversational safety assistant** that:

- 🚦 Detects **risk level (LOW / MEDIUM / HIGH)**  
- 💬 Provides **calm, supportive responses**  
- 📍 Uses **location awareness for contextual advice**  
- 🚨 Suggests **emergency actions instantly**  
- 💖 Offers **emotional support in distress situations**  

---

## ✨ Features

| Feature | Description |
|--------|------------|
| 🧠 AI Risk Detection | Classifies user situations into LOW / MEDIUM / HIGH |
| 💬 Conversational AI | Context-aware responses using chat history |
| 📍 Location Awareness | Detects user location via IP + manual input |
| 🚨 Emergency SOS | Instant access to emergency guidance |
| 💖 Emotional Support | Calming assistance during stress or panic |
| ⚖️ Legal Help | Provides awareness of women’s legal rights |
| 📊 Risk Meter | Visual safety indicator |
| 💬 Multi-Chat Memory | Separate chat sessions like ChatGPT |
| 🎨 Modern UI | Lovable-inspired clean interface |

## 🏗️ Architecture

The system follows a **lightweight agentic pipeline**:
```mermaid
flowchart TD
    A[User Input] --> B[Risk Detection]
    B --> C[Context Processing]
    C --> D[AI Response - Groq LLM]
    D --> E[UI + Risk Display]
---

## 🛠️ Technology Stack

| Layer | Technology |
|------|-----------|
| LLM | Groq API (Llama 3.1 8B Instant) |
| Framework | LangChain |
| UI | Streamlit |
| Backend | Python |
| Location | IP-based API (ipinfo.io) |
| Styling | Custom CSS |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Groq API Key

---

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/SheShield-AI.git
cd SheShield-AI

### **2. Setup Environment**
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

### **3. Install Dependencies**
pip install -r requirements.txt

### **4. Add API Key**
GROQ_API_KEY=your_api_key_here

📂 Project Structure
SheShield-AI/
├── app.py              # Streamlit UI
├── agent.py           # AI logic (risk + response)
├── requirements.txt
├── .env
├── .gitignore
└── README.md

🖥️ Demo

Example queries:

“Someone is following me at night”
“I feel unsafe in my hostel”
“What should I do in emergency?”
“I’m scared and need help”

🧰 Safety Tools Included
📍 Location Detection (Auto + Manual)
⚖️ Legal Rights Awareness
💖 Emotional Support System
🚨 Emergency SOS Guidance

🗺️ Roadmap
 Real-time GPS tracking
 Emergency contact alerts (SMS/WhatsApp)
 Voice input support
 Mobile app version
 AI-based threat prediction

⚠️ Disclaimer

This project is for educational and awareness purposes only.
It is not a replacement for emergency services or legal professionals.

**Author**

Laveeza Zafar
B.Tech CSE

<div align="center">

Made with 💖 for women safety

⭐ Star this repo if you found it useful!

</div> ```
