# 🛠️ Coder Buddy

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green.svg)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/Groq-API-orange.svg)](https://groq.com/)

An **AI-powered autonomous coding assistant** that transforms natural language descriptions into fully functional projects. Built with [LangGraph](https://github.com/langchain-ai/langgraph) and powered by [Groq](https://groq.com/), Coder Buddy simulates a complete development team workflow—planning, architecture design, and implementation—all in one seamless agent pipeline.

## ✨ Features

- 🤖 **Multi-Agent Architecture** – Leverages specialized agents (Planner, Architect, Coder) for different development phases
- 💬 **Natural Language Input** – Simply describe what you want to build
- 📁 **Automatic File Generation** – Creates complete, working projects with proper file structure
- 🔧 **Real Developer Workflow** – Plans → Designs → Implements (just like a real development team)
- 🚀 **Fast & Efficient** – Uses Groq's fast inference for rapid project generation
- 🔄 **Iterative Refinement** – Automatically retries and handles errors gracefully
- 📝 **Context-Aware** – Each agent maintains context from previous stages

---

## 🏗️ Architecture

Coder Buddy uses a multi-agent orchestration pattern:

```
User Request
    ↓
[PLANNER AGENT] → Creates detailed project plan
    ↓
[ARCHITECT AGENT] → Breaks down into implementation tasks
    ↓
[CODER AGENT] → Implements each task and writes files
    ↓
Generated Project Files
```

### Agent Details

| Agent | Role | Output |
|-------|------|--------|
| **Planner** | Analyzes request and creates a structured project plan | JSON with project structure and features |
| **Architect** | Decomposes plan into granular, implementable tasks | Implementation steps with detailed context |
| **Coder** | Implements tasks using available tools (read/write files, run commands) | Complete, working source code files |

<div style="text-align: center;">
    <img src="resources/coder_buddy_diagram.png" alt="Coder Buddy Architecture Diagram" width="90%"/>
</div>

---

## 📋 Prerequisites

Before getting started, ensure you have:

- **Python 3.11+** installed
- **uv** package manager ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Groq API Key** ([Get one here](https://console.groq.com/keys))
- A code editor (VS Code, PyCharm, etc.)

---

## 🚀 Installation & Setup

### Step 1: Clone or Download the Project
```bash
git clone <repository-url>
cd coder-buddy
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
uv venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
uv pip install -r pyproject.toml
```

### Step 4: Configure Environment
Create a `.env` file in the project root:
```bash
cp .sample_env .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

### Step 5: Run the Application
```bash
python main.py
```

Generated projects will be created in the `generated_project/` directory.

---

## 💡 Usage Examples

### Example 1: To-Do List App
```
"Create a colorful modern to-do app with HTML, CSS, and JavaScript"
```
Generates: `index.html`, `styles.css`, `script.js` with full task management functionality

### Example 2: Calculator Web App
```
"Build a simple calculator web application with a clean interface"
```
Generates: `index.html`, `styles.css`, `script.js` with calculator logic

### Example 3: FastAPI Blog
```
"Create a simple blog API in FastAPI with SQLite database"
```
Generates: `main.py`, `models.py`, `database.py` with REST endpoints

---

## 📁 Project Structure

```
coder-buddy/
├── main.py                 # Application entry point
├── pyproject.toml          # Project dependencies
├── .env                    # Environment variables (create this)
├── agent/
│   ├── __init__.py
│   ├── graph.py           # LangGraph workflow orchestration
│   ├── states.py          # Pydantic state models
│   ├── prompts.py         # Agent system prompts
│   └── tools.py           # Tool definitions (file I/O, commands)
├── generated_project/     # Output directory for generated projects
├── resources/
│   ├── coder_buddy_diagram.png   # Architecture diagram
│   └── coder_buddy_diagram.mmd
├── README.md              # This file
└── uv.lock               # Dependency lock file
```

---

## ⚙️ Configuration

### Change the LLM Model
Edit `agent/graph.py`:
```python
llm = ChatGroq(model="openai/gpt-4-turbo")  # Change to desired model
```

Available models: [Groq API Documentation](https://console.groq.com/docs/speech-text)

### Adjust Retry Attempts
In `agent/graph.py`, modify:
```python
max_retries = 3  # Increase for better resilience, decrease for speed
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY not found` | Ensure `.env` file exists with valid API key |
| `Module not found: langchain` | Run `uv pip install -r pyproject.toml` |
| Generation times out | Check internet connection, verify API key, try simpler prompt |
| Incomplete code in files | Check console logs, system has automatic retry logic |

---

## 🔄 Recent Improvements

This project includes enhanced error handling and retry logic:
- **3-attempt retry mechanism** for robust error recovery
- **Smart JSON extraction** for better parsing of model responses
- **Fallback mechanisms** when standard tool calling fails
- **Improved prompts** with explicit formatting guidelines

See [FIXES_APPLIED.md](FIXES_APPLIED.md) for detailed changes.

---

## 🤝 Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📚 Learn More

- [LangGraph Documentation](https://github.com/langchain-ai/langgraph)
- [LangChain Documentation](https://python.langchain.com/)
- [Groq API Docs](https://console.groq.com/docs/speech-text)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 👥 About

Developed by **Codebasics Inc.** – Demonstrating the power of multi-agent AI systems for software development.

**Questions?** Open an issue on GitHub or contact support.

**Last Updated:** March 2026


