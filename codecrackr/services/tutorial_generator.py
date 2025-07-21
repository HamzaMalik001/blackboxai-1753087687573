import json
import markdown2
from typing import Dict, List, Any
from datetime import datetime
import os

from services.llm_service import LLMService
from config import Config

class TutorialGenerator:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.config = Config()
    
    def generate_tutorial(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete tutorial from repository data"""
        tutorial = {
            'metadata': {
                'repository_name': repo_data['name'],
                'repository_url': repo_data['url'],
                'generated_at': datetime.now().isoformat(),
                'file_count': repo_data['file_count'],
                'languages': repo_data['languages'],
                'size_mb': repo_data['size_mb']
            },
            'overview': {},
            'structure': repo_data['structure'],
            'files': {},
            'architecture': {},
            'tutorial_sections': [],
            'learning_path': [],
            'dependencies': repo_data['dependencies'],
            'readme': repo_data['readme']
        }
        
        # Generate project overview
        print("Generating project overview...")
        tutorial['overview'] = self._generate_overview(repo_data)
        
        # Generate architecture overview
        print("Generating architecture overview...")
        tutorial['architecture'] = self._generate_architecture(repo_data)
        
        # Analyze individual files
        print("Analyzing files...")
        tutorial['files'] = self._analyze_files(repo_data['files'])
        
        # Generate tutorial sections
        print("Generating tutorial sections...")
        tutorial['tutorial_sections'] = self._generate_tutorial_sections(repo_data, tutorial['files'])
        
        # Generate learning path
        print("Generating learning path...")
        tutorial['learning_path'] = self._generate_learning_path(repo_data, tutorial['files'])
        
        return tutorial
    
    def _generate_overview(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project overview"""
        # Use LLM to generate comprehensive overview
        overview = self.llm_service.generate_project_summary(repo_data)
        
        # Add basic info
        overview.update({
            'name': repo_data['name'],
            'description': repo_data['description'],
            'languages': repo_data['languages'],
            'file_count': repo_data['file_count'],
            'size_mb': repo_data['size_mb']
        })
        
        return overview
    
    def _generate_architecture(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate architecture overview"""
        architecture = self.llm_service.generate_architecture_overview(repo_data)
        
        # Add structure info
        architecture['structure'] = repo_data['structure']
        architecture['dependencies'] = repo_data['dependencies']
        
        return architecture
    
    def _analyze_files(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze all files and generate tutorials"""
        file_analyses = {}
        
        for i, file_info in enumerate(files):
            print(f"Analyzing file {i+1}/{len(files)}: {file_info['path']}")
            
            try:
                analysis = self.llm_service.generate_file_analysis(file_info)
                file_analyses[file_info['path']] = {
                    'info': file_info,
                    'analysis': analysis
                }
            except Exception as e:
                file_analyses[file_info['path']] = {
                    'info': file_info,
                    'analysis': {
                        'error': str(e),
                        'summary': f"Failed to analyze file: {str(e)}"
                    }
                }
        
        return file_analyses
    
    def _generate_tutorial_sections(self, repo_data: Dict[str, Any], file_analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate structured tutorial sections"""
        sections = []
        
        # Project Introduction
        sections.append({
            'title': 'Project Introduction',
            'description': f'Understanding the {repo_data["name"]} project',
            'difficulty': 'beginner',
            'estimated_time': '15 minutes',
            'content': self._generate_introduction_section(repo_data),
            'key_concepts': ['project_overview', 'architecture', 'purpose']
        })
        
        # Setup and Installation
        sections.append({
            'title': 'Setup and Installation',
            'description': 'Getting the project running locally',
            'difficulty': 'beginner',
            'estimated_time': '20 minutes',
            'content': self._generate_setup_section(repo_data),
            'key_concepts': ['installation', 'dependencies', 'configuration']
        })
        
        # Core Components
        if file_analyses:
            sections.append({
                'title': 'Core Components',
                'description': 'Understanding the main building blocks',
                'difficulty': 'intermediate',
                'estimated_time': '30 minutes',
                'content': self._generate_components_section(file_analyses),
                'key_concepts': ['classes', 'functions', 'modules']
            })
        
        # Architecture Deep Dive
        sections.append({
            'title': 'Architecture Deep Dive',
            'description': 'Exploring the system design and patterns',
            'difficulty': 'advanced',
            'estimated_time': '45 minutes',
            'content': self._generate_architecture_section(repo_data),
            'key_concepts': ['design_patterns', 'data_flow', 'scalability']
        })
        
        # Best Practices
        sections.append({
            'title': 'Best Practices and Patterns',
            'description': 'Learning from the codebase implementation',
            'difficulty': 'intermediate',
            'estimated_time': '25 minutes',
            'content': self._generate_best_practices_section(file_analyses),
            'key_concepts': ['coding_standards', 'patterns', 'optimization']
        })
        
        return sections
    
    def _generate_learning_path(self, repo_data: Dict[str, Any], file_analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate step-by-step learning path"""
        path = []
        
        # Step 1: Overview
        path.append({
            'step': 1,
            'title': 'Project Overview',
            'description': 'Start by understanding what this project does',
            'files_to_study': ['README.md', 'package.json', 'requirements.txt'],
            'key_points': ['Project purpose', 'Technology stack', 'Main features']
        })
        
        # Step 2: Entry Points
        entry_files = [f for f in file_analyses.keys() if any(name in f.lower() for name in ['main', 'app', 'index', 'server'])]
        if entry_files:
            path.append({
                'step': 2,
                'title': 'Entry Points',
                'description': 'Find where the application starts',
                'files_to_study': entry_files[:3],
                'key_points': ['Application initialization', 'Configuration setup', 'Main workflow']
            })
        
        # Step 3: Core Logic
        core_files = [f for f in file_analyses.keys() if f.endswith(('.py', '.js', '.ts', '.java'))][:5]
        if core_files:
            path.append({
                'step': 3,
                'title': 'Core Logic',
                'description': 'Understand the main business logic',
                'files_to_study': core_files,
                'key_points': ['Key algorithms', 'Data processing', 'Business rules']
            })
        
        # Step 4: Data Layer
        data_files = [f for f in file_analyses.keys() if any(name in f.lower() for name in ['model', 'data', 'db', 'storage'])]
        if data_files:
            path.append({
                'step': 4,
                'title': 'Data Layer',
                'description': 'Explore how data is handled',
                'files_to_study': data_files[:3],
                'key_points': ['Data models', 'Storage patterns', 'Database interactions']
            })
        
        # Step 5: Testing
        test_files = [f for f in file_analyses.keys() if 'test' in f.lower()]
        if test_files:
            path.append({
                'step': 5,
                'title': 'Testing',
                'description': 'Learn how the project is tested',
                'files_to_study': test_files[:3],
                'key_points': ['Test structure', 'Testing patterns', 'Quality assurance']
            })
        
        return path
    
    def _generate_introduction_section(self, repo_data: Dict[str, Any]) -> str:
        """Generate project introduction content"""
        return f"""
# Welcome to {repo_data['name']}

## Project Overview
{repo_data['description']}

## Key Statistics
- **Total Files**: {repo_data['file_count']}
- **Languages**: {', '.join(repo_data['languages'].keys())}
- **Project Size**: {repo_data['size_mb']} MB
- **Dependencies**: {sum(len(deps) for deps in repo_data['dependencies'].values())}

## What You'll Learn
This tutorial will guide you through understanding the {repo_data['name']} codebase, covering:
- Project architecture and design patterns
- Key components and their interactions
- Best practices demonstrated in the code
- How to contribute and extend the project

## Prerequisites
Before diving in, you should have:
- Basic knowledge of the primary languages used: {', '.join(repo_data['languages'].keys())}
- Understanding of common software development concepts
- Familiarity with the project's domain (based on README and structure)
"""
    
    def _generate_setup_section(self, repo_data: Dict[str, Any]) -> str:
        """Generate setup and installation content"""
        setup_content = """
# Setup and Installation

## Prerequisites
"""
        
        # Add language-specific setup
        if 'python' in repo_data['languages']:
            setup_content += """
### Python Setup
- Python 3.7 or higher
- pip package manager
- Virtual environment (recommended)
"""
        
        if 'javascript' in repo_data['languages']:
            setup_content += """
### JavaScript Setup
- Node.js (latest LTS recommended)
- npm or yarn package manager
"""
        
        setup_content += """
## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd """ + repo_data['name'] + """
   ```

2. **Install Dependencies**
"""
        
        # Add dependency installation
        if repo_data['dependencies'].get('python'):
            setup_content += """
   **Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
"""
        
        if repo_data['dependencies'].get('javascript'):
            setup_content += """
   **JavaScript dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```
"""
        
        setup_content += """
3. **Configuration**
   - Check for configuration files
   - Set up environment variables
   - Configure any required services

4. **Run the Project**
   - Follow instructions in README.md
   - Check for specific run commands
"""
        
        return setup_content
    
    def _generate_components_section(self, file_analyses: Dict[str, Any]) -> str:
        """Generate core components section"""
        content = """
# Core Components

## Key Files Overview
"""
        
        # Add top 5 most important files
        important_files = list(file_analyses.keys())[:5]
        for file_path in important_files:
            if file_path in file_analyses:
                analysis = file_analyses[file_path]['analysis']
                content += f"""
### {file_path}
{analysis.get('description', 'No description available')}
"""
        
        return content
    
    def _generate_architecture_section(self, repo_data: Dict[str, Any]) -> str:
        """Generate architecture section"""
        return f"""
# Architecture Deep Dive

## System Architecture
{repo_data['structure']}

## Technology Stack
{', '.join(repo_data['languages'].keys())}

## Dependencies
{json.dumps(repo_data['dependencies'], indent=2)}

## Design Patterns
Based on the codebase analysis, this project demonstrates several important design patterns and architectural decisions that we'll explore in detail.
"""
    
    def _generate_best_practices_section(self, file_analyses: Dict[str, Any]) -> str:
        """Generate best practices section"""
        return """
# Best Practices and Patterns

## Code Quality
This section highlights best practices demonstrated in the codebase:

### 1. Clean Code Principles
- Clear naming conventions
- Single responsibility principle
- DRY (Don't Repeat Yourself)

### 2. Documentation
- Inline comments where necessary
- README files for setup instructions
- API documentation

### 3. Testing
- Test structure and patterns
- Coverage considerations
- Test naming conventions

### 4. Error Handling
- Graceful error handling
- Logging practices
- User-friendly error messages
"""
    
    def export_markdown(self, tutorial: Dict[str, Any]) -> str:
        """Export tutorial as markdown"""
        markdown_content = f"""# {tutorial['metadata']['repository_name']} - Code Tutorial

Generated on: {tutorial['metadata']['generated_at']}

## Table of Contents
"""
        
        # Add sections
        for section in tutorial['tutorial_sections']:
            markdown_content += f"- [{section['title']}](#{section['title'].lower().replace(' ', '-')})\n"
        
        # Add content
        for section in tutorial['tutorial_sections']:
            markdown_content += f"\n## {section['title']}\n\n"
            markdown_content += section['content'] + "\n"
        
        return markdown_content
    
    def export_pdf(self, tutorial: Dict[str, Any]) -> str:
        """Export tutorial as PDF (placeholder - would need PDF library)"""
        # This would require a PDF generation library like reportlab
        # For now, return markdown content
        return self.export_markdown(tutorial)
