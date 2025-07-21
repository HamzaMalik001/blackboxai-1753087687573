# CodeCrackr 🚀

Turn any GitHub repository into a comprehensive tutorial with AI-powered code analysis, architecture diagrams, and step-by-step learning guides.

## Features

- **🔍 Repository Analysis**: Deep analysis of code structure, patterns, and architecture
- **🤖 AI-Powered Insights**: GPT-4 powered explanations and tutorials
- **📊 Architecture Diagrams**: Visual representations with Mermaid.js
- **📚 Step-by-Step Guides**: Structured learning paths for any codebase
- **🎯 Multi-Language Support**: Python, JavaScript, TypeScript, Java, C++, and more
- **📤 Export Options**: Download tutorials as Markdown or PDF
- **⚡ Real-time Processing**: Live progress tracking and updates

## Quick Start

### Prerequisites

- Python 3.7+
- Git
- OpenAI API key or OpenRouter API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd codecrackr
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

### Environment Variables

Create a `.env` file with:

```bash
# Required: One of these
OPENAI_API_KEY=your_openai_api_key_here
# OR
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: For higher GitHub API limits
GITHUB_TOKEN=your_github_token_here

# Application settings
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
```

## Usage

1. **Start the application**: `python app.py`
2. **Open browser**: Navigate to `http://localhost:8000`
3. **Enter GitHub URL**: Paste any public GitHub repository URL
4. **Generate tutorial**: Click "Generate Tutorial" and wait for analysis
5. **Explore results**: Browse through sections, architecture diagrams, and file explanations

## API Endpoints

- `GET /` - Main page with input form
- `POST /analyze` - Start repository analysis
- `GET /status/<task_id>` - Check analysis progress
- `GET /results/<task_id>` - View generated tutorial
- `GET /export/<task_id>/<format>` - Export tutorial (markdown/pdf)

## Project Structure

```
codecrackr/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── services/             # Core business logic
│   ├── repo_analyzer.py  # Repository analysis
│   ├── llm_service.py    # AI integration
│   └── tutorial_generator.py  # Tutorial generation
├── utils/                # Utility functions
│   ├── github_utils.py   # GitHub API utilities
│   └── cleanup.py        # File cleanup utilities
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Main page
│   ├── results.html      # Tutorial display
│   └── error.html        # Error page
├── static/               # Static assets
│   ├── css/
│   │   └── styles.css    # Custom styles
│   └── js/
│       └── app.js        # Frontend JavaScript
└── temp/                 # Temporary storage
```

## Supported Languages

- Python
- JavaScript
- TypeScript
- Java
- C/C++
- C#
- Go
- Rust
- PHP
- Ruby
- Swift
- Kotlin
- Scala
- And more...

## Architecture

CodeCrackr uses a modular architecture:

1. **Frontend**: Modern HTML5 with Tailwind CSS and vanilla JavaScript
2. **Backend**: Flask web framework with RESTful API
3. **Analysis**: GitPython for repository cloning, AST parsing for code analysis
4. **AI Integration**: LangChain with OpenAI GPT-4 for intelligent explanations
5. **Storage**: Temporary file storage with automatic cleanup

## Development

### Running in Development
```bash
python app.py
```

### Running with Gunicorn (Production)
```bash
gunicorn app:app -b 0.0.0.0:8000 -w 4
```

### Docker Support
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]
```

## Deployment Options

### Railway
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

### Render
1. Create new web service
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn app:app`

### Heroku
1. Create Heroku app
2. Set buildpack: `heroku/python`
3. Deploy with Git

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Security

- Input validation and sanitization
- Rate limiting by IP
- Temporary file cleanup
- No sensitive data storage
- HTTPS enforcement in production

## Performance

- Asynchronous processing
- Background task management
- Efficient file filtering
- Token-based rate limiting
- Automatic resource cleanup

## Troubleshooting

### Common Issues

1. **"No API key configured"**
   - Set OPENAI_API_KEY or OPENROUTER_API_KEY in .env file

2. **"Repository too large"**
   - Increase MAX_REPO_SIZE_MB in config
   - Use smaller repositories for testing

3. **"GitHub rate limit exceeded"**
   - Add GITHUB_TOKEN for higher limits
   - Wait for rate limit reset

4. **"Analysis failed"**
   - Check repository is public
   - Verify URL format
   - Check network connectivity

## License

MIT License - see LICENSE file for details

## Support

- Create an issue on GitHub
- Check existing issues for solutions
- Join our community discussions

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Powered by [OpenAI GPT-4](https://openai.com/gpt-4)
- Inspired by [PocketFlow](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
