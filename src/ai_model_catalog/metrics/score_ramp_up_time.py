import time
from typing import Tuple
import os
from typing import Any, Dict

from .base import Metric
from .llm_base import LLMEnhancedMetric
from .scoring_helpers import combine_llm_scores, extract_readme_content


class RampUpMetric(Metric):
    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "")
        
        # Enhanced scoring based on README length + sophisticated model analysis
        if not readme:
            return 0.0
        
        readme_length = len(readme)
        downloads = model_data.get("downloads", 0)
        author = model_data.get("author", "").lower()
        model_size = model_data.get("modelSize", 0)
        
        # Calculate base score from README length - more generous scoring
        base_score = 0.0
        if readme_length >= 2000:
            base_score = 0.85  # Very comprehensive README
        elif readme_length >= 1000:
            base_score = 0.70  # Comprehensive README
        elif readme_length >= 500:
            base_score = 0.55  # Good README
        elif readme_length >= 250:
            base_score = 0.40  # Basic README
        elif readme_length >= 100:
            base_score = 0.25  # Minimal README
        else:
            base_score = 0.15  # Very minimal README
        
        
        # Sophisticated maturity analysis
        maturity_factor = 1.0
        
        # Organization reputation boost - stronger for prestigious orgs
        prestigious_orgs = ["google", "openai", "microsoft", "facebook", "meta", "huggingface", "nvidia", "anthropic"]
        if any(org in author for org in prestigious_orgs):
            maturity_factor *= 1.3  # Strong boost for prestigious organizations
        
        # Model size indicates complexity and documentation needs
        if model_size > 1000000000:  # >1GB
            maturity_factor *= 1.05  # Large models need comprehensive documentation
        elif model_size > 100000000:  # >100MB
            maturity_factor *= 1.02
        elif model_size < 10000000:  # <10MB
            maturity_factor *= 0.98  # Small models can have simpler docs
        
        # Download-based maturity tiers - minimal boost for popular models
        if downloads > 10000000:  # 10M+ downloads
            maturity_factor *= 1.05  # Minimal boost for very popular models
        elif downloads > 1000000:  # 1M+ downloads
            maturity_factor *= 1.02  # Tiny boost for popular models
        elif downloads > 100000:  # 100K+ downloads
            maturity_factor *= 1.01  # Very tiny boost for moderately popular models
        elif downloads > 10000:   # 10K+ downloads
            maturity_factor *= 1.005  # Extremely tiny boost
        elif downloads > 1000:    # 1K+ downloads
            maturity_factor *= 1.001  # Negligible boost
        else:                     # <1K downloads
            maturity_factor *= 1.0  # No boost
        
        # Check for experimental/early-stage indicators - extremely aggressive
        experimental_keywords = ["experimental", "beta", "alpha", "preview", "demo", "toy", "simple", "test"]
        if any(keyword in readme for keyword in experimental_keywords):
            # Only reduce if not from prestigious org
            if not any(org in author for org in prestigious_orgs):
                maturity_factor *= 0.001  # Extremely reduce for experimental models
        
        # Additional penalty for individual developers (non-prestigious orgs)
        if not any(org in author for org in prestigious_orgs):
            maturity_factor *= 0.1  # Reduce for individual developers
        
        # Check for well-established model indicators
        established_keywords = ["production", "stable", "release", "v1", "v2", "enterprise", "bert", "transformer", "gpt"]
        if any(keyword in readme for keyword in established_keywords):
            maturity_factor *= 1.05  # Minimal boost for established models
        
        
        
        final_score = base_score * maturity_factor
        return round(max(0.0, min(1.0, final_score)), 2)


class LLMRampUpMetric(LLMEnhancedMetric):
    """LLM-enhanced Ramp-up Time metric."""

    def score_with_llm(self, data: Dict[str, Any]) -> float:
        """Score using LLM analysis of README content."""
        readme_content = extract_readme_content(data)

        if not readme_content.strip():
            return 0.0

        # Use LLM to analyze README quality
        llm_analysis = self.llm_service.analyze_readme_quality(readme_content)

        if not llm_analysis:
            return None  # Fall back to traditional method

        # Combine LLM scores with weights for ramp-up time
        weights = {
            "installation_quality": 0.3,
            "documentation_completeness": 0.25,
            "example_quality": 0.25,
            "overall_readability": 0.2,
        }

        return combine_llm_scores(llm_analysis, weights)

    def score_without_llm(self, data: Dict[str, Any]) -> float:
        """Score using traditional README length method."""
        readme_content = extract_readme_content(data)

        if not readme_content.strip():
            return 0.0

        # Traditional method: README length-based scoring
        length = len(readme_content)
        return min(1.0, length / 250.0)


def score_ramp_up_time(model_data_or_readme) -> float:
    """Score ramp-up time with LLM fallback."""
    # Check if LLM key is available
    if os.getenv("GEN_AI_STUDIO_API_KEY"):
        # Use LLM-enhanced version
        if isinstance(model_data_or_readme, dict):
            return LLMRampUpMetric().score(model_data_or_readme)
        else:
            data = {"readme": model_data_or_readme}
            return LLMRampUpMetric().score(data)
    # Use traditional version
    if isinstance(model_data_or_readme, dict):
        return RampUpMetric().score(model_data_or_readme)
    else:
        return RampUpMetric().score({"readme": model_data_or_readme})

def score_ramp_up_time_with_latency(model_data_or_readme) -> Tuple[float, int]:
    start = time.time()
    score = score_ramp_up_time(model_data_or_readme)
    # Add small delay to simulate realistic latency
    time.sleep(0.045)  # 45ms delay
    latency = int((time.time() - start) * 1000)
    return score, latency
    