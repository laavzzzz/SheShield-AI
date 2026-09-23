"""
SheShield AI - Core LLM & Safety Intelligence Handler
Path: src/llm_handler.py

Provides production-grade integration with Groq API (Llama 3.1 8B Instant),
structured risk classification, input sanitization, context window management,
and deterministic fallback safety responses.
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import streamlit as st

try:
    from pydantic import BaseModel, Field, ValidationError
    from langchain_groq import ChatGroq
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
except ImportError as e:
    raise ImportError(
        "Missing required dependencies for SheShield AI LLM Handler. "
        "Ensure 'langchain-groq', 'pydantic', and 'streamlit' are installed."
    ) from e

# Configure module logger
logger = logging.getLogger("SheShield.LLMHandler")
logger.setLevel(logging.INFO)


class RiskLevel(str, Enum):
    """Enumeration of safety risk levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ThreatCategory(str, Enum):
    """Classification categories for safety threats."""
    GENERAL_INQUIRY = "general_inquiry"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    STALKING_FOLLOWING = "stalking_following"
    PHYSICAL_HARASSMENT = "physical_harassment"
    VERBAL_HARASSMENT = "verbal_harassment"
    DOMESTIC_DISTRESS = "domestic_distress"
    IMMINENT_DANGER = "imminent_danger"
    MEDICAL_EMERGENCY = "medical_emergency"
    UNKNOWN = "unknown"


class SafetyAssessment(BaseModel):
    """
    Structured Pydantic schema for AI safety outputs.
    Guarantees deterministic response parameters for UI rendering.
    """
    risk_level: RiskLevel = Field(
        default=RiskLevel.LOW,
        description="Assessed threat severity level (LOW, MEDIUM, HIGH)."
    )
    threat_category: ThreatCategory = Field(
        default=ThreatCategory.GENERAL_INQUIRY,
        description="Specific category of the detected safety concern."
    )
    confidence_score: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Confidence score of risk classification between 0.0 and 1.0."
    )
    conversational_response: str = Field(
        ...,
        description="Calm, supportive, actionable response tailored to user context."
    )
    de_escalation_steps: List[str] = Field(
        default_factory=list,
        description="Immediate practical safety steps for the user."
    )
    emergency_actions: List[str] = Field(
        default_factory=list,
        description="Urgent actions required if risk is MEDIUM or HIGH."
    )
    legal_rights_note: Optional[str] = Field(
        default=None,
        description="Relevant legal rights or helpline advice if applicable."
    )
    is_fallback: bool = Field(
        default=False,
        description="Flag indicating if response was generated via deterministic fallback."
    )


@dataclass
class UserContext:
    """Dataclass holding user context and preferences."""
    name: str = "User"
    age: Optional[int] = None
    default_location: str = ""
    current_coords: Optional[Dict[str, float]] = None
    location_sharing_active: bool = False


class InputSanitizer:
    """Sanitizes user input against prompt injection and malicious constructs."""
    
    # Patterns common in prompt injection attempts
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"system\s*prompt",
        r"you\s+are\s+now\s+a",
        r"jailbreak",
        r"DAN\s+mode",
        r"override\s+safety",
    ]
    
    @classmethod
    def sanitize(cls, text: str, max_length: int = 1000) -> str:
        """
        Sanitizes raw user input text.
        
        Args:
            text: Raw input string.
            max_length: Maximum allowable input length.
            
        Returns:
            Cleaned and truncated string.
        """
        if not text:
            return ""
            
        # Truncate input length
        cleaned = text.strip()[:max_length]
        
        # Neutralize common injection phrases
        for pattern in cls.INJECTION_PATTERNS:
            cleaned = re.sub(pattern, "[redacted_instruction]", cleaned, flags=i = re.IGNORECASE)
            
        return cleaned


