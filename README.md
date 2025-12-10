# AI Reading Assistant

A powerful AI-driven application designed to enhance reading comprehension and learning by providing intelligent text analysis, summarization, and interactive features.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Overview

AI Reading Assistant is an innovative tool that leverages artificial intelligence to help users:
- Understand complex texts more effectively
- Generate intelligent summaries
- Extract key concepts and insights
- Get real-time definitions and explanations
- Track reading progress and comprehension

Whether you're a student, researcher, or lifelong learner, this assistant makes reading more productive and engaging.

## Features

### Core Features
- **Intelligent Text Summarization**: Generate concise summaries of any text
- **Key Concept Extraction**: Automatically identify and highlight important terms
- **Real-time Explanations**: Get instant clarifications on difficult concepts
- **Reading Analytics**: Track reading time, comprehension level, and progress
- **Multi-language Support**: Process texts in multiple languages
- **Interactive Q&A**: Ask questions about the content and get AI-powered answers

### Advanced Features
- **Document Upload**: Support for PDF, DOCX, TXT, and other formats
- **Customizable Themes**: Dark mode, light mode, and custom color schemes
- **Offline Mode**: Basic features available without internet connection
- **Export Options**: Save summaries and notes in multiple formats
- **Integration**: API endpoints for third-party integrations

## Requirements

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: 2GB free space for installation and models
- **Python**: 3.8 or higher

### Dependencies
- Python 3.8+
- pip (Python package manager)
- Git (for cloning the repository)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/TMNadim/AI-Reading-Assistant.git
cd AI-Reading-Assistant
```

### Step 2: Create a Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Download Required Models

```bash
python setup.py
```

This will download the necessary AI models (~500MB). Internet connection required.

### Step 5: Verify Installation

```bash
python -m tests.test_installation
```

A success message should appear indicating everything is set up correctly.

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# API Configuration
API_HOST=localhost
API_PORT=5000
DEBUG=False

# AI Model Configuration
MODEL_TYPE=transformer
MAX_SUMMARY_LENGTH=150
CONFIDENCE_THRESHOLD=0.7

# Database Configuration
DATABASE_URL=sqlite:///data/assistant.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Optional: External API Keys
OPENAI_API_KEY=your_key_here
HUGGINGFACE_API_KEY=your_key_here
```

### Configuration Files

- **config/settings.yaml**: Application settings
- **config/models.json**: Model configurations
- **config/languages.json**: Supported languages

## Usage

### Running the Application

**Command Line Interface:**
```bash
python main.py
```

**Web Interface:**
```bash
python app.py
# Navigate to http://localhost:5000 in your browser
```

**API Server:**
```bash
python api_server.py
# API available at http://localhost:8000
```

### Basic Examples

#### Example 1: Summarize a Text

```python
from ai_reading_assistant import TextProcessor

processor = TextProcessor()
text = "Your long text here..."
summary = processor.summarize(text, max_length=100)
print(summary)
```

#### Example 2: Extract Key Concepts

```python
from ai_reading_assistant import KeywordExtractor

extractor = KeywordExtractor()
concepts = extractor.extract(text, top_n=10)
for concept in concepts:
    print(f"{concept['term']}: {concept['importance']}")
```

#### Example 3: Get Explanations

```python
from ai_reading_assistant import ExplanationEngine

engine = ExplanationEngine()
explanation = engine.explain("quantum entanglement")
print(explanation)
```

### Command Line Usage

```bash
# Summarize a file
python main.py summarize -f document.txt -l 100

# Extract keywords
python main.py extract -f document.txt -n 10

# Get text statistics
python main.py stats -f document.txt

# Interactive mode
python main.py interactive
```

## Project Structure

