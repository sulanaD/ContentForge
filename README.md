# 🚀 ContentForge AI - Multi-Agent Content Creation Orchestrator

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Framework-Flask-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status">
</p>

**ContentForge AI** is an intelligent multi-agent workflow orchestrator that automates the entire content creation pipeline. From research to SEO optimization, this system coordinates specialized AI agents to produce high-quality, human-like content that meets your exact specifications.

## ✨ Features

### 🤖 Multi-Agent Architecture
- **Research Agent** - Gathers information from Wikipedia, web sources, and knowledge bases
- **Writer Agent** - Generates structured, engaging content from research data
- **Humanization Agent** - Transforms AI-generated text into natural, human-like writing
- **Editor Agent** - Polishes grammar, style, readability, and coherence
- **SEO Agent** - Optimizes content for search engines with keywords and meta descriptions
- **QA Agent** - Validates content meets requirements and triggers regeneration if needed

### 🔄 Intelligent Workflow Management
- **Automated Pipeline** - Seamlessly coordinates all agents in sequence
- **Quality Assurance Loop** - Automatically regenerates content that doesn't meet specifications
- **Customizable Workflows** - Choose from preset templates or create custom pipelines
- **Real-time Progress Tracking** - Monitor each stage via WebSocket updates

### 🧠 LLM Integration (Optional)
- **OpenAI** (GPT-4, GPT-3.5-Turbo)
- **Anthropic** (Claude 3)
- **Ollama** (Local models like Llama 2)
- **Template Fallback** - Works without any API keys using rule-based generation

