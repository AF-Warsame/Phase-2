"""Comprehensive tests for CLI module to improve coverage."""

import pytest
import json
from unittest.mock import patch, MagicMock, mock_open
import typer

from ai_model_catalog.cli import (
    safe_float,
    safe_int,
    build_ndjson_line,
    models,
    hf_model,
    hf_dataset,
    multiple_urls,
    interactive,
)


class TestSafeFloat:
    """Test the safe_float utility function."""

    def test_safe_float_valid_string(self):
        """Test safe_float with valid string input."""
        assert safe_float("3.14") == 3.14

    def test_safe_float_valid_int(self):
        """Test safe_float with valid int input."""
        assert safe_float(42) == 42.0

    def test_safe_float_valid_float(self):
        """Test safe_float with valid float input."""
        assert safe_float(3.14) == 3.14

    def test_safe_float_invalid_string(self):
        """Test safe_float with invalid string input."""
        assert safe_float("invalid") == 0.0

    def test_safe_float_none(self):
        """Test safe_float with None input."""
        assert safe_float(None) == 0.0

    def test_safe_float_empty_string(self):
        """Test safe_float with empty string input."""
        assert safe_float("") == 0.0


class TestSafeInt:
    """Test the safe_int utility function."""

    def test_safe_int_valid_string(self):
        """Test safe_int with valid string input."""
        assert safe_int("42") == 42

    def test_safe_int_valid_int(self):
        """Test safe_int with valid int input."""
        assert safe_int(42) == 42

    def test_safe_int_valid_float(self):
        """Test safe_int with valid float input."""
        assert safe_int(42.7) == 42

    def test_safe_int_invalid_string(self):
        """Test safe_int with invalid string input."""
        assert safe_int("invalid") == 0

    def test_safe_int_none(self):
        """Test safe_int with None input."""
        assert safe_int(None) == 0

    def test_safe_int_empty_string(self):
        """Test safe_int with empty string input."""
        assert safe_int("") == 0


class TestBuildNdjsonLine:
    """Test the build_ndjson_line utility function."""

    def test_build_ndjson_line_basic(self):
        """Test basic ndjson line building."""
        scores = {
            "net_score": 0.85,
            "ramp_up_time": 0.75,
            "bus_factor": 0.90,
            "size_score": {
                "raspberry_pi": 0.1,
                "jetson_nano": 0.2,
                "desktop_pc": 0.8,
                "aws_server": 0.9
            }
        }
        
        result = build_ndjson_line("test-model", "MODEL", scores)
        
        assert result["name"] == "test-model"
        assert result["category"] == "MODEL"
        assert result["net_score"] == 0.85
        assert result["ramp_up_time"] == 0.75
        assert result["bus_factor"] == 0.90
        assert result["size_score"]["raspberry_pi"] == 0.1

    def test_build_ndjson_line_with_size_key(self):
        """Test ndjson line building with custom size key."""
        scores = {
            "net_score": 0.85,
            "size": {
                "raspberry_pi": 0.1,
                "jetson_nano": 0.2
            }
        }
        
        result = build_ndjson_line("test-model", "MODEL", scores, "size")
        
        assert result["size_score"]["raspberry_pi"] == 0.1

    def test_build_ndjson_line_invalid_size_score(self):
        """Test ndjson line building with invalid size score."""
        scores = {
            "net_score": 0.85,
            "size_score": "invalid"
        }
        
        result = build_ndjson_line("test-model", "MODEL", scores)
        
        assert result["size_score"] == {}

    def test_build_ndjson_line_missing_scores(self):
        """Test ndjson line building with missing scores."""
        scores = {}
        
        result = build_ndjson_line("test-model", "MODEL", scores)
        
        assert result["name"] == "test-model"
        assert result["category"] == "MODEL"
        assert result["net_score"] == 0.0
        assert result["ramp_up_time"] == 0.0
        assert result["bus_factor"] == 0.0


