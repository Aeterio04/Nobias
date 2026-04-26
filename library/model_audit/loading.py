"""
Model and dataset loading utilities.
"""
import pickle
import joblib
from pathlib import Path
from typing import Any, Union, Tuple
import pandas as pd
import numpy as np
from .models import ModelType


class ModelLoadError(Exception):
    """Raised when model loading fails."""
    pass


class DataLoadError(Exception):
    """Raised when data loading fails."""
    pass


def load_model(model: Union[str, Path, Any]) -> Tuple[Any, str]:
    """
    Load a model from file or accept a model object directly.
    
    Args:
        model: Path to serialized model (.pkl, .joblib) or model object
        
    Returns:
        Tuple of (model_object, model_name)
        
    Raises:
        ModelLoadError: If model cannot be loaded
    """
    if isinstance(model, (str, Path)):
        model_path = Path(model)
        
        if not model_path.exists():
            raise ModelLoadError(f"Model file not found: {model_path}")
        
        # Try different loading methods based on extension
        try:
            if model_path.suffix == '.pkl':
                # Try joblib first (more robust), then pickle
                try:
                    model_obj = joblib.load(model_path)
                except Exception:
                    with open(model_path, 'rb') as f:
                        model_obj = pickle.load(f)
            elif model_path.suffix == '.joblib':
                model_obj = joblib.load(model_path)
            else:
                # Try joblib first, then pickle
                try:
                    model_obj = joblib.load(model_path)
                except Exception:
                    with open(model_path, 'rb') as f:
                        model_obj = pickle.load(f)
            
            model_name = model_path.stem
            return model_obj, model_name
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load model from {model_path}: {e}")
    else:
        # Model object passed directly
        model_name = model.__class__.__name__
        return model, model_name


def detect_model_type(model: Any, y_test: np.ndarray) -> ModelType:
    """
    Detect whether model is binary classifier, multiclass classifier, or regressor.
    
    Args:
        model: The model object
        y_test: Test labels to help determine type
        
    Returns:
        ModelType enum value
    """
    # Check if model has predict_proba (classifier indicator)
    has_predict_proba = hasattr(model, 'predict_proba') and callable(model.predict_proba)
    
    # Check if model has classes_ attribute
    has_classes = hasattr(model, 'classes_')
    
    if has_predict_proba or has_classes:
        # It's a classifier
        if has_classes:
            n_classes = len(model.classes_)
        else:
            # Infer from target
            n_classes = len(np.unique(y_test))
        
        if n_classes == 2:
            return ModelType.CLASSIFIER_BINARY
        else:
            return ModelType.CLASSIFIER_MULTICLASS
    else:
        # Assume regressor
        return ModelType.REGRESSOR


