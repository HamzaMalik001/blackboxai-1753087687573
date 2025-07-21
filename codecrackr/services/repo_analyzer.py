import os
import git
import shutil
import fnmatch
from pathlib import Path
from typing import Dict, List, Any
import ast
import json
from datetime import datetime

from config import Config

class RepoAnalyzer:
    def __init__(self):
        self.config = Config()
        self.temp_dir = self.config.TEMP_DIR
    
    def analyze_repository(self, github_url: str) -> Dict[str, Any]:
        """Main method to analyze a GitHub repository"""
        repo_name = self._extract_repo_name(github_url)
        clone_path = os.path.join(self.temp_dir, f"{repo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        try:
            # Clone repository
            repo = self._clone_repository(github_url, clone_path)
            
            # Analyze repository structure
            repo_data = {
                'name': repo_name,
                'url': github_url,
                'clone_path': clone_path,
                'description': self._get_repo_description(repo),
                'structure': self._analyze_structure(clone_path),
                'files': self._analyze_files(clone_path),
                'dependencies': self._extract_dependencies(clone_path),
                'readme': self._extract_readme(clone_path),
                'languages': self._detect_languages(clone_path),
                'size_mb': self._get_directory_size(clone_path),
                'file_count': 0,
                'analyzed_at': datetime.now().isoformat()
            }
            
            repo_data['file_count'] = len(repo_data['files'])
            
            return repo_data
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path, ignore_errors=True)
            raise Exception(f"Repository analysis failed: {str(e)}")
    
    def _extract_repo_name(self, github_url: str) -> str:
        """Extract repository name from GitHub URL"""
        # Handle different GitHub URL formats
        if github_url.endswith('.git'):
            github_url = github_url[:-4]
        
        parts = github_url.rstrip('/').split('/')
        return f"{parts[-2]}_{parts[-1]}"
    
    def _clone_repository(self, github_url: str, clone_path: str) -> git.Repo:
        """Clone GitHub repository"""
        try:
            # Ensure temp directory exists
            os.makedirs(self.temp_dir, exist_ok=True)
            
            # Clone with depth=1 for faster cloning
            repo = git.Repo.clone_from(
                github_url, 
                clone_path,
                depth=1,
                single_branch=True
            )
            
            return repo
            
        except git.exc.GitCommandError as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def _get_repo_description(self, repo: git.Repo) -> str:
        """Get repository description from git config or README"""
        try:
            # Try to get description from git config
            config_reader = repo.config_reader()
            if config_reader.has_section('remote "origin"'):
                return "Repository cloned successfully"
            return "No description available"
        except:
            return "No description available"
    
    def _analyze_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository directory structure"""
        structure = {
            'directories': [],
            'root_files': [],
            'depth': 0,
            'tree': {}
        }
        
        try:
            # Get directory tree
            structure['tree'] = self._build_directory_tree(repo_path)
            
            # Get root level items
            for item in os.listdir(repo_path):
                item_path = os.path.join(repo_path, item)
                if os.path.isdir(item_path) and not self._should_ignore(item):
                    structure['directories'].append(item)
                elif os.path.isfile(item_path):
                    structure['root_files'].append(item)
            
            # Calculate max depth
            structure['depth'] = self._calculate_max_depth(repo_path)
            
        except Exception as e:
            print(f"Error analyzing structure: {e}")
        
        return structure
    
    def _build_directory_tree(self, path: str, max_depth: int = 3, current_depth: int = 0) -> Dict:
        """Build a nested directory tree structure"""
        if current_depth >= max_depth:
            return {}
        
        tree = {}
        try:
            for item in os.listdir(path):
                if self._should_ignore(item):
                    continue
                
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    tree[item] = {
                        'type': 'directory',
                        'children': self._build_directory_tree(item_path, max_depth, current_depth + 1)
                    }
                else:
                    tree[item] = {
                        'type': 'file',
                        'size': os.path.getsize(item_path) if os.path.exists(item_path) else 0
                    }
        except PermissionError:
            pass
        
        return tree
    
    def _analyze_files(self, repo_path: str) -> List[Dict[str, Any]]:
        """Analyze all relevant files in the repository"""
        files = []
        
        for root, dirs, filenames in os.walk(repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for filename in filenames:
                if self._should_ignore(filename):
                    continue
                
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, repo_path)
                
                # Check if file extension is supported
                _, ext = os.path.splitext(filename)
                if ext.lower() not in self.config.SUPPORTED_EXTENSIONS:
                    continue
                
                try:
                    file_info = self._analyze_single_file(file_path, relative_path)
                    if file_info:
                        files.append(file_info)
                except Exception as e:
                    print(f"Error analyzing file {relative_path}: {e}")
                    continue
        
        return files
    
    def _analyze_single_file(self, file_path: str, relative_path: str) -> Dict[str, Any]:
        """Analyze a single file"""
        try:
            file_size = os.path.getsize(file_path)
            
            # Skip very large files
            if file_size > 1024 * 1024:  # 1MB limit
                return None
            
            _, ext = os.path.splitext(file_path)
            language = self.config.SUPPORTED_EXTENSIONS.get(ext.lower(), 'unknown')
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            file_info = {
                'path': relative_path,
                'name': os.path.basename(file_path),
                'extension': ext,
                'language': language,
                'size': file_size,
                'lines': len(content.splitlines()),
                'content': content[:10000],  # Limit content size
                'analysis': {}
            }
            
            # Language-specific analysis
            if language == 'python':
                file_info['analysis'] = self._analyze_python_file(content)
            elif language in ['javascript', 'typescript']:
                file_info['analysis'] = self._analyze_js_file(content)
            
            return file_info
            
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def _analyze_python_file(self, content: str) -> Dict[str, Any]:
        """Analyze Python file using AST"""
        analysis = {
            'classes': [],
            'functions': [],
            'imports': [],
            'docstring': None
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    else:
                        module = node.module or ''
                        for alias in node.names:
                            analysis['imports'].append(f"{module}.{alias.name}")
            
            # Get module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                analysis['docstring'] = tree.body[0].value.value
                
        except SyntaxError:
            pass
        
        return analysis
    
    def _analyze_js_file(self, content: str) -> Dict[str, Any]:
        """Basic JavaScript/TypeScript file analysis"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': []
        }
        
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Function declarations
            if line.startswith('function ') or ' function ' in line:
                func_name = self._extract_js_function_name(line)
                if func_name:
                    analysis['functions'].append({'name': func_name, 'line': i})
            
            # Class declarations
            if line.startswith('class '):
                class_name = line.split()[1].split('(')[0].split('{')[0]
                analysis['classes'].append({'name': class_name, 'line': i})
            
            # Imports
            if line.startswith('import ') or line.startswith('const ') and 'require(' in line:
                analysis['imports'].append(line)
            
            # Exports
            if line.startswith('export ') or line.startswith('module.exports'):
                analysis['exports'].append(line)
        
        return analysis
    
    def _extract_js_function_name(self, line: str) -> str:
        """Extract function name from JavaScript line"""
        try:
            if 'function ' in line:
                parts = line.split('function ')
                if len(parts) > 1:
                    name_part = parts[1].split('(')[0].strip()
                    return name_part
        except:
            pass
        return None
    
    def _extract_dependencies(self, repo_path: str) -> Dict[str, List[str]]:
        """Extract project dependencies"""
        dependencies = {
            'python': [],
            'javascript': [],
            'java': [],
            'other': []
        }
        
        # Python dependencies
        requirements_files = ['requirements.txt', 'Pipfile', 'pyproject.toml', 'setup.py']
        for req_file in requirements_files:
            req_path = os.path.join(repo_path, req_file)
            if os.path.exists(req_path):
                dependencies['python'].extend(self._parse_python_requirements(req_path))
        
        # JavaScript dependencies
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            dependencies['javascript'].extend(self._parse_package_json(package_json))
        
        # Java dependencies
        pom_xml = os.path.join(repo_path, 'pom.xml')
        if os.path.exists(pom_xml):
            dependencies['java'].extend(self._parse_pom_xml(pom_xml))
        
        return dependencies
    
    def _parse_python_requirements(self, file_path: str) -> List[str]:
        """Parse Python requirements file"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before version specifiers)
                        pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
                        if pkg_name:
                            deps.append(pkg_name)
        except:
            pass
        return deps
    
    def _parse_package_json(self, file_path: str) -> List[str]:
        """Parse package.json dependencies"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in data:
                    deps.extend(data[dep_type].keys())
        except:
            pass
        return deps
    
    def _parse_pom_xml(self, file_path: str) -> List[str]:
        """Parse Maven pom.xml dependencies"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Simple regex-based parsing (could be improved with XML parser)
            import re
            artifact_pattern = r'<artifactId>(.*?)</artifactId>'
            matches = re.findall(artifact_pattern, content)
            deps.extend(matches)
        except:
            pass
        return deps
    
    def _extract_readme(self, repo_path: str) -> str:
        """Extract README content"""
        readme_files = ['README.md', 'README.txt', 'README.rst', 'README']
        
        for readme_file in readme_files:
            readme_path = os.path.join(repo_path, readme_file)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except:
                    try:
                        with open(readme_path, 'r', encoding='latin-1') as f:
                            return f.read()
                    except:
                        continue
        
        return "No README found"
    
    def _detect_languages(self, repo_path: str) -> Dict[str, int]:
        """Detect programming languages and their file counts"""
        languages = {}
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for file in files:
                if self._should_ignore(file):
                    continue
                
                _, ext = os.path.splitext(file)
                if ext.lower() in self.config.SUPPORTED_EXTENSIONS:
                    lang = self.config.SUPPORTED_EXTENSIONS[ext.lower()]
                    languages[lang] = languages.get(lang, 0) + 1
        
        return languages
    
    def _should_ignore(self, name: str) -> bool:
        """Check if file/directory should be ignored"""
        for pattern in self.config.IGNORE_PATTERNS:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False
    
    def _calculate_max_depth(self, path: str, current_depth: int = 0) -> int:
        """Calculate maximum directory depth"""
        max_depth = current_depth
        
        try:
            for item in os.listdir(path):
                if self._should_ignore(item):
                    continue
                
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    depth = self._calculate_max_depth(item_path, current_depth + 1)
                    max_depth = max(max_depth, depth)
        except PermissionError:
            pass
        
        return max_depth
    
    def _get_directory_size(self, path: str) -> float:
        """Get directory size in MB"""
        total_size = 0
        
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    pass
        
        return round(total_size / (1024 * 1024), 2)  # Convert to MB
