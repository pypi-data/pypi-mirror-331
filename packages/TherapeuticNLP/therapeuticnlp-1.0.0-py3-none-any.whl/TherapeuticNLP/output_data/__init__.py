"""
Default Output data directory for TherapeuticNLP Package.

This package manages the output data files generated during the analysis of
therapeutic conversations, including feature files, metrics, and results.
"""

OUTPUT_FORMATS = ["csv", "xlsx", "json"]

def get_output_path(filename):
    """
    Get the absolute path for an output file in this directory.
    
    Args:
        filename (str): Name of the output file
        
    Returns:
        str: Absolute path to the output file location
    """
    import os
    output_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(output_dir, filename)

def save_features(data, filename, format="csv"):
    """
    Save feature data to the output directory.
    
    Args:
        data: Data to save (typically a pandas DataFrame)
        filename (str): Name for the output file
        format (str): Format to save in (csv, xlsx, json)
        
    Returns:
        str: Path where the file was saved
    """
    import os
    import pandas as pd
    
    if format not in OUTPUT_FORMATS:
        raise ValueError(f"Format must be one of {OUTPUT_FORMATS}")
    
    output_path = get_output_path(filename)
    
    if format == "csv":
        data.to_csv(output_path, index=False)
    elif format == "xlsx":
        data.to_excel(output_path, index=False)
    elif format == "json":
        data.to_json(output_path, orient="records")
    
    return output_path