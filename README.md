<div align="center">
  <h1>🤖 AutoReadme AI</h1>
  <p><b>Keep your documentation perfectly in sync with your codebase.</b></p>
</div>

  <p align="center">
    <a href="https://github.com/Michael-Steenkamp/repo-readme-generator/actions"><img src="https://img.shields.io/badge/GitHub%20Actions-Active-blue.svg" alt="GitHub Actions Workflow Status"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.x-blue.svg" alt="Python Version"></a>
    <a href="https://github.com/Michael-Steenkamp/repo-readme-generator/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <a href="https://github.com/Michael-Steenkamp/repo-readme-generator/releases/latest"><img src="https://img.shields.io/badge/Release-v1.0.0-blue" alt="Action Release"></a>
  </p>

---

## 📖 Overview
<b>AutoReadme AI</b> is a robust, serverless Git automation pipeline designed to keep your project documentation perpetually updated. It intelligently extracts project state, routes update requests to large language models (LLMs), and seamlessly integrates changes via Pull Requests.

Stop writing READMEs. Start shipping code.

---

## 🏗️ Architecture & Phases

The AutoReadme AI pipeline operates in three core phases:

### Phase A: Environment & Extraction
*   **Diff Extraction:** Gathers the latest Git diff (`HEAD~1 HEAD`) for analysis.
*   **Tree Generation:** Constructs a token-efficient, LLM-friendly directory tree.
*   **Custom Rules:** Applies exclusion and inclusion rules defined in `.autoreadme.yml`.
*   **State Parsing:** Robustly extracts hidden AI state from `README.md` to maintain continuous context across runs.

### Phase B: The AI Pipeline
*   **Payload Compilation:** Assembles a comprehensive, context-rich prompt for the LLM.
*   **Tiered LLM Routing:** Intelligently routes requests to the most efficient AI provider based on payload size (e.g., small diffs to fast models, large changes to heavy models).
*   **State Injection:** Injects rolling-state memory to ensure context persistence.
*   **Execution & Sanitization:** Enforces raw-markdown output and rigorously sanitizes responses using Regex to ensure clean, valid documentation.

### Phase C: Version Control Reconciliation
*   **Cloud & Local Execution:** Designed to run seamlessly within GitHub Actions or as a local CLI tool, automating PRs with updated documentation or direct file modifications.

---

<h2>✨ Key Features</h2>
<ul>
  <li>📦 <b>Plug-and-Play Integration:</b> Seamlessly integrate via a single GitHub Action `uses` step or run as a local CLI tool.</li>
  <li>🧠 <b>Rolling-State Memory:</b> Maintains context across pushes by robustly extracting hidden HTML comments from the README, ensuring continuous, intelligent updates.</li>
  <li>📏 <b>Smart Git Diffing:</b> Optimizes API costs and performance by intelligently processing diffs, falling back to a `--stat` summary for massive changes.</li>
  <li>🔀 <b>Tiered LLM Routing:</b> Dynamically selects the most efficient AI provider (e.g., Gemini, OpenAI, Anthropic) based on diff length and task complexity.</li>
  <li>⚡ <b>Zero-Dependency Core:</b> Built with standard Python libraries for lightweight, fast, and reliable execution.</li>
  <li>🛡️ <b>Output Sanitization:</b> Guarantees clean, valid markdown output by enforcing strict formatting and sanitizing LLM responses using Regex.</li>
</ul>

---

<h2>⚖️ Legal & Licensing</h2>
This project is distributed under the MIT License. A copy can be found in the <a href="LICENSE">LICENSE</a> file.

---

<h2>🚀 Getting Started</h2>
Integrate AutoReadme AI directly into your repository using the official GitHub Action for cloud-based automation, or run it as a local command-line tool for immediate updates. It automatically opens PRs with documentation updates on code pushes (via GitHub Actions) or modifies files directly (via local execution).

<h3>1. Initialize the Repository</h3>
Create your GitHub repository and clone it. The engine can generate a fresh `README.md` if none exists.

<h3>2. Grant Pull Request Permissions (for GitHub Actions)</h3>
Configure repository settings to allow the Action to open PRs.
<ul>
  <li>Go to your repository on GitHub.</li>
  <li>Navigate to <b>Settings</b> > <b>Actions</b> > <b>General</b>.</li>
  <li>Scroll to <b>Workflow permissions</b>.</li>
  <li>Check <b>Allow GitHub Actions to create and approve pull requests</b>.</li>
  <li>Click <b>Save</b>.</li>
