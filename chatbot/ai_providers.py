"""
5 Free AI Provider implementations with rate-limit tracking.

Priority order (automatic fallback):
  1. Google Gemini Flash   — 15 RPM, 1500 RPD  (best context: 1M tokens)
  2. Groq Llama-3.1-8B    — 30 RPM, 14400 RPD (fastest)
  3. OpenRouter Free       — 20 RPM, 50 RPD    (many free models)
  4. Mistral NeMo          — 1 RPS, generous   (reliable fallback)
  5. HuggingFace           — 1000 req/5min     (always available)

Each provider:
  - Tracks rate-limit cooldown automatically
  - Returns None on failure (caller moves to next)
  - Logs which provider was used
"""

import os
import time
import logging
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Base Provider
# ─────────────────────────────────────────────────────────────────────────────

class BaseProvider(ABC):
    name          = "Base"
    cooldown_secs = 60      # seconds to wait after hitting a rate limit

    def __init__(self):
        self._blocked_until  = 0      # epoch time when block lifts
        self._no_key         = False  # True if API key is missing

    # ── public ──────────────────────────────────────────────────────────────

    def is_available(self):
        """True if the provider can accept a request right now."""
        if self._no_key:
            return False
        return time.time() >= self._blocked_until

    def seconds_until_available(self):
        remaining = self._blocked_until - time.time()
        return max(0.0, remaining)

    def generate(self, system_prompt: str, history: list, user_message: str) -> str | None:
        """
        Call the AI and return the response string, or None on any failure.
        history = [{"role": "user"|"assistant", "content": "..."}]
        """
        try:
            result = self._call(system_prompt, history, user_message)
            log.info("[AI] %s responded OK", self.name)
            return result
        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ('429', 'rate_limit', 'rate limit',
                                       'quota', 'exceeded', 'too many')):
                self._blocked_until = time.time() + self.cooldown_secs
                log.warning("[AI] %s rate-limited — blocked for %ss", self.name, self.cooldown_secs)
            else:
                log.error("[AI] %s error: %s", self.name, e)
            return None

    # ── private (override in subclass) ──────────────────────────────────────

    @abstractmethod
    def _call(self, system_prompt: str, history: list, user_message: str) -> str:
        """Make the actual API call. Raise on failure."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# 1. Google Gemini Flash
#    Free: 15 RPM · 1,500 RPD · 1M token context
#    Key:  GEMINI_API_KEY  (aistudio.google.com → Get API Key)
# ─────────────────────────────────────────────────────────────────────────────

class GeminiProvider(BaseProvider):
    name          = "Google Gemini Flash"
    cooldown_secs = 65     # RPM resets every 60s

    _MODEL = "gemini-1.5-flash"

    def __init__(self):
        super().__init__()
        self._api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not self._api_key:
            self._no_key = True
            log.info("[AI] GeminiProvider: GEMINI_API_KEY not set — skipping")
        self._client = None

    def _get_client(self):
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self._client = genai.GenerativeModel(
                model_name=self._MODEL,
                generation_config={"temperature": 0.3, "max_output_tokens": 1024},
            )
        return self._client

    def _call(self, system_prompt, history, user_message):
        model = self._get_client()
        # Gemini doesn't have a separate system role — prepend to first user turn
        prompt = f"{system_prompt}\n\n---\nUser question: {user_message}"
        response = model.generate_content(prompt)
        return response.text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# 2. Groq — Llama-3.1-8B-Instant
#    Free: 30 RPM · 14,400 RPD · 128K context
#    Key:  GROQ_API_KEY  (console.groq.com → API Keys)
# ─────────────────────────────────────────────────────────────────────────────

class GroqProvider(BaseProvider):
    name          = "Groq Llama-3.1-8B"
    cooldown_secs = 65

    _MODEL = "llama-3.1-8b-instant"

    def __init__(self):
        super().__init__()
        self._api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not self._api_key:
            self._no_key = True
            log.info("[AI] GroqProvider: GROQ_API_KEY not set — skipping")
        self._client = None

    def _get_client(self):
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=self._api_key)
        return self._client

    def _call(self, system_prompt, history, user_message):
        client = self._get_client()
        messages = [{"role": "system", "content": system_prompt}]
        # Include last 4 conversation turns for context
        for m in history[-4:]:
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user_message})

        resp = client.chat.completions.create(
            model=self._MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# 3. OpenRouter — Free Models
#    Free: 20 RPM · 50 RPD (no credits) / 200 RPD (with credits)
#    Key:  OPENROUTER_API_KEY  (openrouter.ai → Keys)
# ─────────────────────────────────────────────────────────────────────────────

class OpenRouterProvider(BaseProvider):
    name          = "OpenRouter (Llama-3.2)"
    cooldown_secs = 65

    _MODEL   = "meta-llama/llama-3.2-3b-instruct:free"
    _API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        super().__init__()
        self._api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not self._api_key:
            self._no_key = True
            log.info("[AI] OpenRouterProvider: OPENROUTER_API_KEY not set — skipping")

    def _call(self, system_prompt, history, user_message):
        import requests
        messages = [{"role": "system", "content": system_prompt}]
        for m in history[-4:]:
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user_message})

        resp = requests.post(
            self._API_URL,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "https://indusuni-cse-chatbot.app",
                "X-Title":       "Indus University CSE Chatbot",
            },
            json={
                "model":       self._MODEL,
                "messages":    messages,
                "max_tokens":  1024,
                "temperature": 0.3,
            },
            timeout=30,
        )
        if resp.status_code == 429:
            raise Exception("429 rate limit")
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


# ─────────────────────────────────────────────────────────────────────────────
# 4. Mistral AI — Mistral NeMo (open model)
#    Free: ~1 RPS · 128K context · generous monthly tokens
#    Key:  MISTRAL_API_KEY  (console.mistral.ai → API Keys)
# ─────────────────────────────────────────────────────────────────────────────

class MistralProvider(BaseProvider):
    name          = "Mistral NeMo"
    cooldown_secs = 70   # 1 RPS limit — be safe

    _MODEL = "open-mistral-nemo"

    def __init__(self):
        super().__init__()
        self._api_key = os.getenv("MISTRAL_API_KEY", "").strip()
        if not self._api_key:
            self._no_key = True
            log.info("[AI] MistralProvider: MISTRAL_API_KEY not set — skipping")
        self._client = None

    def _get_client(self):
        if self._client is None:
            from mistralai import Mistral
            self._client = Mistral(api_key=self._api_key)
        return self._client

    def _call(self, system_prompt, history, user_message):
        client = self._get_client()
        messages = [{"role": "system", "content": system_prompt}]
        for m in history[-4:]:
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user_message})

        resp = client.chat.complete(
            model=self._MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# 5. HuggingFace Inference API — Llama-3.1-8B
#    Free: 1,000 requests / 5-min window (resets every 5 min)
#    Key:  HF_TOKEN  (huggingface.co → Settings → Access Tokens)
# ─────────────────────────────────────────────────────────────────────────────

class HuggingFaceProvider(BaseProvider):
    name          = "HuggingFace Llama-3.1"
    cooldown_secs = 310  # Wait 5 min + buffer for window to reset

    _MODEL = "meta-llama/Llama-3.1-8B-Instruct"

    def __init__(self):
        super().__init__()
        self._api_key = os.getenv("HF_TOKEN", "").strip()
        if not self._api_key:
            self._no_key = True
            log.info("[AI] HuggingFaceProvider: HF_TOKEN not set — skipping")
        self._client = None

    def _get_client(self):
        if self._client is None:
            from huggingface_hub import InferenceClient
            self._client = InferenceClient(
                model=self._MODEL,
                token=self._api_key,
            )
        return self._client

    def _call(self, system_prompt, history, user_message):
        client = self._get_client()
        messages = [{"role": "system", "content": system_prompt}]
        for m in history[-4:]:
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user_message})

        resp = client.chat_completion(
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Provider Registry — ordered by priority
# ─────────────────────────────────────────────────────────────────────────────

ALL_PROVIDERS: list[BaseProvider] = [
    GeminiProvider(),       # 1st choice
    GroqProvider(),         # 2nd choice
    OpenRouterProvider(),   # 3rd choice
    MistralProvider(),      # 4th choice
    HuggingFaceProvider(),  # 5th choice (last resort)
]
