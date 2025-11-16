"""LLM service for enhanced README and metadata analysis."""

import hashlib
import json
import logging
import os
import re
import time
from typing import Any, Dict, Optional

import requests

log = logging.getLogger(__name__)

# Purdue GenAI Studio API configuration
PURDUE_GENAI_API_URL = "https://genai.rcac.purdue.edu/api/v1/chat/completions"
PURDUE_GENAI_MODEL = "llama3.2:latest"


class LLMService:
    """Service for interacting with Purdue GenAI Studio API."""

    def __init__(self):
        """Initialize the LLM service."""
        self.api_key = os.getenv("GEN_AI_STUDIO_API_KEY")
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0.0
        self.cache: Dict[str, Any] = {}

    def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def _get_cache_key(self, content: str, analysis_type: str) -> str:
        """Generate a cache key for the given content and analysis type."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{analysis_type}_{content_hash}"

    def _call_api(self, prompt: str, content: str) -> Optional[Dict[str, Any]]:
        """Make a call to the Purdue GenAI Studio API."""
        if not self.api_key:
            log.warning("GEN_AI_STUDIO_API_KEY not set, skipping LLM analysis")
            return None

        self._rate_limit()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": PURDUE_GENAI_MODEL,
            "max_tokens": 1000,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert AI model evaluator. "
                    "Analyze the provided content and return structured JSON responses.",
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nContent to analyze:\n{content}",
                },
            ],
        }

        try:
            response = requests.post(
                PURDUE_GENAI_API_URL, headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Try to extract JSON from response that might have extra text
                    try:
                        json_match = re.search(r"\{.*\}", content, re.DOTALL)
                        if json_match:
                            json_str = json_match.group()
                            return json.loads(json_str)
                    except (json.JSONDecodeError, AttributeError):
                        pass
                    log.warning("Failed to parse LLM response as JSON")
                    return None
            else:
                log.warning("No content in LLM response")
                return None

        except (
            requests.RequestException,
            json.JSONDecodeError,
            KeyError,
            ValueError,
        ) as e:
            log.warning("LLM API request failed: %s", e)
            return None

    def analyze_readme_quality(self, readme_content: str) -> Dict[str, Any]:
        """Analyze README content for quality indicators."""
        cache_key = self._get_cache_key(readme_content, "readme_quality")
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = """
        Analyze this README content and provide a JSON response with the following structure:
        {
            "installation_quality": 0.0-1.0,
            "documentation_completeness": 0.0-1.0,
            "example_quality": 0.0-1.0,
            "overall_readability": 0.0-1.0,
            "technical_depth": 0.0-1.0,
            "reasoning": "Brief explanation of the scores"
        }
        
        Score based on:
        - Installation instructions clarity and completeness
        - Documentation structure and organization
        - Quality and relevance of examples
        - Overall readability and accessibility
        - Technical depth and accuracy
        """

        result = self._call_api(prompt, readme_content)
        if result is None:
            # Fallback to basic analysis
            result = self._basic_readme_analysis(readme_content)

        self.cache[cache_key] = result
        return result

    def analyze_code_quality_indicators(self, readme_content: str) -> Dict[str, Any]:
        """Analyze README for code quality indicators."""
        cache_key = self._get_cache_key(readme_content, "code_quality")
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = """
        Analyze this README content for code quality indicators and provide a JSON response:
        {
            "testing_framework": 0.0-1.0,
            "ci_cd_mentions": 0.0-1.0,
            "linting_tools": 0.0-1.0,
            "documentation_quality": 0.0-1.0,
            "code_organization": 0.0-1.0,
            "reasoning": "Brief explanation of the scores"
        }
        
        Look for mentions of:
        - Testing frameworks (pytest, unittest, etc.)
        - CI/CD pipelines (GitHub Actions, Travis CI, etc.)
        - Linting tools (black, flake8, mypy, etc.)
        - Code documentation standards
        - Project organization and structure
        """

        result = self._call_api(prompt, readme_content)
        if result is None:
            # Fallback to keyword-based analysis
            result = self._basic_code_quality_analysis(readme_content)

        self.cache[cache_key] = result
        return result

    def analyze_dataset_quality(self, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dataset information for quality indicators."""
        dataset_text = json.dumps(dataset_info, indent=2)
        cache_key = self._get_cache_key(dataset_text, "dataset_quality")
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = """
        Analyze this dataset information and provide a JSON response:
        {
            "documentation_completeness": 0.0-1.0,
            "usage_examples": 0.0-1.0,
            "metadata_quality": 0.0-1.0,
            "data_description": 0.0-1.0,
            "overall_quality": 0.0-1.0,
            "reasoning": "Brief explanation of the scores"
        }
        
        Evaluate:
        - Completeness of dataset documentation
        - Quality and clarity of usage examples
        - Richness and accuracy of metadata
        - Description of data structure and content
        - Overall dataset quality indicators
        """

        result = self._call_api(prompt, dataset_text)
        if result is None:
            # Fallback to basic analysis
            result = self._basic_dataset_analysis(dataset_info)

        self.cache[cache_key] = result
        return result

    def _basic_readme_analysis(self, readme_content: str) -> Dict[str, Any]:
        """Fallback basic README analysis."""
        content_lower = readme_content.lower()

        # Simple keyword-based scoring
        installation_score = 0.5
        if any(word in content_lower for word in ["install", "setup", "requirements"]):
            installation_score = 0.8
        if any(
            word in content_lower
            for word in ["pip install", "conda install", "npm install"]
        ):
            installation_score = 1.0

        documentation_score = 0.5
        if len(readme_content) > 500:
            documentation_score = 0.8
        if len(readme_content) > 1000:
            documentation_score = 1.0

        return {
            "installation_quality": installation_score,
            "documentation_completeness": documentation_score,
            "example_quality": 0.5,
            "overall_readability": documentation_score,
            "technical_depth": 0.5,
            "reasoning": "Basic keyword-based analysis (LLM unavailable)",
        }

    def _basic_code_quality_analysis(self, readme_content: str) -> Dict[str, Any]:
        """Fallback basic code quality analysis."""
        content_lower = readme_content.lower()

        testing_score = 0.0
        if any(word in content_lower for word in ["pytest", "unittest", "test"]):
            testing_score = 0.8

        ci_score = 0.0
        if any(word in content_lower for word in ["github actions", "travis", "ci"]):
            ci_score = 0.8

        linting_score = 0.0
        if any(word in content_lower for word in ["black", "flake8", "mypy", "lint"]):
            linting_score = 0.8

        return {
            "testing_framework": testing_score,
            "ci_cd_mentions": ci_score,
            "linting_tools": linting_score,
            "documentation_quality": 0.5,
            "code_organization": 0.5,
            "reasoning": "Basic keyword-based analysis (LLM unavailable)",
        }

    def _basic_dataset_analysis(self, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback basic dataset analysis."""
        description = dataset_info.get("description", "")
        tags = dataset_info.get("tags", [])

        doc_score = 0.5
        if len(description) > 100:
            doc_score = 0.8
        if len(description) > 500:
            doc_score = 1.0

        metadata_score = 0.5
        if len(tags) > 3:
            metadata_score = 0.8
        if len(tags) > 5:
            metadata_score = 1.0

        return {
            "documentation_completeness": doc_score,
            "usage_examples": 0.5,
            "metadata_quality": metadata_score,
            "data_description": doc_score,
            "overall_quality": (doc_score + metadata_score) / 2,
            "reasoning": "Basic analysis (LLM unavailable)",
        }


class LLMServiceSingleton:
    """Singleton class for LLM service instance."""

    _instance: Optional[LLMService] = None

    @classmethod
    def get_instance(cls) -> LLMService:
        """Get the singleton LLM service instance."""
        if cls._instance is None:
            cls._instance = LLMService()
        return cls._instance


def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    return LLMServiceSingleton.get_instance()