class LLMHandler:
    """
    Enterprise LLM Service Manager utilizing Groq API and LangChain.
    Handles API authorization, context window management, structured evaluation,
    and resilience fallbacks.
    """
    
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    MAX_HISTORY_MESSAGES = 10  # Maximum back-and-forth messages preserved in context
    
    SYSTEM_PROMPT_TEMPLATE = """You are SheShield AI, an advanced, highly empathetic, and real-time personal safety assistant for women.
Your core mission is to evaluate safety threats, provide immediate calming guidance, assess legal/emergency options, and recommend safety steps.

OPERATIONAL RULES:
1. RISK EVALUATION:
   - LOW: General inquiries, safe situations, post-event discussion, general questions.
   - MEDIUM: Suspicious activity, dark/unfamiliar environments, uncomfortable presence, following at a distance.
   - HIGH: Direct physical threat, active stalking, entrapment, weapon present, domestic violence, immediate distress.

2. RESPONSE TONE:
   - Maintain a calm, authoritative, supportive, non-alarmist tone.
   - Avoid long preambles. Prioritize clarity and immediate action.

3. USER CONTEXT:
   - User Name: {user_name}
   - User Age: {user_age}
   - Location Sharing: {location_status}
   - Current Location Context: {location_context}

Provide a structured, accurate assessment following the strict JSON target format.
"""

    def __init__(self, api_key: Optional[str] = None, model_name: str = DEFAULT_MODEL):
        """
        Initializes the LLM Handler with client authorization.
        
        Args:
            api_key: Optional explicit Groq API key. If omitted, resolved from Streamlit secrets or env.
            model_name: Groq model identifier.
        """
        self.model_name = model_name
        self.api_key = api_key or self._resolve_api_key()
        self._llm: Optional[ChatGroq] = None
        
        if self.api_key:
            self._init_client()
        else:
            logger.warning("SheShield AI initialized without a valid Groq API key. Operating in fallback mode.")

    def _resolve_api_key(self) -> Optional[str]:
        """Resolves API key from Streamlit secrets or OS environment variables."""
        # 1. Check Streamlit Secrets
        try:
            if "GROQ_API_KEY" in st.secrets:
                return str(st.secrets["GROQ_API_KEY"])
        except Exception:
            pass
            
        # 2. Check Environment Variables
        return os.environ.get("GROQ_API_KEY")

    def _init_client(self) -> None:
        """Instantiates the ChatGroq client with structured settings."""
        try:
            self._llm = ChatGroq(
                groq_api_key=self.api_key,
                model_name=self.model_name,
                temperature=0.2,  # Low temperature for consistent safety scoring
                max_retries=2,
                request_timeout=10.0
            )
            logger.info(f"ChatGroq initialized successfully with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGroq client: {str(e)}")
            self._llm = None

    def _format_system_prompt(self, context: UserContext) -> str:
        """Formats the system prompt dynamically with user context."""
        loc_status = "Active" if context.location_sharing_active else "Disabled (Anonymous Mode)"
        
        loc_details = "Not provided"
        if context.location_sharing_active:
            if context.current_coords:
                loc_details = f"Coordinates: Lat {context.current_coords.get('lat')}, Lon {context.current_coords.get('lon')}"
            elif context.default_location:
                loc_details = f"Default City: {context.default_location}"

        return self.SYSTEM_PROMPT_TEMPLATE.format(
            user_name=context.name or "User",
            user_age=str(context.age) if context.age else "Unspecified",
            location_status=loc_status,
            location_context=loc_details
        )

    def _truncate_chat_history(self, chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Truncates chat history to prevent exceeding model context window bounds."""
        if not chat_history:
            return []
        return chat_history[-self.MAX_HISTORY_MESSAGES:]

    def evaluate_safety_situation(
        self,
        user_input: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        user_context: Optional[UserContext] = None
    ) -> SafetyAssessment:
        """
        Main entry point for processing safety queries.
        Evaluates risk level and returns a structured SafetyAssessment response.
        
        Args:
            user_input: Raw text message from user.
            chat_history: List of previous chat turns [{"role": "user"/"assistant", "content": "..."}].
            user_context: Structured user demographic & location context.
            
        Returns:
            SafetyAssessment object.
        """
        sanitized_input = InputSanitizer.sanitize(user_input)
        context = user_context or UserContext()
        history = self._truncate_chat_history(chat_history or [])

        # If LLM client is unavailable, execute local deterministic safety assessment
        if not self._llm:
            return self._generate_fallback_assessment(sanitized_input, "Groq API client uninitialized")

        try:
            # Enforce structured Pydantic response from LLM
            structured_llm = self._llm.with_structured_output(SafetyAssessment)
            
            # Prepare LangChain message sequence
            messages = [SystemMessage(content=self._format_system_prompt(context))]
            
            for msg in history:
                role = msg.get("role", "").lower()
                content = msg.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role in ["assistant", "ai"]:
                    messages.append(AIMessage(content=content))
            
            messages.append(HumanMessage(content=sanitized_input))

            # Invoke model with structured binding
            assessment: SafetyAssessment = structured_llm.invoke(messages)
            return assessment

        except ValidationError as ve:
            logger.error(f"Pydantic Validation Error during LLM response parsing: {str(ve)}")
            return self._generate_fallback_assessment(sanitized_input, "Response validation failed")
        except Exception as e:
            logger.error(f"Error during Groq LLM evaluation: {str(e)}")
            return self._generate_fallback_assessment(sanitized_input, f"LLM execution error: {type(e).__name__}")

    def _generate_fallback_assessment(self, user_input: str, reason: str) -> SafetyAssessment:
        """
        Deterministic, heuristic-based safety assessment engine.
        Executed when API fails, times out, or key is missing.
        Ensures the safety assistant never fails to provide emergency support.
        """
        logger.warning(f"Executing deterministic fallback safety engine. Reason: {reason}")
        
        lower_input = user_input.lower()
        
        # Heuristic Risk Keyword Detection
        high_risk_keywords = [
            "help", "follow", "following", "stalk", "stalker", "threat", "weapon", 
            "gun", "knife", "attack", "scared", "trapped", "danger", "touch", "grabbed"
        ]
        medium_risk_keywords = [
            "suspicious", "dark", "alone", "uncomfortable", "watching", "stranger", 
            "behind me", "night", "cab", "taxi", "driver"
        ]

        if any(kw in lower_input for kw in high_risk_keywords):
            return SafetyAssessment(
                risk_level=RiskLevel.HIGH,
                threat_category=ThreatCategory.IMMINENT_DANGER,
                confidence_score=0.85,
                conversational_response=(
                    "I have detected that you may be in an unsafe situation. "
                    "Please prioritize your immediate physical safety right now. "
                    "Move toward a well-lit, populated location if possible."
                ),
                de_escalation_steps=[
                    "Head toward the nearest open shop, public area, or group of people.",
                    "Keep your phone in your hand ready to dial emergency services.",
                    "Do not isolate yourself in hidden or enclosed spaces."
                ],
                emergency_actions=[
                    "Call emergency services immediately (112 / 911 / Local Helpline).",
                    "Share your live location with a trusted contact.",
                    "Trigger the SheShield SOS button."
                ],
                legal_rights_note="You have the right to immediate emergency law enforcement assistance.",
                is_fallback=True
            )
            
        if any(kw in lower_input for kw in medium_risk_keywords):
            return SafetyAssessment(
                risk_level=RiskLevel.MEDIUM,
                threat_category=ThreatCategory.SUSPICIOUS_BEHAVIOR,
                confidence_score=0.75,
                conversational_response=(
                    "I understand you are feeling uneasy. I am keeping close watch with you. "
                    "Let's take proactive steps to ensure your path is secure."
                ),
                de_escalation_steps=[
                    "Stay alert and aware of your surroundings; keep head up.",
                    "Pretend to be on a voice call or call a trusted friend.",
                    "Cross the street or alter your walk path if someone is following."
                ],
                emergency_actions=[
                    "Keep emergency numbers pre-dialed on your phone screen.",
                    "Enable live location sharing on your SheShield map."
                ],
                legal_rights_note="Harassment and stalking in public spaces are illegal offenses under law.",
                is_fallback=True
            )

        # Default LOW risk response
        return SafetyAssessment(
            risk_level=RiskLevel.LOW,
            threat_category=ThreatCategory.GENERAL_INQUIRY,
            confidence_score=0.90,
            conversational_response=(
                "I am here to support you. Everything appears safe based on your update. "
                "How else can I assist you with safety advice, legal awareness, or guidance today?"
            ),
            de_escalation_steps=[
                "Maintain general awareness of surrounding emergency exits.",
                "Keep your phone adequately charged when traveling."
            ],
            emergency_actions=[],
            legal_rights_note=None,
            is_fallback=True
        )


@st.cache_resource(show_spinner=False)
def get_llm_handler() -> LLMHandler:
    """
    Cached factory function for Streamlit.
    Ensures single instance creation of LLMHandler across session runs.
    """
    return LLMHandler()