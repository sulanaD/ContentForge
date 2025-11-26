# Contributing to ContentForge AI

First off, thank you for considering contributing to ContentForge AI! It's people like you that make this project better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. By participating, you are expected to uphold this commitment. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- Understanding of multi-agent systems (helpful but not required)

### Finding Issues to Work On

- Look for issues labeled `good first issue` for beginner-friendly tasks
- Issues labeled `help wanted` are great for contributions
- Feel free to ask questions on any issue

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

When reporting a bug, include:
- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **Environment details** (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please include:
- **Use case** - Why is this feature needed?
- **Proposed solution** - How should it work?
- **Alternatives considered** - Other approaches you've thought about

### Adding New Agents

To add a new agent:

1. Create a new file in `agents/` directory
2. Inherit from `BaseAgent` class
3. Implement required methods:
   - `setup()` - Initialize the agent
   - `process()` - Main processing logic
4. Add tests in `tests/` directory
5. Update documentation

Example agent structure:
```python
from agents.base_agent import BaseAgent, AgentInput, AgentOutput

class MyNewAgent(BaseAgent):
    def setup(self) -> None:
        # Initialize your agent
        pass
    
    def process(self, input_data: AgentInput) -> AgentOutput:
        # Process the input and return output
        pass
```

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   conda create -n contentforge-dev python=3.10
   conda activate contentforge-dev
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```
4. Run tests to ensure everything works:
   ```bash
   python -m pytest tests/ -v
   ```

## Pull Request Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our style guidelines

3. **Write/update tests** for your changes

4. **Update documentation** if needed

5. **Run the test suite**:
   ```bash
   python -m pytest tests/ -v
   ```

6. **Commit your changes**:
   ```bash
   git commit -m "Add: brief description of changes"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots if UI changes

### Commit Message Format

Use these prefixes:
- `Add:` New features
- `Fix:` Bug fixes
- `Update:` Updates to existing functionality
- `Refactor:` Code refactoring
- `Docs:` Documentation changes
- `Test:` Test additions/modifications

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) guidelines
- Use type hints for function parameters and returns
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Documentation Style

- Use docstrings for all public functions and classes
- Include examples in docstrings when helpful
- Keep comments concise and meaningful

### Example Code Style

```python
from typing import Dict, Any, Optional

def process_content(
    content: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process content with specified options.
    
    Args:
        content: The raw content to process
        options: Optional processing options
            - 'tone': Target tone (default: 'professional')
            - 'word_count': Target word count
    
    Returns:
        Dictionary containing:
            - 'processed_content': The processed content
            - 'metrics': Processing metrics
    
    Example:
        >>> result = process_content("Hello world", {'tone': 'casual'})
        >>> print(result['processed_content'])
    """
    if options is None:
        options = {}
    
    # Implementation here
    return {
        'processed_content': content,
        'metrics': {}
    }
```

## Questions?

Feel free to open an issue with questions or reach out to the maintainers.

Thank you for contributing! 🎉
