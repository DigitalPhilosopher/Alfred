import dotenv
import os
from pathlib import Path
from agent.logger_config import logger
import subprocess

dotenv.load_dotenv()

def open_project(project_name: str):
    """
    Open a project in Visual Studio Code.

    This function loads the environment variable 'PROJECTS' to determine
    the directory where projects are stored. It then opens the specified
    project directory in VS Code.

    Args:
        project_name: Name of the project directory to open

    Returns:
        str: Success message if project opened successfully

    Raises:
        ValueError: If PROJECTS env var not set
        FileNotFoundError: If project directory doesn't exist
    """
    logger.info(f"Attempting to open project: '{project_name}'")
    
    project_dir = os.getenv("PROJECTS")
    logger.info(f"Retrieved PROJECTS env var: {project_dir}")
    
    if not project_dir:
        logger.error("PROJECTS environment variable is not set")
        raise ValueError("PROJECTS environment variable is not set")
    project_dir = os.path.expanduser(project_dir)
    
    # Use fuzzy matching to find best matching project directory
    from difflib import SequenceMatcher

    def similarity_score(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    # Get all project directories
    logger.info(f"Scanning directory: {project_dir}")
    project_dirs = [
        d for d in os.listdir(project_dir)
        if os.path.isdir(os.path.join(project_dir, d))
    ]
    logger.info(f"Found {len(project_dirs)} potential project directories")
    
    if not project_dirs:
        logger.error(f"No projects found in {project_dir}")
        raise FileNotFoundError(f"No projects found in {project_dir}")
        
    # Find best match using fuzzy string matching
    logger.info("Starting fuzzy matching process")
    matches = [(d, similarity_score(project_name, d)) for d in project_dirs]
    best_match = max(matches, key=lambda x: x[1])
    logger.info(f"Best match: '{best_match[0]}' with similarity score: {best_match[1]:.2f}")
    
    # Require minimum similarity threshold of 0.3
    if best_match[1] < 0.3:
        logger.error(f"No projects found similar to '{project_name}' (best match: '{best_match[0]}' with score {best_match[1]:.2f})")
        raise FileNotFoundError(f"No projects found similar to '{project_name}'")
        
    project_name = best_match[0]
    
    # Build full path to project
    project_path = os.path.join(project_dir, project_name)
    logger.info(f"Full project path: {project_path}")
    
    # Open VS Code in new process
    logger.info(f"Launching VS Code for project: {project_name}")
    try:
        subprocess.Popen(['code', project_path], shell=True)
        logger.info(f"Successfully launched VS Code for project: {project_name}")
    except Exception as e:
        logger.error(f"Failed to launch VS Code: {str(e)}")
        raise
    
    return f"Opened project '{project_name}' in VS Code"
