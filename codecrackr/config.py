import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    # Application Settings
    MAX_REPO_SIZE_MB = int(os.getenv('MAX_REPO_SIZE_MB', '100'))
    TEMP_DIR_CLEANUP_HOURS = int(os.getenv('TEMP_DIR_CLEANUP_HOURS', '24'))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '10'))
    
    # LLM Configuration
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'openai/gpt-4o')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '4000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.1'))
    
    # Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript', 
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.sql': 'sql',
        '.sh': 'bash',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.html': 'html',
        '.css': 'css',
        '.md': 'markdown',
        '.txt': 'text'
    }
    
    # Files to ignore
    IGNORE_PATTERNS = [
        '__pycache__',
        '.git',
        '.gitignore',
        'node_modules',
        '.env',
        '.venv',
        'venv',
        'env',
        '.DS_Store',
        'Thumbs.db',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '*.so',
        '*.egg',
        '*.egg-info',
        'dist',
        'build',
        '.pytest_cache',
        '.coverage',
        'coverage.xml',
        '*.log',
        '.idea',
        '.vscode',
        '*.min.js',
        '*.min.css',
        'package-lock.json',
        'yarn.lock',
        'Pipfile.lock'
    ]
