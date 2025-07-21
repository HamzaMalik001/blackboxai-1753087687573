import re
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

from config import Config

def validate_github_url(url: str) -> bool:
    """Validate if the URL is a valid GitHub repository URL"""
    if not url:
        return False
    
    # Clean the URL
    url = url.strip()
    
    # GitHub URL patterns
    github_patterns = [
        r'^https?://github\.com/[\w\-]+/[\w\-]+/?$',
        r'^https?://github\.com/[\w\-]+/[\w\-]+\.git$',
        r'^https?://github\.com/[\w\-]+/[\w\-]+/tree/.*$',
        r'^https?://github\.com/[\w\-]+/[\w\-]+/blob/.*$',
        r'^git@github\.com:[\w\-]+/[\w\-]+\.git$'
    ]
    
    for pattern in github_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return True
    
    return False

def extract_repo_info(url: str) -> Dict[str, str]:
    """Extract owner and repo name from GitHub URL"""
    if not validate_github_url(url):
        raise ValueError("Invalid GitHub URL")
    
    # Clean URL
    url = url.strip()
    
    # Remove .git suffix
    if url.endswith('.git'):
        url = url[:-4]
    
    # Parse URL
    parsed = urlparse(url)
    
    # Extract path components
    path_parts = parsed.path.strip('/').split('/')
    
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub URL format")
    
    owner = path_parts[0]
    repo = path_parts[1]
    
    # Remove any additional path components
    repo = repo.split('/')[0]
    
    return {
        'owner': owner,
        'repo': repo,
        'full_name': f"{owner}/{repo}",
        'api_url': f"https://api.github.com/repos/{owner}/{repo}",
        'clone_url': f"https://github.com/{owner}/{repo}.git",
        'html_url': f"https://github.com/{owner}/{repo}"
    }

def get_repo_metadata(repo_info: Dict[str, str]) -> Dict[str, Any]:
    """Fetch repository metadata from GitHub API"""
    config = Config()
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'CodeCrackr/1.0'
    }
    
    if config.GITHUB_TOKEN:
        headers['Authorization'] = f'token {config.GITHUB_TOKEN}'
    
    try:
        response = requests.get(repo_info['api_url'], headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'name': data.get('name', ''),
            'full_name': data.get('full_name', ''),
            'description': data.get('description', ''),
            'language': data.get('language', ''),
            'size': data.get('size', 0),
            'stargazers_count': data.get('stargazers_count', 0),
            'forks_count': data.get('forks_count', 0),
            'open_issues_count': data.get('open_issues_count', 0),
            'topics': data.get('topics', []),
            'license': data.get('license', {}).get('name', 'Unknown'),
            'created_at': data.get('created_at', ''),
            'updated_at': data.get('updated_at', ''),
            'clone_url': data.get('clone_url', ''),
            'html_url': data.get('html_url', ''),
            'default_branch': data.get('default_branch', 'main'),
            'has_issues': data.get('has_issues', False),
            'has_projects': data.get('has_projects', False),
            'has_downloads': data.get('has_downloads', False),
            'has_wiki': data.get('has_wiki', False),
            'has_pages': data.get('has_pages', False)
        }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch repository metadata: {str(e)}")

def check_repo_accessibility(repo_info: Dict[str, str]) -> bool:
    """Check if repository is accessible (public)"""
    try:
        metadata = get_repo_metadata(repo_info)
        return True
    except Exception:
        return False

def get_repo_languages(repo_info: Dict[str, str]) -> Dict[str, int]:
    """Get repository languages and their byte counts"""
    config = Config()
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'CodeCrackr/1.0'
    }
    
    if config.GITHUB_TOKEN:
        headers['Authorization'] = f'token {config.GITHUB_TOKEN}'
    
    try:
        url = f"{repo_info['api_url']}/languages"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch repository languages: {str(e)}")

def get_repo_readme(repo_info: Dict[str, str]) -> Optional[str]:
    """Get repository README content"""
    config = Config()
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'CodeCrackr/1.0'
    }
    
    if config.GITHUB_TOKEN:
        headers['Authorization'] = f'token {config.GITHUB_TOKEN}'
    
    # Try different README file names
    readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
    
    for readme_file in readme_files:
        try:
            url = f"{repo_info['api_url']}/contents/{readme_file}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if it's base64 encoded
            import base64
            if 'content' in data:
                content = base64.b64decode(data['content']).decode('utf-8')
                return content
                
        except requests.exceptions.RequestException:
            continue
    
    return None

def get_repo_tree(repo_info: Dict[str, str], recursive: bool = True) -> List[Dict[str, Any]]:
    """Get repository file tree"""
    config = Config()
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'CodeCrackr/1.0'
    }
    
    if config.GITHUB_TOKEN:
        headers['Authorization'] = f'token {config.GITHUB_TOKEN}'
    
    try:
        url = f"{repo_info['api_url']}/git/trees/{repo_info.get('default_branch', 'main')}"
        params = {'recursive': '1' if recursive else '0'}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('tree', [])
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch repository tree: {str(e)}")

def validate_repo_size(repo_info: Dict[str, str], max_size_mb: int = 100) -> bool:
    """Validate repository size is within limits"""
    try:
        metadata = get_repo_metadata(repo_info)
        repo_size_mb = metadata.get('size', 0) / 1024  # GitHub returns size in KB
        
        return repo_size_mb <= max_size_mb
        
    except Exception:
        return False

def sanitize_github_url(url: str) -> str:
    """Sanitize and normalize GitHub URL"""
    if not url:
        return ''
    
    # Remove whitespace
    url = url.strip()
    
    # Ensure HTTPS
    if url.startswith('http://'):
        url = url.replace('http://', 'https://')
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    # Remove .git if present
    if url.endswith('.git'):
        url = url[:-4]
    
    return url

def is_private_repo(url: str) -> bool:
    """Check if repository is private (requires authentication)"""
    try:
        repo_info = extract_repo_info(url)
        metadata = get_repo_metadata(repo_info)
        return False  # If we can fetch metadata, it's public
    except Exception as e:
        # If we get 404, it might be private or doesn't exist
        if '404' in str(e):
            return True
        return False