class TestModelsCommand:
    """Test the models command."""

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.RepositoryHandler')
    @patch('ai_model_catalog.cli.score_repo_from_owner_and_repo')
    def test_models_ndjson_output(self, mock_score, mock_handler_class, mock_logging):
        """Test models command with ndjson output."""
        # Mock handler
        mock_handler = MagicMock()
        mock_handler.fetch_data.return_value = {"full_name": "test/repo"}
        mock_handler_class.return_value = mock_handler
        
        # Mock scoring
        mock_score.return_value = {"net_score": 0.85}
        
        # Mock typer.echo
        with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
            models("test", "repo", "ndjson")
            
            mock_logging.assert_called_once()
            mock_handler.fetch_data.assert_called_once()
            mock_score.assert_called_once_with("test", "repo")
            mock_echo.assert_called_once()
            
            # Verify JSON output
            call_args = mock_echo.call_args[0][0]
            parsed = json.loads(call_args)
            assert parsed["name"] == "test/repo"
            assert parsed["category"] == "REPOSITORY"

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.RepositoryHandler')
    def test_models_text_output(self, mock_handler_class, mock_logging):
        """Test models command with text output."""
        # Mock handler
        mock_handler = MagicMock()
        mock_handler.fetch_data.return_value = {"full_name": "test/repo"}
        mock_handler.format_data.return_value = {"formatted": "data"}
        mock_handler_class.return_value = mock_handler
        
        with patch('ai_model_catalog.cli.typer.echo'):
            models("test", "repo", "text")
            
            mock_logging.assert_called_once()
            mock_handler.fetch_data.assert_called_once()
            mock_handler.format_data.assert_called_once()
            mock_handler.display_data.assert_called_once()


class TestHfModelCommand:
    """Test the hf-model command."""

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.ModelHandler')
    @patch('ai_model_catalog.cli.score_model_from_id')
    def test_hf_model_ndjson_output(self, mock_score, mock_handler_class, mock_logging):
        """Test hf-model command with ndjson output."""
        # Mock handler
        mock_handler = MagicMock()
        mock_handler.fetch_data.return_value = {"model_id": "test-model"}
        mock_handler_class.return_value = mock_handler
        
        # Mock scoring
        mock_score.return_value = {"net_score": 0.85}
        
        # Mock typer.echo
        with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
            hf_model("test-model", "ndjson")
            
            mock_logging.assert_called_once()
            mock_handler.fetch_data.assert_called_once()
            mock_score.assert_called_once_with("test-model")
            mock_echo.assert_called_once()
            
            # Verify JSON output
            call_args = mock_echo.call_args[0][0]
            parsed = json.loads(call_args)
            assert parsed["name"] == "test-model"
            assert parsed["category"] == "MODEL"

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.ModelHandler')
    @patch('ai_model_catalog.cli.score_model_from_id')
    def test_hf_model_ndjson_error(self, mock_score, mock_handler_class, mock_logging):
        """Test hf-model command with ndjson output and scoring error."""
        # Mock handler
        mock_handler = MagicMock()
        mock_handler.fetch_data.return_value = {"model_id": "test-model"}
        mock_handler_class.return_value = mock_handler
        
        # Mock scoring to raise exception
        mock_score.side_effect = Exception("Scoring failed")
        
        # Mock typer.echo
        with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
            hf_model("test-model", "ndjson")
            
            mock_logging.assert_called_once()
            mock_handler.fetch_data.assert_called_once()
            mock_score.assert_called_once_with("test-model")
            
            # Should echo error message
            error_call = mock_echo.call_args
            assert "Error scoring model" in error_call[0][0]
            assert error_call[1]["err"] is True

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.ModelHandler')
    def test_hf_model_text_output(self, mock_handler_class, mock_logging):
        """Test hf-model command with text output."""
        # Mock handler
        mock_handler = MagicMock()
        mock_handler.fetch_data.return_value = {"model_id": "test-model"}
        mock_handler.format_data.return_value = {"formatted": "data"}
        mock_handler_class.return_value = mock_handler
        
        with patch('ai_model_catalog.cli.typer.echo'):
            hf_model("test-model", "text")
            
            mock_logging.assert_called_once()
            mock_handler.fetch_data.assert_called_once()
            mock_handler.format_data.assert_called_once()
            mock_handler.display_data.assert_called_once()


