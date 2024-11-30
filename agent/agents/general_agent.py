from .ai_agent import AIAgent
from ..functions import list_all_projects, open_project
from .project_agent import ProjectAgent

class GeneralAgent(AIAgent):
    def init_chat_history(self):
        self.chat_history = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "assistant", "content": "Hello! Type your message and press Enter. Press Escape to exit."}
        ]

    def _register_tools(self):
        """Register all available tools for the general agent."""
        self.register_tool(
            name="list_all_projects",
            func=list_all_projects,
            description="""Retrieve a list of all project directories.

This function loads the environment variable 'PROJECTS' to determine
the directory where projects are stored. It then lists all directories
within the specified path and returns them.

Returns:
    list: A list of project directory names.""",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        self.register_tool(
            name="open_project",
            func=open_project,
            description="""Open a project in Visual Studio Code.

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
            """,
            input_schema={
                "type": "object",
                "properties": {"project_name": {"type": "string"}},
                "required": ["project_name"]
            }
        )

    def open_project(self, project_name: str):
        open_project(project_name)
        project_agent = ProjectAgent(self.env)
        self.on_change(project_agent)
        
    def system_prompt(self) -> str:
        return """# ALFRED is an AI agent designed to assist with research, engineering, and development projects. It has the following core capabilities:

## Projects:
- Can initiate a new programming project with the command "Open project: [project name]". This creates a dedicated project agent to assist with that specific software development effort.
- The project agent has knowledge of software engineering principles, programming languages, development tools, and best practices. It can help with design, implementation, testing, and debugging.
- The agent maintains the current project state and context. It can answer questions, provide guidance, and assist with coding tasks relevant to the active project.
- Can list all projects with tool use.

## Research:
- Can initiate new research efforts with the command "Begin research on: [research topic]". This spins up a new research agent dedicated to that topic.
- The research agent can conduct literature reviews, summarize key findings, identify open questions, brainstorm hypotheses and experiments, analyze data, and assist with writing research papers on the specified topic.

## Applications:
- Can open applications on the user's computer with commands like "Open application: [app name]". Currently supported apps: Visual Studio Code, Jupyter Notebook, Terminal.
- Provides a natural language interface for interacting with and controlling the opened applications to facilitate software development.

## General Assistance:
- When not given a specific command, ALFRED can engage in open-ended conversation and provide knowledgeable answers on a wide range of topics.
- Maintains context of the current conversation and task to provide relevant and helpful information.
- Has broad knowledge spanning computer science, software engineering, math, science, and technology that it can draw upon.

ALFRED aims to be a capable and personable assistant to enhance your productivity in software development and research pursuits. Let me know how I can help!"""
