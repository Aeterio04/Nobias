import pandas as pd
from pathlib import Path
from typing import Union, Tuple, Dict, Any, List


def load_and_validate(
    data: Union[str, Path, pd.DataFrame],
    protected_attributes: List[str],
    target_column: str,
    positive_value: Any
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load data from file or DataFrame and validate structure.
    
    Args:
        data: File path or DataFrame
        protected_attributes: List of protected column names
        target_column: Name of target column
        positive_value: Value representing positive class
        
    Returns:
        Tuple of (validated DataFrame, metadata dict)
        
    Raises:
        ValueError: If validation fails
    """
    logs = []
    
    # Load data
    if isinstance(data, pd.DataFrame):
        df = data.copy()
        dataset_name = "DataFrame"
    else:
        path = Path(data)
        if not path.exists():
            raise ValueError(f"File not found: {data}")
        
        dataset_name = path.name
        
        if path.suffix.lower() == '.csv':
            df = pd.read_csv(path)
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(path)
        elif path.suffix.lower() == '.parquet':
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    logs.append(f"Loaded dataset: {dataset_name} with {len(df)} rows, {len(df.columns)} columns")
    
    # Validate protected attributes
    for attr in protected_attributes:
        if attr not in df.columns:
            raise ValueError(f"Protected attribute '{attr}' not found in dataset columns")
        
        n_unique = df[attr].nunique()
        if n_unique < 2:
            raise ValueError(f"Protected attribute '{attr}' has only {n_unique} unique value(s). Need at least 2.")
        
        logs.append(f"Protected attribute '{attr}': {n_unique} unique values")
    
    # Validate target column
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset columns")
    
    # Binarize target
    df['_target_binary'] = (df[target_column] == positive_value).astype(int)
    
    if df['_target_binary'].nunique() != 2:
        raise ValueError(
            f"Target column could not be binarized. "
            f"Found {df['_target_binary'].nunique()} unique values after binarization. "
            f"Expected 2 (0 and 1)."
        )
    
    logs.append(f"Target column '{target_column}' binarized: {df['_target_binary'].sum()} positive samples")
    
    # Detect column types
    column_types = {}
    for col in df.columns:
        if col == '_target_binary':
            continue
        
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].nunique() <= 10:
                column_types[col] = 'categorical'
            else:
                column_types[col] = 'numeric'
        else:
            column_types[col] = 'categorical'
    
    metadata = {
        'dataset_name': dataset_name,
        'row_count': len(df),
        'column_count': len(df.columns) - 1,  # Exclude _target_binary
        'column_types': column_types,
        'logs': logs
    }
    
    return df, metadata


def suggest_protected_columns(df: pd.DataFrame, max_unique: int = 10) -> List[str]:
    """
    Suggest columns that might be protected attributes.
    
    Args:
        df: Input DataFrame
        max_unique: Maximum unique values for a column to be suggested
        
    Returns:
        List of suggested column names
    """
    suggestions = []
    
    for col in df.columns:
        n_unique = df[col].nunique()
        if 2 <= n_unique <= max_unique:
            suggestions.append(col)
    
    return suggestions
