"""
Network debugging tests to identify connectivity issues.
Run with: python -m pytest tests/test_network_debug.py -v -s
"""

import logging
import os
import sys
import time
from typing import Any, Dict

import requests

from ai_model_catalog.fetch_repo import (
    HEADERS,
    HF_HEADERS,
    create_session,
)  # noqa: E402
from ai_model_catalog.llm_service import get_llm_service  # noqa: E402
from ai_model_catalog.score_model import (
    score_model_from_id,
)  # noqa: E402

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class NetworkDebugger:
    """Debug network connectivity and API responses."""

    def __init__(self):
        self.session = create_session()
        self.results = {}

    def test_basic_connectivity(self) -> Dict[str, Any]:
        """Test basic internet connectivity."""
        print("\n=== Testing Basic Connectivity ===")

        test_urls = [
            "https://httpbin.org/get",
            "https://api.github.com",
            "https://huggingface.co/api",
        ]

        results = {}
        for url in test_urls:
            try:
                start_time = time.time()
                response = self.session.get(url, timeout=5)
                latency = (time.time() - start_time) * 1000

                results[url] = {
                    "status": "SUCCESS",
                    "status_code": response.status_code,
                    "latency_ms": round(latency, 2),
                    "response_size": len(response.content),
                }
                print(f"✓ {url}: {response.status_code} ({latency:.0f}ms)")

            except requests.ConnectionError as e:
                results[url] = {
                    "status": "CONNECTION_ERROR",
                    "error": str(e),
                    "latency_ms": None,
                }
                print(f"✗ {url}: Connection Error - {e}")

            except requests.Timeout as e:
                results[url] = {
                    "status": "TIMEOUT",
                    "error": str(e),
                    "latency_ms": None,
                }
                print(f"✗ {url}: Timeout - {e}")

            except requests.RequestException as e:
                results[url] = {"status": "ERROR", "error": str(e), "latency_ms": None}
                print(f"✗ {url}: Error - {e}")

        # Determine overall status based on individual URL results
        success_count = sum(1 for r in results.values() if r.get("status") == "SUCCESS")
        total_count = len(results)

        if success_count == total_count:
            overall_status = "SUCCESS"
        elif success_count > 0:
            overall_status = "PARTIAL"
        else:
            overall_status = "FAILED"

        return {
            "status": overall_status,
            "details": results,
            "success_count": success_count,
            "total_count": total_count,
        }

    def test_huggingface_api(self) -> Dict[str, Any]:
        """Test Hugging Face API specifically."""
        print("\n=== Testing Hugging Face API ===")

        model_id = "google-bert/bert-base-uncased"
        api_url = f"https://huggingface.co/api/models/{model_id}"

        try:
            start_time = time.time()
            response = self.session.get(api_url, headers=HF_HEADERS, timeout=10)
            latency = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                result = {
                    "status": "SUCCESS",
                    "status_code": response.status_code,
                    "latency_ms": round(latency, 2),
                    "model_id": data.get("modelId"),
                    "author": data.get("author"),
                    "downloads": data.get("downloads"),
                    "has_readme": bool(data.get("cardData", {}).get("content")),
                    "response_size": len(response.content),
                }
                print(f"✓ HF API: {response.status_code} ({latency:.0f}ms)")
                print(f"  Model: {data.get('modelId')}")
                print(f"  Author: {data.get('author')}")
                print(f"  Downloads: {data.get('downloads'):,}")
                print(f"  Has README: {bool(data.get('cardData', {}).get('content'))}")

            else:
                result = {
                    "status": "HTTP_ERROR",
                    "status_code": response.status_code,
                    "latency_ms": round(latency, 2),
                    "error": f"HTTP {response.status_code}",
                }
                print(f"✗ HF API: HTTP {response.status_code} ({latency:.0f}ms)")

        except requests.ConnectionError as e:
            result = {"status": "CONNECTION_ERROR", "error": str(e), "latency_ms": None}
            print(f"✗ HF API: Connection Error - {e}")

        except requests.Timeout as e:
            result = {"status": "TIMEOUT", "error": str(e), "latency_ms": None}
            print(f"✗ HF API: Timeout - {e}")

        except requests.RequestException as e:
            result = {"status": "ERROR", "error": str(e), "latency_ms": None}
            print(f"✗ HF API: Error - {e}")

        return result

    def test_github_api(self) -> Dict[str, Any]:
        """Test GitHub API if token is available."""
        print("\n=== Testing GitHub API ===")

        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            return {
                "status": "SKIPPED",
                "reason": "No GITHUB_TOKEN environment variable",
            }

        # Test a simple GitHub API call
        api_url = "https://api.github.com/user"
        headers = HEADERS.copy()
        headers["Authorization"] = f"token {github_token}"

        try:
            start_time = time.time()
            response = self.session.get(api_url, headers=headers, timeout=10)
            latency = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                result = {
                    "status": "SUCCESS",
                    "status_code": response.status_code,
                    "latency_ms": round(latency, 2),
                    "user": data.get("login"),
                    "rate_limit": response.headers.get("X-RateLimit-Remaining"),
                }
                print(f"✓ GitHub API: {response.status_code} ({latency:.0f}ms)")
                print(f"  User: {data.get('login')}")
                print(
                    f"  Rate limit remaining: {response.headers.get('X-RateLimit-Remaining')}"
                )

            else:
                result = {
                    "status": "HTTP_ERROR",
                    "status_code": response.status_code,
                    "latency_ms": round(latency, 2),
                    "error": f"HTTP {response.status_code}",
                }
                print(f"✗ GitHub API: HTTP {response.status_code} ({latency:.0f}ms)")

        except requests.RequestException as e:
            result = {"status": "ERROR", "error": str(e), "latency_ms": None}
            print(f"✗ GitHub API: Error - {e}")

        return result

    def test_llm_service(self) -> Dict[str, Any]:
        """Test LLM service connectivity."""
        print("\n=== Testing LLM Service ===")

        llm_service = get_llm_service()
        api_key = os.getenv("GEN_AI_STUDIO_API_KEY")

        if not api_key:
            return {
                "status": "SKIPPED",
                "reason": "No GEN_AI_STUDIO_API_KEY environment variable",
            }

        # Test with a simple README
        test_readme = "# Test Model\n\nThis is a test model for debugging."

        try:
            start_time = time.time()
            result = llm_service.analyze_readme_quality(test_readme)
            latency = (time.time() - start_time) * 1000

            if result:
                return {
                    "status": "SUCCESS",
                    "latency_ms": round(latency, 2),
                    "has_result": True,
                    "keys": list(result.keys()) if isinstance(result, dict) else None,
                }
            return {
                "status": "NO_RESULT",
                "latency_ms": round(latency, 2),
                "reason": "LLM service returned None",
            }

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            return {"status": "ERROR", "error": str(e), "latency_ms": None}

    def test_model_scoring(self) -> Dict[str, Any]:
        """Test the actual model scoring function."""
        print("\n=== Testing Model Scoring ===")

        model_id = "google-bert/bert-base-uncased"

        try:
            start_time = time.time()
            result = score_model_from_id(model_id)
            latency = (time.time() - start_time) * 1000

            return {
                "status": "SUCCESS",
                "latency_ms": round(latency, 2),
                "net_score": result.get("NetScore"),
                "has_scores": bool(result),
                "score_keys": list(result.keys()) if result else [],
            }

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            return {"status": "ERROR", "error": str(e), "latency_ms": None}

    def test_model_scoring_with_timing(self) -> Dict[str, Any]:
        """Test the model scoring with timing function."""
        print("\n=== Testing Model Scoring with Timing ===")

        model_id = "google-bert/bert-base-uncased"

        try:
            start_time = time.time()
            result = score_model_from_id(model_id)
            latency = (time.time() - start_time) * 1000

            return {
                "status": "SUCCESS",
                "total_latency_ms": round(latency, 2),
                "net_score": result.get("net_score"),
                "net_score_latency": result.get("net_score_latency"),
                "has_timing": "latency" in str(result),
                "result_keys": list(result.keys()) if result else [],
            }

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            return {"status": "ERROR", "error": str(e), "latency_ms": None}

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all network tests."""
        print("🔍 Starting Network Debug Tests...")
        print("=" * 50)

        results = {
            "basic_connectivity": self.test_basic_connectivity(),
            "huggingface_api": self.test_huggingface_api(),
            "github_api": self.test_github_api(),
            "llm_service": self.test_llm_service(),
            "model_scoring": self.test_model_scoring(),
            "model_scoring_with_timing": self.test_model_scoring_with_timing(),
        }

        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print("=" * 50)

        for test_name, result in results.items():
            if isinstance(result, dict):
                status = result.get("status", "UNKNOWN")
                latency = result.get("latency_ms", "N/A")
                print(f"{test_name:30} | {status:15} | {latency:>8}ms")
            else:
                print(f"{test_name:30} | {result}")

        return results


def test_network_debug():
    """Main test function."""
    debugger = NetworkDebugger()
    results = debugger.run_all_tests()

    # Check for critical failures
    critical_tests = ["basic_connectivity", "huggingface_api"]
    failures = []

    for test in critical_tests:
        if test in results:
            result = results[test]
            if isinstance(result, dict) and result.get("status") not in [
                "SUCCESS",
                "SKIPPED",
            ]:
                failures.append(test)

    if failures:
        print(f"\n❌ Critical failures detected: {failures}")
        assert False, f"Critical failures: {failures}"
    print("\n✅ All critical tests passed!")


if __name__ == "__main__":
    test_network_debug()
