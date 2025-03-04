from pathlib import Path

FEATURE_FILE_NAME = 'features.yaml'

def find_feature_yaml(start_dir=None) -> str:
    """
    Searches for 'features.yaml' in the given directory and its parents.
    
    Parameters:
        start_dir (str or Path, optional): The directory to start searching from.
                                           If None, starts from the current working directory.
                                           
    Returns:
        Path: The path to 'features.yaml' if found, or None if not found.
    """
    # Start from the current working directory if no start directory is specified
    start_path = Path(start_dir) if start_dir else Path.cwd()

    # Traverse down the directory tree
    feature_file = _search_down(start_path)
    if feature_file:
        return str(feature_file)
    
    # Traverse up the directory tree
    for directory in [start_path] + list(start_path.parents):
        feature_file = directory / FEATURE_FILE_NAME
        if feature_file.exists():
            return str(feature_file)
    
    return None

def _search_down(directory: Path, depth=0, max_depth=3):

    if depth > max_depth:
        return None 
    
    feature_file = directory / FEATURE_FILE_NAME
    if feature_file.exists():
        return str(feature_file)
    
    for subdirectory in directory.iterdir():
        if subdirectory.is_dir():
            feature_file = _search_down(subdirectory, depth + 1)
            if feature_file:
                return str(feature_file)
