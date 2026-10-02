"""
Gemini Engine - AI-powered content generation for Tamil YouTube videos.
Handles topic discovery, script writing, and metadata generation.
Uses Google Gemini free tier.
"""

import json
import logging
import random
import re
import time
from datetime import datetime
from typing import Dict, List

from google import genai
from google.genai import errors as genai_errors

from config import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_FALLBACK_MODELS,
    CONTENT_CATEGORIES, USED_TOPICS_FILE
)

logger = logging.getLogger(__name__)


def _clean_json(text: str) -> str:
    """Strip markdown fences and leading 'json' tag from Gemini output."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


# Retryable HTTP status codes from Gemini (transient errors)
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _is_retryable(exc: Exception) -> bool:
    """Return True for transient Gemini API errors worth retrying."""
    if isinstance(exc, genai_errors.APIError):
        # APIError stores .status on the class; ServerError subclasses it
        status = getattr(exc, "status", None) or getattr(exc, "args", [None])[0]
        try:
            code = int(status) if status is not None else None
        except (TypeError, ValueError):
            code = None
        if code in _RETRYABLE_STATUS_CODES:
            return True
        # Fall back to message inspection
        msg = str(exc)
        if any(s in msg for s in ("429", "500", "502", "503", "504",
                                  "UNAVAILABLE", "OVERLOADED", "RESOURCE_EXHAUSTED")):
            return True
    return False


def _generate_with_retry(client, model_name: str, prompt: str,
                         max_attempts: int = 6, base_delay: float = 5.0,
                         fallback_models=None) -> str:
    """Call generate_content with exponential backoff for transient errors.

    If `fallback_models` is provided, each model is tried in order with its own
    retry loop. A model that returns 404 (permanently unavailable) is skipped
    without retries; transient errors (429/5xx) are retried with backoff before
    moving to the next fallback.
    """
    models_to_try = [model_name] + (fallback_models or [])
    last_exc = None
    for model_idx, mname in enumerate(models_to_try):
        for attempt in range(1, max_attempts + 1):
            try:
                resp = client.models.generate_content(model=mname, contents=prompt)
                if model_idx > 0:
                    logger.info(f"Success using fallback model: {mname}")
                return resp.text
            except Exception as exc:
                last_exc = exc
                # 404 = model doesn't exist; skip to next fallback immediately
                status = getattr(exc, "status", None)
                try:
                    code = int(status) if status is not None else None
                except (TypeError, ValueError):
                    code = None
                if code == 404:
                    logger.info(f"Model {mname} not available (404), trying next fallback...")
                    break
                if not _is_retryable(exc) or attempt == max_attempts:
                    if model_idx < len(models_to_try) - 1:
                        logger.warning(
                            f"Model {mname} failed after {attempt} attempts: {exc}. "
                            f"Trying next fallback model..."
                        )
                        break
                    raise
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1.5)
                logger.warning(
                    f"Gemini transient error on {mname} (attempt {attempt}/{max_attempts}): "
                    f"{exc}. Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
    raise last_exc  # pragma: no cover


class GeminiEngine:
    """Generate video content using Google Gemini."""

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL
        # Fallback models exclude the primary (it's tried first by _generate_with_retry)
        self.fallback_models = [m for m in GEMINI_FALLBACK_MODELS if m != GEMINI_MODEL]
        self.used_topics = self._load_used_topics()

    # ── topic tracking ───────────────────────────────────────

    def _load_used_topics(self) -> List[str]:
        try:
            if USED_TOPICS_FILE.exists():
                return json.loads(USED_TOPICS_FILE.read_text()).get("topics", [])
        except Exception as e:
            logger.warning(f"Could not load used topics: {e}")
        return []

    def _save_used_topics(self):
        try:
            USED_TOPICS_FILE.write_text(json.dumps({
                "topics": self.used_topics[-200:],
                "updated": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.warning(f"Could not save used topics: {e}")

    # ── public API ───────────────────────────────────────────

    def generate_topic(self) -> Dict:
        """Pick a specific, engaging video topic via Gemini."""
        category = random.choice(CONTENT_CATEGORIES)
        recent = "\n".join(f"- {t}" for t in self.used_topics[-30:]) or "None yet"

        prompt = f"""You are a Tamil YouTube content creator whose channel covers facts, history, science, technology, and mysteries.

