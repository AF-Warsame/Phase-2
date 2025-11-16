#!/usr/bin/env python3
"""
Test different timeout values to find optimal settings.
Run with: python test_timeouts.py
"""

import os
import sys
import time
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_timeout_values():
    """Test different timeout values for Hugging Face API."""
    print("⏱️  Testing different timeout values...")

    model_id = "google-bert/bert-base-uncased"
    api_url = f"https://huggingface.co/api/models/{model_id}"
    headers = {
        "User-Agent": "AI-Model-Catalog/1.0",
        "Accept": "application/json",
    }

    timeout_values = [1, 3, 5, 10, 15, 30]

    for timeout in timeout_values:
        print(f"\n  Testing timeout: {timeout}s")

        try:
            start = time.time()
            response = requests.get(api_url, headers=headers, timeout=timeout)
            actual_time = time.time() - start

            if response.status_code == 200:
                print(
                    f"    ✓ Success: {response.status_code} (took {actual_time:.2f}s)"
                )
            else:
                print(
                    f"    ✗ HTTP Error: {response.status_code} (took {actual_time:.2f}s)"
                )

        except requests.Timeout:
            actual_time = time.time() - start
            print(f"    ✗ Timeout after {actual_time:.2f}s")
        except requests.ConnectionError as e:
            actual_time = time.time() - start
            print(f"    ✗ Connection Error after {actual_time:.2f}s: {e}")
        except requests.RequestException as e:
            actual_time = time.time() - start
            print(f"    ✗ Error after {actual_time:.2f}s: {e}")


def test_with_session():
    """Test with requests session and retry strategy."""
    print("\n🔄 Testing with session and retry strategy...")

    from ai_model_catalog.fetch_repo import create_session, HF_HEADERS

    model_id = "google-bert/bert-base-uncased"
    api_url = f"https://huggingface.co/api/models/{model_id}"

    session = create_session()

    try:
        start = time.time()
        response = session.get(api_url, headers=HF_HEADERS, timeout=10)
        actual_time = time.time() - start

        if response.status_code == 200:
            print(
                f"  ✓ Session Success: {response.status_code} (took {actual_time:.2f}s)"
            )
        else:
            print(
                f"  ✗ Session HTTP Error: {response.status_code} (took {actual_time:.2f}s)"
            )

    except requests.RequestException as e:
        actual_time = time.time() - start
        print(f"  ✗ Session Error after {actual_time:.2f}s: {e}")


def test_model_scoring_timing():
    """Test the actual model scoring timing."""
    print("\n📊 Testing model scoring timing...")

    try:
        from ai_model_catalog.score_model import score_model_from_id

        model_id = "google-bert/bert-base-uncased"

        # Test multiple times to get average
        times = []
        for i in range(3):
            start = time.time()
            try:
                result = score_model_from_id(model_id)
                actual_time = time.time() - start
                times.append(actual_time)
                print(
                    f"  Run {i+1}: {actual_time:.2f}s (Net Score: {result.get('NetScore', 'N/A')})"
                )
            except (ImportError, AttributeError, KeyError, ValueError) as e:
                actual_time = time.time() - start
                times.append(actual_time)
                print(f"  Run {i+1}: {actual_time:.2f}s (Error: {e})")

        if times:
            avg_time = sum(times) / len(times)
            print(f"  Average time: {avg_time:.2f}s")

    except (ImportError, AttributeError, KeyError, ValueError) as e:
        print(f"  ✗ Model scoring test failed: {e}")


def main():
    """Run timeout tests."""
    print("🔍 Timeout Debug Test")
    print("=" * 40)

    test_timeout_values()
    test_with_session()
    test_model_scoring_timing()

    print("\n" + "=" * 40)
    print("✅ Timeout debug complete!")


if __name__ == "__main__":
    main()