```
AI-Reading-Assistant/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.py                  # Setup and model download script
├── main.py                   # CLI entry point
├── app.py                    # Web application entry point
├── api_server.py             # API server entry point
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── text_processor.py    # Core text processing logic
│   │   ├── summarizer.py        # Summarization engine
│   │   ├── keyword_extractor.py # Keyword extraction
│   │   └── explanation.py       # Explanation engine
│   ├── models/
│   │   ├── model_loader.py      # Load pre-trained models
│   │   └── fine_tune.py         # Model fine-tuning utilities
│   ├── utils/
│   │   ├── text_utils.py        # Text utility functions
│   │   ├── file_handler.py      # File I/O operations
│   │   └── logger.py            # Logging configuration
│   └── api/
│       ├── routes.py            # API endpoints
│       └── middleware.py        # API middleware
│
├── frontend/
│   ├── index.html               # Main HTML file
│   ├── css/
│   │   └── style.css            # Styles
│   └── js/
│       └── app.js               # Frontend logic
│
├── config/
│   ├── settings.yaml            # Application configuration
│   ├── models.json              # Model configurations
│   └── languages.json           # Language settings
│
├── data/
│   ├── models/                  # Pre-trained models (auto-downloaded)
│   ├── cache/                   # Cached results
│   └── database.db              # Local database
│
├── tests/
│   ├── test_installation.py
│   ├── test_summarizer.py
│   ├── test_extractor.py
│   └── test_api.py
│
├── logs/                        # Application logs
├── .env.example                 # Example environment variables
└── .gitignore                   # Git ignore rules
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### Summarize Text
```
POST /summarize
Content-Type: application/json

{
  "text": "Your text here...",
  "max_length": 150,
  "style": "bullet_points"
}

Response:
{
  "summary": "...",
  "length": 120,
  "original_length": 1500,
  "compression_ratio": 0.08
}
```

#### Extract Keywords
```
POST /extract-keywords
Content-Type: application/json

{
  "text": "Your text here...",
  "top_n": 10,
  "min_frequency": 1
}

Response:
{
  "keywords": [
    {"term": "key", "frequency": 5, "importance": 0.95},
    ...
  ]
}
```

#### Get Explanation
```
POST /explain
Content-Type: application/json

{
  "term": "quantum entanglement",
  "detail_level": "intermediate"
}

Response:
{
  "term": "quantum entanglement",
  "explanation": "...",
  "examples": ["...", "..."],
  "related_terms": ["quantum mechanics", "..."]
}
```

#### Process Document
```
POST /process-document
Content-Type: multipart/form-data

file: <file>
analyze_type: "comprehensive"

Response:
{
  "filename": "document.pdf",
  "status": "processing",
  "job_id": "uuid...",
  "estimated_time": 45
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_summarizer.py -v

# Run with coverage
pytest --cov=src tests/
```

### Building from Source

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Build package
python setup.py build

# Create distribution
python setup.py sdist bdist_wheel
```

### Contributing Guidelines

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a Pull Request

## Troubleshooting

### Common Issues

**Issue: Models fail to download**
- Solution: Check internet connection and try running `python setup.py` again
- Alternatively, download models manually from: [model links]

**Issue: High memory usage**
- Solution: Reduce `max_summary_length` in config or process smaller chunks
- Use `--low-memory` flag: `python main.py --low-memory`

**Issue: API connection refused**
- Solution: Ensure the API server is running: `python api_server.py`
- Check if port 8000 is not in use: `lsof -i :8000`

**Issue: Import errors**
- Solution: Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

For more help, check [Issues](https://github.com/TMNadim/AI-Reading-Assistant/issues)

## Performance Tips

1. **Batch Processing**: Process multiple documents together for better efficiency
2. **Cache Results**: Enable caching to avoid reprocessing same content
3. **Model Selection**: Choose lighter models for faster processing on limited hardware
4. **Async Operations**: Use async API endpoints for non-blocking operations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- Built with [Hugging Face Transformers](https://huggingface.co/transformers/)
- Uses [NLTK](https://www.nltk.org/) for NLP tasks
- Powered by state-of-the-art language models

## Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/TMNadim/AI-Reading-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TMNadim/AI-Reading-Assistant/discussions)
- **Email**: support@example.com

---

**Last Updated**: December 10, 2025

For the latest updates and releases, visit the [GitHub Repository](https://github.com/TMNadim/AI-Reading-Assistant)
