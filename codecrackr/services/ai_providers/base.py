from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Base class for all AI providers"""
    
    def __init__(self, name: str, api_key: str = None):
        self.name = name
        self.api_key = api_key
        self.enabled = bool(api_key)
    
    @abstractmethod
    def generate_file_analysis(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis for a single file"""
        pass
    
    @abstractmethod
    def generate_repository_summary(self, repo_data: Dict[str, Any], file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall repository summary"""
        pass
    
    @abstractmethod
    def generate_architecture_diagram(self, repo_data: Dict[str, Any]) -> str:
        """Generate Mermaid diagram for repository architecture"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available (has valid API key)"""
        return self.enabled
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information for this provider"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "has_api_key": bool(self.api_key)
        }