class TestHfDatasetCommand:
    """Test the hf-dataset command."""

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.fetch_dataset_data')
    @patch('ai_model_catalog.cli.score_dataset_from_id')
    def test_hf_dataset_ndjson_output(self, mock_score, mock_fetch, mock_logging):
        """Test hf-dataset command with ndjson output."""
        # Mock fetch
        mock_fetch.return_value = {"dataset_id": "test-dataset"}
        
        # Mock scoring
        mock_score.return_value = {"net_score": 0.85}
        
        # Mock typer.echo
        with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
            hf_dataset("test-dataset", "ndjson")
            
            mock_logging.assert_called_once()
            mock_fetch.assert_called_once_with("test-dataset")
            mock_score.assert_called_once_with("test-dataset")
            mock_echo.assert_called_once()
            
            # Verify JSON output
            call_args = mock_echo.call_args[0][0]
            parsed = json.loads(call_args)
            assert parsed["name"] == "test-dataset"
            assert parsed["category"] == "DATASET"

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.fetch_dataset_data')
    def test_hf_dataset_text_output(self, mock_fetch, mock_logging):
        """Test hf-dataset command with text output."""
        # Mock fetch
        mock_fetch.return_value = {
            "author": "test-author",
            "license": "MIT",
            "downloads": 1000,
            "lastModified": "2023-01-01",
            "tags": ["nlp", "text"],
            "taskCategories": ["text-classification"]
        }
        
        # Mock typer.echo
        with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
            hf_dataset("test-dataset", "text")
            
            mock_logging.assert_called_once()
            mock_fetch.assert_called_once_with("test-dataset")
            
            # Verify text output calls
            assert mock_echo.call_count >= 5  # Multiple echo calls for text output

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.fetch_dataset_data')
    def test_hf_dataset_text_output_minimal_data(self, mock_fetch, mock_logging):
        """Test hf-dataset command with text output and minimal data."""
        # Mock fetch with minimal data
        mock_fetch.return_value = {}
        
        # Mock typer.echo
        with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
            hf_dataset("test-dataset", "text")
            
            mock_logging.assert_called_once()
            mock_fetch.assert_called_once_with("test-dataset")
            
            # Verify text output calls
            assert mock_echo.call_count >= 3  # Multiple echo calls for text output


class TestMultipleUrlsCommand:
    """Test the multiple-urls command."""

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.score_model_from_id')
    def test_multiple_urls_huggingface_models(self, mock_score, mock_logging):
        """Test multiple-urls command with Hugging Face models."""
        # Mock file content
        file_content = """url1,url2,https://huggingface.co/test/model1
https://huggingface.co/test/model2
https://huggingface.co/test/model3/tree/main"""
        
        # Mock scoring
        mock_score.return_value = {"net_score": 0.85}
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data=file_content)):
            with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
                multiple_urls()
                
                mock_logging.assert_called_once()
                
                # Should process 3 models
                assert mock_score.call_count == 3
                assert mock_echo.call_count == 3

    @patch('ai_model_catalog.cli.configure_logging')
    @patch('ai_model_catalog.cli.score_model_from_id')
    def test_multiple_urls_with_errors(self, mock_score, mock_logging):
        """Test multiple-urls command with scoring errors."""
        # Mock file content
        file_content = """url1,url2,https://huggingface.co/test/model1
https://huggingface.co/test/model2"""
        
        # Mock scoring to raise exception for first model
        mock_score.side_effect = [Exception("Scoring failed"), {"net_score": 0.85}]
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data=file_content)):
            with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
                multiple_urls()
                
                mock_logging.assert_called_once()
                
                # Should process 2 models, one with error
                assert mock_score.call_count == 2
                assert mock_echo.call_count == 2  # One error message, one success

    @patch('ai_model_catalog.cli.configure_logging')
    def test_multiple_urls_empty_file(self, mock_logging):
        """Test multiple-urls command with empty file."""
        # Mock empty file content
        file_content = ""
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data=file_content)):
            with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
                multiple_urls()
                
                mock_logging.assert_called_once()
                
                # Should not process any models
                assert mock_echo.call_count == 0

    @patch('ai_model_catalog.cli.configure_logging')
    def test_multiple_urls_invalid_urls(self, mock_logging):
        """Test multiple-urls command with invalid URLs."""
        # Mock file content with invalid URLs
        file_content = """invalid-url
not-huggingface.com/model
https://huggingface.co/test/model1"""
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data=file_content)):
            with patch('ai_model_catalog.cli.score_model_from_id') as mock_score:
                with patch('ai_model_catalog.cli.typer.echo') as mock_echo:
                    multiple_urls()
                    
                    mock_logging.assert_called_once()
                    
                    # Should only process the valid Hugging Face URL
                    assert mock_score.call_count == 1
                    # May have additional echo calls for error handling or processing
                    assert mock_echo.call_count >= 1


