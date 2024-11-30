# AI Agent Functions

This directory contains the core function modules that serve as tools for AI Agents. These functions are organized into specific submodules, each handling different domains of functionality.

## Available Submodules

### Projects (`/projects`)
Functions for managing and interacting with development projects:
- `list_all_projects()`: Retrieves and displays all available projects from the configured projects directory
- `open_project(project_name)`: Opens a specified project in Visual Studio Code with fuzzy matching support

## Structure

```
functions/
├── projects/           # Project management functions
│   ├── list.py        # Project listing functionality
│   ├── open.py        # Project opening functionality
│   └── README.md      # Projects module documentation
└── README.md          # This file
```

## Usage

Functions from these modules are typically imported and used by AI Agents as tools to perform specific tasks. Example:

```python
from agent.functions import list_all_projects, open_project
```

## Adding New Modules

When adding new function modules:
1. Create a new directory for the module
2. Include a README.md explaining the module's purpose and functions
3. Implement individual functions in separate files
4. Document requirements and usage examples