</ul>

<h3>3. Add Your API Keys (Repository Secrets or Environment Variables)</h3>
Store your API keys securely for the GitHub runner (as repository secrets) or set them as environment variables for local execution. Only add keys for models you plan to use.

<p><b>🔑 Get your API Keys here:</b></p>
<ul>
  <li><b>Gemini:</b> <a href="https://aistudio.google.com/app/apikey">Google AI Studio</a></li>
  <li><b>OpenAI:</b> <a href="https://platform.openai.com/api-keys">OpenAI Platform</a></li>
  <li><b>Anthropic:</b> <a href="https://console.anthropic.com/settings/keys">Anthropic Console</a></li>
</ul>

<p><b>Via GitHub Repository Secrets (for GitHub Actions):</b></p>
<ul>
  <li>Go to <b>Settings</b> > <b>Security</b> > <b>Secrets and variables</b> > <b>Actions</b>.</li>
  <li>Click <b>New repository secret</b>.</li>
  <li>Name it exactly <code>GEMINI_API_KEY</code> and paste your key.</li>
  <li><i>(Optional)</i> Repeat for <code>OPENAI_API_KEY</code> or <code>ANTHROPIC_API_KEY</code>.</li>
</ul>

<p><b>Via GitHub CLI:</b></p>
Use the GitHub CLI to inject secrets:

```bash
gh secret set GEMINI_API_KEY --body "your_actual_api_key_here"
```

<p><b>Via Local Environment Variables (for local execution):</b></p>

```bash
export GEMINI_API_KEY="your_actual_api_key_here"
# export OPENAI_API_KEY="your_actual_api_key_here"
# export ANTHROPIC_API_KEY="your_actual_api_key_here"
```

<h3>4. Add the GitHub Actions Workflow</h3>
Create `.github/workflows/autoreadme.yml` with this configuration:

```yml
# .autoreadme.yml
name: AI Documentation Update
on:
  push:
    branches: [ main ]
    paths-ignore: ['README.md'] # Prevents infinite loops!
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Run AutoReadme AI
        uses: Michael-Steenkamp/repo-readme-generator@v1
        with:
          gemini-api-key: ${{ secrets.GEMINI_API_KEY }}
          # Uncomment below if you set up heavy routing secrets
          # openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          # anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}

includePatterns:
  - "**/*.md"
  - "**/*.txt"
  - "**/*.xml"
  - "**/*.java"
  - "**/*.yaml"
  - "**/*.yml"
  - "**/*.cs"
  
excludePatterns:
  - ".mvn/**"
  - ".idea/**"
  - "target/**"
  - ".gitignore"
  - ".gitattributes"
  - ".github/**"
  - "node_modules/**"

routing:
  threshold_chars: 1500      # Diffs under this size use the fast model
  fast_provider: "gemini"    # Options: gemini, claude, openai
  heavy_provider: "openai"   # Options: gemini, claude, openai

style:
  theme: "developer-first"   # Options: developer-first, minimalist, executive, creative
  include_badges: true       # Set to false to prevent the AI from generating markdown badges
```

<h3>5. Push and Trigger GitHub Actions!</h3>
Commit your new workflow file and push it to the `main` branch. This push will trigger the GitHub Action, which will generate a README based on your project and open a Pull Request.

<h3>6. Run Locally (Optional)</h3>
For immediate feedback or local development, you can run AutoReadme AI directly via Python.

First, ensure you have Python 3.x installed and your API keys are set as environment variables (see Step 3).

```bash
# Clone the AutoReadme AI repository to run its script locally
git clone https://github.com/Michael-Steenkamp/repo-readme-generator.git
cd repo-readme-generator

# Run the update script from the project root (where your README.md is)
python script/update_readme.py
```
This command will update your `README.md` in place, incorporating the latest changes based on your project's state.

<!-- AI_STATE_START
{
  "summary": "AutoReadme AI's architecture is fully implemented, offering robust environment extraction, tiered LLM routing, and seamless version control reconciliation. Key enhancements include strengthened AI state extraction, comprehensive output sanitization, and the integration of a zero-dependency core that supports both GitHub Actions and local CLI execution. The system also features an updated styling configuration for minimalist themes and markdown badges, ensuring a clean and informative project overview."
}
AI_STATE_END -->