Generate ONE specific, engaging video topic in the category: **{category}**

The topic must:
1. Be interesting to Tamil-speaking audiences (college students, professionals, curious viewers).
2. Have enough depth for a 10-15 minute documentary-style video.
3. Not be overly broad ("History of India") or trivially narrow.
4. Have visual storytelling potential.
5. Be clearly different from these recently covered topics:
{recent}

Return ONLY valid JSON — no markdown fences, no extra text:
{{
  "topic": "specific topic in English",
  "tamil_topic": "same topic in Tamil",
  "category": "{category}",
  "angle": "unique angle or hook for this video (1-2 sentences)",
  "key_points": ["point1", "point2", "point3", "point4", "point5"],
  "image_queries": ["image search query 1", "image search query 2", "image search query 3", "image search query 4"]
}}"""

        text = _generate_with_retry(self.client, self.model_name, prompt, fallback_models=self.fallback_models)
        data = json.loads(_clean_json(text))

        self.used_topics.append(data["topic"])
        self._save_used_topics()
        logger.info(f"Topic: {data['topic']} [{data['category']}]")
        return data

    def generate_script(self, topic_data: Dict) -> str:
        """Generate a ~2500-word conversational Tamil narration script."""
        topic = topic_data["topic"]
        tamil_topic = topic_data.get("tamil_topic", topic)
        angle = topic_data.get("angle", "")
        kp = "\n".join(f"- {p}" for p in topic_data.get("key_points", []))

        prompt = f"""You are a professional Tamil YouTube scriptwriter known for engaging, conversational narration — like a popular Tamil creator who keeps viewers hooked.

Write a COMPLETE narration script for a **12-minute** Tamil YouTube video.

Topic: {topic}
Tamil title: {tamil_topic}
Angle: {angle}
Key points to cover:
{kp}

═══ STRICT REQUIREMENTS ═══

1. Write in NATURAL, CONVERSATIONAL Tamil — the way a popular Tamil YouTuber speaks casually yet informatively. NOT formal literary Tamil. NOT textbook Tamil.
2. The script MUST be approximately **2500 Tamil words** (critical for 12 minutes of narration at normal speaking pace).
3. Do NOT use numbered lists, bullet points, or markdown in the narration.
4. Do NOT use English words except those commonly used in everyday Tamil (phone, computer, science, technology, etc.).
5. VARY sentence length — mix short punchy sentences with longer explanations. Never start consecutive sentences the same way.

═══ STRUCTURE ═══

Mark each section exactly as shown:

[SECTION: Hook]
First 30 seconds — grab attention immediately with a surprising fact, provocative question, or dramatic statement.
Example style: "2000 வருடங்களுக்கு முன்னாடி, உலகத்துல மிகப்பெரிய நகரங்களுல ஒன்னு தமிழ்நாட்டுல இருந்தது... இது நம்ம எல்லாருக்கும் தெரிஞ்ச கதை இல்ல..."

[SECTION: Introduction]
~1 minute — why this topic matters, set up the narrative arc.

[SECTION: Background]
~1.5 minutes — historical or contextual background, set the scene.

[SECTION: Main Content Part 1]
~3 minutes — first major pillar of the topic with storytelling, vivid examples, specific details.

[SECTION: Main Content Part 2]
~3 minutes — second major pillar, building on Part 1, going deeper.

[SECTION: Deep Dive]
~2 minutes — lesser-known facts, surprising details. Use: "இதுல சுவாரஸ்யமான விஷயம் என்னன்னா..."

