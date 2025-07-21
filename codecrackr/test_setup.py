#!/usr/bin/env python3
"""
Test script to verify CodeCrackr setup
"""

import os
import sys
from pathlib import Path

# Add the codecrackr directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from config import Config
        print("✓ Config imported successfully")
        
        from services.repo_analyzer import RepoAnalyzer
        print("✓ RepoAnalyzer imported successfully")
        
        from services.llm_service import LLMService
        print("✓ LLMService imported successfully")
        
        from services.tutorial_generator import TutorialGenerator
        print("✓ TutorialGenerator imported successfully")
        
        from utils.github_utils import validate_github_url, extract_repo_info
        print("✓ GitHub utilities imported successfully")
        
        from utils.cleanup import cleanup_temp_files
        print("✓ Cleanup utilities imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        config = Config()
        
        print(f"✓ TEMP_DIR: {config.TEMP_DIR}")
        print(f"✓ MAX_REPO_SIZE_MB: {config.MAX_REPO_SIZE_MB}")
        print(f"✓ SUPPORTED_EXTENSIONS: {len(config.SUPPORTED_EXTENSIONS)} types")
        
        return True
        
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_github_utils():
    """Test GitHub URL validation"""
    print("\nTesting GitHub utilities...")
    
    try:
        from utils.github_utils import validate_github_url, extract_repo_info
        
        test_urls = [
            "https://github.com/user/repo",
            "https://github.com/user/repo.git",
            "https://github.com/user/repo/tree/main",
            "https://github.com/user/repo/blob/main/README.md",
            "invalid-url"
        ]
        
        for url in test_urls:
            is_valid = validate_github_url(url)
            print(f"✓ {url} -> {is_valid}")
            
            if is_valid:
                try:
                    info = extract_repo_info(url)
                    print(f"  Owner: {info['owner']}, Repo: {info['repo']}")
                except Exception as e:
                    print(f"  Error extracting info: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ GitHub utils error: {e}")
        return False

def test_directory_structure():
    """Test directory structure"""
    print("\nTesting directory structure...")
    
    required_dirs = [
        'templates',
        'static/css',
        'static/js',
        'static/images',
        'services',
        'utils',
        'temp'
    ]
    
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} missing")
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"  Created {dir_path}")
    
    return True

def test_environment():
    """Test environment setup"""
    print("\nTesting environment...")
    
    # Check if .env exists
    env_file = Path('.env')
    if env_file.exists():
        print("✓ .env file found")
    else:
        print("⚠ .env file not found, using .env.example")
        env_example = Path('.env.example')
        if env_example.exists():
            env_example.rename('.env')
            print("  Created .env from .env.example")
    
    # Check for API keys
    from config import Config
    config = Config()
    
    if config.OPENAI_API_KEY or config.OPENROUTER_API_KEY:
        print("✓ API key configured")
    else:
        print("⚠ No API key found. Please set OPENAI_API_KEY or OPENROUTER_API_KEY in .env")
    
    return True

def main():
    """Run all tests"""
    print("🔍 CodeCrackr Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_github_utils,
        test_directory_structure,
        test_environment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test failed: {e}")
            print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! CodeCrackr is ready to use.")
        print("\nNext steps:")
        print("1. Set your API key in .env file")
        print("2. Run: python app.py")
        print("3. Open http://localhost:8000 in your browser")
    else:
        print("❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
    
