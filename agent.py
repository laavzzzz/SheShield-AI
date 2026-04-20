import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 🔑 Load environment variables
load_dotenv()

# ✅ Correct API key usage
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found. Check your .env file.")

# 🧠 Initialize model
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=api_key
)

# 🚦 Risk Detection
def detect_risk(user_input):
    prompt = f"""
Classify the risk level of this message into ONLY one word:
LOW, MEDIUM, or HIGH.

Message: {user_input}
"""

    try:
        response = llm.invoke(prompt)
        return response.content.strip().upper()
    except:
        return "LOW"


# 🧠 Main Response Function
def get_response(user_input, chat_history):

    risk = detect_risk(user_input)

    helpline = """
🚨 India Emergency Contacts:
112 - Emergency
100 - Police
1091 - Women Helpline
"""

    prompt = f"""
You are SheShield AI — a women safety and emotional support assistant.

Conversation:
{chat_history}

User: {user_input}

Risk Level: {risk}

Instructions:
- Be calm, supportive, and clear
- HIGH → urgent safety steps + helpline
- MEDIUM → caution + awareness
- LOW → reassurance + guidance
- Never blame or judge the user
- Keep answers practical and easy to follow

Include helpline if needed:
{helpline}
"""

    try:
        response = llm.invoke(prompt)
        answer = response.content
    except Exception as e:
        answer = "⚠️ I'm having trouble responding right now. Please try again."

    return {
        "answer": answer,
        "risk": risk
    }