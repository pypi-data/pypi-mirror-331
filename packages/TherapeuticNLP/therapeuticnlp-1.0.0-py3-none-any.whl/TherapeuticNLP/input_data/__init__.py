"""
Default Input data directory for TherapeuticNLP Package.

This package contains the input data files used in the analysis of therapeutic conversations,
including raw transcripts and any other source materials needed for processing.
"""

INPUT_FORMATS = ["txt", "csv"]

def list_available_input_files():
    """
    List all available input files in the package's data directory.
    
    Returns:
        list: Names of available data files
    """
    import os
    file_dir = os.path.dirname(os.path.abspath(__file__))
    return [f for f in os.listdir(file_dir) 
            if os.path.isfile(os.path.join(file_dir, f)) and 
            not f.startswith("__") and not f.startswith("_") and not f.startswith(".")]