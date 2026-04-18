<div align="center">

# 🤖 AutoReadme AI
**Keep your documentation perfectly in sync with your codebase, without the developer friction.**

[![GitHub Actions Workflow Status](https://img.shields.io/badge/GitHub%20Actions-Active-blue.svg)](#)
[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](#)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

</div>

---

## 📖 Overview

**AutoReadme AI** is a server-less Git automation pipeline and developer tool designed to eliminate the chore of manual documentation updates. It dynamically fetches your project's state, requests intelligent documentation updates from Large Language Models (LLMs), and seamlessly utilizes the GitHub API to submit code changes via Pull Requests (or locally via Git hooks).

Stop writing READMEs. Start shipping code.

---

## 🏗️ Architecture & Phases of Development

The AutoReadme AI pipeline executes in three distinct, highly optimized phases:

### Phase A: Environment & Extraction
* **Diff Extraction:** Extracts the latest Git diff (`HEAD~1 HEAD`) using standard Python libraries.
* **Tree Generation:** Generates a token-efficient directory tree of your project.
* **Custom Rules:** Applies custom exclusion rules via a `.autoreadme.yml` configuration file to ignore irrelevant files.
* **State Parsing:** Parses the current `README.md` to extract hidden AI state memory for continuous context.

### Phase B: The AI Pipeline
* **Payload Compilation:** Compiles a strict, context-rich prompt payload.
* **Tiered LLM Routing:** Intelligently routes the request based on payload size—sending small diffs to fast models (like Gemini 2.5 Flash) and massive architectural shifts to heavy models (like GPT-4o).
* **State Injection:** Injects the rolling-state memory so the AI remembers past decisions.
* **Execution & Sanitization:** Enforces a strict raw-markdown output instruction and actively sanitizes the response using Regex to strip rogue formatting, backticks, or hallucinations.

### Phase C: Version Control Reconciliation
* **Dual-Environment Support:** Adapts to your preferred workflow.
    * *Cloud:* Utilizes GitHub Actions to run the script on push, automatically opening a new branch and Pull Request with the updated documentation.
    * *Local:* Leverages a custom `git autopush` command to run the script, bundle the README changes, and push everything in a single stroke.

---

## ✨ Key Features

* 🧠 **Rolling-State Memory:** Maintains context across pushes without needing an external database by using hidden HTML comments (`<!-- AI_STATE_START ... -->`) embedded directly in the README.
* 📏 **Smart Git Diffing:** Automatically falls back to a `--stat` summary if the code change is massive, protecting your API costs and preventing token limit breaches.
* 🔀 **Tiered LLM Routing:** Dynamically selects the most efficient AI provider based on the character length of the git diff.
* ⚡ **Zero-Dependency Core:** Built entirely using standard Python libraries (`urllib`, `subprocess`, `re`) to ensure lightning-fast execution and zero environment bloating.
* 🛡️ **Output Sanitization:** Employs strict Regex-based hallucination defense to ensure clean, perfectly formatted Markdown every time.

---

## 🔒 Security & Privacy

Your code is your business. AutoReadme AI is designed with strict security principles:

* **Stateless Architecture:** No external databases are used. Data is never stored permanently outside of your repository.
* **Secure Key Management:** API keys are never hardcoded. They are strictly managed via local environment variables or GitHub Actions Secrets.
* **Isolated Execution:** In the cloud workflow, the code is executed in ephemeral, isolated Ubuntu runners via GitHub Actions, leaving no trace behind.

---

## 🚀 Getting Started

Choose the workflow that best fits your development style.

### Option 1: Cloud Workflow (GitHub Actions) — *Recommended*

This method runs entirely in the cloud, automatically opening PRs with documentation updates whenever you push code.

1.  **Add the Script:** Copy `update_readme.py` into a `script/` folder in the root of your repository.
2.  **Add the Action:** Copy your GitHub Action YAML file into `.github/workflows/autoreadme.yml`.
3.  **Configure API Keys:** In your GitHub Repository, navigate to **Settings > Secrets and variables > Actions** and add your LLM API key (e.g., `GEMINI_API_KEY`).
4.  **Grant Permissions:** Go to **Settings > Actions > General**, scroll down to **Workflow permissions**, and check *"Allow GitHub Actions to create and approve pull requests"*.
5.  **Push:** Push your code normally. The bot will automatically open a PR with your updated documentation!

### Option 2: Local Workflow (Git Autopush)

This method updates the README locally and bundles it with your outgoing push. Ideal for solo developers who prefer terminal-driven workflows.

1.  **Add the Script:** Ensure `script/update_readme.py` is in your repository.
2.  **Export your API Key:** Set your key in your terminal session.
    * *Mac/Linux:*
        ```bash
        export GEMINI_API_KEY="your-key-here"
        ```
    * *Windows (PowerShell):*
        ```powershell
        $env:GEMINI_API_KEY="your-key-here"
        ```
3.  **Register the Custom Git Alias:** Run the following command in your terminal to create the `autopush` alias:
    ```bash
    git config --global alias.autopush '!f() { echo "🤖 Running AutoReadme..."; py script/update_readme.py; if git diff --name-only | grep -q "README.md"; then git add README.md && git commit -m "docs(ai): auto-update README"; fi; git push "$@"; }; f'
    ```
4.  **Push:** From now on, simply use the following command instead of `git push`:
    ```bash
    git autopush origin main
    ```

<!-- AI_STATE_START
{
  "summary": "AutoReadme AI core architecture is fully implemented and documented. The system supports three phases: Environment Extraction, AI Pipeline generation with tiered LLM routing (Gemini/OpenAI), and Version Control Reconciliation. It features regex-based output sanitization, zero-dependency Python execution, and dual-environment support. Setup instructions for both Cloud (GitHub Actions) and Local (git autopush alias) workflows are integrated."
}
AI_STATE_END -->