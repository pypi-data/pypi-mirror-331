"""Tests for model serving utils"""

import mlflow
import pytest

mlflow.set_tracking_uri('databricks')
mlflow.set_registry_uri('databricks-uc')

from databricks.model_serving.utils import get_model_specs


def test_get_latest_model_versions():
    """Test getting latest versions for all models"""

    if mlflow.get_registry_uri() != 'databricks-uc':
        pytest.skip("Skipping test_get_latest_model_versions - MLflow not configured for Unity Catalog")

    model_specs = get_model_specs()
    for model_key, model_spec in model_specs.items():
        print(f"\nChecking model {model_key}:")
        print(f"UC Schema: {model_spec.uc_schema}")
        print(f"Version: {model_spec.version}")
        assert model_spec.version is not None, f"Model {model_key} has no version"
