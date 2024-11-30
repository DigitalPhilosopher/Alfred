# Projects AI Agent Functions

This directory contains utility functions used by the Projects AI Agent to manage and interact with development projects.

## Functions

### `list_all_projects()`
Located in `list.py`, this function:
- Retrieves a list of all project directories from the configured projects folder
- Returns a formatted string listing all project directories
- Requires the `PROJECTS` environment variable to be set with the path to your projects directory

### `open_project(project_name: str)`
Located in `open.py`, this function:
- Opens a specified project in Visual Studio Code
- Uses fuzzy matching to find the best matching project directory
- Requires:
  - The `PROJECTS` environment variable to be set
  - Visual Studio Code (`code` command) to be available in the system path
- Includes built-in logging for debugging and tracking

## Environment Setup

These functions require:
1. A `PROJECTS` environment variable pointing to your projects root directory
2. Visual Studio Code installed and accessible via the `code` command
3. Python packages: `python-dotenv`, `pathlib`

## Usage Example

```python
from agent.functions import list_all_projects
from agent.functions import open_project
```

## List all available projects
```python
projects = list_all_projects()
print(projects)
```

## Open a specific project in VS Code
```python
result = open_project("my-project")
print(result)  # "Opened project 'my-project' in VS Code"
```

## Error Handling

The functions include robust error handling for common scenarios:
- Missing environment variables
- Non-existent directories
- Project name mismatches (with fuzzy matching fallback)
- VS Code launching failures