[SECTION: Conclusion]
~1 minute — key takeaways, thought-provoking closing, encourage engagement: "இது பத்தி உங்க கருத்தை comment-ல சொல்லுங்க"

═══ STYLE GUIDELINES ═══

- Conversational transitions: "சரி, இப்போ நாம பாக்கப்போறது...", "இங்க தான் கதை twist ஆகுது...", "நீங்க நம்ப மாட்டீங்க..."
- Rhetorical questions: "இது எப்படி possible-ன்னு யோசிச்சிருக்கீங்களா?"
- Use analogies to explain complex ideas simply.
- Include specific dates, names, numbers for credibility.
- For uncertain claims use: "சிலர் கூறும் கோட்பாடுப்படி", "இதுக்கு உறுதியான ஆதாரம் இல்ல", "ஆராய்ச்சியாளர்கள் கருத்துப்படி"

═══ OUTPUT ═══

Return ONLY the script text with [SECTION: ...] markers. No other formatting or commentary."""

        script = _generate_with_retry(self.client, self.model_name, prompt, fallback_models=self.fallback_models)
        script = script.strip()
        word_count = len(script.split())
        logger.info(f"Script generated: {len(script)} chars, ~{word_count} words")

        # If script is too short, request an extension
        if word_count < 1500:
            logger.warning(f"Script too short ({word_count} words), requesting extension")
            ext_prompt = f"""The following Tamil video script is too short. It must be at least 2500 words for a 12-minute video.

Current script ({word_count} words):
{script}

Please EXTEND every section with more details, examples, stories, and explanations. Keep the same structure and [SECTION: ...] markers. Return the COMPLETE extended script."""
            script2 = _generate_with_retry(self.client, self.model_name, ext_prompt, fallback_models=self.fallback_models)
            script = script2.strip()
            logger.info(f"Extended script: {len(script)} chars, ~{len(script.split())} words")

        return script

    def generate_metadata(self, topic_data: Dict, script: str) -> Dict:
        """Generate YouTube title, description, tags, and thumbnail text."""
        topic = topic_data["topic"]
        category = topic_data.get("category", "Facts")

        prompt = f"""Generate YouTube metadata for a Tamil documentary/facts video.

Topic: {topic}
Category: {category}
Script excerpt: {script[:600]}

Return ONLY valid JSON — no markdown fences:
{{
  "title": "Engaging English title, max 70 chars, curiosity-driven, NOT clickbait",
  "tamil_title": "Short Tamil title for thumbnail (max 5 words)",
  "description": "YouTube description (300-500 chars) with: Tamil summary, key points covered, relevant hashtags, disclaimer for unverified claims if needed",
  "tags": ["15-20 tags mixing Tamil and English, relevant to the topic"],
  "thumbnail_text": "2-4 impactful words for thumbnail overlay (Tamil or English)"
}}"""

        text = _generate_with_retry(self.client, self.model_name, prompt, fallback_models=self.fallback_models)
        metadata = json.loads(_clean_json(text))
        logger.info(f"Metadata — title: {metadata.get('title', '?')}")
        return metadata

    def generate_scene_queries(self, scenes: List[Dict]) -> List[str]:
        """Return one image-search query per scene for stock-photo lookup."""
        summaries = []
        for i, sc in enumerate(scenes):
            preview = sc.get("narration", "")[:150]
            summaries.append(f"Scene {i+1} ({sc.get('section','')}): {preview}")

        prompt = f"""For each scene below, give ONE concise English stock-photo search query that would return a relevant, high-quality photograph.

{chr(10).join(summaries)}

Return ONLY a JSON array of strings — one query per scene, same order:
["query for scene 1", "query for scene 2", ...]"""

        text = _generate_with_retry(self.client, self.model_name, prompt, fallback_models=self.fallback_models)
        queries = json.loads(_clean_json(text))
        logger.info(f"Generated {len(queries)} image queries")
        return queries


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = GeminiEngine()
    topic = engine.generate_topic()
    print(json.dumps(topic, ensure_ascii=False, indent=2))