class TestInteractiveCommand:
    """Test the interactive command."""

    @patch('ai_model_catalog.cli.interactive_main')
    def test_interactive_command(self, mock_interactive_main):
        """Test interactive command."""
        interactive()
        mock_interactive_main.assert_called_once()


class TestCliIntegration:
    """Test CLI integration scenarios."""

    def test_safe_functions_with_edge_cases(self):
        """Test safe functions with various edge cases."""
        # Test safe_float with various inputs
        assert safe_float("") == 0.0
        assert safe_float("0") == 0.0
        assert safe_float("-1.5") == -1.5
        assert safe_float("inf") == float('inf')
        
        # Test safe_int with various inputs
        assert safe_int("") == 0
        assert safe_int("0") == 0
        assert safe_int("-5") == -5
        assert safe_int("3.7") == 0  # safe_int converts "3.7" to 0 due to ValueError

    def test_build_ndjson_line_with_various_scores(self):
        """Test build_ndjson_line with various score configurations."""
        # Test with all possible score keys
        scores = {
            "net_score": 0.85,
            "net_score_latency": 100,
            "ramp_up_time": 0.75,
            "ramp_up_time_latency": 50,
            "bus_factor": 0.90,
            "bus_factor_latency": 75,
            "performance_claims": 0.80,
            "performance_claims_latency": 60,
            "license": 0.95,
            "license_latency": 25,
            "dataset_and_code_score": 0.70,
            "dataset_and_code_score_latency": 80,
            "dataset_quality": 0.65,
            "dataset_quality_latency": 90,
            "code_quality": 0.75,
            "code_quality_latency": 85,
            "size_score": {
                "raspberry_pi": 0.1,
                "jetson_nano": 0.2,
                "desktop_pc": 0.8,
                "aws_server": 0.9
            }
        }
        
        result = build_ndjson_line("comprehensive-model", "MODEL", scores)
        
        # Verify all fields are present
        assert result["name"] == "comprehensive-model"
        assert result["category"] == "MODEL"
        assert result["net_score"] == 0.85
        assert result["net_score_latency"] == 100
        assert result["ramp_up_time"] == 0.75
        assert result["ramp_up_time_latency"] == 50
        assert result["bus_factor"] == 0.90
        assert result["bus_factor_latency"] == 75
        assert result["performance_claims"] == 0.80
        assert result["performance_claims_latency"] == 60
        assert result["license"] == 0.95
        assert result["license_latency"] == 25
        assert result["dataset_and_code_score"] == 0.70
        assert result["dataset_and_code_score_latency"] == 80
        assert result["dataset_quality"] == 0.65
        assert result["dataset_quality_latency"] == 90
        assert result["code_quality"] == 0.75
        assert result["code_quality_latency"] == 85
        assert result["size_score"]["raspberry_pi"] == 0.1
        assert result["size_score"]["jetson_nano"] == 0.2
        assert result["size_score"]["desktop_pc"] == 0.8
        assert result["size_score"]["aws_server"] == 0.9