### 🌐 Modern Web Interface
- Clean, responsive design
- Real-time workflow progress visualization
- One-click content generation
- Export-ready Markdown output

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Architecture](#-architecture)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🛠️ Installation

### Prerequisites

- Python 3.10 or higher
- pip or conda package manager
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/sulanaD/Creative-Writing-Multi-Agent-Workflow.git
cd Creative-Writing-Multi-Agent-Workflow
```

### Step 2: Create Virtual Environment

**Using Conda (Recommended):**
```bash
conda create -n contentforge python=3.10
conda activate contentforge
```

**Using venv:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet'); nltk.download('stopwords')"
```

---

## 🚀 Quick Start

### Start the Web Interface

```bash
python start_web_interface.py
```

Open your browser and navigate to: **http://localhost:5000**

### Run via Command Line

```python
from orchestrator.workflow_manager import WorkflowManager

# Initialize the workflow manager
wm = WorkflowManager()

# Run a content creation workflow
result = wm.run_workflow(
    topic="Benefits of Remote Work",
    workflow_type="quick_post",
    content_type="blog_post",
    target_platform="linkedin",
    custom_parameters={
        "word_count": 700,
        "tone": "professional"
    }
)

# Access the generated content
if result["success"]:
    print(result["output"]["content"])
```

---

## ⚙️ Configuration

### LLM API Keys (Optional)

For enhanced AI-powered content generation, configure your API keys:

**Option 1: Environment Variables**
```bash
# Windows
set OPENAI_API_KEY=your-openai-key
set ANTHROPIC_API_KEY=your-anthropic-key

# Linux/Mac
export OPENAI_API_KEY=your-openai-key
export ANTHROPIC_API_KEY=your-anthropic-key
```

**Option 2: Configuration File**

Edit `config/settings.json`:
```json
{
  "llm": {
    "openai": {
      "api_key": "your-openai-key",
      "model": "gpt-3.5-turbo"
    },
    "anthropic": {
      "api_key": "your-anthropic-key",
      "model": "claude-3-sonnet-20240229"
    }
  }
}
```

### Workflow Settings

Customize agent behavior in `config/settings.json`:

| Setting | Description | Default |
|---------|-------------|---------|
| `agents.writer.default_word_count` | Target word count | 1000 |
| `agents.humanizer.min_improvement_threshold` | Minimum humanization improvement | 5.0 |
| `agents.seo.target_keyword_density` | SEO keyword density target | 1.5% |
| `qa_agent.word_count_tolerance` | Acceptable word count deviation | 20% |
| `qa_agent.max_regeneration_attempts` | Max content regeneration tries | 3 |

---

## 📖 Usage

### Workflow Types

| Workflow | Agents Used | Best For |
|----------|-------------|----------|
| `quick_post` | Research → Writer → Humanizer | Social media, short posts |
| `content_creation_only` | Research → Writer → Humanizer → Editor | Blog posts, articles |
| `full_content_creation` | All agents including SEO & Publisher | Full SEO-optimized content |
| `humanize_existing` | Humanizer → Editor → SEO | Improving existing AI content |

### Content Types

- `blog_post` - Standard blog articles (800-2500 words)
- `article` - Long-form articles with citations (1200-3500 words)
- `social_post` - Social media content (50-300 words)
- `guide` - How-to guides and tutorials (1000-4000 words)

### Target Platforms

- `linkedin` - Professional networking
- `medium` - Long-form blogging
- `wordpress` - General blogging
- `twitter` - Short-form social
- `facebook` - Social media

### Tone Options

- `professional` - Formal business tone
- `casual` - Friendly, conversational
- `informative_engaging` - Educational with engagement
- `instructional` - Step-by-step guidance

---

## 🔌 API Reference

### REST Endpoints

#### Start Workflow
```http
POST /api/start-workflow
Content-Type: application/json

{
  "topic": "Your Topic",
  "workflowType": "quick_post",
  "contentType": "blog_post",
  "targetPlatform": "linkedin",
  "wordCount": 700,
  "tone": "professional"
}
```

#### Get Workflow Status
```http
GET /api/workflow-status/{workflow_id}
```

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `workflow_update` | Server → Client | Real-time progress updates |
| `workflow_complete` | Server → Client | Workflow finished |
| `workflow_error` | Server → Client | Error occurred |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Interface                            │
│                   (Flask + SocketIO)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Workflow Manager                           │
│              (Orchestrates Agent Pipeline)                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Research    │   │    Writer     │   │ Humanization  │
│    Agent      │──▶│    Agent      │──▶│    Agent      │
└───────────────┘   └───────────────┘   └───────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│    Editor     │   │     SEO       │   │      QA       │
│    Agent      │──▶│    Agent      │──▶│    Agent      │
└───────────────┘   └───────────────┘   └───────────────┘
                                              │
                                              ▼
                                    ┌───────────────────┐
                                    │  Pass? Complete   │
                                    │  Fail? Regenerate │
                                    └───────────────────┘
```

### Directory Structure

```
contentforge-ai/
├── agents/                    # Agent implementations
│   ├── base_agent.py         # Base class for all agents
│   ├── research_agent.py     # Web research & data gathering
│   ├── writer_agent.py       # Content generation
│   ├── humanization_agent.py # AI-to-human text conversion
│   ├── editor_agent.py       # Grammar & style correction
│   ├── seo_agent.py          # Search optimization
│   └── qa_agent.py           # Quality assurance validation
├── orchestrator/
│   └── workflow_manager.py   # Main workflow coordinator
├── frontend/
│   ├── app.py               # Flask web application
│   └── templates/
│       └── index.html       # Web interface
├── utils/
│   ├── config.py            # Configuration management
│   ├── logger.py            # Logging utilities
│   └── llm_integration.py   # LLM provider integrations
├── config/
│   └── settings.json        # Application configuration
├── tests/                    # Test suite
├── requirements.txt          # Python dependencies
├── start_web_interface.py    # Web server entry point
└── README.md                 # This file
```

---

## 🧪 Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Test Individual Agents

```bash
python test_full_system.py
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and descriptive

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- NLP powered by [NLTK](https://www.nltk.org/)
- Readability analysis via [textstat](https://pypi.org/project/textstat/)
- Research data from [Wikipedia](https://www.wikipedia.org/)

---

## 📬 Contact

**Sulana Dulwan** - [@sulanaD](https://github.com/sulanaD)

Project Link: [https://github.com/sulanaD/Creative-Writing-Multi-Agent-Workflow](https://github.com/sulanaD/Creative-Writing-Multi-Agent-Workflow)

---

<p align="center">Made with ❤️ for content creators everywhere</p>
