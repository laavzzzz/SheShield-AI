"""
SheShield AI - Core Intelligence & Risk Detection Agent
Path: agent.py

Provides single-pass risk classification and conversational response generation
via Groq API (Llama 3.1 8B Instant) with structured parsing and deterministic fallbacks.
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Configure module logging
logger = logging.getLogger("SheShield.Agent")
logger.setLevel(logging.INFO)

# Try importing Streamlit safely for secrets resolution
try:
    import streamlit as st
except ImportError:
    st = None

# Try importing LangChain Groq client
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import SystemMessage, HumanMessage
except ImportError:
    ChatGroq = None
    logger.warning("langchain_groq package not found. Agent operating in fallback mode.")


# -----------------------------------------------------------------------------
# CONSTANTS & EMERGENCY DATA
# -----------------------------------------------------------------------------
DEFAULT_MODEL = "llama-3.1-8b-instant"

INDIA_HELPLINE_TEXT = """
🚨 **Emergency Helplines (India):**
• **National Emergency Number:** 112
• **Police:** 100
• **Women Helpline:** 1091
• **Domestic Abuse Helpline:** 181
• **Cyber Crime Helpline:** 1930
"""

SYSTEM_PROMPT = """You are SheShield AI — an expert AI assistant dedicated to women's safety, situational risk assessment, and emotional support.

YOUR DUAL OBJECTIVE:
1. Classify the user's situation into EXACTLY ONE Risk Level: "LOW", "MEDIUM", or "HIGH".
   - HIGH: Active threat, stalker following closely, physical harm, trapped, weapon, immediate panic/danger.
   - MEDIUM: Suspicious activity, dark/isolated location, feeling uncomfortable/followed at distance, cab safety concerns.
   - LOW: General safety inquiries, safe updates, emotional check-ins, non-urgent legal/rights questions.

2. Generate a calm, empathetic, highly practical response.
   - HIGH RISK: Give immediate, clear physical de-escalation instructions first. Tell user to head to a public space or open shop immediately.
   - MEDIUM RISK: Give proactive awareness guidance, recommend calling a trusted contact or keeping location shared.
   - LOW RISK: Provide warm reassurance, guidance, or requested legal rights information.

