import os
import json
import requests
from typing import Dict, List, Any, Optional

from config import Config

class LLMService:
    def __init__(self):
        self.config = Config()
        self.setup_llm()
    
    def setup_llm(self):
        """Initialize LLM client"""
        if self.config.OPENROUTER_API_KEY:
            self.use_openrouter = True
            self.api_key = self.config.OPENROUTER_API_KEY
            self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        elif self.config.OPENAI_API_KEY:
            self.use_openrouter = False
            self.api_key = self.config.OPENAI_API_KEY
            self.base_url = "https://api.openai.com/v1/chat/completions"
        else:
            # For demo purposes, use mock responses
            self.use_openrouter = False
            self.api_key = None
            print("⚠️  No API key configured - using mock responses for demo")
    
    def generate_file_analysis(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis for a single file"""
        if not self.api_key:
            return self._mock_file_analysis(file_info)
        
        system_prompt = self._get_file_analysis_prompt()
        
        user_content = f"""
File: {file_info['path']}
Language: {file_info['language']}
Size: {file_info['size']} bytes
Lines: {file_info['lines']}

Content:
```{file_info['language']}
{file_info['content'][:2000]}...
```

Analysis Data:
{json.dumps(file_info.get('analysis', {}), indent=2)}
"""
        
        try:
            response = self._call_llm(system_prompt, user_content)
            
            # Parse the response as JSON
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                return {
                    "file_name": file_info['name'],
                    "description": response[:500] + "..." if len(response) > 500 else response,
                    "key_components": [],
                    "purpose": "Analysis parsing failed",
                    "dependencies": [],
                    "notes": response
                }
                
        except Exception as e:
            return self._mock_file_analysis(file_info)
    
    def generate_repository_summary(self, repo_data: Dict[str, Any], file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall repository summary"""
        if not self.api_key:
            return self._mock_repository_summary(repo_data)
        
        system_prompt = self._get_repository_summary_prompt()
        
        # Prepare repository overview
        repo_overview = {
            "name": repo_data['name'],
            "description": repo_data.get('description', ''),
            "languages": repo_data.get('languages', {}),
            "file_count": repo_data.get('file_count', 0),
            "size_mb": repo_data.get('size_mb', 0),
            "structure": repo_data.get('structure', {}),
            "dependencies": repo_data.get('dependencies', {}),
            "readme_excerpt": repo_data.get('readme', '')[:1000]
        }
        
        user_content = f"""
Repository Overview:
{json.dumps(repo_overview, indent=2)}

Please generate a comprehensive repository summary and tutorial structure.
"""
        
        try:
            response = self._call_llm(system_prompt, user_content)
            
            try:
                summary = json.loads(response)
                return summary
            except json.JSONDecodeError:
                return self._mock_repository_summary(repo_data)
                
        except Exception as e:
            return self._mock_repository_summary(repo_data)
    
    def generate_architecture_diagram(self, repo_data: Dict[str, Any]) -> str:
        """Generate Mermaid diagram for repository architecture"""
        return f"""graph TD
    A[{repo_data['name']}] --> B[Main Components]
    B --> C[Files: {repo_data.get('file_count', 0)}]
    B --> D[Languages: {', '.join(repo_data.get('languages', {}).keys())}]
    C --> E[Size: {repo_data.get('size_mb', 0)} MB]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px"""
    
    def _call_llm(self, system_prompt: str, user_content: str) -> str:
        """Call the LLM with system and user prompts"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.use_openrouter:
            headers["HTTP-Referer"] = "https://codecrackr.app"
            headers["X-Title"] = "CodeCrackr"
        
        data = {
            "model": self.config.DEFAULT_MODEL if self.use_openrouter else "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": self.config.TEMPERATURE,
            "max_tokens": self.config.MAX_TOKENS
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _mock_file_analysis(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Mock file analysis for demo purposes"""
        return {
            "file_name": file_info['name'],
            "description": f"This {file_info['language']} file contains {file_info['lines']} lines of code and appears to be a core component of the project.",
            "key_components": [
                {
                    "name": "main_function",
                    "type": "function",
                    "description": "Primary function that handles the main logic",
                    "line_number": 10
                }
            ],
            "purpose": f"Serves as a {file_info['language']} module for handling specific functionality",
            "dependencies": ["standard_library", "external_packages"],
            "complexity": "medium",
            "notes": "Well-structured code with clear separation of concerns"
        }
    
    def _mock_repository_summary(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock repository summary for demo purposes"""
        return {
            "repository_name": repo_data['name'],
            "overview": f"This is a {', '.join(repo_data.get('languages', {}).keys())} project with {repo_data.get('file_count', 0)} files. It demonstrates modern software development practices and clean architecture.",
            "architecture": {
                "description": "The project follows a modular architecture with clear separation of concerns",
                "key_patterns": ["MVC", "Repository Pattern", "Dependency Injection"],
                "data_flow": "Data flows from input validation through business logic to output formatting"
            },
            "key_features": [
                {
                    "name": "Core Functionality",
                    "description": "Main business logic implementation",
                    "files_involved": ["main.py", "core.js"]
                }
            ],
            "tutorial_sections": [
                {
                    "title": "Getting Started",
                    "description": "Introduction to the project and setup instructions",
                    "difficulty": "beginner",
                    "estimated_time": "15 minutes",
                    "key_concepts": ["setup", "configuration", "first_run"]
                },
                {
                    "title": "Core Concepts",
                    "description": "Understanding the main architectural patterns",
                    "difficulty": "intermediate",
                    "estimated_time": "30 minutes",
                    "key_concepts": ["architecture", "patterns", "design"]
                }
            ],
            "learning_path": [
                {
                    "step": 1,
                    "title": "Project Overview",
                    "description": "Understand what the project does",
                    "files_to_study": ["README.md"]
                },
                {
                    "step": 2,
                    "title": "Core Implementation",
                    "description": "Study the main implementation files",
                    "files_to_study": ["main.py", "app.js"]
                }
            ],
            "technical_stack": list(repo_data.get('languages', {}).keys()),
            "complexity_level": "intermediate",
            "prerequisites": ["Basic programming knowledge", "Understanding of the tech stack"],
            "getting_started": {
                "installation": "Clone the repository and install dependencies",
                "first_steps": "Run the setup script and follow the README",
                "common_issues": "Check the troubleshooting section for common problems"
            }
        }
    
    def _get_file_analysis_prompt(self) -> str:
        """Get system prompt for file analysis"""
        return """You are an expert software engineer and technical writer. Analyze the provided code file and generate a comprehensive analysis.

Return your response as a JSON object with the following structure:
{
    "file_name": "filename.ext",
    "description": "Clear, concise description of what this file does",
    "key_components": [
        {
            "name": "component_name",
            "type": "class|function|module|constant",
            "description": "what this component does",
            "line_number": 123
        }
    ],
    "purpose": "The main purpose/role of this file in the project",
    "dependencies": ["list", "of", "key", "dependencies"],
    "complexity": "low|medium|high",
    "notes": "Any important notes, patterns, or considerations"
}

Focus on:
1. Clear, beginner-friendly explanations
2. Key classes, functions, and their purposes
3. How this file fits into the larger project
4. Important patterns or architectural decisions
5. Dependencies and relationships

Be concise but thorough. Avoid jargon when possible."""
    
    def _get_repository_summary_prompt(self) -> str:
        """Get system prompt for repository summary"""
        return """You are an expert technical writer creating educational content. Generate a comprehensive repository summary and tutorial structure.

Return your response as a JSON object with the following structure:
{
    "repository_name": "repo_name",
    "overview": "High-level description of what this project does and its purpose",
    "architecture": {
        "description": "Explanation of the overall architecture and design patterns",
        "key_patterns": ["pattern1", "pattern2"],
        "data_flow": "How data flows through the system"
    },
    "key_features": [
        {
            "name": "Feature Name",
            "description": "What this feature does",
            "files_involved": ["file1.py", "file2.js"]
        }
    ],
    "tutorial_sections": [
        {
            "title": "Section Title",
            "description": "What this section covers",
            "difficulty": "beginner|intermediate|advanced",
            "estimated_time": "X minutes",
            "key_concepts": ["concept1", "concept2"]
        }
    ],
    "learning_path": [
        {
            "step": 1,
            "title": "Step Title",
            "description": "What to learn in this step",
            "files_to_study": ["file1.py"]
        }
    ],
    "technical_stack": ["technology1", "technology2"],
    "complexity_level": "beginner|intermediate|advanced",
    "prerequisites": ["prerequisite1", "prerequisite2"],
    "getting_started": {
        "installation": "How to install and set up",
        "first_steps": "What to do first",
        "common_issues": "Common problems and solutions"
    }
}

Focus on:
1. Educational value - make it learning-oriented
2. Clear progression from basic to advanced concepts
3. Practical insights about the codebase
4. Real-world applications and use cases
5. Best practices demonstrated in the code

Make it comprehensive but accessible to developers at different skill levels."""

    def count_tokens(self, text: str) -> int:
        """Count tokens in text (rough estimate)"""
        return len(text.split()) * 1.3