def load_test_data(
    test_data: Union[str, Path, pd.DataFrame],
    target_column: str,
    protected_attributes: list[str]
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Load test dataset and validate required columns.
    
    Args:
        test_data: Path to CSV or DataFrame
        target_column: Name of target/label column
        protected_attributes: List of protected attribute column names
        
    Returns:
        Tuple of (features_df, target_series)
        
    Raises:
        DataLoadError: If data cannot be loaded or validated
    """
    # Load data
    if isinstance(test_data, (str, Path)):
        test_path = Path(test_data)
        if not test_path.exists():
            raise DataLoadError(f"Test data file not found: {test_path}")
        
        try:
            df = pd.read_csv(test_path)
        except Exception as e:
            raise DataLoadError(f"Failed to load CSV from {test_path}: {e}")
    elif isinstance(test_data, pd.DataFrame):
        df = test_data.copy()
    else:
        raise DataLoadError(f"Unsupported test_data type: {type(test_data)}")
    
    # Validate required columns
    missing_cols = []
    
    if target_column not in df.columns:
        missing_cols.append(target_column)
    
    for attr in protected_attributes:
        if attr not in df.columns:
            missing_cols.append(attr)
    
    if missing_cols:
        raise DataLoadError(
            f"Missing required columns in test data: {missing_cols}\n"
            f"Available columns: {list(df.columns)}"
        )
    
    # Separate features and target
    y = df[target_column]
    X = df.drop(columns=[target_column])
    
    return X, y


def validate_model_data_alignment(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    protected_attributes: list[str]
) -> pd.DataFrame:
    """
    Validate that model can make predictions on test data.
    
    If model was trained without protected attributes, they will be excluded
    from predictions but kept in the DataFrame for fairness analysis.
    
    Args:
        model: The model object
        X_test: Test features (may include protected attributes)
        y_test: Test labels
        protected_attributes: List of protected attribute names
        
    Returns:
        X_test with only the features the model expects (for predictions)
        
    Raises:
        ModelLoadError: If model cannot predict on test data
    """
    if not hasattr(model, 'predict') or not callable(model.predict):
        raise ModelLoadError(
            f"Model {type(model).__name__} does not have a predict() method"
        )
    
    # Get features model was trained on
    if hasattr(model, 'feature_names_in_'):
        model_features = list(model.feature_names_in_)
    elif hasattr(model, 'n_features_in_'):
        # Model doesn't have feature names, use first n columns
        model_features = list(X_test.columns[:model.n_features_in_])
    else:
        # Try with all features first
        model_features = list(X_test.columns)
    
    # Try prediction with model's expected features
    try:
        X_for_model = X_test[model_features]
        sample = X_for_model.iloc[:1]
        _ = model.predict(sample)
        return X_for_model
    except Exception as e:
        # If that fails, try excluding protected attributes
        features_without_protected = [
            col for col in X_test.columns 
            if col not in protected_attributes
        ]
        
        try:
            X_for_model = X_test[features_without_protected]
            sample = X_for_model.iloc[:1]
            _ = model.predict(sample)
            return X_for_model
        except Exception as e2:
            raise ModelLoadError(
                f"Model cannot make predictions on test data: {e}\n"
                f"Tried with protected attributes excluded: {e2}\n"
                f"Model may have been trained on different features."
            )


def extract_feature_names(model: Any, X_test: pd.DataFrame) -> list[str]:
    """
    Extract feature names from model or dataset.
    
    Args:
        model: The model object
        X_test: Test features DataFrame
        
    Returns:
        List of feature names
    """
    # Try to get from model first
    if hasattr(model, 'feature_names_in_'):
        return list(model.feature_names_in_)
    
    # Fall back to DataFrame columns
    if isinstance(X_test, pd.DataFrame):
        return list(X_test.columns)
    
    # Last resort: generate generic names
    n_features = X_test.shape[1] if hasattr(X_test, 'shape') else len(X_test[0])
    return [f"feature_{i}" for i in range(n_features)]


def prepare_model_and_data(
    model: Union[str, Path, Any],
    test_data: Union[str, Path, pd.DataFrame],
    target_column: str,
    protected_attributes: list[str]
) -> Tuple[Any, str, pd.DataFrame, pd.Series, ModelType, list[str], pd.DataFrame]:
    """
    Complete pipeline to load and validate model and data.
    
    Args:
        model: Path to model or model object
        test_data: Path to test data or DataFrame
        target_column: Target column name
        protected_attributes: Protected attribute column names
        
    Returns:
        Tuple of (model, model_name, X_test_full, y_test, model_type, feature_names, X_for_model)
        - X_test_full: Full test data including protected attributes
        - X_for_model: Test data with only features model expects
    """
    # Load model
    model_obj, model_name = load_model(model)
    
    # Load data
    X_test, y_test = load_test_data(test_data, target_column, protected_attributes)
    
    # Validate alignment and get features for model
    X_for_model = validate_model_data_alignment(model_obj, X_test, y_test, protected_attributes)
    
    # Detect model type
    model_type = detect_model_type(model_obj, y_test.values)
    
    # Extract feature names (from what model uses)
    feature_names = extract_feature_names(model_obj, X_for_model)
    
    return model_obj, model_name, X_test, y_test, model_type, feature_names, X_for_model
