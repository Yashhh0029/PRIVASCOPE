import os
import time
from typing import Dict, Any, Optional
from app.core.config import settings

class BaseAIProvider:
    name: str = "base"
    display_name: str = "Base Provider"
    is_demo: bool = False

    def is_available(self) -> bool:
        return True

    def generate_response(self, prompt: str) -> str:
        raise NotImplementedError

class LocalDemoProvider(BaseAIProvider):
    """
    Deterministic local simulation provider.
    Explicitly labeled as 'PRIVASCOPE LOCAL DEMO PROVIDER'.
    Used to demonstrate the AI Privacy Firewall without requiring paid cloud API keys.
    """
    name = "local_demo"
    display_name = "PRIVASCOPE LOCAL DEMO PROVIDER"
    is_demo = True

    def generate_response(self, prompt: str) -> str:
        # Check what tokens the provider received
        import re
        tokens_found = re.findall(r'<[A-Z_]+_\d{2}>', prompt)
        
        response_lines = [
            f"[{self.display_name}]",
            "Privacy Boundary Confirmation: Received outbound prompt over local loopback.",
        ]
        
        if tokens_found:
            response_lines.append(
                f"Received Sanitized Tokens: {', '.join(sorted(set(tokens_found)))}. "
                "Notice that zero raw personal identifiers were visible to this provider endpoint."
            )
            response_lines.append(
                f"Contextual Analysis: Processing inquiry regarding subject identified as {tokens_found[0]}."
            )
        else:
            response_lines.append(
                "Contextual Analysis: Processing prompt. No sensitive tokens or masked coordinates detected."
            )

        response_lines.append(
            "Security Notice: All sensitive parameters were protected by the local firewall prior to outbound ingress."
        )
        return "\n\n".join(response_lines)

class OpenAIProvider(BaseAIProvider):
    name = "openai"
    display_name = "OpenAI (GPT-4o)"
    is_demo = False

    def is_available(self) -> bool:
        return bool(settings.OPENAI_API_KEY)

    def generate_response(self, prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI API key not configured on server.")
        import httpx
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
        with httpx.Client(timeout=30.0) as client:
            res = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]

class AnthropicProvider(BaseAIProvider):
    name = "anthropic"
    display_name = "Anthropic (Claude 3.5 Sonnet)"
    is_demo = False

    def is_available(self) -> bool:
        return bool(settings.ANTHROPIC_API_KEY)

    def generate_response(self, prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("Anthropic API key not configured on server.")
        import httpx
        headers = {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
        with httpx.Client(timeout=30.0) as client:
            res = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["content"][0]["text"]

class GeminiProvider(BaseAIProvider):
    name = "gemini"
    display_name = "Google Gemini (1.5 Flash)"
    is_demo = False

    def is_available(self) -> bool:
        return bool(settings.GEMINI_API_KEY)

    def generate_response(self, prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("Gemini API key not configured on server.")
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        with httpx.Client(timeout=30.0) as client:
            res = client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

# Provider Registry
PROVIDERS: Dict[str, BaseAIProvider] = {
    "local_demo": LocalDemoProvider(),
    "openai": OpenAIProvider(),
    "anthropic": AnthropicProvider(),
    "gemini": GeminiProvider()
}

def get_provider(name: str) -> BaseAIProvider:
    return PROVIDERS.get(name, PROVIDERS["local_demo"])
