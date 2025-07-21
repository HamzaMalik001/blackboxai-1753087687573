import requests
import json
import logging
from typing import Dict, Any, List
from .base import AIProvider

logger = logging.getLogger(__name__)

class OpenRouterProvider(AIProvider):
    """OpenRouter API provider implementation"""
    
    def __init__(self, api_key: str = None):
        super().__init__("OpenRouter", api_key)
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate_file_analysis(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis for a single file using OpenRouter"""
        if not self.is_available():
            return self._mock_file_analysis(file_info)
        
        try:
            prompt = self._get_file_analysis_prompt()
            content = file_info.get('content', '')
            if len(content) > 4000:
                content = content[:4000] + "... [truncated]"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://codecrackr.app",
                "X-Title": "CodeCrackr"
            }
            
            data = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Analyze this {file_info['language']} file: {file_info['name']}\n\n{content}"}
                ],
                "temperature": 0.1,
                "max_tokens": 1000
            }
            
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()["choices"][0]["message"]["content"]
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {
                        "file_name": file_info['name'],
                        "description": result,
                        "key_components": [],
                        "purpose": "File analysis",
                        "dependencies": [],
                        "complexity": "medium"
                    }
            except:
                return {
                    "file_name": file_info['name'],
                    "description": result,
                    "key_components": [],
                    "purpose": "File analysis",
                    "dependencies": [],
                    "complexity": "medium"
                }
                
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return self._mock_file_analysis(file_info)
    
    def generate_repository_summary(self, repo_data: Dict[str, Any], file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate repository summary using OpenRouter"""
        if not self.is_available():
            return self._mock_repository_summary(repo_data)
        
        try:
            prompt = self._get_repository_summary_prompt()
            
            repo_info = {
                "name": repo_data['name'],
                "languages": repo_data.get('languages', {}),
                "file_count": repo_data.get('file_count', 0),
                "size_mb": repo_data.get('size_mb', 0)
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://codecrackr.app",
                "X-Title": "CodeCrackr"
            }
            
            data = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Generate summary for: {json.dumps(repo_info, indent=2)}"}
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()["choices"][0]["message"]["content"]
            try:
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return self._mock_repository_summary(repo_data)
            except:
                return self._mock_repository_summary(repo_data)
                
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return self._mock_repository_summary(repo_data)
    
    def generate_architecture_diagram(self, repo_data: Dict[str, Any]) -> str:
        """Generate architecture diagram using OpenRouter"""
        if not self.is_available():
            return self._mock_architecture_diagram(repo_data)
        
        try:
            prompt = """Generate a Mermaid diagram showing the high-level architecture of this repository."""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://codecrackr.app",
                "X-Title": "CodeCrackr"
            }
            
            data = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Repository: {repo_data['name']}, Languages: {repo_data.get('languages', {})}"}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return self._mock_architecture_diagram(repo_data)
    
    def _get_file_analysis_prompt(self) -> str:
        return """You are an expert code analyst. Analyze the provided code file and generate a comprehensive tutorial-style explanation in JSON format."""
    
    def _get_repository_summary_prompt(self) -> str:
        return """You are a technical writer. Generate a comprehensive repository summary and tutorial structure in JSON format."""
    
    def _mock_file_analysis(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "file_name": file_info['name'],
            "description": f"OpenRouter analysis for {file_info['language']} file",
            "key_components": [{"name": "main", "type": "function", "description": "Main functionality", "line_number": 1}],
            "purpose": "Core functionality",
            "dependencies": ["standard library"],
            "complexity": "medium"
        }
    
    def _mock_repository_summary(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "repository_name": repo_data['name'],
            "overview": "OpenRouter-powered repository analysis",
            "architecture": {"description": "Modular architecture"},
            "key_features": [{"name": "Core", "description": "Main features"}],
            "tutorial_sections": [{"title": "Getting Started", "description": "Introduction", "difficulty": "beginner"}],
            "learning_path": [{"step": 1, "title": "Overview", "description": "Understand the project"}],
            "technical_stack": list(repo_data.get('languages', {}).keys()),
            "complexity_level": "medium"
        }
    
    def _mock_architecture_diagram(self, repo_data: Dict[str, Any]) -> str:
        return f"""graph TD
    A[{repo_data['name']}] --> B[OpenRouter Analysis]
    B --> C[Files: {repo_data.get('file_count', 0)}]
    B --> D[Languages: {', '.join(repo_data.get('languages', {}).keys())}]"""
