import dotenv
import os
from pathlib import Path

dotenv.load_dotenv()

def list_all_projects():
    """
    Retrieve a list of all project directories.

    This function loads the environment variable 'PROJECTS' to determine
    the directory where projects are stored. It then lists all directories
    within the specified path and returns them.

    Returns:
        list: A list of project directory names.
    """
    project_dir = os.getenv("PROJECTS")
    
    if not project_dir:
        raise ValueError("PROJECTS environment variable is not set")
    
    # Convert to Path object for cross-platform compatibility
    project_path = Path(project_dir).expanduser().resolve()
    
    # Check if directory exists
    if not project_path.exists():
        raise FileNotFoundError(f"Directory {project_path} does not exist")
    
    # List all directories
    return [item.name for item in project_path.iterdir() if item.is_dir()]
