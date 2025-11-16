# src/services/rating_service.py
import sys
import os
from typing import Dict, Optional

# Add Phase 1 source to path
phase1_src = os.path.join(os.path.dirname(__file__), '../../../src')
if phase1_src not in sys.path:
    sys.path.insert(0, phase1_src)

try:
    from ai_model_catalog.score_model import score_model
    from ai_model_catalog.fetch_repo import fetch_repo_data, fetch_hf_model
    PHASE1_AVAILABLE = True
except ImportError:
    PHASE1_AVAILABLE = False

class RatingService:
    """Service for calculating package ratings"""
    
    def calculate_rating(self, repository_url: Optional[str] = None, 
                        huggingface_url: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate comprehensive rating for a package
        Returns scores for: rating, reproducibility, reviewedness, tree_score
        """
        scores = {
            "rating_score": 0.0,
            "reproducibility_score": 0.0,
            "reviewedness_score": 0.0,
            "tree_score": 0.0
        }
        
        if not PHASE1_AVAILABLE:
            # Fallback if Phase 1 code not available
            return scores
        
        try:
            # Fetch data from source
            if repository_url:
                data = self._fetch_from_github(repository_url)
            elif huggingface_url:
                data = self._fetch_from_huggingface(huggingface_url)
            else:
                return scores
            
            if not data:
                return scores
            
            # Calculate Phase 1 metrics
            phase1_scores = score_model(data)
            
            # Base rating from Phase 1 NetScore
            base_score = phase1_scores.get("net_score", 0.0)
            
            # Calculate reproducibility score
            # Based on: code availability, dataset availability, documentation
            reproducibility = self._calculate_reproducibility(data, phase1_scores)
            
            # Calculate reviewedness score
            # Based on: number of reviews, PR activity, issue engagement
            reviewedness = self._calculate_reviewedness(data)
            
            # Calculate tree score (dependency health)
            # Based on: dependency freshness, known vulnerabilities
            tree_score = self._calculate_tree_score(data)
            
            # Combined rating
            rating = (base_score * 0.4 + reproducibility * 0.2 + 
                     reviewedness * 0.2 + tree_score * 0.2)
            
            scores["rating_score"] = round(rating, 3)
            scores["reproducibility_score"] = round(reproducibility, 3)
            scores["reviewedness_score"] = round(reviewedness, 3)
            scores["tree_score"] = round(tree_score, 3)
            
            return scores
            
        except Exception:
            return scores
    
    def _fetch_from_github(self, url: str) -> Optional[Dict]:
        """Fetch repository data from GitHub"""
        try:
            # Parse owner/repo from URL
            parts = url.rstrip('/').split('/')
            if len(parts) >= 2:
                owner = parts[-2]
                repo = parts[-1]
                return fetch_repo_data(owner, repo)
        except Exception:
            pass
        return None
    
    def _fetch_from_huggingface(self, url: str) -> Optional[Dict]:
        """Fetch model data from HuggingFace"""
        try:
            # Extract model_id from URL
            # e.g., https://huggingface.co/bert-base-uncased -> bert-base-uncased
            parts = url.rstrip('/').split('/')
            if 'huggingface.co' in url:
                model_id = '/'.join(parts[-2:]) if len(parts) >= 2 else parts[-1]
                return fetch_hf_model(model_id)
        except Exception:
            pass
        return None
    
    def _calculate_reproducibility(self, data: Dict, scores: Dict) -> float:
        """Calculate reproducibility score"""
        # Factors: code availability, dataset availability, documentation quality
        code_available = scores.get("availability", 0.0)
        dataset_quality = scores.get("dataset_quality", 0.0)
        ramp_up = scores.get("ramp_up_time", 0.0)  # Documentation quality proxy
        
        # Weighted average
        reproducibility = (code_available * 0.4 + dataset_quality * 0.3 + ramp_up * 0.3)
        return min(1.0, max(0.0, reproducibility))
    
    def _calculate_reviewedness(self, data: Dict) -> float:
        """Calculate reviewedness score based on community engagement"""
        # Use GitHub metrics as proxies
        stars = data.get("stars", 0)
        forks = data.get("forks", 0)
        issues = data.get("open_issues", 0)
        
        # Normalize and combine
        star_score = min(1.0, stars / 1000) * 0.4
        fork_score = min(1.0, forks / 100) * 0.3
        issue_score = min(1.0, issues / 50) * 0.3
        
        return min(1.0, star_score + fork_score + issue_score)
    
    def _calculate_tree_score(self, data: Dict) -> float:
        """Calculate dependency tree health score"""
        # Simplified: use code quality as a proxy for dependency management
        code_quality = data.get("code_quality", 0.0)
        
        # In a full implementation, this would analyze:
        # - Dependency versions
        # - Known vulnerabilities
        # - Update frequency
        # - Compatibility
        
        return code_quality
    
    def meets_quality_threshold(self, scores: Dict, threshold: float = 0.5) -> bool:
        """Check if package meets quality threshold for ingestion"""
        rating = scores.get("rating_score", 0.0)
        return rating >= threshold
