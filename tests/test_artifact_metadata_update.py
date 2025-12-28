"""Test that artifact metadata gets automatically updated when loaded with a different model."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.common.classifier import ComplaintClassifier
from src.common.paths import get_classifier_artifact_path
from src.serving.service import _load_classifier


def test_artifact_metadata_updates_on_load():
    """Test that loading an artifact with a different model updates the metadata."""
    
    # Create a temporary copy of an artifact to test with
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy ae-pc artifact to temp location
        source_path = get_classifier_artifact_path("ae-pc")
        test_path = Path(tmpdir) / "test_artifact.json"
        shutil.copy(source_path, test_path)
        
        # Read original metadata
        with open(test_path) as f:
            original_data = json.load(f)
        original_model = original_data.get("metadata", {}).get("model")
        
        # Mock dspy.settings.lm to simulate a different model being configured
        new_model = "openai/test-model-v2"
        mock_lm = Mock()
        mock_lm.model = new_model
        
        with patch("src.serving.service.dspy.settings") as mock_settings:
            mock_settings.lm = mock_lm
            
            # Load the classifier (this should trigger metadata update)
            classifier = _load_classifier(test_path, "ae-pc")
            
            # Verify classifier was loaded
            assert isinstance(classifier, ComplaintClassifier)
            assert classifier.classification_type == "ae-pc"
        
        # Read updated metadata
        with open(test_path) as f:
            updated_data = json.load(f)
        updated_model = updated_data.get("metadata", {}).get("model")
        
        # Verify the model was updated
        assert updated_model == new_model, f"Expected model to be updated to {new_model}, but got {updated_model}"
        assert updated_model != original_model, "Model should have changed"
        
        # Verify other metadata is preserved
        assert updated_data.get("metadata", {}).get("classification_type") == "ae-pc"
        assert "classification_config" in updated_data.get("metadata", {})


def test_artifact_metadata_unchanged_when_model_matches():
    """Test that loading an artifact with the same model doesn't unnecessarily update."""
    
    # Create a temporary copy of an artifact to test with
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy ae-pc artifact to temp location
        source_path = get_classifier_artifact_path("ae-pc")
        test_path = Path(tmpdir) / "test_artifact.json"
        shutil.copy(source_path, test_path)
        
        # Read original metadata
        with open(test_path) as f:
            original_data = json.load(f)
        original_model = original_data.get("metadata", {}).get("model")
        
        # Mock dspy.settings.lm with the SAME model
        mock_lm = Mock()
        mock_lm.model = original_model
        
        # Get original file modification time
        original_mtime = test_path.stat().st_mtime
        
        with patch("src.serving.service.dspy.settings") as mock_settings:
            mock_settings.lm = mock_lm
            
            # Load the classifier
            classifier = _load_classifier(test_path, "ae-pc")
            
            # Verify classifier was loaded
            assert isinstance(classifier, ComplaintClassifier)
        
        # Verify file was not modified (same mtime means file wasn't written)
        # Note: This test may be flaky if the system is slow, but it's a good check
        new_mtime = test_path.stat().st_mtime
        assert new_mtime == original_mtime, "File should not be modified when model matches"
        
        # Verify metadata is unchanged
        with open(test_path) as f:
            updated_data = json.load(f)
        assert updated_data.get("metadata", {}).get("model") == original_model


def test_artifact_metadata_no_update_when_lm_not_configured():
    """Test that loading without configured LM doesn't crash or update metadata."""
    
    # Create a temporary copy of an artifact to test with
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy ae-pc artifact to temp location
        source_path = get_classifier_artifact_path("ae-pc")
        test_path = Path(tmpdir) / "test_artifact.json"
        shutil.copy(source_path, test_path)
        
        # Read original metadata
        with open(test_path) as f:
            original_data = json.load(f)
        original_model = original_data.get("metadata", {}).get("model")
        
        # Mock dspy.settings.lm as None (not configured)
        with patch("src.serving.service.dspy.settings") as mock_settings:
            mock_settings.lm = None
            
            # Load the classifier (should not crash)
            classifier = _load_classifier(test_path, "ae-pc")
            
            # Verify classifier was loaded
            assert isinstance(classifier, ComplaintClassifier)
        
        # Verify metadata is unchanged
        with open(test_path) as f:
            updated_data = json.load(f)
        assert updated_data.get("metadata", {}).get("model") == original_model


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
