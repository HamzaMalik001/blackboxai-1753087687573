import os
import json
import logging
from typing import Dict, Any, List, Optional
from .ai_providers.base import AIProvider
from .ai_providers.openai_provider import OpenAIProvider
from .ai_providers.gemini_provider import GeminiProvider
from .ai_providers.openrouter_provider import OpenRouterProvider
from config import Config

logger = logging.getLogger(__name__)

class AIManager:
    """Manages multiple AI providers with fallback logic"""
    
    def __init__(self):
        self.config = Config()
        self.providers = {}
        self.load_providers()
    
    def load_providers(self):
        """Load all available AI providers"""
        # Load providers only when API keys are available
        self.providers = {}

        if self.config.OPENAI_API_KEY:
            self.providers["openai"] = OpenAIProvider(self.config.OPENAI_API_KEY)

        if getattr(self.config, "GEMINI_API_KEY", None):
            self.providers["gemini"] = GeminiProvider(self.config.GEMINI_API_KEY)

        if self.config.OPENROUTER_API_KEY:
            self.providers["openrouter"] = OpenRouterProvider(self.config.OPENROUTER_API_KEY)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [name for name, provider in self.providers.items() if provider.is_available()]
    
    def get_provider(self, provider_name: str = None) -> Optional[AIProvider]:
        """Get a specific provider or the best available one"""
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
            if provider.is_available():
                return provider
        
        # Fallback to first available provider
        for name, provider in self.providers.items():
            if provider.is_available():
                logger.info(f"Using provider: {name}")
                return provider
        
        # Return mock provider if none available
        logger.warning("No AI providers available, using mock responses")
        return self._create_mock_provider()
    
    def generate_file_analysis(self, file_info: Dict[str, Any], provider_name: str = None) -> Dict[str, Any]:
        """Generate file analysis using the best available provider"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.generate_file_analysis(file_info)
        return self._mock_file_analysis(file_info)
    
    def generate_repository_summary(self, repo_data: Dict[str, Any], file_analyses: List[Dict[str, Any]], provider_name: str = None) -> Dict[str, Any]:
        """Generate repository summary using the best available provider"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.generate_repository_summary(repo_data, file_analyses)
        return self._mock_repository_summary(repo_data)
    
    def generate_architecture_diagram(self, repo_data: Dict[str, Any], provider_name: str = None) -> str:
        """Generate architecture diagram using the best available provider"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.generate_architecture_diagram(repo_data)
        return self._mock_architecture_diagram(repo_data)
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            name: provider.get_usage_info()
            for name, provider in self.providers.items()
        }
    
    def _create_mock_provider(self) -> AIProvider:
        """Create a mock provider for testing"""
        class MockProvider(AIProvider):
            def __init__(self):
                super().__init__("Mock", "mock_key")
            
            def generate_file_analysis(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
                return self._mock_file_analysis(file_info)
            
            def generate_repository_summary(self, repo_data: Dict[str, Any], file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
                return self._mock_repository_summary(repo_data)
            
            def generate_architecture_diagram(self, repo_data: Dict[str, Any]) -> str:
                return self._mock_architecture_diagram(repo_data)
            
            def _mock_file_analysis(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "file_name": file_info['name'],
                    "description": f"Mock analysis for {file_info['language']} file",
                    "key_components": [{"name": "main", "type": "function", "description": "Main functionality"}],
                    "purpose": "Core functionality",
                    "dependencies": ["standard library"],
                    "complexity": "medium"
                }
            
            def _mock_repository_summary(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "repository_name": repo_data['name'],
                    "overview": "Mock repository analysis",
                    "architecture": {"description": "Modular architecture"},
                    "key_features": [{"name": "Core", "description": "Main features"}],
                    "tutorial_sections": [{"title": "Getting Started", "description": "Introduction", "difficulty": "beginner"}],
                    "learning_path": [{"step": 1, "title": "Overview", "description": "Understand the project"}],
                    "technical_stack": list(repo_data.get('languages', {}).keys()),
                    "complexity_level": "medium"
                }
            
            def _mock_architecture_diagram(self, repo_data: Dict[str, Any]) -> str:
                return f"""graph TD
    A[{repo_data['name']}] --> B[Mock Analysis]
    B --> C[Files: {repo_data.get('file_count', 0)}]
    B --> D[Languages: {', '.join(repo_data.get('languages', {}).keys())}]"""
        
        return MockProvider()
