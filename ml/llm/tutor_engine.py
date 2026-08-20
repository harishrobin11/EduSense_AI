"""LLM Conversational Tutor Engine connecting Ollama with Socratic Fallback for EduSense AI."""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional


class LLMTutorEngine:
    """Engine orchestrating context-aware Socratic system prompts and Ollama LLM inference."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "llama3"):
        self.ollama_url = ollama_url
        self.model_name = model_name

    def build_socratic_prompt(
        self,
        student_name: str,
        topic_name: str,
        subject: str,
        recent_score: Optional[float],
        struggle_risk: str,
        weak_topics: List[str],
        prerequisites: List[str],
    ) -> str:
        """Construct a personalized Socratic system prompt based on learner context."""
        prereq_str = ", ".join(prerequisites) if prerequisites else "None"
        weak_str = ", ".join(weak_topics) if weak_topics else "None"
        score_str = f"{recent_score:.1f}%" if recent_score is not None else "No prior attempts"

        system_prompt = (
            f"You are EduSense AI, an empathetic, expert Socratic AI Tutor for {student_name}.\n"
            f"Student Profile & Target Context:\n"
            f"- Current Subject: {subject}\n"
            f"- Target Topic: {topic_name}\n"
            f"- Recent Score on Target Topic: {score_str}\n"
            f"- Identified Struggle Risk Level: {struggle_risk.upper()}\n"
            f"- Identified Weak Areas: {weak_str}\n"
            f"- Topic Prerequisites: {prereq_str}\n\n"
            f"Pedagogical Guidelines:\n"
            f"1. Be encouraging, patient, and clear.\n"
            f"2. Use the Socratic method: guide the student by asking thought-provoking questions rather than giving direct quiz answers immediately.\n"
            f"3. Break complex concepts into small, intuitive steps.\n"
            f"4. If the student exhibits struggle risk, reference prerequisite concepts ({prereq_str}) to rebuild foundational understanding.\n"
            f"5. Keep responses concise (under 250 words) and nicely structured with bullet points or bold text."
        )
        return system_prompt

    def generate_tutor_response(
        self,
        student_name: str,
        topic_name: str,
        subject: str,
        user_message: str,
        chat_history: List[Dict[str, str]],
        recent_score: Optional[float] = None,
        struggle_risk: str = "low",
        weak_topics: List[str] = None,
        prerequisites: List[str] = None,
    ) -> Dict[str, Any]:
        """Generate tutor response via local Ollama endpoint or Socratic Fallback provider."""
        system_prompt = self.build_socratic_prompt(
            student_name=student_name,
            topic_name=topic_name,
            subject=subject,
            recent_score=recent_score,
            struggle_risk=struggle_risk,
            weak_topics=weak_topics or [],
            prerequisites=prerequisites or [],
        )

        # Attempt Ollama HTTP request
        ollama_response = self._call_ollama(system_prompt, user_message, chat_history)
        if ollama_response:
            return {
                "tutor_response": ollama_response,
                "provider": "ollama",
                "model_used": self.model_name,
                "socratic_prompt_used": system_prompt,
            }

        # Fallback to Socratic AI Response Generator
        fallback_text = self._generate_socratic_fallback(
            user_message=user_message,
            topic_name=topic_name,
            subject=subject,
            struggle_risk=struggle_risk,
            prerequisites=prerequisites or [],
        )
        return {
            "tutor_response": fallback_text,
            "provider": "socratic_fallback_ai",
            "model_used": "edusense-socratic-v1",
            "socratic_prompt_used": system_prompt,
        }

    def _call_ollama(
        self, system_prompt: str, user_message: str, chat_history: List[Dict[str, str]]
    ) -> Optional[str]:
        """Query local Ollama /api/chat endpoint."""
        url = f"{self.ollama_url}/api/chat"
        messages = [{"role": "system", "content": system_prompt}]
        for h in chat_history[-6:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    res_body = json.loads(response.read().decode("utf-8"))
                    return res_body.get("message", {}).get("content")
        except Exception:
            return None
        return None

    def _generate_socratic_fallback(
        self,
        user_message: str,
        topic_name: str,
        subject: str,
        struggle_risk: str,
        prerequisites: List[str],
    ) -> str:
        """Structured Socratic AI tutor fallback when external Ollama service is offline."""
        msg_lower = user_message.lower()
        prereq_str = ", ".join(prerequisites) if prerequisites else "core concepts"

        if "explain" in msg_lower or "what is" in msg_lower or "how does" in msg_lower:
            return (
                f"Great question about **{topic_name}** in {subject}!\n\n"
                f"Let's break this down together step-by-step:\n"
                f"1. **Core Concept**: Imagine {topic_name} as a mathematical bridge built on top of **{prereq_str}**.\n"
                f"2. **Key Intuition**: Why do you think we need {topic_name} when solving problems in {subject}?\n\n"
                f"👉 *Socratic Challenge*: Before I give away the full equation, what do you think is the main goal of {topic_name}?"
            )

        if "example" in msg_lower or "problem" in msg_lower or "practice" in msg_lower:
            return (
                f"Let's work through a practical **{topic_name}** example together!\n\n"
                f"Suppose you are training a model on a dataset with 100 observations.\n"
                f"- **Step 1**: Identify your input features and target labels.\n"
                f"- **Step 2**: Apply the fundamental rule of {topic_name}.\n\n"
                f"👉 *Question for you*: What is the first step you would take when preprocessing the data?"
            )

        if struggle_risk.lower() in ("high", "moderate"):
            return (
                f"I notice you've been working hard on **{topic_name}**! Because this is a challenging topic, let's strengthen your foundation in **{prereq_str}** first.\n\n"
                f"- **Key Takeaway**: Mastering the prerequisites makes {topic_name} much easier to understand.\n\n"
                f"👉 *Socratic Prompt*: Would you like to review **{prereq_str}** for 2 minutes, or walk through a simplified {topic_name} diagram together?"
            )

        return (
            f"That's a thoughtful point on **{topic_name}**!\n\n"
            f"To help connect this to your learning goals in {subject}:\n"
            f"- How does this concept connect to what you learned in previous lessons?\n\n"
            f"👉 Tell me in your own words what part of {topic_name} feels clearest or most confusing right now!"
        )


tutor_engine = LLMTutorEngine()