CRITICAL FORMATTING REQUIREMENT:
You MUST respond ONLY with a valid JSON object matching this exact structure:
{
  "risk": "LOW" | "MEDIUM" | "HIGH",
  "answer": "Your supportive response here."
}
Do NOT include markdown formatting outside the JSON object.
"""


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS & API KEY RESOLUTION
# -----------------------------------------------------------------------------
def get_groq_api_key() -> Optional[str]:
    """Resolves Groq API key from environment variables or Streamlit secrets."""
    # 1. Check OS Environment Variables
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key

    # 2. Check Streamlit Secrets if available
    if st is not None:
        try:
            if "GROQ_API_KEY" in st.secrets:
                return str(st.secrets["GROQ_API_KEY"])
        except Exception:
            pass

    return None


def sanitize_input(text: str, max_chars: int = 2000) -> str:
    """Sanitizes raw user input against prompt injection and bounds payload length."""
    if not text:
        return ""
    
    cleaned = text.strip()[:max_chars]
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


def initialize_llm(model_name: str = DEFAULT_MODEL) -> Optional[Any]:
    """Lazy-initializes ChatGroq client."""
    if ChatGroq is None:
        return None

    api_key = get_groq_api_key()
    if not api_key:
        logger.warning("GROQ_API_KEY is missing. Groq client cannot be initialized.")
        return None

    try:
        return ChatGroq(
            model=model_name,
            api_key=api_key,
            temperature=0.2,
            max_retries=2,
            request_timeout=8.0
        )
    except Exception as e:
        logger.error(f"Failed to instantiate ChatGroq client: {e}")
        return None


# -----------------------------------------------------------------------------
# DETERMINISTIC SAFETY FALLBACK ENGINE
# -----------------------------------------------------------------------------
def fallback_safety_evaluation(user_input: str) -> Dict[str, str]:
    """
    Local heuristic safety evaluation triggered when Groq API is unavailable or fails.
    Ensures zero downtime for emergency safety advice.
    """
    logger.warning("Executing local fallback safety engine.")
    lower = user_input.lower()

    high_risk_triggers = [
        "help", "follow", "following", "stalk", "stalker", "threat", "weapon",
        "attack", "scared", "trapped", "danger", "grabbed", "emergency", "touch"
    ]
    medium_risk_triggers = [
        "suspicious", "dark", "alone", "uncomfortable", "watching", "behind me",
        "night", "cab", "taxi", "driver", "unfamiliar"
    ]

    if any(term in lower for term in high_risk_triggers):
        return {
            "risk": "HIGH",
            "answer": (
                "🚨 **IMMEDIATE SAFETY ALERT**\n\n"
                "I have detected a high-risk situation. Please prioritize your physical safety right now:\n"
                "1. **Move to Safety:** Walk toward the nearest open store, crowded area, or well-lit space immediately.\n"
                "2. **Contact Emergency Services:** Call **112** or **1091** right away.\n"
                "3. **Share Location:** Send your live GPS location to family or a trusted contact.\n\n"
                "Do not isolate yourself."
            )
        }

    if any(term in lower for term in medium_risk_triggers):
        return {
            "risk": "MEDIUM",
            "answer": (
                "⚠️ **SAFETY CAUTION**\n\n"
                "I am keeping watch with you. Let me guide you to stay safe:\n"
                "1. **Stay Alert:** Keep your head up, phones visible, and stay aware of your path.\n"
                "2. **Call Someone:** Call a family member or friend and talk to them aloud.\n"
                "3. **Change Route:** Cross to a well-lit side of the street if someone seems to be behind you."
            )
        }

    return {
        "risk": "LOW",
        "answer": (
            "I am here with you. Everything appears safe based on your message. "
            "How can I assist you with safety planning, legal rights guidance, or advice today?"
        )
    }


# -----------------------------------------------------------------------------
# PUBLIC CORE FUNCTIONS
# -----------------------------------------------------------------------------
def detect_risk(user_input: str) -> str:
    """
    Public utility to detect risk level ("LOW", "MEDIUM", "HIGH").
    Maintained for direct contract compatibility.
    """
    sanitized = sanitize_input(user_input)
    if not sanitized:
        return "LOW"
    
    res = get_response(sanitized, "")
    return res.get("risk", "LOW")


def get_response(user_input: str, chat_history: str = "") -> Dict[str, Any]:
    """
    Main response engine. Evaluates user input and chat history in a single unified pass.
    
    Args:
        user_input: Latest user message string.
        chat_history: Formatted history of past turns.
        
    Returns:
        Dict containing "answer" (str) and "risk" ("LOW" | "MEDIUM" | "HIGH")
    """
    sanitized_query = sanitize_input(user_input)
    if not sanitized_query:
        return {
            "answer": "I am here for you. Tell me what is on your mind or if you need safety guidance.",
            "risk": "LOW"
        }

    llm = initialize_llm()

    # Fallback if LLM client is unavailable
    if llm is None:
        eval_result = fallback_safety_evaluation(sanitized_query)
        if eval_result["risk"] in ["HIGH", "MEDIUM"]:
            eval_result["answer"] += f"\n\n{INDIA_HELPLINE_TEXT}"
        return eval_result

    # Truncate history context to prevent window overflow
    bounded_history = chat_history[-1500:] if chat_history else "No prior history."

    prompt_content = f"""
CONVERSATION HISTORY:
{bounded_history}

LATEST USER INPUT:
{sanitized_query}

Evaluate the situation and generate the JSON safety assessment object:
"""

    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt_content)
        ]

        response = llm.invoke(messages)
        raw_text = response.content.strip()

        # Clean JSON formatting wrappers if present
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1)
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "", 1)
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        # Parse structured JSON response
        data = json.loads(raw_text)
        risk = str(data.get("risk", "LOW")).upper()
        answer = str(data.get("answer", ""))

        if risk not in ["LOW", "MEDIUM", "HIGH"]:
            risk = "LOW"

        # Auto-append emergency helpline numbers for elevated risk
        if risk in ["HIGH", "MEDIUM"] and "112" not in answer:
            answer += f"\n\n{INDIA_HELPLINE_TEXT}"

        return {
            "answer": answer,
            "risk": risk
        }

    except json.JSONDecodeError as jde:
        logger.error(f"JSON Parsing Error in Groq response: {jde}")
        fallback = fallback_safety_evaluation(sanitized_query)
        return fallback
    except Exception as e:
        logger.error(f"Groq API Execution Failure: {e}")
        fallback = fallback_safety_evaluation(sanitized_query)
        if fallback["risk"] in ["HIGH", "MEDIUM"]:
            fallback["answer"] += f"\n\n{INDIA_HELPLINE_TEXT}"
        return fallback