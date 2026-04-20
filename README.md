[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Build Status](https://github.com/Michael-Steenkamp/repo-readme-generator/actions/workflows/autoreadme.yml/badge.svg)](https://github.com/Michael-Steenkamp/repo-readme-generator/actions/workflows/autoreadme.yml)

<div align="center">
  <h1>🤖 AutoReadme AI</h1>
  <p><b>Keep your documentation perfectly in sync with your codebase.</b></p>
</div>

---

## 📖 Overview
<b>AutoReadme AI</b> is a server-less Git automation pipeline that updates your documentation. It dynamically fetches project state, requests updates from Large Language Models (LLMs), and submits changes via Pull Requests.

Stop writing READMEs. Start shipping code.

---

## 🏗️ Architecture & Phases

The AutoReadme AI pipeline operates in three phases:

### Phase A: Environment & Extraction
*   **Diff Extraction:** Extracts the latest Git diff (`HEAD~1 HEAD`).
*   **Tree Generation:** Creates a token-efficient directory tree.
*   **Custom Rules:** Applies exclusion rules via `.autoreadme.yml`.
*   **State Parsing:** Extracts hidden AI state from `README.md` for continuous context.

### Phase B: The AI Pipeline
*   **Payload Compilation:** Compiles a context-rich prompt.
*   **Tiered LLM Routing:** Routes requests based on payload size (small diffs to fast models, large changes to heavy models).
*   **State Injection:** Injects rolling-state memory.
*   **Execution & Sanitization:** Enforces raw-markdown output and sanitizes responses using Regex.

### Phase C: Version Control Reconciliation
*   **Cloud Execution:** Utilizes GitHub Actions to run the pipeline on push, automatically opening PRs with updated documentation.

---

<h2>✨ Key Features</h2>
<ul>
  <li>📦 <b>Plug-and-Play Action:</b> Integrate easily via a single <code>uses</code> step.</li>
  <li>🧠 <b>Rolling-State Memory:</b> Maintains context across pushes using hidden HTML comments in the README.</li>
  <li>📏 <b>Smart Git Diffing:</b> Falls back to a <code>--stat</code> summary for massive changes to protect API costs.</li>
  <li>🔀 <b>Tiered LLM Routing:</b> Dynamically selects the most efficient AI provider based on diff length.</li>
  <li>⚡ <b>Zero-Dependency Core:</b> Built with standard Python libraries for fast execution.</li>
</ul>

---

<h2>⚖️ Legal & Licensing</h2>
This project is distributed under the MIT License. A copy can be found in the <a href="LICENSE">LICENSE</a> file.

---

<h2>🚀 Getting Started</h2>
Integrate AutoReadme AI directly into your repository using the official GitHub Action. It runs in the cloud, automatically opening PRs with documentation updates on code pushes.

<h3>1. Initialize the Repository</h3>
Create your GitHub repository and clone it. The engine can generate a fresh `README.md` if none exists.

<h3>2. Grant Pull Request Permissions</h3>
Configure repository settings to allow the Action to open PRs.
<ul>
  <li>Go to your repository on GitHub.</li>
  <li>Navigate to <b>Settings</b> > <b>Actions</b> > <b>General</b>.</li>
  <li>Scroll to <b>Workflow permissions</b>.</li>
  <li>Check <b>Allow GitHub Actions to create and approve pull requests</b>.</li>
  <li>Click <b>Save</b>.</li>
</ul>

<h3>3. Add Your API Keys (Repository Secrets)</h3>
Store your API keys securely for the GitHub runner. Only add keys for models you plan to use.

<p><b>🔑 Get your API Keys here:</b></p>
<ul>
  <li><b>Gemini:</b> <a href="https://aistudio.google.com/app/apikey">Google AI Studio</a></li>
  <li><b>OpenAI:</b> <a href="https://platform.openai.com/api-keys">OpenAI Platform</a></li>
  <li><b>Anthropic:</b> <a href="https://console.anthropic.com/settings/keys">Anthropic Console</a></li>
</ul>

<p><b>Via the Web UI:</b></p>
<ul>
  <li>Go to <b>Settings</b> > <b>Security</b> > <b>Secrets and variables</b> > <b>Actions</b>.</li>
  <li>Click <b>New repository secret</b>.</li>
  <li>Name it exactly <code>GEMINI_API_KEY</code> and paste your key.</li>
  <li><i>(Optional)</i> Repeat for <code>OPENAI_API_KEY</code> or <code>ANTHROPIC_API_KEY</code>.</li>
</ul>

<p><b>Via the Terminal:</b></p>
Use the GitHub CLI to inject secrets:

```bash
gh secret set GEMINI_API_KEY --body "your_actual_api_key_here"
```

<h3>4. Add the Workflow</h3>
Create `.github/workflows/autoreadme.yml` with this configuration:

```yml
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
```

<h3>5. Push and Trigger!</h3>
Commit your new workflow file and push it to the `main` branch. This push will trigger the GitHub Action, which will generate a README based on your project and open a Pull Request.

<!-- AI_STATE_START
{
  "summary": "AutoReadme AI's core architecture is fully implemented, encompassing environment extraction, tiered LLM routing, and version control reconciliation. The AI state extraction has been enhanced for robustness, and output sanitization, zero-dependency execution, and comprehensive setup for GitHub Actions and local workflows are in place. The system's styling configuration has been updated to adopt a minimalist theme and to include markdown badges, ensuring a clean and informative project overview."
}
AI_STATE_END -->
